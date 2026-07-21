# app/services/turno_service.py
"""
Servicio de gestión de turnos (Check-in / Check-out)
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo, Vehiculo, ChoferVehiculo
from app.models.turno import TurnoChofer
from app.models.gasto_turno import GastoTurno
from app.models.auth import Usuario
from app.models.trip import ViajeSolicitado
from app.services.liquidacion_service import LiquidacionService


class TurnoService:
    """Servicio para gestión de turnos de choferes"""

    @staticmethod
    async def check_in(
        db: AsyncSession,
        chofer_id: uuid.UUID,
        vehiculo_id: uuid.UUID,
        km_inicial: float,
        combustible_inicial: str
    ) -> dict:
        """
        Iniciar jornada laboral (Check-in)
        """
        # Validar combustibles
        combustibles_validos = ['RESERVA', '1/4', '1/2', '3/4', 'LLENO']
        if combustible_inicial not in combustibles_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Combustible inválido. Permitidos: {combustibles_validos}"
            )

        # Verificar que el vehículo existe y está activo
        vehiculo = await db.get(Vehiculo, vehiculo_id)
        if not vehiculo or not vehiculo.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado o inactivo"
            )

        # Verificar que el vehículo no tenga un turno activo
        turno_activo = await db.execute(
            select(TurnoChofer)
            .where(
                and_(
                    TurnoChofer.vehiculo_id == vehiculo_id,
                    TurnoChofer.estado == 'ACTIVO'
                )
            )
        )
        if turno_activo.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vehículo ya tiene un turno activo"
            )

        # Verificar que el chofer no haya superado las 12 horas en las últimas 24h
        hace_24h = datetime.now() - timedelta(hours=24)
        horas_trabajadas = await db.execute(
            select(func.sum(
                func.extract('epoch', TurnoChofer.fin_turno - TurnoChofer.inicio_turno) / 3600
            ))
            .where(
                and_(
                    TurnoChofer.chofer_id == chofer_id,
                    TurnoChofer.inicio_turno >= hace_24h,
                    TurnoChofer.estado != 'ACTIVO'
                )
            )
        )
        total_horas = horas_trabajadas.scalar() or 0
        if total_horas >= 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Límite de 12 horas de trabajo excedido en las últimas 24 horas"
            )

        # Obtener contrato activo del chofer con este vehículo
        contrato = await db.execute(
            select(ContratoVehiculo)
            .where(
                and_(
                    ContratoVehiculo.chofer_id == chofer_id,
                    ContratoVehiculo.vehiculo_id == vehiculo_id,
                    ContratoVehiculo.estado_contrato == 'ACTIVO'
                )
            )
        )
        contrato = contrato.scalar_one_or_none()
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes un contrato activo con este vehículo"
            )

        # Crear turno
        turno = TurnoChofer(
            contrato_id=contrato.id,
            chofer_id=chofer_id,
            vehiculo_id=vehiculo_id,
            estado='ACTIVO',
            km_inicial=km_inicial,
            combustible_inicial=combustible_inicial,
            inicio_turno=datetime.now()
        )
        db.add(turno)
        await db.commit()
        await db.refresh(turno)

        # Actualizar estado laboral del chofer en chofer_vehiculo
        chofer_vehiculo = await db.execute(
            select(ChoferVehiculo)
            .where(
                and_(
                    ChoferVehiculo.usuario_id == chofer_id,
                    ChoferVehiculo.vehiculo_id == vehiculo_id
                )
            )
        )
        chofer_vehiculo = chofer_vehiculo.scalar_one_or_none()
        if chofer_vehiculo:
            chofer_vehiculo.estado_laboral = 'ocupado'

        await db.commit()

        return {
            "turno_id": turno.id,
            "estado": turno.estado,
            "mensaje": "Jornada iniciada correctamente",
            "inicio_turno": turno.inicio_turno
        }

    @staticmethod
    async def check_out(
        db: AsyncSession,
        turno_id: uuid.UUID,
        chofer_id: uuid.UUID,
        km_final: float,
        combustible_final: str,
        recaudacion_ticketera: float = 0
    ) -> dict:
        """
        Cerrar turno y liquidar (Check-out)
        """
        # Validar combustibles
        combustibles_validos = ['RESERVA', '1/4', '1/2', '3/4', 'LLENO']
        if combustible_final not in combustibles_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Combustible inválido. Permitidos: {combustibles_validos}"
            )

        # Obtener turno
        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        # Verificar que el turno pertenezca al chofer
        if turno.chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para cerrar este turno"
            )

        # Verificar que el turno esté ACTIVO
        if turno.estado != 'ACTIVO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El turno ya está en estado {turno.estado}"
            )

        # Actualizar turno
        turno.km_final = km_final
        turno.combustible_final = combustible_final
        turno.recaudacion_ticketera_calle = recaudacion_ticketera
        turno.fin_turno = datetime.now()
        turno.estado = 'PENDIENTE_CONFIRMACION'

        await db.commit()
        await db.refresh(turno)

        # Calcular liquidación
        liquidacion = await LiquidacionService.calcular_liquidacion(db, turno.id)

        return {
            "turno_id": turno.id,
            "estado": turno.estado,
            "liquidacion": liquidacion
        }

    @staticmethod
    async def registrar_gasto(
        db: AsyncSession,
        turno_id: uuid.UUID,
        chofer_id: uuid.UUID,
        tipo_gasto: str,
        monto: float,
        km_registro: float = None,
        url_comprobante: str = None
    ) -> dict:
        """
        Registrar gasto durante el turno
        """
        tipos_validos = ['COMBUSTIBLE', 'LUBRICANTE', 'LAVADO', 'REPARACION', 'OTROS']
        if tipo_gasto not in tipos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de gasto inválido. Permitidos: {tipos_validos}"
            )

        # Verificar turno
        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        if turno.chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para registrar gastos en este turno"
            )

        if turno.estado != 'ACTIVO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden registrar gastos en turnos activos"
            )

        # Crear gasto
        gasto = GastoTurno(
            turno_id=turno.id,
            tipo_gasto=tipo_gasto,
            monto=monto,
            km_registro=km_registro,
            url_comprobante=url_comprobante
        )
        db.add(gasto)
        await db.commit()
        await db.refresh(gasto)

        return {
            "gasto_id": gasto.id,
            "mensaje": "Gasto registrado correctamente"
        }