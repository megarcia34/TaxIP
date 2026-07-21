"""
Corporate / Hotel endpoints
Registro de empresas, gestión de viajes corporativos y facturación
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/empresa", tags=["Empresa Corporativa"])


# ============================================
# Schemas
# ============================================

class EmpresaCreate(BaseModel):
    nombre: str
    tipo: str = "hotel"
    email_facturacion: str
    telefono: str
    direccion: str
    latitud: float
    longitud: float
    tarifa_preferencial: float = 0.0
    condiciones_pago: str = "mensual"
    limite_credito: float = 0.0
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None


class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    email_facturacion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    tarifa_preferencial: Optional[float] = None
    condiciones_pago: Optional[str] = None
    limite_credito: Optional[float] = None
    activo: Optional[bool] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None


class EmpresaResponse(BaseModel):
    id: UUID
    nombre: str
    tipo: str
    email_facturacion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    tarifa_preferencial: float
    condiciones_pago: str
    limite_credito: float
    activo: bool
    created_at: datetime
    updated_at: datetime
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None
    total_viajes: Optional[int] = 0
    deuda_pendiente: Optional[float] = 0.0


class EmpresaPublicResponse(BaseModel):
    """✅ NUEVO: Respuesta pública para QR (sin datos sensibles)"""
    id: UUID
    nombre: str
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    tipo: str
    telefono: Optional[str] = None


class EmpleadoCreate(BaseModel):
    email: str
    password: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    rol: str = "recepcionista"


class EmpleadoResponse(BaseModel):
    id: UUID
    email: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    rol: str
    activo: bool
    created_at: datetime


class ViajeCorporativoRequest(BaseModel):
    destino: str
    destino_lat: float
    destino_lng: float
    nombre_pasajero: str
    tipo_vehiculo: str = "sedan"
    fecha_programada: Optional[datetime] = None
    notas: Optional[str] = None


class ViajeCorporativoResponse(BaseModel):
    id: UUID
    estado: str
    destino: str
    nombre_pasajero: str
    precio: float
    creado_en: datetime
    chofer_nombre: Optional[str] = None
    patente: Optional[str] = None


class FacturaResponse(BaseModel):
    id: UUID
    periodo: str
    total: float
    descuento: float
    total_final: float
    estado: str
    pdf_url: Optional[str] = None


# ============================================
# ✅ NUEVO ENDPOINT PÚBLICO PARA QR
# ============================================

@router.get("/public/{empresa_id}", response_model=EmpresaPublicResponse)
async def obtener_empresa_publica(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    ✅ ENDPOINT PÚBLICO - NO REQUIERE AUTENTICACIÓN
    Obtener datos básicos de una empresa para precargar el origen en el formulario público.
    Usado exclusivamente para el flujo de QR.
    """
    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.direccion,
            e.latitud,
            e.longitud,
            e.tipo,
            e.telefono
        FROM tenant.empresa e
        WHERE e.id = :empresa_id AND e.activo = true
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva")
    
    return EmpresaPublicResponse(
        id=row[0],
        nombre=row[1],
        direccion=row[2],
        latitud=float(row[3]) if row[3] else None,
        longitud=float(row[4]) if row[4] else None,
        tipo=row[5] or "empresa",
        telefono=row[6]
    )


# ============================================
# MI EMPRESA (PARA USUARIOS NORMALES)
# ============================================
# ✅ MOVIDO ANTES de /{empresa_id} para evitar que "mi-empresa" sea
#    interpretado como un UUID en la ruta dinámica

