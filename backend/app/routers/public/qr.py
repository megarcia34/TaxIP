# app/routers/public/qr.py
"""
Endpoint público para servir QR sin autenticación
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import qrcode
from io import BytesIO
from fastapi.responses import Response

from app.database import get_db

router = APIRouter(prefix="/public/qr", tags=["Public QR"])


@router.get("/test")
async def test_qr():
    return {"message": "QR router funciona!"}
    """
    Servir imagen QR del vehículo (sin autenticación)
    """
    # Buscar vehículo por QR UUID
    query = text("""
        SELECT v.id, v.patente, v.qr_activo, v.activo
        FROM fleet.vehiculo v
        WHERE v.qr_uuid = :qr_uuid
    """)
    result = await db.execute(query, {"qr_uuid": qr_uuid})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    
    if not row[2] or not row[3]:
        raise HTTPException(status_code=410, detail="QR inactivo o vehículo deshabilitado")
    
    # Generar QR (contenido: URL de vinculación o ID del vehículo)
    # Esta URL será escaneada por la app móvil
    content = f"taxip://vincular?vehiculo={row[0]}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Devolver imagen PNG
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    return Response(
        content=buffered.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache 1 día
            "Content-Disposition": f'inline; filename="qr_{row[1]}.png"'
        }
    )