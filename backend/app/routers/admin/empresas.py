"""
Router para gestión de empresas (Admin Tenant y Admin Empresa)
FASE 2: BACKEND DE GESTIÓN - ADMIN TENANT Y ADMIN EMPRESA
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from typing import Optional

from app.database import get_db
from app.dependencies import (
    AdminTenantUser,
    AdminEmpresaUser,
    CurrentUser,
    get_admin_tenant_user,
    get_admin_empresa_user,
    get_current_user
)
from app.core.security import get_password_hash
from app.core.validations import validar_tenant_activo, validar_empresa_activa

router = APIRouter(prefix="/admin/empresas", tags=["Admin - Empresas"])


# ============================================
# LISTAR EMPRESAS (Admin Tenant)
# ============================================

@router.get("")
async def get_all_empresas(
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo/inactivo/suspendido"),
):
    """
    Obtener todas las empresas del tenant del admin logueado.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.tipo,
            e.email_facturacion,
            e.telefono,
            e.direccion,
            e.latitud,
            e.longitud,
            e.tarifa_preferencial,
            e.condiciones_pago,
            e.limite_credito,
            e.activo,
            e.fecha_suspension,
            e.motivo_suspension,
            e.suspendido_por,
            e.created_at,
            e.updated_at,
            e.contacto_nombre,
            e.contacto_telefono,
            e.contacto_email,
            (
                SELECT COUNT(*) 
                FROM trip.viaje_solicitado vs 
                WHERE vs.empresa_id = e.id
            ) as total_viajes,
            (
                SELECT COALESCE(SUM(f.total_final), 0)
                FROM payment.factura_empresa f 
                WHERE f.empresa_id = e.id AND f.estado = 'pendiente'
            ) as deuda_pendiente,
            (
                SELECT COUNT(*) 
                FROM auth.usuario_empresa ue 
                WHERE ue.empresa_id = e.id AND ue.activo = true
            ) as empleados_activos
        FROM tenant.empresa e
        WHERE e.control_base_id = :control_base_id
    """)
    
    params = {"control_base_id": control_base_id}

    if search:
        query = text(str(query) + """
            AND (e.nombre ILIKE :search 
                 OR e.email_facturacion ILIKE :search 
                 OR e.contacto_nombre ILIKE :search)
        """)
        params["search"] = f"%{search}%"

    if estado:
        if estado == "activo":
            query = text(str(query) + " AND e.activo = true AND e.fecha_suspension IS NULL")
        elif estado == "inactivo":
            query = text(str(query) + " AND e.activo = false")
        elif estado == "suspendido":
            query = text(str(query) + " AND e.fecha_suspension IS NOT NULL")

    query = text(str(query) + " ORDER BY e.nombre ASC")

    result = await db.execute(query, params)
    rows = result.fetchall()

    empresas = []
    for row in rows:
        if row[11] is False:
            estado_real = "inactivo"
        elif row[12] is not None:
            estado_real = "suspendido"
        else:
            estado_real = "activo"

        empresas.append({
            "id": str(row[0]),
            "nombre": row[1],
            "tipo": row[2],
            "email_facturacion": row[3],
            "telefono": row[4],
            "direccion": row[5],
            "latitud": float(row[6]) if row[6] else None,
            "longitud": float(row[7]) if row[7] else None,
            "tarifa_preferencial": float(row[8] or 0),
            "condiciones_pago": row[9] or "mensual",
            "limite_credito": float(row[10] or 0),
            "estado": estado_real,
            "fecha_suspension": row[12],
            "motivo_suspension": row[13],
            "suspendido_por": str(row[14]) if row[14] else None,
            "created_at": row[15],
            "updated_at": row[16],
            "contacto_nombre": row[17],
            "contacto_telefono": row[18],
            "contacto_email": row[19],
            "total_viajes": row[20] or 0,
            "deuda_pendiente": float(row[21] or 0),
            "empleados_activos": row[22] or 0
        })

    return empresas


# ============================================
# OBTENER DETALLE DE EMPRESA
# ============================================

@router.get("/{id}")
async def get_empresa_detail(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle completo de una empresa por ID.
    Verifica que la empresa pertenezca al tenant del admin.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.tipo,
            e.email_facturacion,
            e.telefono,
            e.direccion,
            e.latitud,
            e.longitud,
            e.tarifa_preferencial,
            e.condiciones_pago,
            e.limite_credito,
            e.activo,
            e.fecha_suspension,
            e.motivo_suspension,
            e.suspendido_por,
            e.created_at,
            e.updated_at,
            e.contacto_nombre,
            e.contacto_telefono,
            e.contacto_email,
            (
                SELECT COUNT(*) 
                FROM trip.viaje_solicitado vs 
                WHERE vs.empresa_id = e.id
            ) as total_viajes,
            (
                SELECT COALESCE(SUM(f.total_final), 0)
                FROM payment.factura_empresa f 
                WHERE f.empresa_id = e.id AND f.estado = 'pendiente'
            ) as deuda_pendiente,
            (
                SELECT COUNT(*) 
                FROM auth.usuario_empresa ue 
                WHERE ue.empresa_id = e.id AND ue.activo = true
            ) as empleados_activos
        FROM tenant.empresa e
        WHERE e.id = :id AND e.control_base_id = :control_base_id
    """)

    result = await db.execute(query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o no pertenece a tu tenant"
        )

    if row[11] is False:
        estado_real = "inactivo"
    elif row[12] is not None:
        estado_real = "suspendido"
    else:
        estado_real = "activo"

    return {
        "id": str(row[0]),
        "nombre": row[1],
        "tipo": row[2],
        "email_facturacion": row[3],
        "telefono": row[4],
        "direccion": row[5],
        "latitud": float(row[6]) if row[6] else None,
        "longitud": float(row[7]) if row[7] else None,
        "tarifa_preferencial": float(row[8] or 0),
        "condiciones_pago": row[9] or "mensual",
        "limite_credito": float(row[10] or 0),
        "estado": estado_real,
        "fecha_suspension": row[12],
        "motivo_suspension": row[13],
        "suspendido_por": str(row[14]) if row[14] else None,
        "created_at": row[15],
        "updated_at": row[16],
        "contacto_nombre": row[17],
        "contacto_telefono": row[18],
        "contacto_email": row[19],
        "total_viajes": row[20] or 0,
        "deuda_pendiente": float(row[21] or 0),
        "empleados_activos": row[22] or 0
    }


