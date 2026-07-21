"""
Router para gestión de Tenants (Super Admin)
FASE 2: BACKEND DE GESTIÓN - SUPER ADMIN
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List

from app.database import get_db
from app.dependencies import SuperAdminUser
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantSuspender,
    TenantResponse,
    TenantListResponse,
)

router = APIRouter(prefix="/super-admin/tenants", tags=["Super Admin - Tenants"])


# ============================================
# LISTAR TENANTS
# ============================================

@router.get("", response_model=List[TenantListResponse])
async def get_all_tenants(
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
):
    """Listar todos los tenants del sistema (Super Admin)."""
    
    query = text("""
        SELECT 
            cb.id,
            cb.nombre,
            cb.email,
            cb.telefono,
            cb.latitud,
            cb.longitud,
            cb.activo,
            cb.fecha_suspension,
            cb.motivo_suspension,
            cb.suspendido_por,
            cb.created_at,
            cb.updated_at,
            0 as total_empresas,
            0 as total_usuarios,
            0 as total_viajes
        FROM tenant.control_base cb
        WHERE 1=1
    """)
    
    params = {}
    
    if search:
        query = text(str(query) + """
            AND (cb.nombre ILIKE :search 
                 OR cb.email ILIKE :search)
        """)
        params["search"] = f"%{search}%"
    
    if activo is not None:
        query = text(str(query) + " AND cb.activo = :activo")
        params["activo"] = activo
    
    query = text(str(query) + " ORDER BY cb.created_at DESC")
    
    result = await db.execute(query, params)
    rows = result.fetchall()
    
    tenants = []
    for row in rows:
        tenants.append(TenantListResponse(
            id=row[0],
            nombre=row[1],
            email=row[2],
            telefono=row[3],
            latitud=float(row[4]) if row[4] else None,
            longitud=float(row[5]) if row[5] else None,
            activo=row[6],
            fecha_suspension=row[7],
            motivo_suspension=row[8],
            suspendido_por=row[9],
            created_at=row[10],
            updated_at=row[11],
            total_empresas=0,
            total_usuarios=0,
            total_viajes=0,
        ))
    
    return tenants


# ============================================
# CREAR TENANT
# ============================================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=TenantResponse)
async def create_tenant(
    data: TenantCreate,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Crear un nuevo tenant (Super Admin)."""
    
    # Verificar que no exista con el mismo nombre
    check_query = text("""
        SELECT id FROM tenant.control_base WHERE nombre = :nombre
    """)
    result = await db.execute(check_query, {"nombre": data.nombre})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tenant con ese nombre"
        )
    
    # Crear tenant
    insert_query = text("""
        INSERT INTO tenant.control_base (
            id, nombre, email, telefono, latitud, longitud,
            activo, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :nombre, :email, :telefono, :latitud, :longitud,
            true, NOW(), NOW()
        )
        RETURNING id, nombre, email, telefono, latitud, longitud,
                  activo, fecha_suspension, motivo_suspension, suspendido_por,
                  created_at, updated_at
    """)
    
    result = await db.execute(insert_query, {
        "nombre": data.nombre,
        "email": data.email,
        "telefono": data.telefono,
        "latitud": data.latitud,
        "longitud": data.longitud,
    })
    await db.commit()
    
    row = result.first()
    
    return TenantResponse(
        id=row[0],
        nombre=row[1],
        email=row[2],
        telefono=row[3],
        latitud=float(row[4]) if row[4] else None,
        longitud=float(row[5]) if row[5] else None,
        activo=row[6],
        fecha_suspension=row[7],
        motivo_suspension=row[8],
        suspendido_por=row[9],
        created_at=row[10],
        updated_at=row[11],
    )


# ============================================
# OBTENER DETALLE DE TENANT
# ============================================

