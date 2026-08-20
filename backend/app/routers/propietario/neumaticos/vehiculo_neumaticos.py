"""
Endpoints para neumáticos del vehículo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_propietario_context
from app.routers.propietario.utils import verificar_vehiculo_propietario
from app.routers.propietario.neumaticos.utils import (
    determinar_color_neumatico,
    POSICION_MAP,
    get_posicion_inversa
)
from app.schemas.propietario_schemas import (
    NeumaticosActivosResponse,
    NeumaticoActivoResponse
)

router = APIRouter()


@router.get("/vehiculos/{vehiculo_id}/neumaticos")
async def listar_neumaticos_vehiculo(
    vehiculo_id: UUID,
    estado: Optional[str] = Query(None, pattern="^(ACTIVO|DESMONTADO|DESECHADO)$"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos los neumáticos del vehículo."""
    from app.routers.propietario.utils import obtener_km_actual_vehiculo
    
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    query_config = text("""
        SELECT COALESCE(vida_util_neumaticos_km, 50000) as vida_util
        FROM tenant.configuracion_tenant
        WHERE control_base_id = :control_base_id
    """)
    result = await db.execute(query_config, {"control_base_id": control_base_id})
    config = result.first()
    vida_util_km = int(config[0]) if config else 50000
    
    query = text("""
        SELECT 
            nv.id, nv.codigo_interno, nv.marca, nv.modelo_dibujo,
            nv.medida, nv.tipo_neumatico, nv.estado,
            nv.km_totales_acumulados, nv.fecha_alta, nv.fecha_baja,
            hp.eje_posicion, hp.km_montaje, hp.fecha_montaje,
            hp.fecha_desmontaje,
            (SELECT profundidad_mm FROM fleet.neumatico_medicion 
             WHERE historial_posicion_id = hp.id 
             ORDER BY fecha_medicion DESC LIMIT 1) as ultima_profundidad,
            v.patente
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.vehiculo v ON v.id = nv.vehiculo_id
        LEFT JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id 
            AND hp.fecha_desmontaje IS NULL
        WHERE nv.vehiculo_id = :vehiculo_id AND nv.activo = true
    """)
    
    params = {"vehiculo_id": vehiculo_id}
    if estado:
        query = text(query.text + " AND nv.estado = :estado")
        params["estado"] = estado
    
    query = text(query.text + " ORDER BY nv.created_at DESC")
    result = await db.execute(query, params)
    rows = result.all()
    
    neumaticos = []
    km_actual = await obtener_km_actual_vehiculo(vehiculo_id, db)
    
    for row in rows:
        km_en_posicion = None
        if row[10] is not None and row[11] is not None:
            km_en_posicion = (row[12] - row[11]) if row[13] else (km_actual - row[11])
        
        estado_color = determinar_color_neumatico(row[14], km_en_posicion or 0, vida_util_km)
        
        neumaticos.append({
            "id": str(row[0]),
            "codigo_interno": row[1],
            "marca": row[2],
            "modelo_dibujo": row[3],
            "medida": row[4],
            "tipo_neumatico": row[5],
            "estado": row[6],
            "km_totales_acumulados": int(row[7] or 0),
            "fecha_alta": row[8],
            "fecha_baja": row[9],
            "posicion_actual": row[10],
            "km_montaje": int(row[11]) if row[11] else None,
            "km_en_posicion": int(km_en_posicion) if km_en_posicion is not None else None,
            "ultima_profundidad_mm": float(row[14]) if row[14] is not None else None,
            "estado_color": estado_color,
            "patente": row[15]
        })
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "patente": rows[0][15] if rows else None,
        "total": len(neumaticos),
        "neumaticos": neumaticos
    }


