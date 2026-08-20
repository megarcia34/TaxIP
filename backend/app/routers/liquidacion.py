# app/routers/liquidacion.py
"""
Router para el módulo de liquidaciones
Incluye: Cálculo (D3) + Ciclo de aprobación y pagos (D7)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import (
    get_current_user,
    get_propietario_id,
    get_propietario_context,
    get_current_propietario_user
)
from app.services.liquidacion_engine import LiquidacionEngine
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.schemas.liquidacion import (
    LiquidacionResponse,
    LiquidacionDetalleResponse,
    AprobarLiquidacionRequest,
    RechazarLiquidacionRequest,
    RegistrarPagoRequest,
    LiquidacionEstadoResponse,
    LiquidacionEstadoHistorialResponse
)
from app.models.liquidacion import Liquidacion, LiquidacionEstadoHistorial
from app.models.turno import TurnoChofer
from app.models.fleet import PropietarioVehiculo
from app.core.exceptions import LiquidacionError, TenantMismatchError

router = APIRouter(prefix="/api/liquidacion", tags=["Liquidación"])


# ============================================================
# ENDPOINTS BASE (D3)
# ============================================================

@router.post("/calcular/{turno_id}", response_model=LiquidacionResponse)
async def calcular_liquidacion(
    turno_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula y persiste la liquidación para un turno.
    Solo accesible por el propietario del vehículo.
    """
    propietario_id = ctx["propietario_id"]

    await _verificar_turno_propietario(turno_id, propietario_id, db)

    try:
        engine = LiquidacionEngine(db)
        liquidacion_id = await engine.calcular(turno_id)

        repo = LiquidacionRepository(db)
        liquidacion = await repo.obtener_por_id(liquidacion_id)
        if not liquidacion:
            raise HTTPException(status_code=500, detail="Error al persistir la liquidación")

        return LiquidacionResponse.model_validate(liquidacion)

    except (LiquidacionError, TenantMismatchError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{liquidacion_id}", response_model=LiquidacionResponse)
async def obtener_liquidacion(
    liquidacion_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene una liquidación por su ID. Valida permisos."""
    repo = LiquidacionRepository(db)
    liquidacion = await repo.obtener_por_id(liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    user_id, control_base_id, email, tipo = current_user

    es_propietario = liquidacion.propietario_id == user_id
    es_chofer = liquidacion.chofer_id == user_id
    es_admin = tipo in ["admin", "super_admin"]

    if not (es_propietario or es_chofer or es_admin):
        raise HTTPException(status_code=403, detail="No tiene permiso para ver esta liquidación")

    if liquidacion.control_base_id != control_base_id:
        raise HTTPException(status_code=403, detail="Acceso denegado: tenant incorrecto")

    return LiquidacionResponse.model_validate(liquidacion)


@router.get("/{liquidacion_id}/detalle", response_model=list[LiquidacionDetalleResponse])
async def obtener_detalle_liquidacion(
    liquidacion_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los detalles (líneas) de una liquidación."""
    repo = LiquidacionRepository(db)
    liquidacion = await repo.obtener_por_id(liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    user_id, control_base_id, email, tipo = current_user
    es_propietario = liquidacion.propietario_id == user_id
    es_chofer = liquidacion.chofer_id == user_id
    es_admin = tipo in ["admin", "super_admin"]

    if not (es_propietario or es_chofer or es_admin):
        raise HTTPException(status_code=403, detail="No tiene permiso para ver esta liquidación")

    if liquidacion.control_base_id != control_base_id:
        raise HTTPException(status_code=403, detail="Acceso denegado: tenant incorrecto")

    return [LiquidacionDetalleResponse.model_validate(d) for d in liquidacion.detalles]


@router.get("/turno/{turno_id}", response_model=Optional[LiquidacionResponse])
async def obtener_liquidacion_por_turno(
    turno_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene la liquidación más reciente de un turno."""
    user_id, control_base_id, email, tipo = current_user

    query = select(TurnoChofer).where(TurnoChofer.id == turno_id)
    result = await db.execute(query)
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    es_chofer = turno.chofer_id == user_id
    es_propietario = await _es_propietario_vehiculo(user_id, turno.vehiculo_id, db)
    es_admin = tipo in ["admin", "super_admin"]

    if not (es_chofer or es_propietario or es_admin):
        raise HTTPException(status_code=403, detail="No tiene permiso para ver esta liquidación")

    repo = LiquidacionRepository(db)
    liquidacion = await repo.obtener_por_turno(turno_id)

    if not liquidacion:
        return None

    return LiquidacionResponse.model_validate(liquidacion)


@router.get("/", response_model=list[LiquidacionResponse])
async def listar_liquidaciones(
    propietario_id: Optional[UUID] = Query(None, description="Filtrar por propietario"),
    vehiculo_id: Optional[UUID] = Query(None, description="Filtrar por vehículo"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista liquidaciones con filtros. Solo propietario o admin."""
    user_id, control_base_id, email, tipo = current_user

    query = select(Liquidacion).where(
        Liquidacion.control_base_id == control_base_id
    )

    if tipo in ["propietario", "admin_propietario"]:
        query = query.where(Liquidacion.propietario_id == user_id)
    elif tipo not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="No tiene permiso para listar liquidaciones")

    if propietario_id:
        query = query.where(Liquidacion.propietario_id == propietario_id)
    if vehiculo_id:
        query = query.where(Liquidacion.vehiculo_id == vehiculo_id)
    if estado:
        query = query.where(Liquidacion.estado == estado)

    query = query.order_by(Liquidacion.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    liquidaciones = result.scalars().all()

    return [LiquidacionResponse.model_validate(l) for l in liquidaciones]


# ============================================================
# D7 - CICLO DE APROBACIÓN Y PAGOS
# ============================================================

@router.post("/{liquidacion_id}/aprobar")
async def aprobar_liquidacion(
    liquidacion_id: UUID,
    current_user: tuple = Depends(get_current_propietario_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Aprueba una liquidación en estado CALCULADA o PENDIENTE_APROBACION.
    Solo el propietario del vehículo puede aprobar.
    """
    liquidacion = await db.get(Liquidacion, liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    if liquidacion.propietario_id != current_user[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres el propietario de esta liquidación"
        )

    if liquidacion.estado not in ["CALCULADA", "PENDIENTE_APROBACION"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede aprobar en estado {liquidacion.estado}. Estados válidos: CALCULADA, PENDIENTE_APROBACION"
        )

    estado_anterior = liquidacion.estado
    liquidacion.estado = "APROBADA"
    liquidacion.aprobada_por = current_user[0]
    liquidacion.aprobada_en = datetime.now()

    repo = LiquidacionRepository(db)
    await repo.registrar_cambio_estado(
        liquidacion_id=liquidacion_id,
        estado_anterior=estado_anterior,
        estado_nuevo="APROBADA",
        motivo="Aprobada por propietario",
        usuario_id=current_user[0]
    )

    await db.commit()

    return {
        "success": True,
        "message": "Liquidación aprobada exitosamente",
        "liquidacion_id": liquidacion_id,
        "estado": "APROBADA"
    }


@router.post("/{liquidacion_id}/rechazar")
async def rechazar_liquidacion(
    liquidacion_id: UUID,
    request: RechazarLiquidacionRequest,
    current_user: tuple = Depends(get_current_propietario_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rechaza una liquidación en estado CALCULADA o PENDIENTE_APROBACION.
    Requiere motivo del rechazo.
    """
    liquidacion = await db.get(Liquidacion, liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    if liquidacion.propietario_id != current_user[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres el propietario de esta liquidación"
        )

    if liquidacion.estado not in ["CALCULADA", "PENDIENTE_APROBACION"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede rechazar en estado {liquidacion.estado}. Estados válidos: CALCULADA, PENDIENTE_APROBACION"
        )

    estado_anterior = liquidacion.estado
    liquidacion.estado = "RECHAZADA"
    liquidacion.rechazada_por = current_user[0]
    liquidacion.rechazada_en = datetime.now()
    liquidacion.motivo_rechazo = request.motivo

    repo = LiquidacionRepository(db)
    await repo.registrar_cambio_estado(
        liquidacion_id=liquidacion_id,
        estado_anterior=estado_anterior,
        estado_nuevo="RECHAZADA",
        motivo=f"Rechazada por propietario: {request.motivo}",
        usuario_id=current_user[0]
    )

    await db.commit()

    return {
        "success": True,
        "message": "Liquidación rechazada",
        "liquidacion_id": liquidacion_id,
        "estado": "RECHAZADA",
        "motivo": request.motivo
    }


@router.post("/{liquidacion_id}/pagar")
async def registrar_pago(
    liquidacion_id: UUID,
    request: RegistrarPagoRequest,
    current_user: tuple = Depends(get_current_propietario_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registra el pago de una liquidación aprobada.
    """
    liquidacion = await db.get(Liquidacion, liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    if liquidacion.propietario_id != current_user[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres el propietario de esta liquidación"
        )

    if liquidacion.estado != "APROBADA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La liquidación debe estar APROBADA para pagar. Estado actual: {liquidacion.estado}"
        )

    metodos_validos = ["EFECTIVO", "TRANSFERENCIA", "DEBITO", "CREDITO", "QR"]
    if request.metodo_pago not in metodos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Método de pago inválido. Permitidos: {metodos_validos}"
        )

    estado_anterior = liquidacion.estado
    liquidacion.estado = "PAGADA"
    liquidacion.pagada_por = current_user[0]
    liquidacion.pagada_en = datetime.now()
    liquidacion.metodo_pago = request.metodo_pago
    liquidacion.referencia_pago = request.referencia

    repo = LiquidacionRepository(db)
    await repo.registrar_cambio_estado(
        liquidacion_id=liquidacion_id,
        estado_anterior=estado_anterior,
        estado_nuevo="PAGADA",
        motivo=f"Pago registrado - {request.metodo_pago}",
        usuario_id=current_user[0]
    )

    await db.commit()

    return {
        "success": True,
        "message": "Pago registrado exitosamente",
        "liquidacion_id": liquidacion_id,
        "estado": "PAGADA",
        "metodo_pago": request.metodo_pago,
        "referencia": request.referencia
    }


@router.get("/{liquidacion_id}/estado", response_model=LiquidacionEstadoResponse)
async def obtener_estado_liquidacion(
    liquidacion_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el estado actual y el historial completo de cambios de una liquidación.
    """
    liquidacion = await db.get(Liquidacion, liquidacion_id)
    if not liquidacion:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")

    user_id, control_base_id, email, tipo = current_user

    tiene_acceso = (
        liquidacion.propietario_id == user_id or
        liquidacion.chofer_id == user_id or
        tipo in ["admin", "super_admin"]
    )

    if not tiene_acceso:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver el estado de esta liquidación"
        )

    repo = LiquidacionRepository(db)
    historial = await repo.obtener_historial(liquidacion_id)

    return LiquidacionEstadoResponse(
        id=liquidacion.id,
        estado=liquidacion.estado,
        historial=historial
    )


# ============================================================
# FUNCIONES DE VALIDACIÓN AUXILIARES
# ============================================================

async def _verificar_turno_propietario(turno_id: UUID, propietario_id: UUID, db: AsyncSession):
    """Verifica que el turno pertenezca a un vehículo del propietario"""
    query = select(TurnoChofer).where(TurnoChofer.id == turno_id)
    result = await db.execute(query)
    turno = result.scalar_one_or_none()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    query_prop = select(PropietarioVehiculo).where(
        and_(
            PropietarioVehiculo.vehiculo_id == turno.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    result = await db.execute(query_prop)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="El turno no pertenece a un vehículo del propietario")

    return turno


async def _es_propietario_vehiculo(user_id: UUID, vehiculo_id: UUID, db: AsyncSession) -> bool:
    """Verifica si un usuario es propietario de un vehículo"""
    query = select(PropietarioVehiculo).where(
        and_(
            PropietarioVehiculo.vehiculo_id == vehiculo_id,
            PropietarioVehiculo.propietario_id == user_id,
            PropietarioVehiculo.activo == True
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None