# ============================================
# CREAR EMPRESA (Admin Tenant)
# ============================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_empresa(
    data: dict,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva empresa dentro del tenant del admin.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    required_fields = ["nombre"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field}' es requerido"
            )

    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE nombre = :nombre AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "nombre": data["nombre"],
        "control_base_id": control_base_id
    })
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa con ese nombre en este tenant"
        )

    insert_query = text("""
        INSERT INTO tenant.empresa (
            id, control_base_id, nombre, tipo, email_facturacion, telefono,
            direccion, latitud, longitud, tarifa_preferencial, condiciones_pago,
            limite_credito, contacto_nombre, contacto_telefono, contacto_email,
            activo, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :nombre, :tipo, :email_facturacion, :telefono,
            :direccion, :latitud, :longitud, :tarifa_preferencial, :condiciones_pago,
            :limite_credito, :contacto_nombre, :contacto_telefono, :contacto_email,
            true, NOW(), NOW()
        )
        RETURNING id
    """)

    result = await db.execute(insert_query, {
        "control_base_id": control_base_id,
        "nombre": data["nombre"],
        "tipo": data.get("tipo", "hotel"),
        "email_facturacion": data.get("email_facturacion"),
        "telefono": data.get("telefono"),
        "direccion": data.get("direccion"),
        "latitud": data.get("latitud"),
        "longitud": data.get("longitud"),
        "tarifa_preferencial": data.get("tarifa_preferencial", 0.0),
        "condiciones_pago": data.get("condiciones_pago", "mensual"),
        "limite_credito": data.get("limite_credito", 0.0),
        "contacto_nombre": data.get("contacto_nombre"),
        "contacto_telefono": data.get("contacto_telefono"),
        "contacto_email": data.get("contacto_email")
    })
    await db.commit()

    row = result.first()
    empresa_id = row[0]

    return {
        "message": "Empresa creada correctamente",
        "id": str(empresa_id),
        "nombre": data["nombre"]
    }


# ============================================
# ACTUALIZAR EMPRESA
# ============================================

