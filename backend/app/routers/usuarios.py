"""
User profile and settings routes
Perfil, direcciones frecuentes, taxistas favoritos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import uuid as uuid_lib
from typing import Optional  # Agregar esta línea
from app.dependencies import get_current_user, get_current_admin_user  # Agregar get_current_admin_user
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.usuario_schemas import (
    PerfilResponse,
    ActualizarPerfilRequest,
    DireccionFrecuenteRequest,
    DireccionFrecuenteResponse,
    TaxistaFavoritoResponse
)

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


# ============================================
# PERFIL DE USUARIO
# ============================================

@router.get("/perfil/{user_id}", response_model=PerfilResponse)
async def obtener_perfil(
    user_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile by ID
    Users can only view their own profile (admins can view all)
    """
    current_user_id, _, _, current_user_tipo = current_user
    
    # Check permission: only admin or same user
    if current_user_tipo.lower() != "admin" and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil"
        )
    
    query = text("""
        SELECT 
            u.id,
            u.email,
            p.nombre,
            p.apellido,
            p.telefono,
            p.documento,
            p.ciudad_id,
            tu.nombre as tipo_usuario,
            u.created_at
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.id = :user_id AND u.activo = true
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return PerfilResponse(
        id=row[0],
        email=row[1],
        nombre=row[2],
        apellido=row[3],
        telefono=row[4],
        documento=row[5],
        ciudad_id=row[6],
        foto_perfil_url=None,
        tipo_usuario=row[7],
        created_at=row[8]
    )


@router.put("/perfil/{user_id}")
async def actualizar_perfil(
    user_id: UUID,
    request: ActualizarPerfilRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile
    Users can only update their own profile
    """
    current_user_id, _, _, current_user_tipo = current_user
    
    if current_user_tipo.lower() != "admin" and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este perfil"
        )
    
    # Check if user exists
    check_query = text("SELECT id FROM auth.usuario WHERE id = :user_id AND activo = true")
    result = await db.execute(check_query, {"user_id": user_id})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Build dynamic UPDATE query
    updates = []
    params = {"user_id": user_id}
    
    if request.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = request.nombre
    if request.apellido is not None:
        updates.append("apellido = :apellido")
        params["apellido"] = request.apellido
    if request.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = request.telefono
    if request.documento is not None:
        updates.append("documento = :documento")
        params["documento"] = request.documento
    if request.ciudad_id is not None:
        updates.append("ciudad_id = :ciudad_id")
        params["ciudad_id"] = request.ciudad_id
    
    if updates:
        update_query = text(f"""
            UPDATE auth.perfil_general
            SET {', '.join(updates)}
            WHERE usuario_id = :user_id
        """)
        await db.execute(update_query, params)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Perfil actualizado exitosamente"
    }


# ============================================
# DIRECCIONES FRECUENTES
# ============================================

