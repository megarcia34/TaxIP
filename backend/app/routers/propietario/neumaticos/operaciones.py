"""
Endpoints de operaciones de neumáticos (montaje, rotación, reparación)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import date

from app.database import get_db
from app.dependencies import get_propietario_context
from app.routers.propietario.utils import (
    verificar_vehiculo_propietario,
    verificar_neumatico_propietario,
    obtener_km_actual_vehiculo
)
from app.routers.propietario.neumaticos.utils import (
    generar_codigo_interno,
    get_patente_vehiculo,
    POSICION_MAP
)
from app.schemas.propietario_schemas import (
    NeumaticoMontarRequest,
    RotacionRequest,
    ReparacionRequest
)

router = APIRouter()


@router.post("/vehiculos/{vehiculo_id}/neumaticos/montar", status_code=status.HTTP_201_CREATED)
async def montar_neumaticos(
    vehiculo_id: UUID,
    data: NeumaticoMontarRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Montar uno o más neumáticos en el vehículo."""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    # Verificar que las posiciones estén libres
    posiciones_solicitadas = [n.posicion for n in data.neumaticos]
    for posicion in posiciones_solicitadas:
        if posicion in ['DI', 'DD', 'TI', 'TD']:
            db_posicion = POSICION_MAP.get(posicion, posicion)
            query_check = text("""
                SELECT hp.id FROM fleet.neumatico_historial_posicion hp
                INNER JOIN fleet.neumatico_vehiculo nv ON nv.id = hp.neumatico_vehiculo_id
                WHERE nv.vehiculo_id = :vehiculo_id
                  AND hp.eje_posicion = :posicion
                  AND hp.fecha_desmontaje IS NULL AND nv.estado = 'ACTIVO'
            """)
            result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "posicion": db_posicion})
            if result.first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"La posición {posicion} ya tiene un neumático activo"
                )
    
    # Crear operación
    insert_operacion = text("""
        INSERT INTO fleet.neumatico_operacion (
            id, vehiculo_id, control_base_id, tipo_operacion,
            descripcion, km_vehiculo_actual, fecha_operacion,
            observaciones, creado_por
        ) VALUES (
            gen_random_uuid(), :vehiculo_id, :control_base_id, 'MONTAJE',
            :descripcion, :km_vehiculo_actual, NOW(),
            :observaciones, :creado_por
        ) RETURNING id
    """)
    result = await db.execute(insert_operacion, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id,
        "descripcion": f"Montaje de {len(data.neumaticos)} neumáticos",
        "km_vehiculo_actual": data.km_vehiculo_actual,
        "observaciones": data.observaciones_generales,
        "creado_por": user_id
    })
    operacion_id = result.scalar()
    
    neumaticos_creados = []
    
    for idx, neumatico_data in enumerate(data.neumaticos):
        if not neumatico_data.codigo_interno:
            codigo_interno = generar_codigo_interno(
                await get_patente_vehiculo(vehiculo_id, db),
                neumatico_data.posicion,
                idx + 1
            )
        else:
            codigo_interno = neumatico_data.codigo_interno
        
        query_check = text("""
            SELECT id FROM fleet.neumatico_vehiculo
            WHERE vehiculo_id = :vehiculo_id AND codigo_interno = :codigo AND activo = true
        """)
        result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "codigo": codigo_interno})
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código {codigo_interno} ya existe para este vehículo"
            )
        
        insert_neumatico = text("""
            INSERT INTO fleet.neumatico_vehiculo (
                id, vehiculo_id, control_base_id, codigo_interno,
                marca, modelo_dibujo, medida, tipo_neumatico,
                fecha_fabricacion, estado, fecha_alta,
                observaciones, activo
            ) VALUES (
                gen_random_uuid(), :vehiculo_id, :control_base_id, :codigo_interno,
                :marca, :modelo_dibujo, :medida, :tipo_neumatico,
                :fecha_fabricacion, 'ACTIVO', NOW(),
                :observaciones, true
            ) RETURNING id
        """)
        result = await db.execute(insert_neumatico, {
            "vehiculo_id": vehiculo_id,
            "control_base_id": control_base_id,
            "codigo_interno": codigo_interno,
            "marca": neumatico_data.marca,
            "modelo_dibujo": neumatico_data.modelo_dibujo,
            "medida": neumatico_data.medida,
            "tipo_neumatico": neumatico_data.tipo_neumatico,
            "fecha_fabricacion": neumatico_data.fecha_fabricacion,
            "observaciones": neumatico_data.observaciones
        })
        neumatico_id = result.scalar()
        
        db_posicion = POSICION_MAP.get(neumatico_data.posicion, neumatico_data.posicion)
        
        insert_historial = text("""
            INSERT INTO fleet.neumatico_historial_posicion (
                id, neumatico_vehiculo_id, vehiculo_id, control_base_id,
                eje_posicion, km_montaje, fecha_montaje, operacion_id
            ) VALUES (
                gen_random_uuid(), :neumatico_id, :vehiculo_id, :control_base_id,
                :posicion, :km_montaje, NOW(), :operacion_id
            )
        """)
        await db.execute(insert_historial, {
            "neumatico_id": neumatico_id,
            "vehiculo_id": vehiculo_id,
            "control_base_id": control_base_id,
            "posicion": db_posicion,
            "km_montaje": data.km_vehiculo_actual,
            "operacion_id": operacion_id
        })
        
        insert_detalle = text("""
            INSERT INTO fleet.neumatico_operacion_detalle (
                id, operacion_id, neumatico_vehiculo_id,
                posicion_despues, km_neumatico_en_operacion
            ) VALUES (
                gen_random_uuid(), :operacion_id, :neumatico_id,
                :posicion, :km_vehiculo
            )
        """)
        await db.execute(insert_detalle, {
            "operacion_id": operacion_id,
            "neumatico_id": neumatico_id,
            "posicion": db_posicion,
            "km_vehiculo": data.km_vehiculo_actual
        })
        
        neumaticos_creados.append({
            "id": str(neumatico_id),
            "codigo_interno": codigo_interno,
            "posicion": neumatico_data.posicion,
            "estado": "ACTIVO"
        })
    
    await db.commit()
    
    return {
        "mensaje": "Neumáticos montados correctamente",
        "operacion_id": str(operacion_id),
        "neumaticos_creados": neumaticos_creados
    }


