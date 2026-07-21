# app/services/contrato_service.py
"""
Servicio de gestión de contratos entre propietario y chofer
"""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo, Vehiculo, ChoferVehiculo
from app.models.auth import Usuario
from app.models.notification import Notificacion


class ContratoService:
    """Servicio para gestión de contratos"""

    @staticmethod
    async def solicitar_vinculacion(
        db: AsyncSession,
        chofer_id: uuid.UUID,
        vehiculo_id: uuid.UUID
    ) -> dict:
        """
        Chofer escanea QR y solicita vinculación
        """
        # Verificar vehículo
        vehiculo = await db.get(Vehiculo, vehiculo_id)
        if not vehiculo or not vehiculo.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado o inactivo"
            )

        # Verificar que el vehículo no tenga contrato activo
        contrato_activo = await db.execute(
            select(ContratoVehiculo)
            .where(
                and_(
                    ContratoVehiculo.vehiculo_id == vehiculo_id,
                    ContratoVehiculo.estado_contrato == 'ACTIVO'
                )
            )
        )
        if contrato_activo.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vehículo ya tiene un contrato activo"
            )

        # Verificar que el chofer no tenga contrato activo en otro vehículo
        chofer_contrato = await db.execute(
            select(ContratoVehiculo)
            .where(
                and_(
                    ContratoVehiculo.chofer_id == chofer_id,
                    ContratoVehiculo.estado_contrato == 'ACTIVO'
                )
            )
        )
        if chofer_contrato.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El chofer ya tiene un contrato activo con otro vehículo"
            )

        # Obtener propietario del vehículo
        propietario_rel = await db.execute(
            select(PropietarioVehiculo)
            .where(
                and_(
                    PropietarioVehiculo.vehiculo_id == vehiculo_id,
                    PropietarioVehiculo.activo == True
                )
            )
        )
        propietario = propietario_rel.scalar_one_or_none()
        if not propietario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vehículo no tiene un propietario asignado"
            )

        # Crear contrato en estado PENDIENTE_CONFIGURACION
        contrato = ContratoVehiculo(
            control_base_id=vehiculo.control_base_id,
            propietario_id=propietario.propietario_id,
            vehiculo_id=vehiculo_id,
            chofer_id=chofer_id,
            tipo_contrato='PORCENTAJE',  # Valor por defecto, propietario configurará
            turno_asignado='mañana',     # Valor por defecto, propietario configurará
            estado_contrato='PENDIENTE_CONFIGURACION',
            fecha_inicio=datetime.now()
        )
        db.add(contrato)
        await db.commit()
        await db.refresh(contrato)

        # Crear notificación para el propietario
        notificacion = Notificacion(
            usuario_id=propietario.propietario_id,
            titulo="Nueva solicitud de vinculación",
            mensaje=f"El chofer ha solicitado vincularse al vehículo {vehiculo.patente}",
            tipo="contrato_pendiente",
            leida=False
        )
        db.add(notificacion)
        await db.commit()

        return {
            "contrato_id": contrato.id,
            "estado": contrato.estado_contrato,
            "mensaje": "Solicitud enviada. Esperando configuración del propietario."
        }

    @staticmethod
    async def configurar_contrato(
        db: AsyncSession,
        contrato_id: uuid.UUID,
        propietario_id: uuid.UUID,
        tipo_contrato: str,
        turno_asignado: str,
        valor: float,
        duracion_max_horas: int = 12
    ) -> dict:
        """
        Propietario configura las condiciones del contrato
        """
        contrato = await db.get(ContratoVehiculo, contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato no encontrado"
            )

        # Verificar que el propietario sea el dueño del vehículo
        if contrato.propietario_id != propietario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para configurar este contrato"
            )

        # Verificar que el contrato esté pendiente
        if contrato.estado_contrato != 'PENDIENTE_CONFIGURACION':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El contrato ya fue configurado"
            )

        # Validar tipo de contrato
        tipos_validos = ['PORCENTAJE', 'MONTO_FIJO', 'AUTO_GESTION']
        if tipo_contrato not in tipos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de contrato inválido. Permitidos: {tipos_validos}"
            )

        # Validar turno
        turnos_validos = ['mañana', 'tarde', 'noche']
        if turno_asignado not in turnos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Turno inválido. Permitidos: {turnos_validos}"
            )

        # Actualizar contrato
        contrato.tipo_contrato = tipo_contrato
        contrato.turno_asignado = turno_asignado
        contrato.duracion_max_horas = duracion_max_horas

        if tipo_contrato == 'PORCENTAJE':
            if valor < 0 or valor > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El porcentaje debe estar entre 0 y 100"
                )
            contrato.porcentaje_chofer = valor
            contrato.monto_diario = None
        elif tipo_contrato == 'MONTO_FIJO':
            if valor <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El monto fijo debe ser mayor a 0"
                )
            contrato.monto_diario = valor
            contrato.porcentaje_chofer = None
        else:  # AUTO_GESTION
            contrato.porcentaje_chofer = None
            contrato.monto_diario = None

        contrato.estado_contrato = 'ACTIVO'
        contrato.fecha_inicio = datetime.now()
        await db.commit()
        await db.refresh(contrato)

        # Notificar al chofer que el contrato está activo
        notificacion = Notificacion(
            usuario_id=contrato.chofer_id,
            titulo="Contrato activado",
            mensaje=f"Tu contrato para el vehículo {contrato.vehiculo.patente} ha sido activado",
            tipo="contrato_activado",
            leida=False
        )
        db.add(notificacion)
        await db.commit()

        return {
            "contrato_id": contrato.id,
            "estado": contrato.estado_contrato,
            "mensaje": "Contrato configurado y activado exitosamente"
        }