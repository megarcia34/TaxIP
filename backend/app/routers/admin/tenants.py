"""
Router para gestión del Tenant propio (Admin Tenant)
Permite al administrador del municipio ver y actualizar su propia información.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import AdminTenantUser
from app.schemas.tenant import (
    TenantUpdate,
    TenantResponse,
)

router = APIRouter(prefix="/admin/tenant", tags=["Admin Tenant"])


# ============================================
# OBTENER MI TENANT (detalle de mi propio municipio)
# ============================================

@router.get("", response_model=TenantResponse)
async def get_my_tenant(
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db),
):
    """Obtener la información del tenant del usuario autenticado."""
    
    # current_user = (user_id, control_base_id, email, tipo_usuario)
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if not control_base_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no está asociado a ningún tenant"
        )
    
    query = text("""
        SELECT 
            cb.id, cb.nombre, cb.email, cb.telefono, cb.direccion,
            cb.latitud, cb.longitud, cb.ciudad_id,
            g.nombre as ciudad_nombre,
            cb.activo, cb.fecha_suspension, cb.motivo_suspension, cb.suspendido_por,
            cb.created_at, cb.updated_at
        FROM tenant.control_base cb
        LEFT JOIN geo.ciudad g ON g.id = cb.ciudad_id
        WHERE cb.id = :tenant_id
    """)
    
    result = await db.execute(query, {"tenant_id": control_base_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )
    
    return TenantResponse(
        id=row[0],
        nombre=row[1],
        email=row[2],
        telefono=row[3],
        direccion=row[4],
        latitud=float(row[5]) if row[5] else None,
        longitud=float(row[6]) if row[6] else None,
        ciudad_id=row[7],
        ciudad_nombre=row[8],
        codigo_postal=None,
        activo=row[9],
        fecha_suspension=row[10],
        motivo_suspension=row[11],
        suspendido_por=row[12],
        created_at=row[13],
        updated_at=row[14],
    )


# ============================================
# ACTUALIZAR MI TENANT
# ============================================

@router.put("", response_model=TenantResponse)
async def update_my_tenant(
    data: TenantUpdate,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db),
):
    """Actualizar la información del tenant del usuario autenticado."""
    
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if not control_base_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no está asociado a ningún tenant"
        )
    
    # Verificar que el tenant existe
    check_query = text("""
        SELECT id FROM tenant.control_base WHERE id = :tenant_id
    """)
    result = await db.execute(check_query, {"tenant_id": control_base_id})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )
    
    # Construir actualización dinámica
    updates = []
    params = {"tenant_id": control_base_id}
    
    if data.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = data.nombre
    
    if data.email is not None:
        updates.append("email = :email")
        params["email"] = data.email
    
    if data.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = data.telefono
    
    if data.direccion is not None:
        updates.append("direccion = :direccion")
        params["direccion"] = data.direccion
    
    if data.latitud is not None:
        updates.append("latitud = :latitud")
        params["latitud"] = data.latitud
    
    if data.longitud is not None:
        updates.append("longitud = :longitud")
        params["longitud"] = data.longitud
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar"
        )
    
    updates.append("updated_at = NOW()")
    
    query_update = text(f"""
        UPDATE tenant.control_base 
        SET {', '.join(updates)}
        WHERE id = :tenant_id
        RETURNING id, nombre, email, telefono, direccion, latitud, longitud,
                  ciudad_id, activo, fecha_suspension, motivo_suspension, suspendido_por,
                  created_at, updated_at
    """)
    
    result = await db.execute(query_update, params)
    await db.commit()
    row = result.first()
    
    return TenantResponse(
        id=row[0],
        nombre=row[1],
        email=row[2],
        telefono=row[3],
        direccion=row[4],
        latitud=float(row[5]) if row[5] else None,
        longitud=float(row[6]) if row[6] else None,
        ciudad_id=row[7],
        ciudad_nombre=None,
        codigo_postal=None,
        activo=row[8],
        fecha_suspension=row[9],
        motivo_suspension=row[10],
        suspendido_por=row[11],
        created_at=row[12],
        updated_at=row[13],
    )