# app/routers/super_admin/tenants.py
# Gestión de tenants (crear, listar, editar, eliminar)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid as uuid_lib
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_super_admin_user
from app.core.security import get_password_hash

# ✅ Importación correcta desde app.schemas.tenant
from app.schemas.tenant import (
    TenantCreate as TenantCreateRequest,
    TenantCreateResponse,
    TenantResponse
)

router = APIRouter(prefix="/api/super-admin/tenants", tags=["Super Admin - Tenants"])


# ============================================================
# LISTAR TENANTS
# ============================================================

@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    current_user: tuple = Depends(get_current_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los tenants de la plataforma
    """
    query = text("""
        SELECT 
            cb.id,
            cb.nombre,
            cb.email,
            cb.telefono,
            cb.direccion,
            cb.latitud,
            cb.longitud,
            cb.ciudad_id,
            g.nombre as ciudad_nombre,
            cb.activo,
            cb.fecha_suspension,
            cb.motivo_suspension,
            cb.suspendido_por,
            cb.created_at,
            cb.updated_at
        FROM tenant.control_base cb
        LEFT JOIN geo.ciudad g ON g.id = cb.ciudad_id
        WHERE cb.activo = true
        ORDER BY cb.nombre
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        TenantResponse(
            id=row[0],
            nombre=row[1],
            email=row[2],
            telefono=row[3],
            direccion=row[4],
            latitud=float(row[5]) if row[5] else None,
            longitud=float(row[6]) if row[6] else None,
            ciudad_id=row[7],
            ciudad_nombre=row[8],
            activo=row[9],
            fecha_suspension=row[10],
            motivo_suspension=row[11],
            suspendido_por=row[12],
            created_at=row[13],
            updated_at=row[14]
        )
        for row in rows
    ]


