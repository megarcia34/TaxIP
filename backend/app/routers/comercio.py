"""
Comercio (QR) endpoints
Registro de establecimientos y generación de códigos QR
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import hashlib
import qrcode
from io import BytesIO
from fastapi.responses import Response
import base64

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/comercios", tags=["Comercios QR"])


# ============================================
# Schemas
# ============================================

class ComercioCreate(BaseModel):
    nombre: str
    rubro: Optional[str] = None
    direccion: str
    latitud: float
    longitud: float
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None


class ComercioUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class ComercioResponse(BaseModel):
    id: UUID
    nombre: str
    rubro: Optional[str] = None
    direccion: str
    latitud: float
    longitud: float
    codigo_qr: str
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    total_escaneos: int = 0
    total_viajes: int = 0
    url_qr: Optional[str] = None


class ComercioListResponse(BaseModel):
    id: UUID
    nombre: str
    rubro: Optional[str] = None
    direccion: str
    codigo_qr: str
    viajes_generados: int
    escaneos: int
    activo: bool
    created_at: datetime


# ============================================
# Funciones auxiliares
# ============================================

def generar_codigo_qr(nombre: str, lat: float, lng: float) -> str:
    """Genera un código único para el QR basado en nombre y ubicación"""
    import time
    data = f"{nombre}|{lat}|{lng}|{time.time()}"
    return hashlib.md5(data.encode()).hexdigest()[:16]


# ============================================
# Endpoints públicos (sin autenticación)
# ============================================

@router.post("/registro", response_model=ComercioResponse)
async def registrar_comercio(
    comercio: ComercioCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new commerce/establishment and generate QR code
    Public endpoint - no authentication required
    """
    
    # Obtener control_base_id por defecto
    cb_query = text("SELECT id FROM tenant.control_base LIMIT 1")
    cb_result = await db.execute(cb_query)
    control_base_id = cb_result.first()[0]
    
    # Generar código único para QR
    codigo_qr = generar_codigo_qr(comercio.nombre, comercio.latitud, comercio.longitud)
    
    # Verificar que el código no exista
    check_query = text("SELECT id FROM public.comercio WHERE codigo_qr = :codigo")
    result = await db.execute(check_query, {"codigo": codigo_qr})
    while result.first():
        codigo_qr = generar_codigo_qr(comercio.nombre, comercio.latitud, comercio.longitud)
        result = await db.execute(check_query, {"codigo": codigo_qr})
    
    # Insertar comercio
    comercio_id = uuid4()
    insert_query = text("""
        INSERT INTO public.comercio (
            id, nombre, rubro, direccion, latitud, longitud,
            codigo_qr, email_contacto, telefono, control_base_id, activo, created_at, updated_at
        )
        VALUES (
            :id, :nombre, :rubro, :direccion, :latitud, :longitud,
            :codigo_qr, :email, :telefono, :control_base_id, true, NOW(), NOW()
        )
        RETURNING id, nombre, rubro, direccion, latitud, longitud, codigo_qr,
                  email_contacto, telefono, activo, created_at, updated_at
    """)
    
    result = await db.execute(insert_query, {
        "id": comercio_id,
        "nombre": comercio.nombre,
        "rubro": comercio.rubro,
        "direccion": comercio.direccion,
        "latitud": comercio.latitud,
        "longitud": comercio.longitud,
        "codigo_qr": codigo_qr,
        "email": comercio.email_contacto,
        "telefono": comercio.telefono,
        "control_base_id": control_base_id
    })
    
    await db.commit()
    row = result.first()
    
    # Generar URL del QR
    base_url = "http://localhost:3000"
    url_qr = f"{base_url}/reservar?qr={codigo_qr}"
    
    return ComercioResponse(
        id=row[0],
        nombre=row[1],
        rubro=row[2],
        direccion=row[3],
        latitud=float(row[4]),
        longitud=float(row[5]),
        codigo_qr=row[6],
        email_contacto=row[7],
        telefono=row[8],
        activo=row[9],
        created_at=row[10],
        updated_at=row[11],
        url_qr=url_qr,
        total_escaneos=0,
        total_viajes=0
    )


@router.get("/qr/{codigo_qr}")
async def obtener_comercio_por_qr(
    codigo_qr: str,
    db: AsyncSession = Depends(get_db)
):
    """Get commerce by QR code (for redirection) - public"""
    query = text("""
        SELECT id, nombre, rubro, direccion, latitud, longitud, codigo_qr
        FROM public.comercio
        WHERE codigo_qr = :codigo AND activo = true
    """)
    
    result = await db.execute(query, {"codigo": codigo_qr})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="QR no válido")
    
    return {
        "id": str(row[0]),
        "nombre": row[1],
        "rubro": row[2],
        "direccion": row[3],
        "latitud": float(row[4]),
        "longitud": float(row[5]),
        "codigo_qr": row[6]
    }