@router.post("/vehiculos/{vehiculo_id}/neumaticos/rotacion")
async def rotar_neumaticos(
    vehiculo_id: UUID,
    data: RotacionRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Rotar los 4 neumáticos (patrón cruzado)."""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    query_neumaticos = text("""
        SELECT nv.id, nv.codigo_interno, hp.eje_posicion, hp.km_montaje, hp.id as historial_id
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.neumatico_historial_posicion hp ON hp.neumatico_vehiculo_id = nv.id
        WHERE nv.vehiculo_id = :vehiculo_id
          AND hp.fecha_desmontaje IS NULL AND nv.estado = 'ACTIVO'
          AND nv.activo = true AND hp.eje_posicion IN ('D1', 'D2', 'T1', 'T2')
        ORDER BY hp.eje_posicion
    """)
    result = await db.execute(query_neumaticos, {"vehiculo_id": vehiculo_id})
    rows = result.all()
    
    if len(rows) != 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Se necesitan 4 neumáticos activos. Actualmente hay {len(rows)}"
        )
    
    rotacion_map_db = {
        "D1": "T2",
        "D2": "T1",
        "T1": "D1",
        "T2": "D2"
    }
    
    posicion_inversa = {v: k for k, v in POSICION_MAP.items()}
    
    insert_operacion = text("""
        INSERT INTO fleet.neumatico_operacion (
            id, vehiculo_id, control_base_id, tipo_operacion,
            descripcion, km_vehiculo_actual, fecha_operacion,
            observaciones, creado_por
        ) VALUES (
            gen_random_uuid(), :vehiculo_id, :control_base_id, 'ROTACION',
            'Rotación de neumáticos (patrón cruzado)', :km_vehiculo_actual, NOW(),
            :observaciones, :creado_por
        ) RETURNING id
    """)
    result = await db.execute(insert_operacion, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id,
        "km_vehiculo_actual": data.km_vehiculo_actual,
        "observaciones": data.observaciones,
        "creado_por": user_id
    })
    operacion_id = result.scalar()
    
    cambios = []
    
    for row in rows:
        neumatico_id = row[0]
        codigo_interno = row[1]
        posicion_actual_db = row[2]
        km_montaje = int(row[3])
        historial_id = row[4]
        nueva_posicion_db = rotacion_map_db[posicion_actual_db]
        
        posicion_actual_frontend = posicion_inversa.get(posicion_actual_db, posicion_actual_db)
        nueva_posicion_frontend = posicion_inversa.get(nueva_posicion_db, nueva_posicion_db)
        
        update_historial = text("""
            UPDATE fleet.neumatico_historial_posicion
            SET km_desmontaje = :km_desmontaje, fecha_desmontaje = NOW()
            WHERE id = :historial_id
        """)
        await db.execute(update_historial, {
            "km_desmontaje": data.km_vehiculo_actual,
            "historial_id": historial_id
        })
        
        insert_historial = text("""
            INSERT INTO fleet.neumatico_historial_posicion (
                id, neumatico_vehiculo_id, vehiculo_id, control_base_id,
                eje_posicion, km_montaje, fecha_montaje, operacion_id
            ) VALUES (
                gen_random_uuid(), :neumatico_id, :vehiculo_id, :control_base_id,
                :nueva_posicion, :km_montaje, NOW(), :operacion_id
            )
        """)
        await db.execute(insert_historial, {
            "neumatico_id": neumatico_id,
            "vehiculo_id": vehiculo_id,
            "control_base_id": control_base_id,
            "nueva_posicion": nueva_posicion_db,
            "km_montaje": data.km_vehiculo_actual,
            "operacion_id": operacion_id
        })
        
        insert_detalle = text("""
            INSERT INTO fleet.neumatico_operacion_detalle (
                id, operacion_id, neumatico_vehiculo_id,
                posicion_antes, posicion_despues, km_neumatico_en_operacion
            ) VALUES (
                gen_random_uuid(), :operacion_id, :neumatico_id,
                :posicion_antes, :posicion_despues, :km_vehiculo
            )
        """)
        await db.execute(insert_detalle, {
            "operacion_id": operacion_id,
            "neumatico_id": neumatico_id,
            "posicion_antes": posicion_actual_db,
            "posicion_despues": nueva_posicion_db,
            "km_vehiculo": data.km_vehiculo_actual
        })
        
        cambios.append({
            "codigo_interno": codigo_interno,
            "posicion_antes": posicion_actual_frontend,
            "posicion_despues": nueva_posicion_frontend,
            "km_recorridos_en_posicion": data.km_vehiculo_actual - km_montaje
        })
    
    update_sugerencias = text("""
        UPDATE fleet.neumatico_sugerencia
        SET estado = 'ACCIONADA', fecha_atendida = NOW(), atendida_por = :user_id
        WHERE vehiculo_id = :vehiculo_id
          AND tipo_sugerencia = 'ROTACION' AND estado = 'PENDIENTE'
    """)
    await db.execute(update_sugerencias, {
        "vehiculo_id": vehiculo_id,
        "user_id": user_id
    })
    
    await db.commit()
    
    return {
        "mensaje": "Rotación realizada correctamente",
        "operacion_id": str(operacion_id),
        "cambios": cambios
    }


@router.get("/operaciones/vehiculo/{vehiculo_id}")
async def listar_operaciones_neumaticos(
    vehiculo_id: UUID,
    tipo: Optional[str] = Query(None, pattern="^(MONTAJE_INICIAL|ROTACION|DESMONTAJE|REPARACION|CAMBIO|DESECHO)$"),
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Listar operaciones de neumáticos del vehículo."""
    propietario_id = UUID(ctx["propietario_id"])
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    query = text("""
        SELECT 
            o.id, o.tipo_operacion, o.fecha_operacion,
            o.km_vehiculo_actual, o.descripcion, o.observaciones,
            o.costo, o.proveedor,
            STRING_AGG(
                nv.codigo_interno || '(' || od.posicion_antes || '→' || od.posicion_despues || ')',
                ', '
            ) as neumaticos_afectados
        FROM fleet.neumatico_operacion o
        LEFT JOIN fleet.neumatico_operacion_detalle od ON od.operacion_id = o.id
        LEFT JOIN fleet.neumatico_vehiculo nv ON nv.id = od.neumatico_vehiculo_id
        WHERE o.vehiculo_id = :vehiculo_id
    """)
    
    params = {"vehiculo_id": vehiculo_id}
    
    if tipo:
        query = text(query.text + " AND o.tipo_operacion = :tipo")
        params["tipo"] = tipo
    
    if desde:
        query = text(query.text + " AND o.fecha_operacion::date >= :desde")
        params["desde"] = desde
    
    if hasta:
        query = text(query.text + " AND o.fecha_operacion::date <= :hasta")
        params["hasta"] = hasta
    
    query = text(query.text + " GROUP BY o.id ORDER BY o.fecha_operacion DESC LIMIT :limit OFFSET :offset")
    params["limit"] = limit
    params["offset"] = offset
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "total": len(rows),
        "operaciones": [
            {
                "id": str(row[0]),
                "tipo": row[1],
                "fecha": row[2],
                "km_vehiculo": int(row[3] or 0),
                "descripcion": row[4],
                "observaciones": row[5],
                "costo": float(row[6]) if row[6] else None,
                "proveedor": row[7],
                "neumaticos_afectados": row[8].split(', ') if row[8] else []
            }
            for row in rows
        ]
    }


