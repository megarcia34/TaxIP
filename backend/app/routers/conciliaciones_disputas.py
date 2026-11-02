"""
Router de Disputas de Conciliacion.

Endpoints:
- POST /api/conciliaciones/{turno_id}/disputa          -> Abrir disputa
- GET  /api/conciliaciones/{turno_id}/disputa          -> Ver disputa
- POST /api/conciliaciones/{turno_id}/disputa/resolver -> Resolver disputa
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.services.conciliacion_service import ConciliacionService
from app.schemas.conciliacion import (
    AbrirDisputaRequest,
    ResolverDisputaRequest,
    DisputaResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conciliaciones", tags=["Conciliaciones - Disputas"])


@router.post("/{turno_id}/disputa", response_model=DisputaResponse)
async def abrir_disputa(
    turno_id: UUID,
    request: AbrirDisputaRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Abre una disputa sobre una conciliacion."""
    user_id = current_user[0]
    service = ConciliacionService(db)
    try:
        return await service.abrir_disputa(turno_id, user_id, request.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{turno_id}/disputa", response_model=DisputaResponse)
async def obtener_disputa(
    turno_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la disputa activa de un turno."""
    # TODO: implementar en el servicio
    raise HTTPException(status_code=404, detail="Disputa no encontrada")


@router.post("/{turno_id}/disputa/resolver")
async def resolver_disputa(
    turno_id: UUID,
    request: ResolverDisputaRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resuelve una disputa (solo tenant o plataforma)."""
    user_id = current_user[0]
    service = ConciliacionService(db)
    try:
        # TODO: obtener disputa_id del turno
        raise HTTPException(status_code=501, detail="No implementado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))