@router.get("/mi-empresa")
async def obtener_mi_empresa(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the company of the logged-in user
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT e.id, e.nombre, e.tipo, e.email_facturacion, e.telefono,
               e.direccion, e.latitud, e.longitud, e.tarifa_preferencial,
               e.limite_credito, e.condiciones_pago
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id 
          AND ue.activo = true
          AND e.activo = true
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return {
        "id": row[0],
        "nombre": row[1],
        "tipo": row[2],
        "email_facturacion": row[3],
        "telefono": row[4],
        "direccion": row[5],
        "latitud": float(row[6]) if row[6] else None,
        "longitud": float(row[7]) if row[7] else None,
        "tarifa_preferencial": float(row[8] or 0),
        "limite_credito": float(row[9] or 0),
        "condiciones_pago": row[10] or 'mensual'
    }


# ============================================
# UBICACIÓN DE LA EMPRESA DEL USUARIO
# ============================================
# ✅ MOVIDO ANTES de /{empresa_id} para evitar que "ubicacion" sea
#    interpretado como un UUID en la ruta dinámica

@router.get("/ubicacion")
async def obtener_ubicacion_empresa(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la ubicación (dirección y coordenadas) de la empresa 
    asociada al usuario autenticado.
    """
    user_id = current_user[0]
    
    # Primero, obtener el empresa_id del usuario
    empresa_query = text("""
        SELECT ue.empresa_id 
        FROM auth.usuario_empresa ue
        WHERE ue.usuario_id = :user_id 
          AND ue.activo = true
        LIMIT 1
    """)
    empresa_result = await db.execute(empresa_query, {"user_id": user_id})
    empresa_row = empresa_result.first()
    
    if not empresa_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró una empresa asociada al usuario"
        )
    
    empresa_id = empresa_row[0]
    
    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.direccion,
            e.latitud,
            e.longitud,
            e.telefono,
            e.email_facturacion
        FROM tenant.empresa e
        WHERE e.id = :empresa_id 
          AND e.activo = true
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada o inactiva"
        )
    
    return {
        "id": str(row[0]),
        "nombre": row[1],
        "direccion": row[2],
        "latitud": float(row[3]) if row[3] else None,
        "longitud": float(row[4]) if row[4] else None,
        "telefono": row[5],
        "email_facturacion": row[6]
    }


# ============================================
# Endpoints de Empresa (Admin)
# ============================================
# ✅ Las rutas dinámicas /{empresa_id} van AL FINAL para no "comerse"
#    las rutas estáticas que aparecen después

@router.get("/lista", response_model=List[EmpresaResponse])
async def listar_empresas(
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None,
    activo: Optional[bool] = None
):
    """
    Listar todas las empresas/clientes corporativos del tenant
    """
    control_base_id = current_user[1]
    
    params = {
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }
    
    filters = ["e.control_base_id = :control_base_id"]
    
    if search:
        filters.append("(e.nombre ILIKE :search OR e.email_facturacion ILIKE :search OR e.contacto_nombre ILIKE :search)")
        params["search"] = f"%{search}%"
    
    if activo is not None:
        filters.append("e.activo = :activo")
        params["activo"] = activo
    
    where_clause = " AND ".join(filters)
    
    query = text(f"""
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
            e.created_at,
            e.updated_at,
            e.contacto_nombre,
            e.contacto_telefono,
            e.contacto_email,
            COUNT(vs.id) as total_viajes,
            COALESCE(SUM(CASE WHEN f.estado = 'pendiente' THEN f.total_final ELSE 0 END), 0) as deuda_pendiente
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id
        LEFT JOIN payment.factura_empresa f ON f.empresa_id = e.id
        WHERE {where_clause}
        GROUP BY e.id
        ORDER BY e.nombre ASC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        EmpresaResponse(
            id=row[0],
            nombre=row[1],
            tipo=row[2],
            email_facturacion=row[3],
            telefono=row[4],
            direccion=row[5],
            latitud=float(row[6]) if row[6] else None,
            longitud=float(row[7]) if row[7] else None,
            tarifa_preferencial=float(row[8] or 0),
            condiciones_pago=row[9] or 'mensual',
            limite_credito=float(row[10] or 0),
            activo=row[11],
            created_at=row[12],
            updated_at=row[13],
            contacto_nombre=row[14],
            contacto_telefono=row[15],
            contacto_email=row[16],
            total_viajes=row[17] or 0,
            deuda_pendiente=float(row[18] or 0)
        )
        for row in rows
    ]


@router.post("/registro", response_model=EmpresaResponse)
async def registrar_empresa(
    empresa: EmpresaCreate,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new company/hotel (admin only)
    """
    control_base_id = current_user[1]
    
    # Verificar que no exista con el mismo nombre
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE nombre = :nombre AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "nombre": empresa.nombre,
        "control_base_id": control_base_id
    })
    if result.first():
        raise HTTPException(status_code=400, detail="Ya existe una empresa con ese nombre")
    
    empresa_id = uuid4()
    
    insert_query = text("""
        INSERT INTO tenant.empresa (
            id, control_base_id, nombre, tipo, email_facturacion, telefono,
            direccion, latitud, longitud, tarifa_preferencial, condiciones_pago,
            limite_credito, contacto_nombre, contacto_telefono, contacto_email,
            activo, created_at, updated_at
        )
        VALUES (
            :id, :control_base_id, :nombre, :tipo, :email, :telefono,
            :direccion, :latitud, :longitud, :tarifa_preferencial, :condiciones_pago,
            :limite_credito, :contacto_nombre, :contacto_telefono, :contacto_email,
            true, NOW(), NOW()
        )
        RETURNING id, nombre, tipo, email_facturacion, telefono,
                  direccion, latitud, longitud, tarifa_preferencial,
                  condiciones_pago, limite_credito, activo, created_at, updated_at,
                  contacto_nombre, contacto_telefono, contacto_email
    """)
    
    result = await db.execute(insert_query, {
        "id": empresa_id,
        "control_base_id": control_base_id,
        "nombre": empresa.nombre,
        "tipo": empresa.tipo,
        "email": empresa.email_facturacion,
        "telefono": empresa.telefono,
        "direccion": empresa.direccion,
        "latitud": empresa.latitud,
        "longitud": empresa.longitud,
        "tarifa_preferencial": empresa.tarifa_preferencial,
        "condiciones_pago": empresa.condiciones_pago,
        "limite_credito": empresa.limite_credito,
        "contacto_nombre": empresa.contacto_nombre,
        "contacto_telefono": empresa.contacto_telefono,
        "contacto_email": empresa.contacto_email
    })
    
    await db.commit()
    row = result.first()
    
    return EmpresaResponse(
        id=row[0],
        nombre=row[1],
        tipo=row[2],
        email_facturacion=row[3],
        telefono=row[4],
        direccion=row[5],
        latitud=float(row[6]),
        longitud=float(row[7]),
        tarifa_preferencial=float(row[8] or 0),
        condiciones_pago=row[9] or 'mensual',
        limite_credito=float(row[10] or 0),
        activo=row[11],
        created_at=row[12],
        updated_at=row[13],
        contacto_nombre=row[14],
        contacto_telefono=row[15],
        contacto_email=row[16],
        total_viajes=0,
        deuda_pendiente=0.0
    )


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obtener_empresa(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle de una empresa específica
    """
    control_base_id = current_user[1]
    
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
            e.created_at,
            e.updated_at,
            e.contacto_nombre,
            e.contacto_telefono,
            e.contacto_email,
            COUNT(vs.id) as total_viajes,
            COALESCE(SUM(CASE WHEN f.estado = 'pendiente' THEN f.total_final ELSE 0 END), 0) as deuda_pendiente
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id
        LEFT JOIN payment.factura_empresa f ON f.empresa_id = e.id
        WHERE e.id = :empresa_id AND e.control_base_id = :control_base_id
        GROUP BY e.id
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return EmpresaResponse(
        id=row[0],
        nombre=row[1],
        tipo=row[2],
        email_facturacion=row[3],
        telefono=row[4],
        direccion=row[5],
        latitud=float(row[6]) if row[6] else None,
        longitud=float(row[7]) if row[7] else None,
        tarifa_preferencial=float(row[8] or 0),
        condiciones_pago=row[9] or 'mensual',
        limite_credito=float(row[10] or 0),
        activo=row[11],
        created_at=row[12],
        updated_at=row[13],
        contacto_nombre=row[14],
        contacto_telefono=row[15],
        contacto_email=row[16],
        total_viajes=row[17] or 0,
        deuda_pendiente=float(row[18] or 0)
    )


@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def actualizar_empresa(
    empresa_id: UUID,
    empresa: EmpresaUpdate,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update company (admin only)
    """
    control_base_id = current_user[1]
    
    # Verificar que existe
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    updates = []
    params = {"id": empresa_id}
    
    if empresa.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = empresa.nombre
    if empresa.tipo is not None:
        updates.append("tipo = :tipo")
        params["tipo"] = empresa.tipo
    if empresa.email_facturacion is not None:
        updates.append("email_facturacion = :email")
        params["email"] = empresa.email_facturacion
    if empresa.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = empresa.telefono
    if empresa.direccion is not None:
        updates.append("direccion = :direccion")
        params["direccion"] = empresa.direccion
    if empresa.latitud is not None:
        updates.append("latitud = :latitud")
        params["latitud"] = empresa.latitud
    if empresa.longitud is not None:
        updates.append("longitud = :longitud")
        params["longitud"] = empresa.longitud
    if empresa.tarifa_preferencial is not None:
        updates.append("tarifa_preferencial = :tarifa")
        params["tarifa"] = empresa.tarifa_preferencial
    if empresa.condiciones_pago is not None:
        updates.append("condiciones_pago = :condiciones_pago")
        params["condiciones_pago"] = empresa.condiciones_pago
    if empresa.limite_credito is not None:
        updates.append("limite_credito = :limite_credito")
        params["limite_credito"] = empresa.limite_credito
    if empresa.activo is not None:
        updates.append("activo = :activo")
        params["activo"] = empresa.activo
    if empresa.contacto_nombre is not None:
        updates.append("contacto_nombre = :contacto_nombre")
        params["contacto_nombre"] = empresa.contacto_nombre
    if empresa.contacto_telefono is not None:
        updates.append("contacto_telefono = :contacto_telefono")
        params["contacto_telefono"] = empresa.contacto_telefono
    if empresa.contacto_email is not None:
        updates.append("contacto_email = :contacto_email")
        params["contacto_email"] = empresa.contacto_email
    
    if updates:
        updates.append("updated_at = NOW()")
        update_query = text(f"""
            UPDATE tenant.empresa
            SET {', '.join(updates)}
            WHERE id = :id
        """)
        await db.execute(update_query, params)
        await db.commit()
    
    return await obtener_empresa(empresa_id, current_user, db)


@router.delete("/{empresa_id}")
async def eliminar_empresa(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete company (admin only)
    """
    control_base_id = current_user[1]
    
    # Verificar que existe y está activa
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id AND activo = true
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Empresa no encontrada o ya inactiva")
    
    # Verificar si tiene viajes pendientes
    query_viajes = text("""
        SELECT COUNT(*) FROM trip.viaje_solicitado 
        WHERE empresa_id = :empresa_id AND estado IN ('pendiente', 'aceptado', 'en_curso')
    """)
    result_viajes = await db.execute(query_viajes, {"empresa_id": empresa_id})
    viajes_pendientes = result_viajes.scalar()
    
    if viajes_pendientes > 0:
        raise HTTPException(
            400,
            f"No se puede eliminar la empresa porque tiene {viajes_pendientes} viajes pendientes. "
            "Primero finalice o cancele los viajes."
        )
    
    query_delete = text("""
        UPDATE tenant.empresa
        SET activo = false, updated_at = NOW()
        WHERE id = :id
    """)
    
    result = await db.execute(query_delete, {"id": empresa_id})
    await db.commit()
    
    return {"success": True, "message": "Empresa eliminada correctamente"}


# ============================================
# Endpoints de Empleados
# ============================================

@router.post("/{empresa_id}/empleados", response_model=EmpleadoResponse)
async def crear_empleado(
    empresa_id: UUID,
    empleado: EmpleadoCreate,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create employee for a company"""
    
    control_base_id = current_user[1]
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado para esta empresa")
    
    # Verificar si el email ya existe
    email_check = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(email_check, {"email": empleado.email})
    if result.first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear usuario
    usuario_id = uuid4()
    
    # Obtener o crear tipo_usuario_id para 'empleado'
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'empleado'")
    tipo_result = await db.execute(tipo_query)
    tipo_id = tipo_result.first()
    
    if not tipo_id:
        # Si no existe 'empleado', crearlo
        insert_tipo = text("""
            INSERT INTO auth.tipo_usuario (id, nombre)
            VALUES (gen_random_uuid(), 'empleado')
            ON CONFLICT (nombre) DO NOTHING
            RETURNING id
        """)
        tipo_result = await db.execute(insert_tipo)
        tipo_id = tipo_result.first()
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
        VALUES (:id, :tipo_id, :control_base_id, :email, :password_hash, true, NOW())
    """)
    
    await db.execute(insert_user, {
        "id": usuario_id,
        "tipo_id": tipo_id[0],
        "control_base_id": control_base_id,
        "email": empleado.email,
        "password_hash": get_password_hash(empleado.password)
    })
    
    # Crear perfil
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, created_at)
        VALUES (gen_random_uuid(), :user_id, :nombre, :apellido, :telefono, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "user_id": usuario_id,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "telefono": empleado.telefono
    })
    
    # Crear relación empresa-usuario
    insert_relacion = text("""
        INSERT INTO auth.usuario_empresa (id, empresa_id, usuario_id, rol, activo, created_at)
        VALUES (gen_random_uuid(), :empresa_id, :usuario_id, :rol, true, NOW())
    """)
    
    await db.execute(insert_relacion, {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "rol": empleado.rol
    })
    
    await db.commit()
    
    return EmpleadoResponse(
        id=usuario_id,
        email=empleado.email,
        nombre=empleado.nombre,
        apellido=empleado.apellido,
        telefono=empleado.telefono,
        rol=empleado.rol,
        activo=True,
        created_at=datetime.now()
    )


@router.get("/{empresa_id}/empleados", response_model=List[EmpleadoResponse])
async def listar_empleados(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List employees of a company"""
    
    control_base_id = current_user[1]
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado")
    
    query = text("""
        SELECT 
            u.id, u.email, p.nombre, p.apellido, p.telefono,
            ue.rol, ue.activo, u.created_at
        FROM auth.usuario_empresa ue
        JOIN auth.usuario u ON u.id = ue.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE ue.empresa_id = :empresa_id
        ORDER BY u.created_at DESC
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id})
    rows = result.all()
    
    return [
        EmpleadoResponse(
            id=row[0],
            email=row[1],
            nombre=row[2] or "",
            apellido=row[3] or "",
            telefono=row[4],
            rol=row[5],
            activo=row[6],
            created_at=row[7]
        )
        for row in rows
    ]


