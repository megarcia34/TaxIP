# app/services/contrato_service.py
"""
Servicio de gestión de contratos entre propietario y chofer
CON JORNADAS FLEXIBLES - SIN turno_asignado
"""

import uuid
from datetime import datetime, time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo, Vehiculo, ChoferVehiculo, PropietarioVehiculo
from app.models.auth import Usuario
from app.models.notification import Notificacion


class ContratoService:
    """Servicio para gestión de contratos con jornadas flexibles"""

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

        # ============================================================
        # CREAR CONTRATO CON JORNADAS FLEXIBLES
        # SIN turno_asignado (campo eliminado de la BD)
        # El contrato se crea en estado PENDIENTE_CONFIGURACION
        # El propietario deberá configurar los horarios (hora_inicio, hora_fin, dias_contractuales)
        # ============================================================
        contrato = ContratoVehiculo(
            control_base_id=vehiculo.control_base_id,
            propietario_id=propietario.propietario_id,
            vehiculo_id=vehiculo_id,
            chofer_id=chofer_id,
            tipo_contrato='PORCENTAJE',  # Valor por defecto, propietario configurará
            # Horarios flexibles - valores por defecto (propietario deberá configurar)
            hora_inicio=time(6, 0),  # 06:00 por defecto
            hora_fin=time(14, 0),    # 14:00 por defecto
            duracion_minima_horas=6,
            permite_extension=False,
            # Campos de alquiler
            canon_diario=None,
            km_incluidos_dia=None,
            valor_km_excedente=None,
            modalidad_computo='DIARIO',
            tratamiento_dia_no_trabajado='POR_DISPONIBILIDAD',
            dias_contractuales=[],
            dia_inicio_semana='lunes',
            compensacion_km='DIARIA',
            # Estado
            estado_contrato='PENDIENTE_CONFIGURACION',
            fecha_inicio=datetime.now(),
            porcentaje_chofer=70,  # Valor por defecto
            monto_diario=None
        )
        db.add(contrato)
        await db.commit()
        await db.refresh(contrato)

        # Crear notificación para el propietario
        notificacion = Notificacion(
            usuario_id=propietario.propietario_id,
            titulo="Nueva solicitud de vinculación",
            mensaje=f"El chofer ha solicitado vincularse al vehículo {vehiculo.patente}. "
                    f"Debes configurar los horarios y condiciones del contrato.",
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
        valor: float,
        hora_inicio: str,
        hora_fin: str,
        dias_contractuales: list,
        duracion_minima_horas: int = 6,
        permite_extension: bool = False,
        hora_fin_extension: Optional[str] = None,
        canon_diario: Optional[float] = None,
        km_incluidos_dia: Optional[float] = None,
        valor_km_excedente: Optional[float] = None,
        modalidad_computo: str = 'DIARIO',
        tratamiento_dia_no_trabajado: str = 'POR_DISPONIBILIDAD',
        dia_inicio_semana: str = 'lunes',
        compensacion_km: str = 'DIARIA'
    ) -> dict:
        """
        Propietario configura las condiciones del contrato con jornadas flexibles.
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
        tipos_validos = ['PORCENTAJE', 'ALQUILER', 'AUTO_GESTION']
        if tipo_contrato not in tipos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de contrato inválido. Permitidos: {tipos_validos}"
            )

        # Validar horarios
        try:
            hora_inicio_obj = datetime.strptime(hora_inicio, "%H:%M").time()
            hora_fin_obj = datetime.strptime(hora_fin, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de hora inválido. Use HH:MM"
            )

        if hora_fin_extension:
            try:
                hora_fin_extension_obj = datetime.strptime(hora_fin_extension, "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de hora de extensión inválido. Use HH:MM"
                )
        else:
            hora_fin_extension_obj = None

        # Validar días contractuales
        dias_validos = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        if dias_contractuales:
            for dia in dias_contractuales:
                if dia.lower() not in dias_validos:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Día inválido: {dia}. Permitidos: {dias_validos}"
                    )

        # Actualizar contrato
        contrato.tipo_contrato = tipo_contrato
        contrato.hora_inicio = hora_inicio_obj
        contrato.hora_fin = hora_fin_obj
        contrato.duracion_minima_horas = duracion_minima_horas
        contrato.permite_extension = permite_extension
        contrato.hora_fin_extension = hora_fin_extension_obj
        contrato.dias_contractuales = [d.lower() for d in dias_contractuales]
        contrato.dia_inicio_semana = dia_inicio_semana.lower()
        contrato.compensacion_km = compensacion_km
        contrato.modalidad_computo = modalidad_computo
        contrato.tratamiento_dia_no_trabajado = tratamiento_dia_no_trabajado

        if tipo_contrato == 'PORCENTAJE':
            if valor < 0 or valor > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El porcentaje debe estar entre 0 y 100"
                )
            contrato.porcentaje_chofer = valor
            contrato.monto_diario = None
            contrato.canon_diario = None
            contrato.km_incluidos_dia = None
            contrato.valor_km_excedente = None

        elif tipo_contrato == 'ALQUILER':
            if not canon_diario or canon_diario <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El canon diario es obligatorio y debe ser mayor a 0"
                )
            contrato.monto_diario = None
            contrato.porcentaje_chofer = None
            contrato.canon_diario = canon_diario
            contrato.km_incluidos_dia = km_incluidos_dia
            contrato.valor_km_excedente = valor_km_excedente

        else:  # AUTO_GESTION
            contrato.porcentaje_chofer = None
            contrato.monto_diario = None
            contrato.canon_diario = None
            contrato.km_incluidos_dia = None
            contrato.valor_km_excedente = None

        contrato.estado_contrato = 'ACTIVO'
        contrato.fecha_inicio = datetime.now()
        await db.commit()
        await db.refresh(contrato)

        # Notificar al chofer que el contrato está activo
        notificacion = Notificacion(
            usuario_id=contrato.chofer_id,
            titulo="Contrato activado",
            mensaje=f"Tu contrato para el vehículo {contrato.vehiculo.patente} ha sido activado. "
                    f"Horario: {hora_inicio}-{hora_fin}",
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