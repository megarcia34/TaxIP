"""
Viajes - Rutas principales
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timedelta
import uuid as uuid_lib
from typing import Optional

from app.database import get_db
from app.dependencies import (
    get_current_user,
    get_current_passenger_user,
    get_current_driver_user,
    get_current_admin_user
)
from app.services.storage import storage_service

from .schemas import (
    ViajeEstadoResponse,
    HistorialViajeResponse,
    SolicitarViajeRequest,
    SolicitarViajeResponse,
    CancelarViajeRequest,
    CalificarViajeRequest,
    CalificarViajeResponse,
    CalcularCostoRequest,
    CalcularCostoResponse,
    ObjetoOlvidadoRequest,
    ObjetoOlvidadoResponse,
    CompartirViajeResponse,
    ReservarViajeRequest,
    ReservarViajeResponse,
    ReservaPendienteResponse,
)

from .queries import (
    GET_VIAJE_BY_ID,
    GET_HISTORIAL_VIAJES,
    GET_VIAJES_POR_ESTADO
)
from .services import (
    actualizar_estado_viaje,
    formatear_respuesta_viaje,
    calcular_distancia,
    calcular_tiempo_estimado,
    calcular_precio,
    es_horario_nocturno,
    obtener_tarifas_default
)

router = APIRouter(prefix="/api/viajes", tags=["Viajes"])


# ============================================
# CALCULAR COSTO
# ============================================

@router.post("/calcular-costo", response_model=CalcularCostoResponse)
async def calcular_costo(
    request: CalcularCostoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calcular costo estimado de un viaje"""
    _, control_base_id, _, _ = current_user

    query = text("""
        SELECT tarifa_base, precio_por_km, precio_por_minuto, recargo_nocturno
        FROM payment.configuracion_tarifa
        WHERE control_base_id = :control_base_id AND activo = true
        ORDER BY created_at DESC
        LIMIT 1
    """)

    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()

    if not row:
        tarifa_base, precio_km, precio_minuto, recargo_nocturno = obtener_tarifas_default()
    else:
        tarifa_base = float(row[0])
        precio_km = float(row[1])
        precio_minuto = float(row[2])
        recargo_nocturno = float(row[3])

    distancia_metros = calcular_distancia(
        request.origen_latitud, request.origen_longitud,
        request.destino_latitud, request.destino_longitud
    )
    tiempo_estimado_segundos = calcular_tiempo_estimado(distancia_metros)

    es_nocturno = es_horario_nocturno(datetime.now())
    recargo = recargo_nocturno if es_nocturno else 1.0

    precio_estimado = calcular_precio(
        distancia_metros,
        tiempo_estimado_segundos,
        tarifa_base,
        precio_km,
        precio_minuto,
        recargo
    )

    return CalcularCostoResponse(
        distancia_metros=distancia_metros,
        tiempo_estimado_segundos=tiempo_estimado_segundos,
        precio_estimado=precio_estimado,
        tarifa_base=tarifa_base,
        costo_km=precio_km,
        costo_minuto=precio_minuto
    )


# ============================================
# SOLICITAR VIAJE
# ============================================

@router.post("/solicitar", response_model=SolicitarViajeResponse)
async def solicitar_viaje(
    request: SolicitarViajeRequest,
    current_user: tuple = Depends(get_current_passenger_user),
    db: AsyncSession = Depends(get_db)
):
    """Solicitar un viaje"""
    user_id, control_base_id, _, _ = current_user

    if not control_base_id:
        default_cb = await db.execute(text("SELECT id FROM tenant.control_base LIMIT 1"))
        control_base_id = default_cb.scalar()
        if not control_base_id:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")

    driver_query = text("""
        SELECT cv.id, cv.usuario_id, cv.vehiculo_id
        FROM fleet.chofer_vehiculo cv
        WHERE cv.control_base_id = :control_base_id
          AND cv.estado_laboral = 'libre'
          AND cv.activo = true
        LIMIT 1
    """)

    driver_result = await db.execute(driver_query, {"control_base_id": control_base_id})
    driver_row = driver_result.first()

    if not driver_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay conductores disponibles"
        )

    chofer_vehiculo_id = driver_row[0]
    chofer_id = driver_row[1]
    vehiculo_id = driver_row[2]

    viaje_id = uuid_lib.uuid4()

    insert_query = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id, pasajero_id, chofer_id, vehiculo_id,
            direccion_origen, direccion_destino,
            estado, created_at
        )
        VALUES (
            :id, :control_base_id, :pasajero_id, :chofer_id, :vehiculo_id,
            :direccion_origen, :direccion_destino,
            'pendiente', NOW()
        )
        RETURNING id
    """)

    await db.execute(insert_query, {
        "id": viaje_id,
        "control_base_id": control_base_id,
        "pasajero_id": user_id,
        "chofer_id": chofer_id,
        "vehiculo_id": vehiculo_id,
        "direccion_origen": request.direccion_origen,
        "direccion_destino": request.direccion_destino
    })

    update_driver = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = 'ocupado'
        WHERE id = :chofer_vehiculo_id
    """)
    await db.execute(update_driver, {"chofer_vehiculo_id": chofer_vehiculo_id})

    await db.commit()

    return SolicitarViajeResponse(
        success=True,
        viaje_id=viaje_id,
        estado="pendiente",
        mensaje="Viaje solicitado. Esperando confirmación del conductor.",
        tiempo_estimado_segundos=None,
        precio_estimado=None
    )


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
# HISTORIAL
# ============================================

