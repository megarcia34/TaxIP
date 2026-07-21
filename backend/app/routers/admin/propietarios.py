from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/admin/propietarios")
async def get_all_propietarios(
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo/inactivo"),
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener todos los propietarios registrados.
    Solo accesible para administradores.
    """
    admin_id, admin_control_base_id, admin_email, admin_tipo = current_user

    # ========== CORREGIDO: usar propietario_vehiculo ==========
    query = text("""
        SELECT 
            u.id,
            p.nombre,
            p.apellido,
            u.email,
            u.activo,
            u.created_at,
            p.telefono,
            (
                SELECT COUNT(*) 
                FROM fleet.propietario_vehiculo pv
                JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
                WHERE pv.propietario_id = u.id AND pv.activo = true AND v.activo = true
            ) as total_vehiculos,
            (
                SELECT COUNT(*) 
                FROM fleet.contrato_vehiculo c 
                WHERE c.propietario_id = u.id AND c.activo = true
            ) as total_contratos
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.tipo_usuario_id = (
            SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario'
        )
    """)

    params = {}

    if search:
        query = text(str(query) + """
            AND (p.nombre ILIKE :search 
                 OR p.apellido ILIKE :search 
                 OR u.email ILIKE :search)
        """)
        params["search"] = f"%{search}%"

    if estado:
        if estado == "activo":
            query = text(str(query) + " AND u.activo = true")
        elif estado == "inactivo":
            query = text(str(query) + " AND u.activo = false")

    query = text(str(query) + " ORDER BY u.created_at DESC")

    result = await db.execute(query, params)
    rows = result.fetchall()

    propietarios = []
    for row in rows:
        propietarios.append({
            "id": str(row[0]),
            "usuario_id": str(row[0]),
            "nombre": f"{row[1]} {row[2]}" if row[1] and row[2] else row[1] or row[2] or "Sin nombre",
            "email": row[3],
            "telefono": row[6],
            "estado": "activo" if row[4] else "inactivo",
            "total_vehiculos": row[7] or 0,
            "total_contratos": row[8] or 0,
            "fecha_registro": row[5],
        })

    return propietarios


@router.get("/admin/propietarios/{id}")
async def get_propietario_detail(
    id: str,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle completo de un propietario por ID.
    """
    admin_id, admin_control_base_id, admin_email, admin_tipo = current_user

    # ========== CORREGIDO: usar propietario_vehiculo ==========
    query_prop = text("""
        SELECT 
            u.id,
            p.nombre,
            p.apellido,
            u.email,
            u.activo,
            u.created_at,
            p.telefono,
            (
                SELECT COUNT(*) 
                FROM fleet.propietario_vehiculo pv
                JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
                WHERE pv.propietario_id = u.id AND pv.activo = true AND v.activo = true
            ) as total_vehiculos,
            (
                SELECT COUNT(*) 
                FROM fleet.contrato_vehiculo c 
                WHERE c.propietario_id = u.id AND c.activo = true
            ) as total_contratos
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.id = :id 
        AND u.tipo_usuario_id = (
            SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario'
        )
    """)

    result = await db.execute(query_prop, {"id": UUID(id)})
    prop = result.first()

    if not prop:
        raise HTTPException(404, "Propietario no encontrado")

    return {
        "id": str(prop[0]),
        "usuario_id": str(prop[0]),
        "nombre": f"{prop[1]} {prop[2]}" if prop[1] and prop[2] else prop[1] or prop[2] or "Sin nombre",
        "email": prop[3],
        "telefono": prop[6],
        "estado": "activo" if prop[4] else "inactivo",
        "total_vehiculos": prop[7] or 0,
        "total_contratos": prop[8] or 0,
        "fecha_registro": prop[5],
    }


@router.put("/admin/propietarios/{id}")
async def update_propietario(
    id: str,
    data: dict,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar datos de un propietario.
    Solo accesible para administradores.
    """
    admin_id, admin_control_base_id, admin_email, admin_tipo = current_user

    query_check = text("""
        SELECT id FROM auth.usuario 
        WHERE id = :id 
        AND tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario')
    """)
    result = await db.execute(query_check, {"id": UUID(id)})
    if not result.first():
        raise HTTPException(404, "Propietario no encontrado")

    # Actualizar usuario
    updates = []
    params = {"id": UUID(id)}

    if "estado" in data and data["estado"] is not None:
        updates.append("activo = :activo")
        params["activo"] = data["estado"] == "activo"

    if updates:
        query_update = text(f"""
            UPDATE auth.usuario 
            SET {', '.join(updates)}
            WHERE id = :id
        """)
        await db.execute(query_update, params)

    # Actualizar perfil (nombre, apellido, telefono)
    perfil_updates = []
    perfil_params = {"usuario_id": UUID(id)}

    if "nombre" in data and data["nombre"] is not None:
        perfil_updates.append("nombre = :nombre")
        perfil_params["nombre"] = data["nombre"]

    if "apellido" in data and data["apellido"] is not None:
        perfil_updates.append("apellido = :apellido")
        perfil_params["apellido"] = data["apellido"]

    if "telefono" in data and data["telefono"] is not None:
        perfil_updates.append("telefono = :telefono")
        perfil_params["telefono"] = data["telefono"]

    if perfil_updates:
        # Verificar si existe perfil
        query_perfil = text("""
            SELECT id FROM auth.perfil_general WHERE usuario_id = :usuario_id
        """)
        result_perfil = await db.execute(query_perfil, {"usuario_id": UUID(id)})
        perfil = result_perfil.first()

        if perfil:
            query_update_perfil = text(f"""
                UPDATE auth.perfil_general 
                SET {', '.join(perfil_updates)}
                WHERE usuario_id = :usuario_id
            """)
            await db.execute(query_update_perfil, perfil_params)
        else:
            # Insertar perfil si no existe
            query_insert_perfil = text("""
                INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono)
                VALUES (gen_random_uuid(), :usuario_id, :nombre, :apellido, :telefono)
            """)
            await db.execute(query_insert_perfil, perfil_params)

    await db.commit()

    return {
        "message": "Propietario actualizado correctamente",
        "id": id
    }


@router.delete("/admin/propietarios/{id}")
async def delete_propietario(
    id: str,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar (baja lógica) un propietario.
    Solo accesible para administradores.
    """
    admin_id, admin_control_base_id, admin_email, admin_tipo = current_user

    query_check = text("""
        SELECT id FROM auth.usuario 
        WHERE id = :id 
        AND tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario')
        AND activo = true
    """)
    result = await db.execute(query_check, {"id": UUID(id)})
    if not result.first():
        raise HTTPException(404, "Propietario no encontrado o ya inactivo")

    # Verificar si tiene vehículos activos
    query_vehiculos = text("""
        SELECT COUNT(*) FROM fleet.propietario_vehiculo 
        WHERE propietario_id = :propietario_id AND activo = true
    """)
    result_vehiculos = await db.execute(query_vehiculos, {"propietario_id": UUID(id)})
    total_vehiculos = result_vehiculos.scalar()

    if total_vehiculos > 0:
        raise HTTPException(
            400, 
            f"No se puede eliminar el propietario porque tiene {total_vehiculos} vehículos activos. "
            "Primero desactive o transfiera los vehículos."
        )

    query_delete = text("""
        UPDATE auth.usuario SET activo = false WHERE id = :id
    """)
    await db.execute(query_delete, {"id": UUID(id)})
    await db.commit()

    return {
        "message": "Propietario desactivado correctamente",
        "id": id,
        "estado": "inactivo"
    }