# ============================================
# VIAJES CORPORATIVOS
# ============================================

@router.post("/{empresa_id}/viajes", response_model=ViajeCorporativoResponse)
async def solicitar_viaje_corporativo(
    empresa_id: UUID,
    request: ViajeCorporativoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request a corporate trip (recepcionist only)"""
    
    user_id, control_base_id, email, user_tipo = current_user
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Verificar que el usuario pertenece a la empresa
    user_check = text("""
        SELECT id FROM auth.usuario_empresa
        WHERE empresa_id = :empresa_id AND usuario_id = :user_id AND activo = true
    """)
    user_result = await db.execute(user_check, {
        "empresa_id": empresa_id,
        "user_id": user_id
    })
    if not user_result.first():
        raise HTTPException(status_code=403, detail="No autorizado para esta empresa")
    
    # Obtener dirección de la empresa
    empresa_query = text("SELECT direccion, latitud, longitud FROM tenant.empresa WHERE id = :id")
    empresa_result = await db.execute(empresa_query, {"id": empresa_id})
    empresa_row = empresa_result.first()
    
    if not empresa_row:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Crear viaje
    viaje_id = uuid4()
    insert_viaje = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id, empresa_id, pasajero_id,
            direccion_origen, direccion_destino,
            origen, destino,
            nombre_pasajero, notas, estado, created_at
        )
        VALUES (
            :id, :control_base_id, :empresa_id, :pasajero_id,
            :origen, :destino,
            ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326),
            ST_SetSRID(ST_MakePoint(:destino_lng, :destino_lat), 4326),
            :nombre_pasajero, :notas, 'pendiente', NOW()
        )
        RETURNING id
    """)
    
    await db.execute(insert_viaje, {
        "id": viaje_id,
        "control_base_id": control_base_id,
        "empresa_id": empresa_id,
        "pasajero_id": user_id,
        "origen": empresa_row[0],
        "origen_lat": empresa_row[1],
        "origen_lng": empresa_row[2],
        "destino": request.destino,
        "destino_lat": request.destino_lat,
        "destino_lng": request.destino_lng,
        "nombre_pasajero": request.nombre_pasajero,
        "notas": request.notas
    })
    
    await db.commit()
    
    return ViajeCorporativoResponse(
        id=viaje_id,
        estado="pendiente",
        destino=request.destino,
        nombre_pasajero=request.nombre_pasajero,
        precio=0,
        creado_en=datetime.now(),
        chofer_nombre=None,
        patente=None
    )


