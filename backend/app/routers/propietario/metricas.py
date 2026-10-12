"""
Metricas del propietario.

R17 - G63: alerta si el motor de precios cae a fallback.

Endpoints:
- GET /api/propietario/metricas/fallbacks: listado de fallbacks de precio
  en los viajes de los vehiculos del propietario.

Fuente de datos: audit.log_acciones con accion='FALLBACK_PRECIO'.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


@router.get("/metricas/fallbacks")
async def listar_fallbacks_precio(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Lista los fallbacks de precio ocurridos en los viajes del propietario.

    Un fallback ocurre cuando el motor de precios no puede calcular el
    precio final y se usa el precio estimado como definitivo.

    Devuelve:
    - total_fallbacks: cantidad total en el historico.
    - viajes_afectados: listado paginado con detalle de cada viaje.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Contar total de fallbacks del propietario
    count_query = text("""
        SELECT COUNT(*) AS total
        FROM audit.log_acciones la
        INNER JOIN trip.viaje_solicitado vs ON vs.id = la.registro_id
        INNER JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE la.accion = 'FALLBACK_PRECIO'
          AND la.control_base_id = :control_base_id
          AND pv.propietario_id = :propietario_id
          AND pv.activo = true
    """)
    count_result = await db.execute(count_query, {
        "propietario_id": str(propietario_id),
        "control_base_id": str(control_base_id),
    })
    total = count_result.scalar() or 0

    # 2. Listar los fallbacks paginados
    list_query = text("""
        SELECT
            la.id AS accion_id,
            la.registro_id AS viaje_id,
            la.created_at,
            la.datos_nuevos->>'precio_estimado' AS precio_estimado,
            la.datos_nuevos->>'motivo' AS motivo,
            vs.estado AS viaje_estado,
            vs.precio_final AS precio_final,
            vs.finalizado_en,
            v.patente AS vehiculo_patente,
            v.marca AS vehiculo_marca,
            v.modelo AS vehiculo_modelo
        FROM audit.log_acciones la
        INNER JOIN trip.viaje_solicitado vs ON vs.id = la.registro_id
        INNER JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE la.accion = 'FALLBACK_PRECIO'
          AND la.control_base_id = :control_base_id
          AND pv.propietario_id = :propietario_id
          AND pv.activo = true
        ORDER BY la.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    list_result = await db.execute(list_query, {
        "propietario_id": str(propietario_id),
        "control_base_id": str(control_base_id),
        "limit": limit,
        "offset": offset,
    })
    rows = list_result.fetchall()

    viajes = []
    for row in rows:
        viajes.append({
            "accion_id": str(row[0]),
            "viaje_id": str(row[1]),
            "fecha": row[2].isoformat() if row[2] else None,
            "precio_estimado": float(row[3]) if row[3] else None,
            "motivo": row[4],
            "viaje_estado": row[5],
            "precio_final": float(row[6]) if row[6] else None,
            "finalizado_en": row[7].isoformat() if row[7] else None,
            "vehiculo": {
                "patente": row[8],
                "marca": row[9],
                "modelo": row[10],
            },
        })

    return {
        "total_fallbacks": total,
        "limit": limit,
        "offset": offset,
        "viajes_afectados": viajes,
    }