"""
Chofer self-registration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/chofer", tags=["Chofer Registro"])


# ============================================
# Schemas
# ============================================

class RegistroChoferRequest(BaseModel):
    email: str
    password: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    documento: Optional[str] = None
    patente: str
    marca: str
    modelo: str
    anio: Optional[int] = None


class RegistroChoferResponse(BaseModel):
    success: bool
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"
    message: str
    requiere_aprobacion: bool


# ============================================
# Endpoints
# ============================================

@router.post("/registro-completo", response_model=RegistroChoferResponse)
async def registrar_chofer_con_vehiculo(
    request: RegistroChoferRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete registration for a new driver with their vehicle
    
    Creates:
    - User account (auth.usuario)
    - Profile (auth.perfil_general)
    - Vehicle (fleet.vehiculo)
    - Driver-vehicle relationship (fleet.chofer_vehiculo) with 'pendiente' approval
    
    Returns JWT access token so the driver can immediately upload documents.
    """
    
    # 1. Verificar si el email ya existe
    check_query = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_query, {"email": request.email})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # 2. Obtener control_base_id por defecto
    cb_query = text("SELECT id FROM tenant.control_base LIMIT 1")
    cb_result = await db.execute(cb_query)
    control_base_id = cb_result.first()[0]
    
    # 3. Obtener tipo_usuario_id para chofer
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer'")
    tipo_result = await db.execute(tipo_query)
    tipo_usuario_id = tipo_result.first()[0]
    
    # 4. Crear usuario
    user_id = uuid4()
    password_hash = get_password_hash(request.password)
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
        VALUES (:id, :tipo_usuario_id, :control_base_id, :email, :password_hash, true, NOW())
    """)
    
    await db.execute(insert_user, {
        "id": user_id,
        "tipo_usuario_id": tipo_usuario_id,
        "control_base_id": control_base_id,
        "email": request.email,
        "password_hash": password_hash
    })
    
    # 5. Crear perfil
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, documento, created_at)
        VALUES (gen_random_uuid(), :user_id, :nombre, :apellido, :telefono, :documento, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "user_id": user_id,
        "nombre": request.nombre,
        "apellido": request.apellido,
        "telefono": request.telefono,
        "documento": request.documento
    })
    
    # 6. Crear vehículo
    vehiculo_id = uuid4()
    insert_vehiculo = text("""
        INSERT INTO fleet.vehiculo (id, control_base_id, patente, marca, modelo, anio, activo, created_at)
        VALUES (:id, :control_base_id, :patente, :marca, :modelo, :anio, true, NOW())
    """)
    
    await db.execute(insert_vehiculo, {
        "id": vehiculo_id,
        "control_base_id": control_base_id,
        "patente": request.patente.upper(),
        "marca": request.marca,
        "modelo": request.modelo,
        "anio": request.anio
    })
    
    # 7. Crear relación chofer-vehiculo (con estado pendiente de aprobación)
    insert_chofer_vehiculo = text("""
        INSERT INTO fleet.chofer_vehiculo (
            id, usuario_id, vehiculo_id, control_base_id,
            estado_laboral, estado_aprobacion, calificacion_promedio, activo, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :user_id, :vehiculo_id, :control_base_id,
            'libre', 'pendiente', 5.0, true, NOW(), NOW()
        )
    """)
    
    await db.execute(insert_chofer_vehiculo, {
        "user_id": user_id,
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    
    await db.commit()
    
    # 8. Generar JWT token para que la app pueda subir documentos inmediatamente
    access_token = create_access_token(
        data={
            "sub": str(user_id),
            "email": request.email,
            "tipo": "chofer",
            "control_base_id": str(control_base_id)
        }
    )
    
    return RegistroChoferResponse(
        success=True,
        user_id=str(user_id),
        email=request.email,
        access_token=access_token,
        message="Chofer registrado correctamente. Pendiente de aprobación.",
        requiere_aprobacion=True
    )