# ============================================================
# OBTENER TENANT POR ID
# ============================================================

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid_lib.UUID,
    current_user: tuple = Depends(get_current_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un tenant específico por su ID
    """
    query = text("""
        SELECT 
            cb.id,
            cb.nombre,
            cb.email,
            cb.telefono,
            cb.direccion,
            cb.latitud,
            cb.longitud,
            cb.ciudad_id,
            g.nombre as ciudad_nombre,
            cb.activo,
            cb.fecha_suspension,
            cb.motivo_suspension,
            cb.suspendido_por,
            cb.created_at,
            cb.updated_at
        FROM tenant.control_base cb
        LEFT JOIN geo.ciudad g ON g.id = cb.ciudad_id
        WHERE cb.id = :tenant_id
    """)
    
    result = await db.execute(query, {"tenant_id": tenant_id})
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
        activo=row[9],
        fecha_suspension=row[10],
        motivo_suspension=row[11],
        suspendido_por=row[12],
        created_at=row[13],
        updated_at=row[14]
    )


# ============================================================
# CREAR TENANT (con ciudad)
# ============================================================

@router.post("/", response_model=TenantCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    current_user: tuple = Depends(get_current_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo tenant (empresa de taxis) con ciudad asociada.
    
    Si la ciudad no existe, se crea automáticamente en geo.ciudad.
    También se crea un usuario admin_tenant asociado al tenant.
    """
    
    super_admin_id = current_user[0]
    
    # ============================================================
    # 1. VALIDACIONES BÁSICAS
    # ============================================================
    
    # Verificar que el nombre del tenant no exista
    check_tenant = text("SELECT id FROM tenant.control_base WHERE nombre = :nombre")
    result = await db.execute(check_tenant, {"nombre": request.nombre})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un tenant con el nombre '{request.nombre}'"
        )
    
    # Verificar que el email no esté registrado como usuario
    check_email = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_email, {"email": request.email})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{request.email}' ya está registrado como usuario"
        )
    
    # ============================================================
    # 2. VALIDAR O CREAR CIUDAD
    # ============================================================
    
    # Buscar ciudad por nombre (insensible a mayúsculas)
    ciudad_query = text("""
        WITH ciudad AS (
            SELECT id, nombre, codigo_postal 
            FROM geo.ciudad 
            WHERE nombre ILIKE :ciudad_nombre
            LIMIT 1
        ),
        ciudad_creada AS (
            INSERT INTO geo.ciudad (id, nombre, codigo_postal)
            SELECT gen_random_uuid(), :ciudad_nombre, :codigo_postal
            WHERE NOT EXISTS (SELECT 1 FROM ciudad)
            RETURNING id, nombre, codigo_postal
        )
        SELECT id, nombre, codigo_postal FROM ciudad
        UNION ALL
        SELECT id, nombre, codigo_postal FROM ciudad_creada
    """)
    
    result = await db.execute(ciudad_query, {
        "ciudad_nombre": request.ciudad_nombre.strip(),
        "codigo_postal": request.codigo_postal
    })
    ciudad_row = result.first()
    
    if not ciudad_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear o validar la ciudad"
        )
    
    ciudad_id = ciudad_row[0]
    ciudad_nombre = ciudad_row[1]
    ciudad_codigo_postal = ciudad_row[2]
    
    # ============================================================
    # 3. CREAR TENANT
    # ============================================================
    
    tenant_id = uuid_lib.uuid4()
    
    insert_tenant = text("""
        INSERT INTO tenant.control_base (
            id, nombre, email, telefono, direccion, 
            latitud, longitud, ciudad_id, activo,
            created_at, updated_at
        )
        VALUES (
            :id, :nombre, :email, :telefono, :direccion,
            :latitud, :longitud, :ciudad_id, true,
            NOW(), NOW()
        )
    """)
    
    await db.execute(insert_tenant, {
        "id": tenant_id,
        "nombre": request.nombre,
        "email": request.email,
        "telefono": request.telefono,
        "direccion": request.direccion,
        "latitud": request.latitud,
        "longitud": request.longitud,
        "ciudad_id": ciudad_id
    })
    
    # ============================================================
    # 4. CREAR USUARIO ADMIN_TENANT
    # ============================================================
    
    # Obtener ID del tipo "admin_tenant"
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'admin_tenant'")
    result = await db.execute(tipo_query)
    tipo_row = result.first()
    
    if not tipo_row:
        # Si no existe el tipo, crear uno
        insert_tipo = text("""
            INSERT INTO auth.tipo_usuario (id, nombre)
            VALUES (gen_random_uuid(), 'admin_tenant')
            ON CONFLICT (nombre) DO NOTHING
            RETURNING id
        """)
        result = await db.execute(insert_tipo)
        tipo_row = result.first()
        if not tipo_row:
            # Si aún no hay, obtener el id de admin_tenant (recién creado)
            result = await db.execute(text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'admin_tenant'"))
            tipo_row = result.first()
    
    tipo_admin_tenant_id = tipo_row[0]
    
    # Generar contraseña temporal
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    password_hash = get_password_hash(temp_password)
    
    usuario_id = uuid_lib.uuid4()
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, control_base_id, tipo_usuario_id, email, password_hash, activo, created_at, updated_at)
        VALUES (:id, :control_base_id, :tipo_usuario_id, :email, :password_hash, true, NOW(), NOW())
    """)
    
    await db.execute(insert_user, {
        "id": usuario_id,
        "control_base_id": tenant_id,
        "tipo_usuario_id": tipo_admin_tenant_id,
        "email": request.email,
        "password_hash": password_hash
    })
    
    # ============================================================
    # 5. CREAR PERFIL DEL ADMIN_TENANT
    # ============================================================
    
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, created_at)
        VALUES (gen_random_uuid(), :usuario_id, 'Admin', 'Tenant', :telefono, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "usuario_id": usuario_id,
        "telefono": request.telefono
    })
    
    # ============================================================
    # 6. CREAR CONFIGURACIÓN POR DEFECTO DEL TENANT
    # ============================================================
    
    insert_config = text("""
        INSERT INTO tenant.configuracion_tenant (
            id, control_base_id, moneda_default, timezone, idioma,
            habilitar_fidelizacion, habilitar_pagos_online, created_at
        )
        VALUES (
            gen_random_uuid(), :control_base_id, 'ARS', 'America/Argentina/Tucuman', 'es',
            false, true, NOW()
        )
    """)
    
    await db.execute(insert_config, {"control_base_id": tenant_id})
    
    await db.commit()
    
    # ============================================================
    # 7. RESPONDER
    # ============================================================
    
    return TenantCreateResponse(
        success=True,
        tenant_id=tenant_id,
        tenant_nombre=request.nombre,
        ciudad_id=ciudad_id,
        ciudad_nombre=ciudad_nombre,
        admin_email=request.email,
        temp_password=temp_password,
        message="Tenant creado exitosamente. El admin del tenant puede iniciar sesión con las credenciales generadas."
    )