@router.get("/historial", response_model=list[HistorialViajeResponse])
async def obtener_historial_viajes(
    limit: int = 100,
    offset: int = 0,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener historial de viajes"""
    _, control_base_id, _, user_tipo = current_user

    query = text("""
        SELECT 
            vs.id,
            COALESCE(pp.nombre || ' ' || pp.apellido, up.email) as pasajero_nombre,
            COALESCE(pc.nombre || ' ' || pc.apellido, uc.email) as chofer_nombre,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_final,
            vs.precio_estimado,
            vs.estado,
            vs.created_at,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            c.puntaje as calificacion,
            ST_X(vs.origen::geometry) as origen_lat,
            ST_Y(vs.origen::geometry) as origen_lng,
            ST_X(vs.destino::geometry) as destino_lat,
            ST_Y(vs.destino::geometry) as destino_lng,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en
        FROM trip.viaje_solicitado vs
        JOIN auth.usuario up ON up.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general pp ON pp.usuario_id = up.id
        LEFT JOIN auth.usuario uc ON uc.id = vs.chofer_id
        LEFT JOIN auth.perfil_general pc ON pc.usuario_id = uc.id
        LEFT JOIN trip.calificacion c ON c.viaje_id = vs.id 
            AND c.calificador_id = vs.pasajero_id
        WHERE vs.control_base_id = :control_base_id
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, {
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.all()

    return [
        HistorialViajeResponse(
            id=row[0],
            pasajero_nombre=row[1],
            chofer_nombre=row[2],
            direccion_origen=row[3] or '',
            direccion_destino=row[4] or '',
            precio_final=float(row[5]) if row[5] else None,
            precio_estimado=float(row[6]) if row[6] else None,
            estado=row[7],
            creado_en=row[8],
            distancia_metros=row[9],
            tiempo_estimado_segundos=row[10],
            calificacion_dada=row[11],
            origen_lat=float(row[12]) if row[12] else None,
            origen_lng=float(row[13]) if row[13] else None,
            destino_lat=float(row[14]) if row[14] else None,
            destino_lng=float(row[15]) if row[15] else None,
            aceptado_en=row[16],
            iniciado_en=row[17],
            finalizado_en=row[18]
        )
        for row in rows
    ]


# ============================================
# ESTADO DEL VIAJE
# ============================================

@router.get("/{viaje_id}/estado", response_model=ViajeEstadoResponse)
async def obtener_estado_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estado de un viaje específico"""
    result = await db.execute(GET_VIAJE_BY_ID, {"viaje_id": viaje_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    return await formatear_respuesta_viaje(row)


# ============================================
# ACEPTAR, INICIAR, FINALIZAR, CANCELAR
# ============================================

@router.post("/{viaje_id}/aceptar")
async def aceptar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """Aceptar un viaje (chofer)"""
    driver_id, control_base_id, _, _ = current_user

    result = await actualizar_estado_viaje(db, viaje_id, control_base_id, "aceptado", "aceptado_en")

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    await db.commit()
    return {"success": True, "message": "Viaje aceptado"}


@router.post("/{viaje_id}/iniciar")
async def iniciar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """Iniciar un viaje (chofer)"""
    driver_id, control_base_id, _, _ = current_user

    result = await actualizar_estado_viaje(db, viaje_id, control_base_id, "en_curso", "iniciado_en")

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    await db.commit()
    return {"success": True, "message": "Viaje iniciado"}


@router.post("/{viaje_id}/finalizar")
async def finalizar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """Finalizar un viaje (chofer)"""
    driver_id, control_base_id, _, _ = current_user

    result = await actualizar_estado_viaje(db, viaje_id, control_base_id, "finalizado", "finalizado_en")

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    await db.commit()
    return {"success": True, "message": "Viaje finalizado"}


@router.post("/{viaje_id}/cancelar")
async def cancelar_viaje(
    viaje_id: UUID,
    request: CancelarViajeRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancelar un viaje"""
    _, control_base_id, _, _ = current_user

    result = await actualizar_estado_viaje(db, viaje_id, control_base_id, "cancelado", "cancelado_en")

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    if request.motivo:
        query = text("""
            UPDATE trip.viaje_solicitado
            SET motivo_cancelacion = :motivo
            WHERE id = :viaje_id
        """)
        await db.execute(query, {"viaje_id": viaje_id, "motivo": request.motivo})

    await db.commit()
    return {"success": True, "message": "Viaje cancelado"}


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