from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text  # <--- AGREGAR ESTA LÍNEA
from uuid import UUID

from app.database import get_db
from app.dependencies import get_propietario_context
from app.schemas.turno_schemas import GenerarQrRequest, GenerarQrResponse
from app.services.qr_service import QRService

router = APIRouter(prefix="/contratos", tags=["QR Operativo"])

@router.post("/{contrato_id}/generar-qr", response_model=GenerarQrResponse)
async def generar_qr_operativo(
    contrato_id: UUID,
    request: GenerarQrRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = UUID(ctx["propietario_id"])
    
    # Verificar contrato
    query_contrato = text("""
        SELECT id, estado_contrato, activo
        FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id AND propietario_id = :propietario_id
    """)
    result = await db.execute(query_contrato, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id
    })
    row = result.first()
    if not row:
        raise HTTPException(404, "Contrato no encontrado")
    if row[1] != "ACTIVO" or not row[2]:
        raise HTTPException(400, "El contrato no está ACTIVO")
    
    resultado = await QRService.generar_qr(
        propietario_id=propietario_id,
        contrato_id=contrato_id,
        db=db,
        dias_validez=request.dias_validez or 30
    )
    
    return GenerarQrResponse(
        token=resultado["token"],
        contrato_id=contrato_id,
        expires_at=resultado.get("fecha_expiracion"),
        mensaje="QR generado exitosamente"
    )