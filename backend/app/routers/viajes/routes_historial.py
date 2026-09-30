"""
Viajes - Endpoints de historial, estado y calificación.
Extraído de routes.py (refactor 2026-09-24).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user

from .queries import GET_VIAJE_BY_ID
from .services import formatear_respuesta_viaje
from .schemas import (
    ViajeEstadoResponse,
    CalificarViajeRequest,
    CalificarViajeResponse,
)

router = APIRouter()


# ============================================
# CALIFICAR VIAJE
# ============================================

@router.post("/{viaje_id}/calificar", response_model=CalificarViajeResponse)
async def calificar_viaje(
    viaje_id: UUID,
    request: CalificarViajeRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calificar un viaje completado"""
    user_id, _, _, user_tipo = current_user

    if user_tipo.lower() == "pasajero":
        calificado_tipo = "chofer"
        get_query = text("""
            SELECT id, chofer_id, estado FROM trip.viaje_solicitado
            WHERE id = :viaje_id AND pasajero_id = :user_id AND estado = 'finalizado'
        """)
    else:
        calificado_tipo = "pasajero"
        get_query = text("""
            SELECT id, pasajero_id, estado FROM trip.viaje_solicitado
            WHERE id = :viaje_id AND chofer_id = :user_id AND estado = 'finalizado'
        """)

    result = await db.execute(get_query, {"viaje_id": viaje_id, "user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Viaje no encontrado o no finalizado"
        )

    calificado_id = row[1]

    check_rate = text("""
        SELECT id FROM trip.calificacion
        WHERE viaje_id = :viaje_id AND calificador_id = :user_id
    """)

    rate_result = await db.execute(check_rate, {"viaje_id": viaje_id, "user_id": user_id})
    if rate_result.first():
        raise HTTPException(status_code=400, detail="Ya calificaste este viaje")

    insert_query = text("""
        INSERT INTO trip.calificacion (
            id, viaje_id, calificador_id, calificado_id, puntaje, comentario, created_at
        )
        VALUES (gen_random_uuid(), :viaje_id, :calificador_id, :calificado_id, :puntaje, :comentario, NOW())
    """)

    await db.execute(insert_query, {
        "viaje_id": viaje_id,
        "calificador_id": user_id,
        "calificado_id": calificado_id,
        "puntaje": request.puntaje,
        "comentario": request.comentario
    })

    if calificado_tipo == "chofer":
        update_rating = text("""
            UPDATE fleet.chofer_vehiculo
            SET calificacion_promedio = (
                SELECT AVG(puntaje)::DECIMAL(3,2)
                FROM trip.calificacion
                WHERE calificado_id = :chofer_id
            ),
            total_calificaciones = total_calificaciones + 1
            WHERE usuario_id = :chofer_id
        """)
        await db.execute(update_rating, {"chofer_id": calificado_id})

    await db.commit()

    return CalificarViajeResponse(
        success=True,
        message="Calificación registrada"
    )


# ============================================
# HISTORIAL (MEJORADO CON MÁS DATOS)
# ============================================

@router.get("/historial", response_model=dict)
async def obtener_historial_viajes(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    estado: Optional[str] = None,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener historial de viajes con más detalles
    """
    _, control_base_id, _, _ = current_user

    filters = ["vs.control_base_id = :control_base_id"]
    params = {"control_base_id": control_base_id, "limit": limit, "offset": offset}

    if estado:
        filters.append("vs.estado = :estado")
        params["estado"] = estado

    where_clause = " AND ".join(filters)

    # ✅ CONSULTA CON FECHA Y HORA SEPARADOS
    query = text(f"""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_estimado,
            vs.precio_final,
            vs.created_at,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            
            -- Pasajero
            COALESCE(p.nombre || ' ' || p.apellido, up.email) as pasajero_nombre,
            
            -- Chofer
            COALESCE(p2.nombre || ' ' || p2.apellido, uc.email, 'Sin asignar') as chofer_nombre,
            
            -- ✅ FECHA formateada (DD/MM/YYYY)
            TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
            
            -- ✅ HORA formateada (HH24:MI)
            TO_CHAR(vs.created_at, 'HH24:MI') as hora,
            
            -- ✅ PRECIO según estado
            CASE 
                WHEN vs.estado = 'finalizado' THEN vs.precio_final
                ELSE vs.precio_estimado
            END as precio_mostrado,
            
            -- ✅ EMPRESA
            cb.nombre as empresa,
            
            -- ✅ PROPIETARIO
            COALESCE(
                p_prop.nombre || ' ' || p_prop.apellido,
                u_prop.email,
                'No asignado'
            ) as propietario_nombre,
            
            -- Datos del vehículo
            v.patente,
            v.marca,
            v.modelo,
            
            -- Calificación
            c.puntaje as calificacion,
            
            -- Coordenadas
            ST_X(vs.origen::geometry) as origen_lat,
            ST_Y(vs.origen::geometry) as origen_lng,
            ST_X(vs.destino::geometry) as destino_lat,
            ST_Y(vs.destino::geometry) as destino_lng

        FROM trip.viaje_solicitado vs

        -- Pasajero
        JOIN auth.usuario up ON up.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = up.id

        -- Chofer
        LEFT JOIN auth.usuario uc ON uc.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = uc.id

        -- ✅ EMPRESA
        LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

        -- Vehículo
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

        -- ✅ PROPIETARIO
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

        -- Calificación (solo si existe)
        LEFT JOIN trip.calificacion c ON c.viaje_id = vs.id 
            AND c.calificador_id = vs.pasajero_id

        WHERE {where_clause}
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, params)
    rows = result.all()

    return {
        "total": len(rows),
        "limit": limit,
        "offset": offset,
        "viajes": [
            {
                "id": row[0],
                "estado": row[1],
                "direccion_origen": row[2] or '',
                "direccion_destino": row[3] or '',
                "precio_estimado": float(row[4]) if row[4] else None,
                "precio_final": float(row[5]) if row[5] else None,
                "created_at": row[6],
                "aceptado_en": row[7],
                "iniciado_en": row[8],
                "finalizado_en": row[9],
                "distancia_metros": row[10],
                "tiempo_estimado_segundos": row[11],
                "pasajero_nombre": row[12],
                "chofer_nombre": row[13] or "Sin asignar",
                "fecha": row[14],
                "hora": row[15],
                "precio_mostrado": float(row[16]) if row[16] else None,
                "empresa": row[17] or "N/A",
                "propietario_nombre": row[18] or "No asignado",
                "patente": row[19] or "N/A",
                "marca": row[20] or "N/A",
                "modelo": row[21] or "N/A",
                "calificacion": row[22],
                "origen_lat": float(row[23]) if row[23] else None,
                "origen_lng": float(row[24]) if row[24] else None,
                "destino_lat": float(row[25]) if row[25] else None,
                "destino_lng": float(row[26]) if row[26] else None
            }
            for row in rows
        ]
    }


# ============================================
# ESTADO DEL VIAJE
# ============================================

@router.get("/{viaje_id}/estado", response_model=ViajeEstadoResponse)
async def obtener_estado_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estado de un viaje especifico"""
    _, control_base_id, _, _ = current_user

    result = await db.execute(GET_VIAJE_BY_ID, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    return await formatear_respuesta_viaje(row)