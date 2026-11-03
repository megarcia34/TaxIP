"""
Router de Conciliaciones del Propietario.

Endpoints:
- GET  /api/propietario/conciliaciones              -> Bandeja de pendientes
- GET  /api/propietario/conciliaciones/{turno_id}   -> Detalle de un turno
- POST /api/propietario/conciliaciones/{turno_id}/aprobar-gasto/{gasto_id}
- POST /api/propietario/conciliaciones/{turno_id}/rechazar-gasto/{gasto_id}
- POST /api/propietario/conciliaciones/{turno_id}/cerrar
- POST /api/propietario/conciliaciones/{turno_id}/saldar-diferencia/{diferencia_id}
- GET  /api/propietario/conciliaciones/historial
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.database import get_db
from app.dependencies import get_propietario_id, get_current_user
from app.services.conciliacion_service import ConciliacionService
from app.schemas.conciliacion import (
    ConciliacionPendienteResponse,
    ConciliacionDetalleResponse,
    RechazarGastoRequest,
    CerrarConciliacionRequest,
    SaldarDiferenciaRequest,
    ConciliacionHistorialResponse,
    ConciliacionHistorialItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/propietario/conciliaciones", tags=["Propietario - Conciliaciones"])


# ============================================================
# BANDEJA DE PENDIENTES
# ============================================================

@router.get("", response_model=ConciliacionPendienteResponse)
async def listar_conciliaciones_pendientes(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los turnos pendientes de conciliar del propietario."""
    service = ConciliacionService(db)
    return await service.listar_pendientes(propietario_id)


# ============================================================
# DETALLE DE UN TURNO
# ============================================================

@router.get("/{turno_id}", response_model=ConciliacionDetalleResponse)
async def obtener_detalle_conciliacion(
    turno_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el detalle completo de un turno para conciliar."""
    service = ConciliacionService(db)
    try:
        return await service.obtener_detalle(turno_id, propietario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# APROBAR / RECHAZAR GASTO
# ============================================================

@router.post("/{turno_id}/aprobar-gasto/{gasto_id}")
async def aprobar_gasto(
    turno_id: UUID,
    gasto_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aprueba un gasto declarado por el chofer."""
    service = ConciliacionService(db)
    try:
        await service.aprobar_gasto(turno_id, gasto_id, propietario_id)
        return {"success": True, "message": "Gasto aprobado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{turno_id}/rechazar-gasto/{gasto_id}")
async def rechazar_gasto(
    turno_id: UUID,
    gasto_id: UUID,
    request: RechazarGastoRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rechaza un gasto declarado por el chofer."""
    service = ConciliacionService(db)
    try:
        await service.rechazar_gasto(turno_id, gasto_id, request.motivo, propietario_id)
        return {"success": True, "message": "Gasto rechazado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# CERRAR CONCILIACION
# ============================================================

@router.post("/{turno_id}/cerrar")
async def cerrar_conciliacion(
    turno_id: UUID,
    request: CerrarConciliacionRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cierra la conciliacion de un turno y genera la liquidacion."""
    service = ConciliacionService(db)
    try:
        await service.cerrar_conciliacion(turno_id, propietario_id, request.observaciones)
        return {"success": True, "message": "Conciliacion cerrada"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# SALDAR DIFERENCIA
# ============================================================

@router.post("/{turno_id}/saldar-diferencia/{diferencia_id}")
async def saldar_diferencia(
    turno_id: UUID,
    diferencia_id: UUID,
    request: SaldarDiferenciaRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marca una diferencia como saldada."""
    service = ConciliacionService(db)
    try:
        await service.saldar_diferencia(diferencia_id, propietario_id)
        return {"success": True, "message": "Diferencia saldada"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# HISTORIAL
# ============================================================

@router.get("/historial/listado", response_model=ConciliacionHistorialResponse)
async def listar_historial_conciliaciones(
    limit: int = 50,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista el historial de conciliaciones cerradas del propietario."""
    service = ConciliacionService(db)
    items = await service.listar_historial(propietario_id, limit, offset)
    return ConciliacionHistorialResponse(
        total=len(items),
        conciliaciones=[ConciliacionHistorialItem(**item) for item in items],
    )