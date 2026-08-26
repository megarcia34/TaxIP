"""
Recaudacion Service - Centraliza la gestión de ingresos por turno
Maneja efectivo, electrónico, taxímetro e ingresos manuales
Reemplaza los campos legacy de recaudación en turno_chofer
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func
from sqlalchemy.orm import selectinload

from app.models.fleet import IngresoTurno
from app.models.turno import TurnoChofer
from app.models.trip import ViajeSolicitado
from app.models.auth import Usuario
from app.models.payment import Transaccion
from app.schemas.recaudacion_schemas import (
    IngresoCreate,
    IngresoUpdate,
    IngresoResponse,
    IngresoListFilter,
    ResumenIngresosTurno
)
from app.core.exceptions import (
    RecaudacionError,
    RecaudacionNotFoundError,
    RecaudacionInvalidStateError,
    RecaudacionPermissionError
)


class RecaudacionService:
    """
    Servicio centralizado para la gestión de ingresos/recaudación por turno
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # CRUD BÁSICO
    # ============================================================

    async def crear_ingreso(self, data: IngresoCreate) -> IngresoTurno:
        """
        Registrar un nuevo ingreso en un turno
        """
        # Validar que el turno existe
        turno = await self.db.get(TurnoChofer, data.turno_id)
        if not turno:
            raise RecaudacionNotFoundError(f"Turno {data.turno_id} no encontrado")

        # Validar que el turno esté activo
        if turno.estado not in ["ACTIVO", "CERRADO"]:
            raise RecaudacionInvalidStateError(f"Turno en estado {turno.estado} - no se pueden registrar ingresos")

        # Validar que el declarante existe (si se proporcionó)
        if data.declarado_por:
            declarante = await self.db.get(Usuario, data.declarado_por)
            if not declarante:
                raise RecaudacionNotFoundError(f"Usuario {data.declarado_por} no encontrado")

        # Si es un ingreso automático (vía transacción), validar la transacción
        if data.transaccion_id:
            transaccion = await self.db.get(Transaccion, data.transaccion_id)
            if not transaccion:
                raise RecaudacionNotFoundError(f"Transacción {data.transaccion_id} no encontrada")

        # Crear el ingreso
        ingreso = IngresoTurno(
            id=uuid.uuid4(),
            turno_id=data.turno_id,
            viaje_id=data.viaje_id,
            tipo_ingreso=data.tipo_ingreso,
            medio_pago=data.medio_pago,
            origen=data.origen,
            monto=data.monto,
            moneda=data.moneda or "ARS",
            fecha_hora=data.fecha_hora or datetime.now(),
            declarado_por=data.declarado_por,
            estado="pendiente" if data.tipo_ingreso in ["taximetro", "manual"] else "aprobado",
            observaciones=data.observaciones,
            referencia_pago=data.referencia_pago,
            transaccion_id=data.transaccion_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(ingreso)
        await self.db.flush()

        # ============================================================
        # NOTA: Los campos legacy (recaudacion_app_efectivo, etc.)
        # ya NO existen en la base de datos.
        # La recaudación se obtiene consultando IngresoTurno.
        # ============================================================

        await self.db.commit()
        await self.db.refresh(ingreso)

        return ingreso

    async def get_ingreso(self, ingreso_id: UUID) -> Optional[IngresoTurno]:
        """
        Obtener un ingreso por ID
        """
        query = select(IngresoTurno).where(
            IngresoTurno.id == ingreso_id
        ).options(
            selectinload(IngresoTurno.turno),
            selectinload(IngresoTurno.viaje),
            selectinload(IngresoTurno.declarante)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_ingresos(self, filters: IngresoListFilter) -> List[IngresoTurno]:
        """
        Listar ingresos con filtros
        """
        query = select(IngresoTurno)

        if filters.turno_id:
            query = query.where(IngresoTurno.turno_id == filters.turno_id)
        if filters.viaje_id:
            query = query.where(IngresoTurno.viaje_id == filters.viaje_id)
        if filters.tipo_ingreso:
            query = query.where(IngresoTurno.tipo_ingreso == filters.tipo_ingreso)
        if filters.medio_pago:
            query = query.where(IngresoTurno.medio_pago == filters.medio_pago)
        if filters.origen:
            query = query.where(IngresoTurno.origen == filters.origen)
        if filters.estado:
            query = query.where(IngresoTurno.estado == filters.estado)
        if filters.fecha_desde:
            query = query.where(IngresoTurno.fecha_hora >= filters.fecha_desde)
        if filters.fecha_hasta:
            query = query.where(IngresoTurno.fecha_hora <= filters.fecha_hasta)

        query = query.order_by(IngresoTurno.fecha_hora.desc())

        if filters.limit:
            query = query.limit(filters.limit)
        if filters.offset:
            query = query.offset(filters.offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_ingreso(self, ingreso_id: UUID, data: IngresoUpdate) -> IngresoTurno:
        """
        Actualizar un ingreso
        """
        ingreso = await self.get_ingreso(ingreso_id)
        if not ingreso:
            raise RecaudacionNotFoundError(f"Ingreso {ingreso_id} no encontrado")

        # Si el ingreso está aprobado, no se puede modificar el monto
        if ingreso.estado == "aprobado" and data.monto is not None:
            raise RecaudacionInvalidStateError("No se puede modificar el monto de un ingreso aprobado")

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ingreso, key, value)

        ingreso.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(ingreso)

        return ingreso

    # ============================================================
    # APROBACIÓN Y GESTIÓN DE ESTADOS
    # ============================================================

    async def aprobar_ingreso(self, ingreso_id: UUID, usuario_id: UUID) -> IngresoTurno:
        """
        Aprobar un ingreso pendiente
        """
        ingreso = await self.get_ingreso(ingreso_id)
        if not ingreso:
            raise RecaudacionNotFoundError(f"Ingreso {ingreso_id} no encontrado")

        if ingreso.estado != "pendiente":
            raise RecaudacionInvalidStateError(f"Ingreso en estado {ingreso.estado} - solo se pueden aprobar pendientes")

        ingreso.estado = "aprobado"
        ingreso.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(ingreso)

        return ingreso

    async def rechazar_ingreso(self, ingreso_id: UUID, motivo: str) -> IngresoTurno:
        """
        Rechazar un ingreso pendiente
        """
        ingreso = await self.get_ingreso(ingreso_id)
        if not ingreso:
            raise RecaudacionNotFoundError(f"Ingreso {ingreso_id} no encontrado")

        if ingreso.estado != "pendiente":
            raise RecaudacionInvalidStateError(f"Ingreso en estado {ingreso.estado} - solo se pueden rechazar pendientes")

        ingreso.estado = "rechazado"
        ingreso.observaciones = (ingreso.observaciones or "") + f"\nMotivo rechazo: {motivo}"
        ingreso.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(ingreso)

        return ingreso

    async def disputar_ingreso(self, ingreso_id: UUID, motivo: str) -> IngresoTurno:
        """
        Disputar un ingreso aprobado
        """
        ingreso = await self.get_ingreso(ingreso_id)
        if not ingreso:
            raise RecaudacionNotFoundError(f"Ingreso {ingreso_id} no encontrado")

        if ingreso.estado != "aprobado":
            raise RecaudacionInvalidStateError(f"Ingreso en estado {ingreso.estado} - solo se pueden disputar aprobados")

        ingreso.estado = "disputado"
        ingreso.observaciones = (ingreso.observaciones or "") + f"\nMotivo disputa: {motivo}"
        ingreso.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(ingreso)

        return ingreso

    # ============================================================
    # MÉTODOS DE CONSULTA
    # ============================================================

    async def get_resumen_turno(self, turno_id: UUID) -> ResumenIngresosTurno:
        """
        Obtener resumen de ingresos de un turno
        """
        # Validar que el turno existe
        turno = await self.db.get(TurnoChofer, turno_id)
        if not turno:
            raise RecaudacionNotFoundError(f"Turno {turno_id} no encontrado")

        # Obtener todos los ingresos del turno
        query = select(IngresoTurno).where(IngresoTurno.turno_id == turno_id)
        result = await self.db.execute(query)
        ingresos = result.scalars().all()

        # Calcular totales por tipo y estado
        total_ingresos = Decimal(0)
        total_aprobados = Decimal(0)
        total_pendientes = Decimal(0)
        total_rechazados = Decimal(0)
        total_efectivo = Decimal(0)
        total_electronico = Decimal(0)
        total_taximetro = Decimal(0)
        total_manual = Decimal(0)
        total_corporativo = Decimal(0)

        for ingreso in ingresos:
            monto = ingreso.monto or Decimal(0)
            total_ingresos += monto

            if ingreso.estado == "aprobado":
                total_aprobados += monto
            elif ingreso.estado == "pendiente":
                total_pendientes += monto
            elif ingreso.estado == "rechazado":
                total_rechazados += monto

            if ingreso.tipo_ingreso == "efectivo":
                total_efectivo += monto
            elif ingreso.tipo_ingreso == "electronico":
                total_electronico += monto
            elif ingreso.tipo_ingreso == "taximetro":
                total_taximetro += monto
            elif ingreso.tipo_ingreso == "manual":
                total_manual += monto
            elif ingreso.tipo_ingreso == "corporativo":
                total_corporativo += monto

        return ResumenIngresosTurno(
            turno_id=turno_id,
            total_ingresos=total_ingresos,
            total_aprobados=total_aprobados,
            total_pendientes=total_pendientes,
            total_rechazados=total_rechazados,
            total_efectivo=total_efectivo,
            total_electronico=total_electronico,
            total_taximetro=total_taximetro,
            total_manual=total_manual,
            total_corporativo=total_corporativo,
            cantidad_ingresos=len(ingresos)
        )

    async def get_ingresos_por_medio_pago(self, turno_id: UUID) -> Dict[str, Decimal]:
        """
        Obtener ingresos agrupados por medio de pago
        """
        query = select(
            IngresoTurno.medio_pago,
            func.sum(IngresoTurno.monto).label('total')
        ).where(
            and_(
                IngresoTurno.turno_id == turno_id,
                IngresoTurno.estado == "aprobado"
            )
        ).group_by(IngresoTurno.medio_pago)

        result = await self.db.execute(query)
        rows = result.all()

        return {row.medio_pago: row.total or Decimal(0) for row in rows}