@router.get("/{empresa_id}/viajes", response_model=List[ViajeCorporativoResponse])
async def listar_viajes_corporativos(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """List corporate trips for a company"""
    
    user_id, control_base_id, email, user_tipo = current_user
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado")
    
    query = text("""
        SELECT 
            vs.id, vs.estado, vs.direccion_destino,
            vs.nombre_pasajero, vs.precio_final, vs.created_at,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            v.patente
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        WHERE vs.empresa_id = :empresa_id
        ORDER BY vs.created_at DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id, "limit": limit})
    rows = result.all()
    
    return [
        ViajeCorporativoResponse(
            id=row[0],
            estado=row[1],
            destino=row[2],
            nombre_pasajero=row[3],
            precio=float(row[4]) if row[4] else 0,
            creado_en=row[5],
            chofer_nombre=row[6],
            patente=row[7]
        )
        for row in rows
    ]


# ============================================
# ESTADÍSTICAS DE EMPRESA
# ============================================

@router.get("/{empresa_id}/estadisticas")
async def obtener_estadisticas_empresa(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a company"""
    
    user_id, control_base_id, email, user_tipo = current_user
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado")
    
    query = text("""
        SELECT 
            COUNT(vs.id) as total_viajes,
            COUNT(CASE WHEN DATE_TRUNC('month', vs.created_at) = DATE_TRUNC('month', NOW()) THEN 1 END) as viajes_mes,
            COALESCE(SUM(vs.precio_final), 0) as total_gastado,
            COALESCE(SUM(CASE WHEN DATE_TRUNC('month', vs.created_at) = DATE_TRUNC('month', NOW()) THEN vs.precio_final END), 0) as gasto_mes,
            COUNT(DISTINCT ue.usuario_id) as empleados_activos
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario_empresa ue ON ue.empresa_id = vs.empresa_id AND ue.activo = true
        WHERE vs.empresa_id = :empresa_id
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id})
    row = result.first()
    
    return {
        "total_viajes": row[0] or 0,
        "viajes_mes": row[1] or 0,
        "total_gastado": float(row[2] or 0),
        "gasto_mes": float(row[3] or 0),
        "empleados_activos": row[4] or 0
    }


# ============================================
# FACTURAS
# ============================================

@router.get("/{empresa_id}/facturas", response_model=List[FacturaResponse])
async def listar_facturas_empresa(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List invoices for a company"""
    
    user_id, control_base_id, email, user_tipo = current_user
    
    # Verificar que la empresa pertenece al tenant del usuario
    check_query = text("""
        SELECT id FROM tenant.empresa 
        WHERE id = :empresa_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="No autorizado")
    
    query = text("""
        SELECT id, periodo, total, descuento, total_final, estado, pdf_url
        FROM payment.factura_empresa
        WHERE empresa_id = :empresa_id
        ORDER BY periodo DESC
    """)
    
    result = await db.execute(query, {"empresa_id": empresa_id})
    rows = result.all()
    
    return [
        FacturaResponse(
            id=row[0],
            periodo=row[1],
            total=float(row[2]),
            descuento=float(row[3]),
            total_final=float(row[4]),
            estado=row[5],
            pdf_url=row[6]
        )
        for row in rows
    ]