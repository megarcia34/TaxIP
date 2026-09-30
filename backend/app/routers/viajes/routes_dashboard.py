"""
Viajes - Endpoints del dashboard.
Extraído de routes.py (refactor 2026-09-24).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()


# ============================================
# NUEVO: DASHBOARD DE VIAJES (CON TODOS LOS DATOS)
# ============================================

@router.get("/dashboard")
async def obtener_viajes_dashboard(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de viajes a mostrar"),
    offset: int = Query(0, ge=0, description="Paginación - offset"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de viajes para el dashboard
    CON TODOS LOS DATOS MEJORADOS:
    - ID del viaje
    - Pasajero (nombre completo o email)
    - Chofer (nombre completo o "Sin asignar")
    - Fecha y hora formateadas
    - Precio (estimado o final según estado)
    - Empresa (control_base)
    - Propietario del vehículo
    - Datos del vehículo (patente, marca, modelo)
    """
    _, control_base_id, _, _ = current_user

    # Construir filtros dinámicos
    filters = ["vs.control_base_id = :control_base_id"]
    params = {
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }

    if estado:
        filters.append("vs.estado = :estado")
        params["estado"] = estado

    if fecha_desde:
        filters.append("vs.created_at::date >= :fecha_desde")
        params["fecha_desde"] = fecha_desde

    if fecha_hasta:
        filters.append("vs.created_at::date <= :fecha_hasta")
        params["fecha_hasta"] = fecha_hasta

    where_clause = " AND ".join(filters)

    # Consulta mejorada con TODOS los datos necesarios
    query = text(f"""
        SELECT
            -- ID del viaje
            vs.id as viaje_id,

            -- Estado
            vs.estado,

            -- Direcciones
            vs.direccion_origen,
            vs.direccion_destino,

            -- Precios
            vs.precio_estimado,
            vs.precio_final,

            -- Fechas
            vs.created_at,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en,

            -- Distancia y tiempo
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,

            -- 1. PASAJERO: nombre + apellido o email
            COALESCE(
                p.nombre || ' ' || p.apellido,
                u.email
            ) as pasajero_nombre,

            -- 2. CHOFER: nombre + apellido o "Sin asignar"
            COALESCE(
                p2.nombre || ' ' || p2.apellido,
                u2.email,
                'Sin asignar'
            ) as chofer_nombre,

            -- 3. FECHA formateada (DD/MM/YYYY)
            TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,

            -- 4. HORA formateada (HH:MM AM/PM)
            TO_CHAR(vs.created_at, 'HH:MI AM') as hora,

            -- 5. PRECIO (estimado o final según estado)
            CASE
                WHEN vs.estado = 'finalizado' THEN vs.precio_final
                ELSE vs.precio_estimado
            END as precio_mostrado,

            -- 6. EMPRESA (control_base)
            cb.nombre as empresa,

            -- 7. PROPIETARIO del vehículo
            COALESCE(
                p_prop.nombre || ' ' || p_prop.apellido,
                u_prop.email,
                'No asignado'
            ) as propietario,

            -- 8. DATOS DEL VEHÍCULO
            v.patente,
            v.marca,
            v.modelo,

            -- Coordenadas (para mapa)
            ST_X(vs.origen::geometry) as origen_lat,
            ST_Y(vs.origen::geometry) as origen_lng,
            ST_X(vs.destino::geometry) as destino_lat,
            ST_Y(vs.destino::geometry) as destino_lng

        FROM trip.viaje_solicitado vs

        -- Pasajero
        JOIN auth.usuario u ON u.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id

        -- Chofer
        LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id

        -- Empresa (control_base)
        LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

        -- Vehículo
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

        -- Propietario del vehículo
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

        WHERE {where_clause}
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, params)
    rows = result.all()

    # Obtener total de viajes para la paginación
    count_query = text(f"""
        SELECT COUNT(*)
        FROM trip.viaje_solicitado vs
        WHERE {where_clause}
    """)
    count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
    count_result = await db.execute(count_query, count_params)
    total = count_result.scalar() or 0

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "viajes": [
            {
                "viaje_id": str(row[0]),
                "estado": row[1],
                "direccion_origen": row[2] or "",
                "direccion_destino": row[3] or "",
                "precio_estimado": float(row[4]) if row[4] else None,
                "precio_final": float(row[5]) if row[5] else None,
                "created_at": row[6],
                "aceptado_en": row[7],
                "iniciado_en": row[8],
                "finalizado_en": row[9],
                "distancia_metros": row[10],
                "tiempo_estimado_segundos": row[11],
                "pasajero": row[12],
                "chofer": row[13],
                "fecha": row[14],
                "hora": row[15],
                "precio": float(row[16]) if row[16] else None,
                "empresa": row[17],
                "propietario": row[18],
                "patente": row[19],
                "marca": row[20],
                "modelo": row[21],
                "origen_lat": float(row[22]) if row[22] else None,
                "origen_lng": float(row[23]) if row[23] else None,
                "destino_lat": float(row[24]) if row[24] else None,
                "destino_lng": float(row[25]) if row[25] else None
            }
            for row in rows
        ]
    }


# ============================================
# ESTADÍSTICAS RÁPIDAS PARA EL DASHBOARD
# ============================================

@router.get("/dashboard/estadisticas")
async def obtener_estadisticas_dashboard(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas rápidas para el dashboard:
    - Total de viajes
    - Por estado (pendiente, aceptado, en_curso, finalizado, cancelado)
    - Recaudación total del día
    - Viajes de hoy
    """
    _, control_base_id, _, _ = current_user

    query = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
            COUNT(CASE WHEN estado = 'aceptado' THEN 1 END) as aceptados,
            COUNT(CASE WHEN estado = 'en_curso' THEN 1 END) as en_curso,
            COUNT(CASE WHEN estado = 'finalizado' THEN 1 END) as finalizados,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as cancelados,
            COUNT(CASE WHEN created_at::date = CURRENT_DATE THEN 1 END) as hoy,
            COALESCE(SUM(CASE WHEN estado = 'finalizado' AND created_at::date = CURRENT_DATE 
                THEN precio_final ELSE 0 END), 0) as recaudacion_hoy
        FROM trip.viaje_solicitado
        WHERE control_base_id = :control_base_id
    """)

    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()

    return {
        "total": row[0] or 0,
        "por_estado": {
            "pendiente": row[1] or 0,
            "aceptado": row[2] or 0,
            "en_curso": row[3] or 0,
            "finalizado": row[4] or 0,
            "cancelado": row[5] or 0
        },
        "hoy": {
            "viajes": row[6] or 0,
            "recaudacion": float(row[7] or 0)
        }
    }