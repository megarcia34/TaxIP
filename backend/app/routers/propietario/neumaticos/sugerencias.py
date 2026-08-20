"""
Endpoints de sugerencias de neumáticos
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_propietario_context
from app.routers.propietario.utils import verificar_vehiculo_propietario
from app.routers.propietario.neumaticos.utils import get_posicion_inversa
from app.schemas.propietario_schemas import SugerenciaAtenderRequest, SugerenciaDesestimarRequest

router = APIRouter()


@router.get("/vehiculos/{vehiculo_id}/neumaticos/sugerencias")
async def listar_sugerencias_vehiculo(
    vehiculo_id: UUID,
    estado: Optional[str] = Query(None, pattern="^(PENDIENTE|VISTA|ACCIONADA|DESESTIMADA)$"),
    prioridad: Optional[str] = Query(None, pattern="^(ALTA|MEDIA|BAJA)$"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Listar sugerencias de neumáticos del vehículo."""
    propietario_id = UUID(ctx["propietario_id"])
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    query = text("""
        SELECT 
            ns.id, ns.tipo_sugerencia, ns.mensaje, ns.prioridad,
            ns.km_actual, ns.km_umbral, ns.estado,
            ns.fecha_generacion, ns.fecha_atendida,
            nv.codigo_interno, hp.eje_posicion,
            EXTRACT(DAY FROM (NOW() - ns.fecha_generacion))::INTEGER as dias_activa
        FROM fleet.neumatico_sugerencia ns
        LEFT JOIN fleet.neumatico_vehiculo nv ON nv.id = ns.neumatico_vehiculo_id
        LEFT JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id 
            AND hp.fecha_desmontaje IS NULL
        WHERE ns.vehiculo_id = :vehiculo_id
    """)
    
    params = {"vehiculo_id": vehiculo_id}
    
    if estado:
        query = text(query.text + " AND ns.estado = :estado")
        params["estado"] = estado
    
    if prioridad:
        query = text(query.text + " AND ns.prioridad = :prioridad")
        params["prioridad"] = prioridad
    
    query = text(query.text + " ORDER BY ns.fecha_generacion DESC")
    result = await db.execute(query, params)
    rows = result.all()
    
    sugerencias = []
    resumen = {"pendientes": 0, "atendidas": 0, "desestimadas": 0, "rojas": 0, "amarillas": 0, "verdes": 0}
    posicion_inversa = get_posicion_inversa()
    
    for row in rows:
        color = "ROJO" if row[3] == "ALTA" else "AMARILLO" if row[3] == "MEDIA" else "VERDE"
        posicion_frontend = posicion_inversa.get(row[10], row[10]) if row[10] else None
        
        if row[6] == "PENDIENTE":
            resumen["pendientes"] += 1
            if color == "ROJO":
                resumen["rojas"] += 1
            elif color == "AMARILLO":
                resumen["amarillas"] += 1
            else:
                resumen["verdes"] += 1
        elif row[6] == "ACCIONADA":
            resumen["atendidas"] += 1
        elif row[6] == "DESESTIMADA":
            resumen["desestimadas"] += 1
        
        sugerencias.append({
            "id": str(row[0]),
            "tipo": row[1],
            "mensaje": row[2],
            "prioridad": row[3],
            "color": color,
            "km_actual": int(row[4] or 0),
            "km_umbral": int(row[5] or 0),
            "estado": row[6],
            "fecha_generacion": row[7],
            "fecha_atendida": row[8],
            "neumatico": row[9],
            "posicion": posicion_frontend,
            "dias_activa": int(row[11] or 0)
        })
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "total": len(sugerencias),
        "sugerencias": sugerencias,
        "resumen": resumen
    }


@router.put("/sugerencias/{sugerencia_id}/atender")
async def atender_sugerencia(
    sugerencia_id: UUID,
    data: SugerenciaAtenderRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Marcar sugerencia como atendida."""
    propietario_id = UUID(ctx["propietario_id"])
    user_id = UUID(ctx["user_id"])
    
    query_check = text("""
        SELECT ns.id
        FROM fleet.neumatico_sugerencia ns
        INNER JOIN fleet.vehiculo v ON v.id = ns.vehiculo_id
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE ns.id = :sugerencia_id
          AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"sugerencia_id": sugerencia_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(
            status_code=404,
            detail="Sugerencia no encontrada o no pertenece al propietario"
        )
    
    update_query = text("""
        UPDATE fleet.neumatico_sugerencia
        SET estado = 'ACCIONADA', fecha_atendida = NOW(),
            atendida_por = :user_id, updated_at = NOW()
        WHERE id = :sugerencia_id
        RETURNING estado
    """)
    result = await db.execute(update_query, {
        "sugerencia_id": sugerencia_id,
        "user_id": user_id
    })
    row = result.first()
    
    await db.commit()
    
    return {
        "mensaje": "Sugerencia marcada como atendida",
        "sugerencia_id": str(sugerencia_id),
        "estado_anterior": row[0],
        "estado_actual": "ACCIONADA",
        "fecha_atendida": datetime.now()
    }


@router.put("/sugerencias/{sugerencia_id}/desestimar")
async def desestimar_sugerencia(
    sugerencia_id: UUID,
    data: SugerenciaDesestimarRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Desestimar sugerencia."""
    propietario_id = UUID(ctx["propietario_id"])
    
    query_check = text("""
        SELECT ns.id
        FROM fleet.neumatico_sugerencia ns
        INNER JOIN fleet.vehiculo v ON v.id = ns.vehiculo_id
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE ns.id = :sugerencia_id
          AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"sugerencia_id": sugerencia_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(
            status_code=404,
            detail="Sugerencia no encontrada o no pertenece al propietario"
        )
    
    update_query = text("""
        UPDATE fleet.neumatico_sugerencia
        SET estado = 'DESESTIMADA',
            observaciones = CONCAT(COALESCE(observaciones, ''), ' | Desestimada: ', :motivo),
            updated_at = NOW()
        WHERE id = :sugerencia_id
        RETURNING estado
    """)
    result = await db.execute(update_query, {
        "sugerencia_id": sugerencia_id,
        "motivo": data.motivo
    })
    row = result.first()
    
    await db.commit()
    
    return {
        "mensaje": "Sugerencia desestimada",
        "sugerencia_id": str(sugerencia_id),
        "estado_anterior": "PENDIENTE",
        "estado_actual": "DESESTIMADA"
    }