@router.get("/{id}", response_model=TenantResponse)
async def get_tenant_detail(
    id: str,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Obtener detalle de un tenant (Super Admin)."""
    
    query = text("""
        SELECT 
            cb.id, cb.nombre, cb.email, cb.telefono,
            cb.latitud, cb.longitud, cb.activo,
            cb.fecha_suspension, cb.motivo_suspension, cb.suspendido_por,
            cb.created_at, cb.updated_at
        FROM tenant.control_base cb
        WHERE cb.id = :id
    """)
    
    result = await db.execute(query, {"id": UUID(id)})
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
        latitud=float(row[4]) if row[4] else None,
        longitud=float(row[5]) if row[5] else None,
        activo=row[6],
        fecha_suspension=row[7],
        motivo_suspension=row[8],
        suspendido_por=row[9],
        created_at=row[10],
        updated_at=row[11],
    )


# ============================================
# ACTUALIZAR TENANT
# ============================================

@router.put("/{id}", response_model=TenantResponse)
async def update_tenant(
    id: str,
    data: TenantUpdate,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Actualizar un tenant (Super Admin)."""
    
    # Verificar que existe
    check_query = text("""
        SELECT id FROM tenant.control_base WHERE id = :id
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )
    
    # Construir actualización
    updates = []
    params = {"id": UUID(id)}
    
    if data.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = data.nombre
    
    if data.email is not None:
        updates.append("email = :email")
        params["email"] = data.email
    
    if data.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = data.telefono
    
    if data.latitud is not None:
        updates.append("latitud = :latitud")
        params["latitud"] = data.latitud
    
    if data.longitud is not None:
        updates.append("longitud = :longitud")
        params["longitud"] = data.longitud
    
    if data.activo is not None:
        updates.append("activo = :activo")
        params["activo"] = data.activo
    
    if updates:
        updates.append("updated_at = NOW()")
        query_update = text(f"""
            UPDATE tenant.control_base 
            SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, nombre, email, telefono, latitud, longitud,
                      activo, fecha_suspension, motivo_suspension, suspendido_por,
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
            latitud=float(row[4]) if row[4] else None,
            longitud=float(row[5]) if row[5] else None,
            activo=row[6],
            fecha_suspension=row[7],
            motivo_suspension=row[8],
            suspendido_por=row[9],
            created_at=row[10],
            updated_at=row[11],
        )
    
    # Si no hay cambios, devolver el tenant actual
    return await get_tenant_detail(id, current_user, db)


# ============================================
# SUSPENDER TENANT
# ============================================

@router.post("/{id}/suspender")
async def suspender_tenant(
    id: str,
    data: TenantSuspender,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Suspender un tenant (Super Admin)."""
    
    # Verificar que existe
    check_query = text("""
        SELECT id, activo, fecha_suspension FROM tenant.control_base WHERE id = :id
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )
    
    if row[2] is not None:  # fecha_suspension no es NULL
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tenant ya está suspendido"
        )
    
    # Suspender tenant
    update_query = text("""
        UPDATE tenant.control_base 
        SET 
            activo = false,
            fecha_suspension = NOW(),
            motivo_suspension = :motivo,
            suspendido_por = :suspendido_por,
            updated_at = NOW()
        WHERE id = :id
        RETURNING id, nombre, email, telefono, latitud, longitud,
                  activo, fecha_suspension, motivo_suspension, suspendido_por,
                  created_at, updated_at
    """)
    
    result = await db.execute(update_query, {
        "id": UUID(id),
        "motivo": data.motivo,
        "suspendido_por": current_user.user_id
    })
    await db.commit()
    
    row = result.first()
    
    return {
        "message": "Tenant suspendido correctamente",
        "id": str(row[0]),
        "nombre": row[1],
        "motivo": data.motivo,
        "suspendido_por": str(current_user.user_id)
    }


# ============================================
# ACTIVAR TENANT
# ============================================

@router.post("/{id}/activar")
async def activar_tenant(
    id: str,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Activar un tenant previamente suspendido (Super Admin)."""
    
    # Verificar que existe
    check_query = text("""
        SELECT id, fecha_suspension FROM tenant.control_base WHERE id = :id
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )
    
    if row[1] is None:  # fecha_suspension es NULL
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tenant no está suspendido"
        )
    
    # Activar tenant
    update_query = text("""
        UPDATE tenant.control_base 
        SET 
            activo = true,
            fecha_suspension = NULL,
            motivo_suspension = NULL,
            suspendido_por = NULL,
            updated_at = NOW()
        WHERE id = :id
        RETURNING id, nombre, email, telefono, latitud, longitud,
                  activo, fecha_suspension, motivo_suspension, suspendido_por,
                  created_at, updated_at
    """)
    
    result = await db.execute(update_query, {"id": UUID(id)})
    await db.commit()
    
    row = result.first()
    
    return {
        "message": "Tenant activado correctamente",
        "id": str(row[0]),
        "nombre": row[1]
    }


# ============================================
# ELIMINAR TENANT (baja lógica)
# ============================================

@router.delete("/{id}")
async def delete_tenant(
    id: str,
    current_user: SuperAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Eliminar (baja lógica) un tenant (Super Admin)."""
    
    # Verificar que existe y está activo
    check_query = text("""
        SELECT id FROM tenant.control_base WHERE id = :id AND activo = true
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado o ya inactivo"
        )
    
    # Verificar si tiene empresas activas
    query_empresas = text("""
        SELECT COUNT(*) FROM tenant.empresa WHERE control_base_id = :id AND activo = true
    """)
    result = await db.execute(query_empresas, {"id": UUID(id)})
    empresas_activas = result.scalar()
    
    if empresas_activas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el tenant porque tiene {empresas_activas} empresas activas. "
                   "Primero desactive todas las empresas."
        )
    
    # Desactivar tenant
    update_query = text("""
        UPDATE tenant.control_base 
        SET activo = false, updated_at = NOW() 
        WHERE id = :id
    """)
    await db.execute(update_query, {"id": UUID(id)})
    await db.commit()
    
    return {
        "message": "Tenant desactivado correctamente",
        "id": id,
        "estado": "inactivo"
    }