@router.get("/direcciones", response_model=list[DireccionFrecuenteResponse])
async def listar_direcciones(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List frequent addresses for current user
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT id, nombre, latitud, longitud, direccion_texto, created_at
        FROM auth.direccion_frecuente
        WHERE usuario_id = :user_id
        ORDER BY created_at DESC
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    rows = result.all()
    
    return [
        DireccionFrecuenteResponse(
            id=row[0],
            nombre=row[1],
            latitud=float(row[2]) if row[2] else None,
            longitud=float(row[3]) if row[3] else None,
            direccion_texto=row[4],
            created_at=row[5]
        )
        for row in rows
    ]


@router.post("/direcciones", response_model=DireccionFrecuenteResponse)
async def crear_direccion(
    request: DireccionFrecuenteRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a frequent address
    """
    user_id = current_user[0]
    direccion_id = uuid_lib.uuid4()
    
    query = text("""
        INSERT INTO auth.direccion_frecuente (
            id, usuario_id, nombre, latitud, longitud, direccion_texto, created_at
        )
        VALUES (:id, :user_id, :nombre, :latitud, :longitud, :direccion_texto, NOW())
        RETURNING id, nombre, latitud, longitud, direccion_texto, created_at
    """)
    
    result = await db.execute(query, {
        "id": direccion_id,
        "user_id": user_id,
        "nombre": request.nombre,
        "latitud": request.latitud,
        "longitud": request.longitud,
        "direccion_texto": request.direccion_texto
    })
    
    await db.commit()
    row = result.first()
    
    return DireccionFrecuenteResponse(
        id=row[0],
        nombre=row[1],
        latitud=float(row[2]) if row[2] else None,
        longitud=float(row[3]) if row[3] else None,
        direccion_texto=row[4],
        created_at=row[5]
    )


@router.delete("/direcciones/{direccion_id}")
async def eliminar_direccion(
    direccion_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a frequent address
    """
    user_id = current_user[0]
    
    query = text("""
        DELETE FROM auth.direccion_frecuente
        WHERE id = :direccion_id AND usuario_id = :user_id
        RETURNING id
    """)
    
    result = await db.execute(query, {
        "direccion_id": direccion_id,
        "user_id": user_id
    })
    
    await db.commit()
    
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada"
        )
    
    return {"success": True, "message": "Dirección eliminada"}


# ============================================
# TAXISTAS FAVORITOS
# ============================================

@router.get("/favoritos", response_model=list[TaxistaFavoritoResponse])
async def listar_favoritos(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List favorite drivers for current passenger
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT 
            tf.id,
            tf.chofer_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre_chofer,
            cv.calificacion_promedio,
            tf.created_at
        FROM auth.taxista_favorito tf
        JOIN auth.usuario u ON u.id = tf.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        WHERE tf.pasajero_id = :user_id
        ORDER BY tf.created_at DESC
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    rows = result.all()
    
    return [
        TaxistaFavoritoResponse(
            id=row[0],
            chofer_id=row[1],
            nombre_chofer=row[2],
            calificacion_promedio=float(row[3]) if row[3] else None,
            created_at=row[4]
        )
        for row in rows
    ]


@router.post("/favoritos/{chofer_id}")
async def agregar_favorito(
    chofer_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a driver to favorites
    """
    pasajero_id = current_user[0]
    
    # Check if driver exists and is a driver
    check_query = text("""
        SELECT u.id FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        WHERE u.id = :chofer_id AND tu.nombre = 'chofer' AND u.activo = true
    """)
    
    result = await db.execute(check_query, {"chofer_id": chofer_id})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chofer no encontrado"
        )
    
    # Check if already favorite
    check_fav = text("""
        SELECT id FROM auth.taxista_favorito
        WHERE pasajero_id = :pasajero_id AND chofer_id = :chofer_id
    """)
    
    fav_result = await db.execute(check_fav, {
        "pasajero_id": pasajero_id,
        "chofer_id": chofer_id
    })
    
    if fav_result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El chofer ya está en tus favoritos"
        )
    
    # Add to favorites
    insert_query = text("""
        INSERT INTO auth.taxista_favorito (id, pasajero_id, chofer_id, created_at)
        VALUES (gen_random_uuid(), :pasajero_id, :chofer_id, NOW())
    """)
    
    await db.execute(insert_query, {
        "pasajero_id": pasajero_id,
        "chofer_id": chofer_id
    })
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Chofer agregado a favoritos"
    }


@router.delete("/favoritos/{favorito_id}")
async def eliminar_favorito(
    favorito_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a driver from favorites
    """
    user_id = current_user[0]
    
    query = text("""
        DELETE FROM auth.taxista_favorito
        WHERE id = :favorito_id AND pasajero_id = :user_id
        RETURNING id
    """)
    
    result = await db.execute(query, {
        "favorito_id": favorito_id,
        "user_id": user_id
    })
    
    await db.commit()
    
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )
    
    return {"success": True, "message": "Chofer eliminado de favoritos"}


# ============================================
# ESTADÍSTICAS DEL USUARIO
# ============================================

@router.get("/estadisticas")
async def obtener_estadisticas(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user statistics (trips count, rating, etc.)
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT 
            COUNT(CASE WHEN vs.estado = 'finalizado' THEN 1 END) as viajes_completados,
            COUNT(CASE WHEN vs.estado = 'cancelado' THEN 1 END) as viajes_cancelados,
            AVG(c.puntaje) as calificacion_promedio,
            COUNT(c.id) as total_calificaciones
        FROM auth.usuario u
        LEFT JOIN trip.viaje_solicitado vs ON vs.pasajero_id = u.id
        LEFT JOIN trip.calificacion c ON c.calificado_id = u.id
        WHERE u.id = :user_id
        GROUP BY u.id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    return {
        "viajes_completados": row[0] or 0,
        "viajes_cancelados": row[1] or 0,
        "calificacion_promedio": float(row[2]) if row[2] else 0,
        "total_calificaciones": row[3] or 0
    }

# ============================================
# LISTAR USUARIOS POR TIPO (para admin)
# ============================================

@router.get("/lista")
async def listar_usuarios_por_tipo(
    tipo: Optional[str] = None,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List users filtered by type (admin only)
    """
    control_base_id = current_user[1]
    
    # Construir la consulta base
    query = text("""
        SELECT 
            u.id,
            u.email,
            u.activo,
            u.created_at,
            tu.nombre as tipo,
            p.nombre,
            p.apellido,
            p.telefono,
            p.documento,
            p.foto_perfil_url
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.control_base_id = :control_base_id
    """)
    
    params = {"control_base_id": control_base_id}
    
    # Agregar filtro por tipo si se especifica
    if tipo:
        query = text(str(query) + " AND tu.nombre = :tipo")
        params["tipo"] = tipo
    
    query = text(str(query) + " ORDER BY u.created_at DESC")
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "email": row[1],
            "activo": row[2],
            "created_at": row[3],
            "tipo": row[4],
            "nombre": row[5],
            "apellido": row[6],
            "telefono": row[7],
            "documento": row[8],
            "foto_perfil_url": row[9]
        }
        for row in rows
    ]