@router.put("/{id}")
async def update_empresa(
    id: str,
    data: dict,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar datos de una empresa.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o no pertenece a tu tenant"
        )

    updates = []
    params = {"id": UUID(id)}

    campo_mapping = {
        "nombre": "nombre",
        "tipo": "tipo",
        "email_facturacion": "email_facturacion",
        "telefono": "telefono",
        "direccion": "direccion",
        "latitud": "latitud",
        "longitud": "longitud",
        "tarifa_preferencial": "tarifa_preferencial",
        "condiciones_pago": "condiciones_pago",
        "limite_credito": "limite_credito",
        "contacto_nombre": "contacto_nombre",
        "contacto_telefono": "contacto_telefono",
        "contacto_email": "contacto_email"
    }

    for key, column in campo_mapping.items():
        if key in data and data[key] is not None:
            updates.append(f"{column} = :{key}")
            params[key] = data[key]

    if "estado" in data and data["estado"] is not None:
        updates.append("activo = :activo")
        params["activo"] = data["estado"] == "activo"

    if updates:
        updates.append("updated_at = NOW()")
        query_update = text(f"""
            UPDATE tenant.empresa 
            SET {', '.join(updates)}
            WHERE id = :id
        """)
        await db.execute(query_update, params)
        await db.commit()

    return {
        "message": "Empresa actualizada correctamente",
        "id": id
    }


# ============================================
# SUSPENDER / ACTIVAR EMPRESA (Admin Tenant)
# ============================================

@router.post("/{id}/suspender")
async def suspender_empresa(
    id: str,
    data: dict,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Suspender una empresa (solo Admin Tenant).
    Requiere motivo de suspensión.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    motivo = data.get("motivo")
    if not motivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El motivo de suspensión es requerido"
        )

    check_query = text("""
        SELECT id, activo, fecha_suspension FROM tenant.empresa 
        WHERE id = :id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o no pertenece a tu tenant"
        )

    if row[2] is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa ya está suspendida"
        )

    update_query = text("""
        UPDATE tenant.empresa 
        SET 
            fecha_suspension = NOW(),
            motivo_suspension = :motivo,
            suspendido_por = :suspendido_por,
            activo = false,
            updated_at = NOW()
        WHERE id = :id
    """)

    await db.execute(update_query, {
        "id": UUID(id),
        "motivo": motivo,
        "suspendido_por": user_id
    })

    update_empleados = text("""
        UPDATE auth.usuario_empresa 
        SET activo = false 
        WHERE empresa_id = :empresa_id
    """)
    await db.execute(update_empleados, {"empresa_id": UUID(id)})

    await db.commit()

    return {
        "message": "Empresa suspendida correctamente",
        "id": id,
        "motivo": motivo,
        "suspendido_por": str(user_id)
    }


@router.post("/{id}/activar")
async def activar_empresa(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Activar una empresa previamente suspendida (solo Admin Tenant).
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    check_query = text("""
        SELECT id, fecha_suspension FROM tenant.empresa 
        WHERE id = :id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o no pertenece a tu tenant"
        )

    if row[1] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa no está suspendida"
        )

    update_query = text("""
        UPDATE tenant.empresa 
        SET 
            fecha_suspension = NULL,
            motivo_suspension = NULL,
            suspendido_por = NULL,
            activo = true,
            updated_at = NOW()
        WHERE id = :id
    """)

    await db.execute(update_query, {"id": UUID(id)})
    await db.commit()

    return {
        "message": "Empresa activada correctamente",
        "id": id
    }


# ============================================
# ELIMINAR EMPRESA (baja lógica)
# ============================================

@router.delete("/{id}")
async def delete_empresa(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar (baja lógica) una empresa.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :id AND control_base_id = :control_base_id AND activo = true
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o ya inactiva"
        )

    query_viajes = text("""
        SELECT COUNT(*) FROM trip.viaje_solicitado 
        WHERE empresa_id = :empresa_id AND estado IN ('pendiente', 'aceptado', 'en_curso')
    """)
    result_viajes = await db.execute(query_viajes, {"empresa_id": UUID(id)})
    viajes_pendientes = result_viajes.scalar()

    if viajes_pendientes > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la empresa porque tiene {viajes_pendientes} viajes pendientes. "
                   "Primero finalice o cancele los viajes."
        )

    query_delete = text("""
        UPDATE tenant.empresa SET activo = false, updated_at = NOW() 
        WHERE id = :id
    """)
    await db.execute(query_delete, {"id": UUID(id)})

    query_empleados = text("""
        UPDATE auth.usuario_empresa 
        SET activo = false 
        WHERE empresa_id = :empresa_id
    """)
    await db.execute(query_empleados, {"empresa_id": UUID(id)})

    await db.commit()

    return {
        "message": "Empresa desactivada correctamente",
        "id": id,
        "estado": "inactivo"
    }


# ============================================
# CREAR EMPLEADO PARA EMPRESA (Admin Tenant o Admin Empresa)
# ============================================

