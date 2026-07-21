"""
Vehicle QR Code endpoints
Generate and validate QR codes for vehicle/driver verification
"""

import uuid
import json
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import jwt, JWTError

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.core.config import settings
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/api/vehiculo", tags=["Vehículos"])

# QR Secret from settings
QR_SECRET = settings.QR_SECRET_KEY
QR_EXPIRATION = settings.QR_EXPIRATION_MINUTES


# ============================================
# Schemas
# ============================================

class GenerarQRRequest(BaseModel):
    chofer_vehiculo_id: UUID


class GenerarQRResponse(BaseModel):
    qr_code_base64: str
    token: str
    expiration_minutes: int


class ValidarQRRequest(BaseModel):
    qr_token: str


class ValidarQRResponse(BaseModel):
    es_valido: bool
    datos_conductor: Optional[dict] = None
    datos_vehiculo: Optional[dict] = None
    mensaje: Optional[str] = None


class SubirFotoRequest(BaseModel):
    viaje_id: UUID


class SubirFotoResponse(BaseModel):
    success: bool
    foto_id: UUID
    url: str
    mensaje: str


# ============================================
# QR Endpoints
# ============================================

@router.post("/qr/generar", response_model=GenerarQRResponse)
async def generar_qr(
    request: GenerarQRRequest,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate QR code for vehicle/driver verification (Admin only)
    """
    control_base_id = current_user[1]  # current_user = (id, control_base_id, email, tipo)
    
    query = text("""
        SELECT 
            cv.id as chofer_vehiculo_id,
            cv.usuario_id,
            u.email,
            COALESCE(p.nombre, '') as nombre,
            COALESCE(p.apellido, '') as apellido,
            v.patente,
            COALESCE(v.marca, '') as marca,
            COALESCE(v.modelo, '') as modelo,
            v.anio
        FROM fleet.chofer_vehiculo cv
        JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        WHERE cv.id = :chofer_vehiculo_id
          AND cv.control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "chofer_vehiculo_id": request.chofer_vehiculo_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo/Conductor no encontrado")
    
    payload = {
        "chofer_vehiculo_id": str(row[0]),
        "usuario_id": str(row[1]),
        "email": row[2],
        "nombre": row[3],
        "apellido": row[4],
        "patente": row[5],
        "marca": row[6],
        "modelo": row[7],
        "anio": str(row[8]) if row[8] else "",
        "exp": datetime.utcnow() + timedelta(minutes=QR_EXPIRATION),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, QR_SECRET, algorithm="HS256")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return GenerarQRResponse(
        qr_code_base64=f"data:image/png;base64,{qr_base64}",
        token=token,
        expiration_minutes=QR_EXPIRATION
    )


@router.post("/qr/validar", response_model=ValidarQRResponse)
async def validar_qr(
    request: ValidarQRRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate QR code scanned from vehicle
    """
    try:
        payload = jwt.decode(request.qr_token, QR_SECRET, algorithms=["HS256"])
        
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return ValidarQRResponse(
                es_valido=False,
                mensaje="QR code expirado"
            )
        
        query = text("""
            SELECT cv.activo as driver_active, v.activo as vehicle_active, cv.estado_laboral
            FROM fleet.chofer_vehiculo cv
            JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
            WHERE cv.id = :chofer_vehiculo_id
        """)
        
        result = await db.execute(query, {"chofer_vehiculo_id": payload["chofer_vehiculo_id"]})
        row = result.first()
        
        if not row or not row[0] or not row[1]:
            return ValidarQRResponse(
                es_valido=False,
                mensaje="Vehículo o conductor inactivo"
            )
        
        return ValidarQRResponse(
            es_valido=True,
            datos_conductor={
                "nombre": payload.get("nombre", ""),
                "apellido": payload.get("apellido", ""),
                "email": payload.get("email", ""),
                "estado_laboral": row[2] if row else "desconocido"
            },
            datos_vehiculo={
                "patente": payload.get("patente", ""),
                "marca": payload.get("marca", ""),
                "modelo": payload.get("modelo", ""),
                "anio": payload.get("anio", "")
            }
        )
    
    except JWTError as e:
        return ValidarQRResponse(es_valido=False, mensaje=f"QR inválido: {str(e)}")
    except Exception as e:
        return ValidarQRResponse(es_valido=False, mensaje=f"Error: {str(e)}")