# ============================================
# Endpoints de administración (requieren login)
# ============================================

@router.get("/lista", response_model=List[ComercioListResponse])
async def listar_comercios(
    rubro: Optional[str] = None,
    search: Optional[str] = None,
    activo: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all commerce establishments (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    params = {
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }
    
    filters = ["c.control_base_id = :control_base_id"]
    
    if rubro:
        filters.append("c.rubro = :rubro")
        params["rubro"] = rubro
    
    if search:
        filters.append("(c.nombre ILIKE :search OR c.direccion ILIKE :search)")
        params["search"] = f"%{search}%"
    
    if activo is not None:
        filters.append("c.activo = :activo")
        params["activo"] = activo
    
    where_clause = " AND ".join(filters)
    
    # CORREGIDO: GROUP BY con todas las columnas del SELECT
    query = text(f"""
        SELECT 
            c.id,
            c.nombre,
            c.rubro,
            c.direccion,
            c.codigo_qr,
            c.activo,
            c.created_at,
            COUNT(DISTINCT e.id) as escaneos,
            COUNT(DISTINCT vs.id) as viajes_generados
        FROM public.comercio c
        LEFT JOIN public.escaneo_qr e ON e.comercio_id = c.id
        LEFT JOIN trip.viaje_solicitado vs ON vs.comercio_id = c.id
        WHERE {where_clause}
        GROUP BY c.id, c.nombre, c.rubro, c.direccion, c.codigo_qr,
                 c.activo, c.created_at
        ORDER BY viajes_generados DESC, c.nombre ASC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        ComercioListResponse(
            id=row[0],
            nombre=row[1],
            rubro=row[2],
            direccion=row[3],
            codigo_qr=row[4],
            activo=row[5],
            created_at=row[6],
            escaneos=row[7] or 0,
            viajes_generados=row[8] or 0
        )
        for row in rows
    ]


@router.get("/{comercio_id}", response_model=ComercioResponse)
async def obtener_comercio(
    comercio_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get commerce by ID (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    query = text("""
        SELECT 
            c.id, c.nombre, c.rubro, c.direccion, 
            c.latitud, c.longitud, c.codigo_qr,
            c.email_contacto, c.telefono, c.activo, 
            c.created_at, c.updated_at,
            COUNT(DISTINCT e.id) as total_escaneos,
            COUNT(DISTINCT vs.id) as total_viajes
        FROM public.comercio c
        LEFT JOIN public.escaneo_qr e ON e.comercio_id = c.id
        LEFT JOIN trip.viaje_solicitado vs ON vs.comercio_id = c.id
        WHERE c.id = :id AND c.control_base_id = :control_base_id
        GROUP BY c.id, c.nombre, c.rubro, c.direccion, c.latitud, c.longitud,
                 c.codigo_qr, c.email_contacto, c.telefono, c.activo,
                 c.created_at, c.updated_at
    """)
    
    result = await db.execute(query, {
        "id": comercio_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    
    base_url = "http://localhost:3000"
    url_qr = f"{base_url}/reservar?qr={row[6]}"
    
    return ComercioResponse(
        id=row[0],
        nombre=row[1],
        rubro=row[2],
        direccion=row[3],
        latitud=float(row[4]),
        longitud=float(row[5]),
        codigo_qr=row[6],
        email_contacto=row[7],
        telefono=row[8],
        activo=row[9],
        created_at=row[10],
        updated_at=row[11],
        total_escaneos=row[12] or 0,
        total_viajes=row[13] or 0,
        url_qr=url_qr
    )


@router.put("/{comercio_id}", response_model=ComercioResponse)
async def actualizar_comercio(
    comercio_id: UUID,
    comercio: ComercioUpdate,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update commerce information (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    # Verificar que existe y pertenece al tenant
    check_query = text("""
        SELECT id FROM public.comercio 
        WHERE id = :id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "id": comercio_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    
    # Construir update dinámico
    updates = []
    params = {"id": comercio_id}
    
    if comercio.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = comercio.nombre
    if comercio.rubro is not None:
        updates.append("rubro = :rubro")
        params["rubro"] = comercio.rubro
    if comercio.direccion is not None:
        updates.append("direccion = :direccion")
        params["direccion"] = comercio.direccion
    if comercio.latitud is not None:
        updates.append("latitud = :latitud")
        params["latitud"] = comercio.latitud
    if comercio.longitud is not None:
        updates.append("longitud = :longitud")
        params["longitud"] = comercio.longitud
    if comercio.email_contacto is not None:
        updates.append("email_contacto = :email")
        params["email"] = comercio.email_contacto
    if comercio.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = comercio.telefono
    if comercio.activo is not None:
        updates.append("activo = :activo")
        params["activo"] = comercio.activo
    
    updates.append("updated_at = NOW()")
    
    if updates:
        update_query = text(f"""
            UPDATE public.comercio
            SET {', '.join(updates)}
            WHERE id = :id
        """)
        await db.execute(update_query, params)
        await db.commit()
    
    return await obtener_comercio(comercio_id, current_user, db)


@router.delete("/{comercio_id}")
async def eliminar_comercio(
    comercio_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a commerce (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    query = text("""
        UPDATE public.comercio
        SET activo = false, updated_at = NOW()
        WHERE id = :id AND control_base_id = :control_base_id
        RETURNING id
    """)
    
    result = await db.execute(query, {
        "id": comercio_id,
        "control_base_id": control_base_id
    })
    await db.commit()
    
    if not result.first():
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    
    return {"success": True, "message": "Comercio eliminado correctamente"}


# ============================================
# GENERAR QR
# ============================================

@router.get("/{comercio_id}/qr")
async def obtener_qr_comercio(
    comercio_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    format: str = "png"
):
    """
    Obtener QR del comercio en diferentes formatos
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    query = text("""
        SELECT id, nombre, codigo_qr, activo
        FROM public.comercio
        WHERE id = :comercio_id AND control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "comercio_id": comercio_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    
    content = f"taxip://solicitar?comercio={row[0]}&qr={row[2]}"
    
    if format == "url":
        return {
            "url": f"/reservar?qr={row[2]}",
            "qr_uuid": row[2],
            "comercio_id": str(row[0]),
            "comercio_nombre": row[1]
        }
    
    # Generar imagen QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    if format == "base64":
        return {
            "qr_base64": base64.b64encode(buffered.getvalue()).decode('utf-8'),
            "qr_uuid": row[2],
            "comercio_id": str(row[0]),
            "comercio_nombre": row[1]
        }
    
    return Response(
        content=buffered.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f'inline; filename="qr_{row[1]}.png"'
        }
    )


# ============================================
# Endpoint de estadísticas (admin)
# ============================================

@router.get("/estadisticas")
async def obtener_estadisticas_qr(
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get QR statistics for admin dashboard
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    # Total comercios del tenant
    total_comercios = await db.execute(
        text("SELECT COUNT(*) FROM public.comercio WHERE control_base_id = :cb_id AND activo = true"),
        {"cb_id": control_base_id}
    )
    
    # Total viajes generados por QR del tenant
    total_viajes = await db.execute(
        text("""
            SELECT COUNT(*) FROM trip.viaje_solicitado 
            WHERE comercio_id IS NOT NULL AND control_base_id = :cb_id
        """),
        {"cb_id": control_base_id}
    )
    
    # Top rubros del tenant
    top_rubros = await db.execute(text("""
        SELECT rubro, COUNT(*) as cantidad
        FROM public.comercio
        WHERE rubro IS NOT NULL AND control_base_id = :cb_id
        GROUP BY rubro
        ORDER BY cantidad DESC
        LIMIT 5
    """), {"cb_id": control_base_id})
    
    # Top comercios del tenant
    top_comercios = await db.execute(text("""
        SELECT c.nombre, COUNT(vs.id) as viajes
        FROM public.comercio c
        JOIN trip.viaje_solicitado vs ON vs.comercio_id = c.id
        WHERE c.control_base_id = :cb_id
        GROUP BY c.id, c.nombre
        ORDER BY viajes DESC
        LIMIT 10
    """), {"cb_id": control_base_id})
    
    # Viajes por mes (últimos 6 meses) del tenant
    viajes_por_mes = await db.execute(text("""
        SELECT 
            TO_CHAR(DATE_TRUNC('month', vs.created_at), 'YYYY-MM') as mes,
            COUNT(*) as viajes
        FROM trip.viaje_solicitado vs
        WHERE vs.comercio_id IS NOT NULL
          AND vs.control_base_id = :cb_id
          AND vs.created_at > NOW() - INTERVAL '6 months'
        GROUP BY DATE_TRUNC('month', vs.created_at)
        ORDER BY mes DESC
    """), {"cb_id": control_base_id})
    
    return {
        "total_comercios": total_comercios.scalar() or 0,
        "total_qrs": total_comercios.scalar() or 0,
        "total_viajes_generados": total_viajes.scalar() or 0,
        "top_rubros": [{"rubro": row[0], "cantidad": row[1]} for row in top_rubros.all()],
        "top_comercios": [{"nombre": row[0], "viajes": row[1]} for row in top_comercios.all()],
        "viajes_por_mes": [{"mes": row[0], "viajes": row[1]} for row in viajes_por_mes.all()]
    }