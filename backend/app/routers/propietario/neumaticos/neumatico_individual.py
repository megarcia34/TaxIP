"""
Endpoints para neumático individual
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_propietario_context
from app.routers.propietario.utils import (
    verificar_vehiculo_propietario,
    verificar_neumatico_propietario,
    obtener_km_actual_vehiculo
)
from app.routers.propietario.neumaticos.utils import (
    determinar_color_neumatico,
    POSICION_MAP,
    get_posicion_inversa,
    generar_sugerencia_neumatico
)
from app.schemas.propietario_schemas import (
    DesmontarRequest,
    CambiarEstadoRequest,
    MedicionRequest
)

router = APIRouter()


@router.get("/neumaticos/{neumatico_id}")
async def obtener_neumatico(
    neumatico_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Obtener detalle completo de un neumático."""
    propietario_id = UUID(ctx["propietario_id"])
    
    await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
    
    query = text("""
        SELECT 
            nv.id, nv.codigo_interno, nv.marca, nv.modelo_dibujo,
            nv.medida, nv.tipo_neumatico, nv.estado,
            nv.km_totales_acumulados, nv.fecha_alta, nv.fecha_baja,
            nv.observaciones,
            v.id as vehiculo_id, v.patente,
            hp.eje_posicion as posicion_actual, hp.km_montaje,
            hp.fecha_montaje, hp.fecha_desmontaje,
            (SELECT profundidad_mm FROM fleet.neumatico_medicion 
             WHERE historial_posicion_id = hp.id 
             ORDER BY fecha_medicion DESC LIMIT 1) as ultima_profundidad,
            (SELECT fecha_medicion FROM fleet.neumatico_medicion 
             WHERE historial_posicion_id = hp.id 
             ORDER BY fecha_medicion DESC LIMIT 1) as ultima_medicion_fecha
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.vehiculo v ON v.id = nv.vehiculo_id
        LEFT JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id
            AND hp.fecha_desmontaje IS NULL
        WHERE nv.id = :neumatico_id AND nv.activo = true
    """)
    result = await db.execute(query, {"neumatico_id": neumatico_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Neumático no encontrado")
    
    km_actual = await obtener_km_actual_vehiculo(row[11], db)
    km_en_posicion = None
    if row[14] is not None and row[13] is not None:
        km_en_posicion = km_actual - int(row[14])
    
    posicion_inversa = get_posicion_inversa()
    posicion_frontend = posicion_inversa.get(row[13], row[13]) if row[13] else None
    
    # Historial de posiciones
    query_historial = text("""
        SELECT eje_posicion, km_montaje, km_desmontaje, fecha_montaje, fecha_desmontaje
        FROM fleet.neumatico_historial_posicion
        WHERE neumatico_vehiculo_id = :neumatico_id
        ORDER BY fecha_montaje DESC
    """)
    result_hist = await db.execute(query_historial, {"neumatico_id": neumatico_id})
    historial_rows = result_hist.all()
    
    historial = []
    for h in historial_rows:
        pos_frontend = posicion_inversa.get(h[0], h[0])
        historial.append({
            "eje": pos_frontend,
            "km_montaje": int(h[1] or 0),
            "km_desmontaje": int(h[2]) if h[2] is not None else None,
            "fecha_montaje": h[3],
            "fecha_desmontaje": h[4]
        })
    
    # Mediciones
    query_mediciones = text("""
        SELECT m.id, m.fecha_medicion, m.profundidad_mm, m.observaciones,
               CONCAT(p.nombre, ' ', p.apellido) as medido_por
        FROM fleet.neumatico_medicion m
        LEFT JOIN auth.perfil_general p ON p.usuario_id = m.medido_por
        WHERE m.historial_posicion_id = (
            SELECT id FROM fleet.neumatico_historial_posicion
            WHERE neumatico_vehiculo_id = :neumatico_id
            ORDER BY fecha_montaje DESC LIMIT 1
        )
        ORDER BY m.fecha_medicion DESC LIMIT 10
    """)
    result_med = await db.execute(query_mediciones, {"neumatico_id": neumatico_id})
    mediciones_rows = result_med.all()
    
    mediciones = []
    for m in mediciones_rows:
        color = "VERDE" if float(m[2]) >= 4.0 else "AMARILLO" if float(m[2]) >= 2.0 else "ROJO"
        mediciones.append({
            "id": str(m[0]),
            "fecha": m[1],
            "profundidad_mm": float(m[2]),
            "estado_color": color,
            "medido_por": m[4],
            "observaciones": m[3]
        })
    
    # Operaciones
    query_operaciones = text("""
        SELECT o.tipo_operacion, o.fecha_operacion, o.km_vehiculo_actual, o.descripcion
        FROM fleet.neumatico_operacion o
        INNER JOIN fleet.neumatico_operacion_detalle od ON od.operacion_id = o.id
        WHERE od.neumatico_vehiculo_id = :neumatico_id
        ORDER BY o.fecha_operacion DESC LIMIT 10
    """)
    result_op = await db.execute(query_operaciones, {"neumatico_id": neumatico_id})
    operaciones_rows = result_op.all()
    
    operaciones = []
    for o in operaciones_rows:
        operaciones.append({
            "tipo": o[0],
            "fecha": o[1],
            "km_vehiculo": int(o[2] or 0),
            "descripcion": o[3]
        })
    
    estado_color = determinar_color_neumatico(row[17], km_en_posicion or 0, 50000)
    
    return {
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
        "observaciones": row[10],
        "vehiculo_id": str(row[11]),
        "patente": row[12],
        "posicion_actual": posicion_frontend,
        "km_en_posicion_actual": km_en_posicion,
        "estado_color": estado_color,
        "ultima_profundidad_mm": float(row[17]) if row[17] is not None else None,
        "ultima_medicion_fecha": row[18],
        "historial_posiciones": historial,
        "mediciones": mediciones,
        "operaciones": operaciones
    }

@router.put("/neumaticos/{neumatico_id}/desmontar")
async def desmontar_neumatico(
    neumatico_id: UUID,
    data: DesmontarRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Desmontar un neumático de su posición actual."""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])
    
    await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
    
    # ✅ AGREGAR hp.km_montaje al SELECT
    query_check = text("""
        SELECT nv.id, nv.vehiculo_id, hp.id as historial_id, hp.eje_posicion, hp.km_montaje
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id
        WHERE nv.id = :neumatico_id AND nv.estado = 'ACTIVO' AND hp.fecha_desmontaje IS NULL
    """)
    result = await db.execute(query_check, {"neumatico_id": neumatico_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El neumático no está ACTIVO o no está montado en ninguna posición"
        )
    
    vehiculo_id = row[1]
    historial_id = row[2]
    posicion = row[3]
    km_montaje = row[4]  # ✅ Obtener km_montaje
    
    insert_operacion = text("""
        INSERT INTO fleet.neumatico_operacion (
            id, vehiculo_id, control_base_id, tipo_operacion,
            descripcion, km_vehiculo_actual, fecha_operacion,
            observaciones, creado_por
        ) VALUES (
            gen_random_uuid(), :vehiculo_id, :control_base_id, 'DESMONTAJE',
            :descripcion, :km_vehiculo_actual, NOW(),
            :observaciones, :creado_por
        ) RETURNING id
    """)
    result = await db.execute(insert_operacion, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id,
        "descripcion": f"Desmontaje por {data.motivo}",
        "km_vehiculo_actual": data.km_vehiculo_actual,
        "observaciones": data.observaciones,
        "creado_por": user_id
    })
    operacion_id = result.scalar()
    
    update_historial = text("""
        UPDATE fleet.neumatico_historial_posicion
        SET km_desmontaje = :km_desmontaje, fecha_desmontaje = NOW(), operacion_id = :operacion_id
        WHERE id = :historial_id
    """)
    await db.execute(update_historial, {
        "km_desmontaje": data.km_vehiculo_actual,
        "operacion_id": operacion_id,
        "historial_id": historial_id
    })
    
    update_neumatico = text("""
        UPDATE fleet.neumatico_vehiculo
        SET estado = 'BAJA', updated_at = NOW()
        WHERE id = :neumatico_id
    """)
    await db.execute(update_neumatico, {"neumatico_id": neumatico_id})
    
    await db.commit()
    
    posicion_inversa = get_posicion_inversa()
    posicion_frontend = posicion_inversa.get(posicion, posicion)
    
    return {
        "mensaje": "Neumático desmontado correctamente",
        "operacion_id": str(operacion_id),
        "neumatico_id": str(neumatico_id),
        "posicion": posicion_frontend,
        "km_recorridos_en_posicion": data.km_vehiculo_actual - int(km_montaje)  # ✅ Usar km_montaje
    }

@router.put("/neumaticos/{neumatico_id}/estado")
async def cambiar_estado_neumatico(
    neumatico_id: UUID,
    data: CambiarEstadoRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Cambiar estado de un neumático (BAJA, DESECHADO)."""
    propietario_id = UUID(ctx["propietario_id"])
    
    await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
    
    query_check = text("""
        SELECT estado FROM fleet.neumatico_vehiculo
        WHERE id = :neumatico_id AND activo = true
    """)
    result = await db.execute(query_check, {"neumatico_id": neumatico_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Neumático no encontrado")
    
    estado_actual = row[0]
    
    if data.estado == "DESECHADO" and estado_actual != "BAJA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede desechar un neumático que está en estado BAJA"
        )
    
    if data.estado == "BAJA" and estado_actual != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede dar de baja un neumático que está ACTIVO"
        )
    
    # ✅ Usar SQL con comillas simples y concatenación segura
    # Solo lo hacemos porque data.estado es un valor controlado (viene de un enum)
    update_query = text(f"""
        UPDATE fleet.neumatico_vehiculo
        SET estado = '{data.estado}',
            fecha_baja = CASE WHEN '{data.estado}' = 'DESECHADO' THEN NOW() ELSE fecha_baja END,
            updated_at = NOW()
        WHERE id = '{neumatico_id}'
    """)
    await db.execute(update_query)
    
    await db.commit()
    
    return {
        "mensaje": f"Estado actualizado a {data.estado}",
        "estado_anterior": estado_actual,
        "estado_actual": data.estado
    }

@router.post("/neumaticos/{neumatico_id}/medicion")
async def registrar_medicion(
    neumatico_id: UUID,
    data: MedicionRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Registrar medición de profundidad de dibujo."""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])
    
    await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
    
    query_historial = text("""
        SELECT hp.id, hp.neumatico_vehiculo_id, nv.vehiculo_id
        FROM fleet.neumatico_historial_posicion hp
        INNER JOIN fleet.neumatico_vehiculo nv ON nv.id = hp.neumatico_vehiculo_id
        WHERE hp.neumatico_vehiculo_id = :neumatico_id
          AND hp.fecha_desmontaje IS NULL AND nv.estado = 'ACTIVO'
    """)
    result = await db.execute(query_historial, {"neumatico_id": neumatico_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El neumático debe estar ACTIVO y montado para registrar medición"
        )
    
    historial_id = row[0]
    vehiculo_id = row[2]
    
    insert_medicion = text("""
        INSERT INTO fleet.neumatico_medicion (
            id, historial_posicion_id, control_base_id,
            profundidad_mm, fecha_medicion, medido_por,
            observaciones
        ) VALUES (
            gen_random_uuid(), :historial_id, :control_base_id,
            :profundidad, NOW(), :medido_por, :observaciones
        ) RETURNING id
    """)
    result = await db.execute(insert_medicion, {
        "historial_id": historial_id,
        "control_base_id": control_base_id,
        "profundidad": data.profundidad_mm,
        "medido_por": user_id,
        "observaciones": data.observaciones
    })
    medicion_id = result.scalar()
    
    await db.commit()
    
    color = "VERDE" if data.profundidad_mm >= 4.0 else "AMARILLO" if data.profundidad_mm >= 2.0 else "ROJO"
    interpretacion = ""
    sugerencia_generada = None
    
    if color == "ROJO":
        interpretacion = "Desgaste crítico. ¡Cambiar neumático inmediatamente!"
        sugerencia_generada = await generar_sugerencia_neumatico(
            neumatico_id, vehiculo_id, control_base_id,
            "CAMBIO", "ALTA",
            f"Neumático con profundidad de {data.profundidad_mm}mm. ¡Cambio inmediato requerido!",
            data.profundidad_mm,
            db
        )
    elif color == "AMARILLO":
        interpretacion = "Desgaste significativo. Planificar cambio en los próximos 5,000 km."
        sugerencia_generada = await generar_sugerencia_neumatico(
            neumatico_id, vehiculo_id, control_base_id,
            "CAMBIO", "MEDIA",
            f"Neumático con profundidad de {data.profundidad_mm}mm. Planificar cambio.",
            data.profundidad_mm,
            db
        )
    else:
        interpretacion = "Neumático en buen estado. Mantener."
    
    return {
        "mensaje": "Medición registrada correctamente",
        "medicion_id": str(medicion_id),
        "profundidad_mm": data.profundidad_mm,
        "estado_color": color,
        "interpretacion": interpretacion,
        "sugerencia_generada": sugerencia_generada
    }


@router.get("/neumaticos/{neumatico_id}/mediciones")
async def listar_mediciones(
    neumatico_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Historial de mediciones del neumático."""
    propietario_id = UUID(ctx["propietario_id"])
    await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
    
    query = text("""
        SELECT m.id, m.fecha_medicion, m.profundidad_mm, m.observaciones,
               CONCAT(p.nombre, ' ', p.apellido) as medido_por
        FROM fleet.neumatico_medicion m
        LEFT JOIN auth.perfil_general p ON p.usuario_id = m.medido_por
        WHERE m.historial_posicion_id IN (
            SELECT id FROM fleet.neumatico_historial_posicion
            WHERE neumatico_vehiculo_id = :neumatico_id
        )
        ORDER BY m.fecha_medicion DESC LIMIT :limit
    """)
    result = await db.execute(query, {"neumatico_id": neumatico_id, "limit": limit})
    rows = result.all()
    
    mediciones = []
    for row in rows:
        color = "VERDE" if float(row[2]) >= 4.0 else "AMARILLO" if float(row[2]) >= 2.0 else "ROJO"
        mediciones.append({
            "id": str(row[0]),
            "fecha": row[1],
            "profundidad_mm": float(row[2]),
            "estado_color": color,
            "medido_por": row[4],
            "observaciones": row[3]
        })
    
    if mediciones:
        avg = sum(m["profundidad_mm"] for m in mediciones) / len(mediciones)
        ultima = mediciones[0]["profundidad_mm"] if mediciones else None
        if len(mediciones) > 1:
            penultima = mediciones[1]["profundidad_mm"]
            tendencia = "DECRECIENTE" if ultima < penultima else "CRECIENTE" if ultima > penultima else "ESTABLE"
        else:
            tendencia = "SIN_DATOS"
    else:
        avg = 0
        ultima = None
        tendencia = "SIN_DATOS"
    
    return {
        "neumatico_id": str(neumatico_id),
        "total": len(mediciones),
        "mediciones": mediciones,
        "tendencia": tendencia,
        "promedio": round(avg, 2),
        "ultima_medicion": ultima
    }