@router.post("/{id}/empleados", status_code=status.HTTP_201_CREATED)
async def create_empleado(
    id: str,
    data: dict,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un empleado para una empresa específica.
    - Admin Tenant: puede crear en cualquier empresa de su tenant
    - Admin Empresa: solo puede crear en su propia empresa
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    check_query = text("""
        SELECT id, control_base_id FROM tenant.empresa 
        WHERE id = :id
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    empresa_row = result.first()

    if not empresa_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    empresa_id = empresa_row[0]
    empresa_control_base = empresa_row[1]

    if empresa_control_base != control_base_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La empresa no pertenece a tu tenant"
        )

    es_admin_tenant = tipo == "admin" and control_base_id is not None
    es_admin_empresa = False

    if not es_admin_tenant:
        check_rol = text("""
            SELECT id FROM auth.usuario_empresa 
            WHERE usuario_id = :user_id 
              AND empresa_id = :empresa_id 
              AND rol IN ('admin_empresa', 'administrador_empresa')
              AND activo = true
        """)
        result = await db.execute(check_rol, {
            "user_id": user_id,
            "empresa_id": empresa_id
        })
        if result.first():
            es_admin_empresa = True

    if not es_admin_tenant and not es_admin_empresa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear empleados en esta empresa"
        )

    required_fields = ["email", "password", "nombre", "apellido"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field}' es requerido"
            )

    email_check = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(email_check, {"email": data["email"]})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'empleado'")
    tipo_result = await db.execute(tipo_query)
    tipo_id = tipo_result.first()

    if not tipo_id:
        tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero'")
        tipo_result = await db.execute(tipo_query)
        tipo_id = tipo_result.first()

    usuario_id = uuid4()
    insert_user = text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
        VALUES (:id, :tipo_id, :control_base_id, :email, :password_hash, true, NOW())
    """)

    await db.execute(insert_user, {
        "id": usuario_id,
        "tipo_id": tipo_id[0],
        "control_base_id": control_base_id,
        "email": data["email"],
        "password_hash": get_password_hash(data["password"])
    })

    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, created_at)
        VALUES (gen_random_uuid(), :user_id, :nombre, :apellido, :telefono, NOW())
    """)

    await db.execute(insert_perfil, {
        "user_id": usuario_id,
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "telefono": data.get("telefono")
    })

    insert_relacion = text("""
        INSERT INTO auth.usuario_empresa (id, empresa_id, usuario_id, rol, activo, created_at)
        VALUES (gen_random_uuid(), :empresa_id, :usuario_id, :rol, true, NOW())
    """)

    await db.execute(insert_relacion, {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "rol": data.get("rol", "recepcionista")
    })

    await db.commit()

    return {
        "message": "Empleado creado correctamente",
        "id": str(usuario_id),
        "email": data["email"],
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "rol": data.get("rol", "recepcionista")
    }


# ============================================
# LISTAR EMPLEADOS DE EMPRESA
# ============================================

@router.get("/{id}/empleados")
async def get_empleados_empresa(
    id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener todos los empleados de una empresa.
    - Admin Tenant: puede ver de cualquier empresa de su tenant
    - Admin Empresa: solo puede ver los de su propia empresa
    - Empleado: solo puede ver los de su empresa (si tiene permiso)
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    check_query = text("""
        SELECT id, control_base_id FROM tenant.empresa 
        WHERE id = :id
    """)
    result = await db.execute(check_query, {"id": UUID(id)})
    empresa_row = result.first()

    if not empresa_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    empresa_id = empresa_row[0]
    empresa_control_base = empresa_row[1]

    if empresa_control_base != control_base_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La empresa no pertenece a tu tenant"
        )

    es_admin_tenant = tipo == "admin" and control_base_id is not None
    es_admin_empresa = False
    es_empleado_de_empresa = False

    if not es_admin_tenant:
        check_rol = text("""
            SELECT rol FROM auth.usuario_empresa 
            WHERE usuario_id = :user_id AND empresa_id = :empresa_id AND activo = true
        """)
        result = await db.execute(check_rol, {
            "user_id": user_id,
            "empresa_id": empresa_id
        })
        rol_row = result.first()
        
        if rol_row:
            rol = rol_row[0]
            if rol in ('admin_empresa', 'administrador_empresa'):
                es_admin_empresa = True
            elif rol == 'recepcionista':
                es_empleado_de_empresa = True

    if not es_admin_tenant and not es_admin_empresa and not es_empleado_de_empresa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los empleados de esta empresa"
        )

    query = text("""
        SELECT 
            u.id,
            u.email,
            p.nombre,
            p.apellido,
            p.telefono,
            ue.rol,
            ue.activo,
            u.created_at,
            u.activo as usuario_activo
        FROM auth.usuario_empresa ue
        JOIN auth.usuario u ON u.id = ue.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE ue.empresa_id = :empresa_id
        ORDER BY u.created_at DESC
    """)

    result = await db.execute(query, {"empresa_id": empresa_id})
    rows = result.fetchall()

    empleados = []
    for row in rows:
        empleados.append({
            "id": str(row[0]),
            "email": row[1],
            "nombre": row[2] or "",
            "apellido": row[3] or "",
            "telefono": row[4],
            "rol": row[5] or "recepcionista",
            "activo": row[6],
            "usuario_activo": row[8],
            "created_at": row[7]
        })

    return empleados


# ============================================
# CUENTA CORRIENTE DE EMPRESA
# ============================================

@router.get("/{id}/cuenta-corriente")
async def get_cuenta_corriente(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado de cuenta corriente de una empresa.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.limite_credito,
            COALESCE(SUM(vs.precio_final), 0) as deuda_total,
            COUNT(CASE WHEN vs.estado IN ('pendiente', 'aceptado', 'en_curso') THEN 1 END) as viajes_pendientes,
            COUNT(CASE WHEN f.estado = 'pendiente' THEN 1 END) as facturas_pendientes
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id AND vs.estado != 'cancelado'
        LEFT JOIN payment.factura_empresa f ON f.empresa_id = e.id AND f.estado = 'pendiente'
        WHERE e.id = :id AND e.control_base_id = :control_base_id
        GROUP BY e.id, e.nombre, e.limite_credito
    """)

    result = await db.execute(query, {
        "id": UUID(id),
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    deuda_total = float(row[3] or 0)
    limite_credito = float(row[2] or 0)

    return {
        "empresa_id": str(row[0]),
        "empresa_nombre": row[1],
        "limite_credito": limite_credito,
        "saldo_disponible": limite_credito - deuda_total,
        "deuda_total": deuda_total,
        "viajes_pendientes": row[4] or 0,
        "facturas_pendientes": row[5] or 0
    }


# ============================================
# ESTADÍSTICAS DE EMPRESA
# ============================================

@router.get("/{id}/estadisticas")
async def get_estadisticas_empresa(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas de viajes de una empresa.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    query = text("""
        SELECT 
            COUNT(*) as total_viajes,
            COUNT(CASE WHEN estado = 'finalizado' THEN 1 END) as viajes_completados,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as viajes_cancelados,
            COUNT(CASE WHEN estado IN ('pendiente', 'aceptado', 'en_curso') THEN 1 END) as viajes_activos,
            COALESCE(AVG(precio_final), 0) as promedio_gasto,
            COALESCE(SUM(precio_final), 0) as total_gastado,
            COUNT(DISTINCT pasajero_id) as pasajeros_distintos
        FROM trip.viaje_solicitado
        WHERE empresa_id = :empresa_id AND control_base_id = :control_base_id
    """)

    result = await db.execute(query, {
        "empresa_id": UUID(id),
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    return {
        "total_viajes": row[0] or 0,
        "viajes_completados": row[1] or 0,
        "viajes_cancelados": row[2] or 0,
        "viajes_activos": row[3] or 0,
        "promedio_gasto": float(row[4] or 0),
        "total_gastado": float(row[5] or 0),
        "pasajeros_distintos": row[6] or 0
    }


# ============================================
# VIAJES DE EMPRESA
# ============================================

@router.get("/{id}/viajes")
async def get_viajes_empresa(
    id: str,
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, description="Límite de resultados"),
    offset: int = Query(0, description="Desplazamiento para paginación"),
):
    """
    Obtener todos los viajes de una empresa.
    Solo accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    await validar_tenant_activo(control_base_id, db)

    query = text("""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_final,
            vs.created_at,
            vs.finalizado_en,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
            COALESCE(pc.nombre || ' ' || pc.apellido, uc.email) as chofer_nombre,
            v.patente
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN auth.usuario uc ON uc.id = vs.chofer_id
        LEFT JOIN auth.perfil_general pc ON pc.usuario_id = uc.id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        WHERE vs.empresa_id = :empresa_id 
          AND vs.control_base_id = :control_base_id
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, {
        "empresa_id": UUID(id),
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.fetchall()

    viajes = []
    for row in rows:
        viajes.append({
            "id": str(row[0]),
            "estado": row[1],
            "origen": row[2],
            "destino": row[3],
            "precio_final": float(row[4]) if row[4] else None,
            "created_at": row[5],
            "finalizado_en": row[6],
            "pasajero": row[7],
            "chofer": row[8],
            "patente": row[9]
        })

    return viajes