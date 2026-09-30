"""
Viajes - Endpoints de objetos olvidados.
Extraído de routes.py (refactor 2026-09-24).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.dependencies import (
    get_current_passenger_user,
    get_current_admin_user,
)

from .schemas import (
    ObjetoOlvidadoRequest,
    ObjetoOlvidadoResponse,
)

router = APIRouter()


# ============================================
# OBJETOS OLVIDADOS
# ============================================

@router.post("/objeto-olvidado", response_model=ObjetoOlvidadoResponse)
async def reportar_objeto_olvidado(
    request: ObjetoOlvidadoRequest,
    current_user: tuple = Depends(get_current_passenger_user),
    db: AsyncSession = Depends(get_db)
):
    """Reportar objeto olvidado"""
    user_id = current_user[0]

    trip_query = text("""
        SELECT id, chofer_id FROM trip.viaje_solicitado
        WHERE pasajero_id = :user_id AND estado = 'finalizado'
        ORDER BY finalizado_en DESC
        LIMIT 1
    """)

    result = await db.execute(trip_query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="No se encontraron viajes recientes")

    viaje_id = row[0]
    chofer_id = row[1]

    insert_query = text("""
        INSERT INTO trip.objeto_olvidado (
            id, viaje_id, pasajero_id, chofer_id, descripcion, foto_url, estado, created_at, control_base_id
        )
        SELECT 
            gen_random_uuid(), :viaje_id, :pasajero_id, :chofer_id, :descripcion, :foto_url, 'reportado', NOW(),
            control_base_id
        FROM auth.usuario
        WHERE id = :pasajero_id
        RETURNING id, estado, descripcion, created_at
    """)

    result = await db.execute(insert_query, {
        "viaje_id": viaje_id,
        "pasajero_id": user_id,
        "chofer_id": chofer_id,
        "descripcion": request.descripcion,
        "foto_url": request.foto_url
    })

    await db.commit()
    row = result.first()

    return ObjetoOlvidadoResponse(
        id=row[0],
        viaje_id=viaje_id,
        descripcion=request.descripcion,
        estado="reportado",
        created_at=datetime.now(),
        foto_url=request.foto_url
    )


@router.get("/objeto-olvidado")
async def listar_objetos_olvidados(
    viaje_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar objetos olvidados (admin)"""
    control_base_id = current_user[1]

    filters = ["u.control_base_id = :control_base_id"]
    params = {"control_base_id": control_base_id, "limit": limit, "offset": offset}

    if viaje_id:
        filters.append("oo.viaje_id = :viaje_id")
        params["viaje_id"] = viaje_id

    if estado:
        filters.append("oo.estado = :estado")
        params["estado"] = estado

    where_clause = " AND ".join(filters)

    query = text(f"""
        SELECT 
            oo.id,
            oo.viaje_id,
            oo.descripcion,
            oo.estado,
            oo.created_at as fecha_reporte,
            oo.updated_at as fecha_entrega,
            oo.foto_url,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
            u.email as pasajero_email,
            COALESCE(p2.nombre || ' ' || p2.apellido, u2.email) as chofer_nombre,
            vs.direccion_origen as origen,
            vs.direccion_destino as destino,
            oo.observaciones
        FROM trip.objeto_olvidado oo
        JOIN auth.usuario u ON u.id = oo.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        JOIN auth.usuario u2 ON u2.id = oo.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
        JOIN trip.viaje_solicitado vs ON vs.id = oo.viaje_id
        WHERE {where_clause}
        ORDER BY oo.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, params)
    rows = result.all()

    return [
        {
            "id": str(row[0]),
            "viaje_id": str(row[1]),
            "descripcion": row[2],
            "estado": row[3],
            "fecha_reporte": row[4],
            "fecha_entrega": row[5],
            "foto_url": row[6],
            "pasajero_nombre": row[7],
            "pasajero_email": row[8],
            "chofer_nombre": row[9],
            "origen": row[10],
            "destino": row[11],
            "observaciones": row[12]
        }
        for row in rows
    ]


@router.get("/objeto-olvidado/{objeto_id}")
async def obtener_objeto_olvidado(
    objeto_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener detalle de objeto olvidado (admin)"""
    control_base_id = current_user[1]

    query = text("""
        SELECT 
            oo.id,
            oo.viaje_id,
            oo.descripcion,
            oo.estado,
            oo.created_at as fecha_reporte,
            oo.updated_at as fecha_entrega,
            oo.foto_url,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
            u.email as pasajero_email,
            COALESCE(p2.nombre || ' ' || p2.apellido, u2.email) as chofer_nombre,
            vs.direccion_origen as origen,
            vs.direccion_destino as destino,
            oo.observaciones
        FROM trip.objeto_olvidado oo
        JOIN auth.usuario u ON u.id = oo.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        JOIN auth.usuario u2 ON u2.id = oo.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
        JOIN trip.viaje_solicitado vs ON vs.id = oo.viaje_id
        WHERE oo.id = :objeto_id
          AND u.control_base_id = :control_base_id
    """)

    result = await db.execute(query, {
        "objeto_id": objeto_id,
        "control_base_id": control_base_id
    })
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")

    return {
        "id": str(row[0]),
        "viaje_id": str(row[1]),
        "descripcion": row[2],
        "estado": row[3],
        "fecha_reporte": row[4],
        "fecha_entrega": row[5],
        "foto_url": row[6],
        "pasajero_nombre": row[7],
        "pasajero_email": row[8],
        "chofer_nombre": row[9],
        "origen": row[10],
        "destino": row[11],
        "observaciones": row[12]
    }


@router.put("/objeto-olvidado/{objeto_id}")
async def actualizar_estado_objeto(
    objeto_id: UUID,
    estado: str = Query(..., description="reportado, encontrado, entregado"),
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar estado de objeto (admin)"""
    valid_estados = ["reportado", "encontrado", "entregado"]
    if estado not in valid_estados:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Permitidos: {valid_estados}"
        )

    check_query = text("""
        SELECT oo.id FROM trip.objeto_olvidado oo
        JOIN auth.usuario u ON u.id = oo.pasajero_id
        WHERE oo.id = :objeto_id AND u.control_base_id = :control_base_id
    """)

    result = await db.execute(check_query, {
        "objeto_id": objeto_id,
        "control_base_id": current_user[1]
    })

    if not result.first():
        raise HTTPException(status_code=404, detail="Objeto no encontrado")

    update_query = text("""
        UPDATE trip.objeto_olvidado
        SET estado = :estado,
            updated_at = NOW()
        WHERE id = :objeto_id
        RETURNING id
    """)

    await db.execute(update_query, {
        "estado": estado,
        "objeto_id": objeto_id
    })
    await db.commit()

    return {"success": True, "message": f"Estado actualizado a {estado}"}


@router.post("/objeto-olvidado/{objeto_id}/notificar")
async def notificar_pasajero_objeto(
    objeto_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Notificar al pasajero sobre objeto encontrado (admin)"""
    query = text("""
        SELECT 
            oo.id, 
            oo.estado, 
            vs.pasajero_id, 
            oo.descripcion,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre
        FROM trip.objeto_olvidado oo
        JOIN trip.viaje_solicitado vs ON vs.id = oo.viaje_id
        JOIN auth.usuario u ON u.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE oo.id = :objeto_id
          AND u.control_base_id = :control_base_id
    """)

    result = await db.execute(query, {
        "objeto_id": objeto_id,
        "control_base_id": current_user[1]
    })
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")

    if row[1] == 'entregado':
        raise HTTPException(status_code=400, detail="El objeto ya fue entregado")

    insert = text("""
        INSERT INTO notification.notificacion (
            id, usuario_id, titulo, mensaje, tipo, leida, created_at
        )
        VALUES (
            gen_random_uuid(), :pasajero_id,
            '📦 Objeto encontrado',
            'Hemos encontrado el objeto que reportaste como perdido: "' || :descripcion || '". Por favor, revisa el detalle para coordinar la entrega.',
            'objeto_encontrado',
            false,
            NOW()
        )
    """)

    await db.execute(insert, {
        "pasajero_id": row[2],
        "descripcion": row[3][:100] if row[3] else "objeto"
    })
    await db.commit()

    return {
        "success": True,
        "message": f"Notificación enviada a {row[4] or 'pasajero'}"
    }