@router.get("/vehiculos/{vehiculo_id}/neumaticos/activos")
async def listar_neumaticos_activos(
    vehiculo_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Listar los 4 neumáticos montados (DI, DD, TI, TD)."""
    from app.routers.propietario.utils import obtener_km_actual_vehiculo
    
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    # Obtener datos del vehículo (siempre los necesitamos)
    query_vehiculo = text("""
        SELECT v.patente, v.marca, v.modelo
        FROM fleet.vehiculo v
        WHERE v.id = :vehiculo_id
    """)
    result_vehiculo = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
    vehiculo_row = result_vehiculo.first()
    
    patente = vehiculo_row[0] if vehiculo_row else "SIN PATENTE"
    vehiculo_marca = vehiculo_row[1] if vehiculo_row else "SIN MARCA"
    vehiculo_modelo = vehiculo_row[2] if vehiculo_row else "SIN MODELO"
    
    query_config = text("""
        SELECT 
            COALESCE(vida_util_neumaticos_km, 50000) as vida_util,
            COALESCE(umbral_rotacion_neumaticos_km, 10000) as umbral_rotacion,
            COALESCE(umbral_cambio_neumaticos_km, 45000) as umbral_cambio
        FROM tenant.configuracion_tenant
        WHERE control_base_id = :control_base_id
    """)
    result = await db.execute(query_config, {"control_base_id": control_base_id})
    config = result.first()
    
    vida_util_km = int(config[0]) if config else 50000
    
    km_actual = await obtener_km_actual_vehiculo(vehiculo_id, db)
    
    query = text("""
        SELECT 
            nv.id, nv.codigo_interno, nv.marca, nv.modelo_dibujo,
            nv.medida, hp.eje_posicion, hp.km_montaje,
            hp.fecha_montaje, nv.km_totales_acumulados,
            (SELECT profundidad_mm FROM fleet.neumatico_medicion 
             WHERE historial_posicion_id = hp.id 
             ORDER BY fecha_medicion DESC LIMIT 1) as ultima_profundidad,
            (SELECT mensaje FROM fleet.neumatico_sugerencia 
             WHERE neumatico_vehiculo_id = nv.id 
               AND estado = 'PENDIENTE'
               AND prioridad = 'ALTA'
             ORDER BY fecha_generacion DESC LIMIT 1) as sugerencia_roja,
            (SELECT mensaje FROM fleet.neumatico_sugerencia 
             WHERE neumatico_vehiculo_id = nv.id 
               AND estado = 'PENDIENTE'
               AND prioridad = 'MEDIA'
             ORDER BY fecha_generacion DESC LIMIT 1) as sugerencia_amarilla
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.vehiculo v ON v.id = nv.vehiculo_id
        INNER JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id
        WHERE nv.vehiculo_id = :vehiculo_id
          AND hp.fecha_desmontaje IS NULL
          AND nv.estado = 'ACTIVO'
          AND nv.activo = true
          AND hp.eje_posicion IN ('D1', 'D2', 'T1', 'T2')
        ORDER BY hp.eje_posicion
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id})
    rows = result.all()
    
    neumaticos = {}
    resumen = {"verde": 0, "amarillo": 0, "rojo": 0}
    posicion_inversa = get_posicion_inversa()
    
    # Inicializar las 4 posiciones como None
    posiciones = ["DI", "DD", "TI", "TD"]
    for pos in posiciones:
        neumaticos[pos] = None
    
    for row in rows:
        km_recorridos = km_actual - int(row[6])
        profundidad = float(row[9]) if row[9] is not None else None
        
        estado_color = determinar_color_neumatico(profundidad, km_recorridos, vida_util_km)
        resumen[estado_color.lower()] = resumen.get(estado_color.lower(), 0) + 1
        
        sugerencia = row[10] or row[11]
        posicion_frontend = posicion_inversa.get(row[5], row[5])
        
        neumaticos[posicion_frontend] = NeumaticoActivoResponse(
            id=row[0],
            codigo_interno=row[1],
            marca=row[2],
            modelo_dibujo=row[3],
            medida=row[4],
            km_montaje=int(row[6]),
            km_recorridos=km_recorridos,
            ultima_profundidad_mm=profundidad,
            estado_color=estado_color,
            sugerencia=sugerencia
        )
    
    return NeumaticosActivosResponse(
        vehiculo_id=vehiculo_id,
        patente=patente,
        vehiculo_marca=vehiculo_marca,
        vehiculo_modelo=vehiculo_modelo,
        neumaticos=neumaticos,
        resumen=resumen
    )

@router.get("/vehiculos/{vehiculo_id}/neumaticos/historial")
async def historial_neumaticos_vehiculo(
    vehiculo_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Historial completo de neumáticos del vehículo."""
    propietario_id = UUID(ctx["propietario_id"])
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    query = text("""
        SELECT 
            nv.id, nv.codigo_interno, nv.marca, nv.modelo_dibujo,
            nv.medida, nv.tipo_neumatico, nv.estado,
            nv.km_totales_acumulados, nv.fecha_alta, nv.fecha_baja,
            COUNT(hp.id) as cantidad_posiciones,
            STRING_AGG(hp.eje_posicion || '(' || hp.km_montaje || '-' || COALESCE(hp.km_desmontaje::text, 'ACTUAL') || ')', ', ') as posiciones
        FROM fleet.neumatico_vehiculo nv
        LEFT JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id
        WHERE nv.vehiculo_id = :vehiculo_id AND nv.activo = true
        GROUP BY nv.id
        ORDER BY nv.fecha_alta DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id, "limit": limit, "offset": offset})
    rows = result.all()
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "total": len(rows),
        "historial": [
            {
                "id": str(row[0]),
                "codigo_interno": row[1],
                "marca": row[2],
                "modelo_dibujo": row[3],
                "medida": row[4],
                "tipo_neumatico": row[5],
                "estado": row[6],
                "km_totales_recorridos": int(row[7] or 0),
                "fecha_alta": row[8],
                "fecha_baja": row[9],
                "cantidad_posiciones": int(row[10] or 0),
                "posiciones": row[11]
            }
            for row in rows
        ]
    }