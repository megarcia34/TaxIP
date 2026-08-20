"""
Medios de pago para propietarios
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/pagos", tags=["Pagos Propietario"])


@router.get("/medios")
async def get_medios_pago(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los medios de pago disponibles para el propietario.
    """
    user_id, control_base_id, email, tipo = current_user
    
    # Verificar que es propietario
    query = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")
    
    return {
        "efectivo": {"nombre": "Efectivo", "activo": True},
        "transferencia": {"nombre": "Transferencia Bancaria", "activo": True},
        "qr": {"nombre": "QR", "activo": True},
        "debito": {"nombre": "Débito", "activo": True},
        "credito": {"nombre": "Crédito", "activo": False},
        "wallet": {"nombre": "Billetera TaxIP", "activo": True}
    }