@router.post("/operaciones/reparacion", status_code=status.HTTP_201_CREATED)
async def registrar_reparacion(
    data: ReparacionRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Registrar reparación de un neumático."""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])
    
    await verificar_vehiculo_propietario(data.vehiculo_id, propietario_id, db)
    await verificar_neumatico_propietario(data.neumatico_id, propietario_id, db)
    
    query_check = text("""
        SELECT estado FROM fleet.neumatico_vehiculo
        WHERE id = :neumatico_id AND activo = true
    """)
    result = await db.execute(query_check, {"neumatico_id": data.neumatico_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Neumático no encontrado")
    
    if row[0] != "BAJA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede reparar un neumático que está en estado BAJA"
        )
    
    insert_operacion = text("""
        INSERT INTO fleet.neumatico_operacion (
            id, vehiculo_id, control_base_id, tipo_operacion,
            descripcion, km_vehiculo_actual, fecha_operacion,
            costo, moneda, proveedor, observaciones, creado_por
        ) VALUES (
            gen_random_uuid(), :vehiculo_id, :control_base_id, 'REPARACION',
            :descripcion, :km_vehiculo_actual, NOW(),
            :costo, 'ARS', :proveedor, :observaciones, :creado_por
        ) RETURNING id
    """)
    result = await db.execute(insert_operacion, {
        "vehiculo_id": data.vehiculo_id,
        "control_base_id": control_base_id,
        "descripcion": f"Reparación: {data.tipo_reparacion}",
        "km_vehiculo_actual": data.km_vehiculo_actual,
        "costo": data.costo,
        "proveedor": data.proveedor,
        "observaciones": data.observaciones,
        "creado_por": user_id
    })
    operacion_id = result.scalar()
    
    insert_detalle = text("""
        INSERT INTO fleet.neumatico_operacion_detalle (
            id, operacion_id, neumatico_vehiculo_id,
            posicion_antes, km_neumatico_en_operacion
        ) VALUES (
            gen_random_uuid(), :operacion_id, :neumatico_id,
            'REPUESTO', :km_vehiculo
        )
    """)
    await db.execute(insert_detalle, {
        "operacion_id": operacion_id,
        "neumatico_id": data.neumatico_id,
        "km_vehiculo": data.km_vehiculo_actual
    })
    
    await db.commit()
    
    return {
        "mensaje": "Reparación registrada correctamente",
        "operacion_id": str(operacion_id),
        "neumatico_estado": "BAJA"
    }