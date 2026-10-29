"""
Public endpoints for web booking (no authentication required)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4, UUID
from datetime import datetime
import logging
import asyncio

from app.database import get_db
from app.routers.viajes.schemas import (
    SolicitarViajePublicoRequest,
    SolicitarViajePublicoResponse
)
from app.services.precio_estimado import calcular_precio_estimado
from app.schemas.reserva_schemas import EstimacionPrecioRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/public/viajes", tags=["Public - Viajes"])


@router.post("/calcular-tarifa")
async def calcular_tarifa_publico(
    origen_lat: float,
    origen_lng: float,
    destino_lat: float,
    destino_lng: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate estimated fare (public endpoint)
    USANDO EL MISMO SERVICIO QUE EL DASHBOARD CORPORATIVO
    """
    try:
        # 1. Obtener control_base_id por defecto
        query = text("SELECT id FROM tenant.control_base LIMIT 1")
        result = await db.execute(query)
        row = result.first()
        if not row:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")
        control_base_id = row[0]
        
        # 2. Calcular distancia (Haversine)
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        lat1, lon1 = radians(origen_lat), radians(origen_lng)
        lat2, lon2 = radians(destino_lat), radians(destino_lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distancia_km = R * c
        
        # 3. Calcular tiempo estimado (~2 min por km)
        tiempo_minutos = max(1, int(distancia_km * 2))
        
        # 4. Usar el servicio unificado de cálculo de tarifa
        estimacion_request = EstimacionPrecioRequest(
            tipo_vehiculo="standard",
            direccion_origen="",
            direccion_destino="",
            paradas_intermedias=[],
            tiempo_espera_minutos=0,
            latitud_origen=origen_lat,
            longitud_origen=origen_lng,
            latitud_destino=destino_lat,
            longitud_destino=destino_lng
        )
        
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now()
        )
        
        return {
            "success": True,
            "tarifa": resultado.precio_estimado,
            "distancia_km": resultado.distancia_km,
            "tiempo_estimado_min": resultado.tiempo_minutos,
            "tarifa_base": resultado.desglose.get("bajada", 0),
            "precio_por_km": resultado.desglose.get("precio_por_km", 0),
            "modo_calculo": resultado.modo_calculo,
            "moneda": resultado.moneda,
            "desglose": resultado.desglose,
            "recargos": resultado.recargos_aplicados
        }
        
    except Exception as e:
        logger.error(f"Error calculando tarifa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular tarifa: {str(e)}"
        )


@router.get("/calcular-tarifa")
async def calcular_tarifa_publico_get(
    origen_lat: float,
    origen_lng: float,
    destino_lat: float,
    destino_lng: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate estimated fare (public endpoint) - GET version
    """
    return await calcular_tarifa_publico(origen_lat, origen_lng, destino_lat, destino_lng, db)


# ============================================
# FUNCION AUXILIAR: BARRIDO PROGRESIVO
# ============================================
async def publicar_viaje_progresivo(
    db: AsyncSession,
    viaje_id: UUID,
    control_base_id: UUID,
    origen_lat: float,
    origen_lng: float,
    viaje_data: dict,
):
    """
    Publica el viaje a choferes cercanos en radios progresivos:
    1km -> 2km -> 3km -> 5km. Espera 10 segundos entre cada radio.
    Si alguien acepta antes, corta el barrido.
    """
    from app.websocket.connection_manager import manager
    from app.websocket.events import EventType

    radios = [1000, 2000, 3000, 5000]  # 1km, 2km, 3km, 5km
    notificados = set()

    for radio_metros in radios:
        # Verificar si el viaje ya fue aceptado (estado distinto de 'pendiente')
        check_estado = await db.execute(
            text("SELECT estado FROM trip.viaje_solicitado WHERE id = :viaje_id"),
            {"viaje_id": viaje_id}
        )
        estado_actual = check_estado.scalar()
        if estado_actual != 'pendiente':
            logger.info(
                f"Viaje {viaje_id} ya no está pendiente (estado={estado_actual}). "
                f"Deteniendo barrido progresivo."
            )
            break

        # Buscar choferes conectados por WS y disponibles
        todos_conectados = manager.get_choferes_disponibles(
            control_base_id=str(control_base_id)
        )
        if not todos_conectados:
            logger.warning(f"No hay choferes conectados por WS para el tenant {control_base_id}")
            await asyncio.sleep(10)
            continue

        # Filtrar por PostGIS
        ids_str = ",".join([f"'{uid}'" for uid in todos_conectados])
        query_cercanos = text(f"""
            SELECT usuario_id
            FROM fleet.chofer_vehiculo
            WHERE usuario_id IN ({ids_str})
              AND ubicacion IS NOT NULL
              AND ST_DWithin(
                  ubicacion,
                  ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326)::geography,
                  :radio_metros
              )
        """)
        result_cercanos = await db.execute(query_cercanos, {
            "origen_lat": origen_lat,
            "origen_lng": origen_lng,
            "radio_metros": radio_metros,
        })
        choferes_cercanos = [str(row[0]) for row in result_cercanos.fetchall()]

        # Solo notificar a los que no fueron notificados antes
        nuevos = [c for c in choferes_cercanos if c not in notificados]

        if nuevos:
            for chofer_id in nuevos:
                await manager.send_personal(
                    user_id=chofer_id,
                    event=EventType.NUEVO_VIAJE,
                    data=viaje_data,
                )
                notificados.add(chofer_id)
            logger.info(
                f"Viaje {viaje_id}: notificado a {len(nuevos)} choferes "
                f"en radio de {radio_metros}m."
            )

        # Esperar 10 segundos antes de ampliar el radio
        await asyncio.sleep(10)

    logger.info(
        f"Barrido progresivo finalizado para viaje {viaje_id}. "
        f"Notificados: {len(notificados)} choferes."
    )

@router.post("/solicitar", response_model=SolicitarViajePublicoResponse)
async def solicitar_viaje_publico(
    request: SolicitarViajePublicoRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a trip (public endpoint) - publica el viaje a choferes cercanos
    con barrido progresivo (1km -> 2km -> 3km -> 5km).
    """
    try:
        # Obtener control_base_id por defecto
        query = text("SELECT id FROM tenant.control_base LIMIT 1")
        result = await db.execute(query)
        row = result.first()
        if not row:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")
        control_base_id = row[0]
        
        # Obtener o crear pasajero
        pasajero_id = None
        
        if request.telefono_pasajero:
            query = text("""
                SELECT u.id FROM auth.usuario u
                JOIN auth.perfil_general p ON p.usuario_id = u.id
                WHERE p.telefono = :telefono
            """)
            result = await db.execute(query, {"telefono": request.telefono_pasajero})
            row = result.first()
            if row:
                pasajero_id = row[0]
        
        if not pasajero_id:
            tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero'")
            tipo_result = await db.execute(tipo_query)
            tipo_row = tipo_result.first()
            if not tipo_row:
                raise HTTPException(status_code=400, detail="Tipo de usuario 'pasajero' no encontrado")
            tipo_usuario_id = tipo_row[0]
            
            pasajero_id = uuid4()
            insert_user = text("""
                INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
                VALUES (:id, :tipo_id, :control_base_id, :email, :password_hash, true, NOW())
            """)
            await db.execute(insert_user, {
                "id": pasajero_id,
                "tipo_id": tipo_usuario_id,
                "control_base_id": control_base_id,
                "email": request.telefono_pasajero + "@temp.taxip.com" if request.telefono_pasajero else f"{uuid4()}@temp.taxip.com",
                "password_hash": "$2b$12$temp"
            })
            
            insert_perfil = text("""
                INSERT INTO auth.perfil_general (id, usuario_id, nombre, telefono, created_at)
                VALUES (gen_random_uuid(), :user_id, :nombre, :telefono, NOW())
            """)
            await db.execute(insert_perfil, {
                "user_id": pasajero_id,
                "nombre": request.nombre_pasajero or "Usuario Web",
                "telefono": request.telefono_pasajero
            })
            
            await db.commit()
        
        # Crear viaje en estado 'pendiente'
        viaje_id = uuid4()
        
        # Extraer distancia y tiempo del request (si vienen)
        distancia_metros = getattr(request, 'distancia_metros', None)
        tiempo_estimado_segundos = getattr(request, 'tiempo_estimado_segundos', None)

        insert_viaje = text("""
            INSERT INTO trip.viaje_solicitado (
                id, control_base_id, pasajero_id,
                direccion_origen, direccion_destino,
                origen, destino,
                estado, precio_estimado, created_at, nombre_pasajero,
                distancia_metros, tiempo_estimado_segundos
            )
            VALUES (
                :id, :control_base_id, :pasajero_id,
                :direccion_origen, :direccion_destino,
                ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326),
                ST_SetSRID(ST_MakePoint(:destino_lng, :destino_lat), 4326),
                'pendiente', :precio_estimado, NOW(), :nombre_pasajero,
                :distancia_metros, :tiempo_estimado_segundos
            )
            RETURNING id
        """)
        
        await db.execute(insert_viaje, {
            "id": viaje_id,
            "control_base_id": control_base_id,
            "pasajero_id": pasajero_id,
            "direccion_origen": request.direccion_origen,
            "direccion_destino": request.direccion_destino,
            "origen_lat": request.origen_lat,
            "origen_lng": request.origen_lng,
            "destino_lat": request.destino_lat,
            "destino_lng": request.destino_lng,
            "precio_estimado": request.precio_estimado or 0,
            "nombre_pasajero": request.nombre_pasajero or "Usuario Web",
            "distancia_metros": distancia_metros,
            "tiempo_estimado_segundos": tiempo_estimado_segundos
        })
        
        await db.commit()

        # ============================================
        # PUBLICAR VIAJE CON BARRIDO PROGRESIVO
        # ============================================
        viaje_data = {
            "id": str(viaje_id),
            "direccion_origen": request.direccion_origen,
            "direccion_destino": request.direccion_destino,
            "origen_lat": request.origen_lat,
            "origen_lng": request.origen_lng,
            "destino_lat": request.destino_lat,
            "destino_lng": request.destino_lng,
            "precio_estimado": float(request.precio_estimado or 0),
            "nombre_pasajero": request.nombre_pasajero or "Usuario Web",
            "estado": "pendiente",
            # ✅ AGREGADO: distancia y tiempo para que la app chofer no muestre "—"
            "distancia_metros": distancia_metros,
            "tiempo_estimado_segundos": tiempo_estimado_segundos,
        }

        # Lanzamos el barrido en background
        asyncio.create_task(
            publicar_viaje_progresivo(
                db=db,
                viaje_id=viaje_id,
                control_base_id=control_base_id,
                origen_lat=request.origen_lat,
                origen_lng=request.origen_lng,
                viaje_data=viaje_data,
            )
        )

        return SolicitarViajePublicoResponse(
            success=True,
            viaje_id=viaje_id,
            mensaje="Viaje solicitado correctamente - Buscando conductor...",
            chofer_asignado=None,
            tiempo_espera_estimado=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solicitando viaje público: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al solicitar viaje: {str(e)}"
        )
    
## ============================================
# OBTENER ESTADO DEL VIAJE (PÚBLICO)
# ============================================
@router.get("/{viaje_id}/estado")
async def obtener_estado_viaje_publico(
    viaje_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado de un viaje (público - sin autenticación)
    """
    query = text("""
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
            vs.motivo_cancelacion,
            vs.nombre_pasajero,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            ST_Y(vs.origen::geometry) as origen_lat,
            ST_X(vs.origen::geometry) as origen_lng,
            ST_Y(vs.destino::geometry) as destino_lat,
            ST_X(vs.destino::geometry) as destino_lng
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE vs.id = :viaje_id
    """)
    
    result = await db.execute(query, {"viaje_id": viaje_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": row[2],
        "direccion_destino": row[3],
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "motivo_cancelacion": row[10] if row[10] else None,  # ✅ CORREGIDO
        "pasajero_nombre": row[11],                          # ✅ CORREGIDO
        "chofer_nombre": row[12],                            # ✅ CORREGIDO
        "origen_lat": float(row[13]) if row[13] else None,
        "origen_lng": float(row[14]) if row[14] else None,
        "destino_lat": float(row[15]) if row[15] else None,
        "destino_lng": float(row[16]) if row[16] else None,
    }
# ============================================
# CANCELAR VIAJE (PUBLICO)
# ============================================

@router.post("/{viaje_id}/cancelar")
async def cancelar_viaje_publico(
    viaje_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancela un viaje publico. Solo permitido si el viaje esta en estado
    'pendiente' o 'aceptado' (no se puede cancelar un viaje en curso o finalizado).

    Si el viaje ya tenia un chofer asignado, se le notifica por WebSocket.
    """
    from app.websocket.connection_manager import manager
    from app.websocket.events import EventType

    # 1. Verificar estado actual del viaje
    query = text("""
        SELECT id, estado, chofer_id, control_base_id
        FROM trip.viaje_solicitado
        WHERE id = :viaje_id
    """)
    result = await db.execute(query, {"viaje_id": viaje_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    viaje_id_db, estado_actual, chofer_id, control_base_id = row

    # 2. Validar estado
    if estado_actual in ('finalizado', 'cancelado'):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cancelar un viaje en estado '{estado_actual}'"
        )

    # 3. Actualizar estado a 'cancelado'
    update_query = text("""
        UPDATE trip.viaje_solicitado
        SET estado = 'cancelado',
            cancelado_en = NOW(),
            updated_at = NOW()
        WHERE id = :viaje_id
    """)
    await db.execute(update_query, {"viaje_id": viaje_id})

    # 4. Registrar en historial de estados
    historial_query = text("""
        INSERT INTO trip.historial_estado_viaje (
            id, viaje_id, estado, observacion, created_at
        ) VALUES (
            gen_random_uuid(), :viaje_id, 'cancelado',
            'Cancelado por el pasajero desde la landing', NOW()
        )
    """)
    await db.execute(historial_query, {"viaje_id": viaje_id})

    # 5. Notificar al chofer si estaba asignado
    if chofer_id:
        try:
            await manager.send_personal(
                user_id=str(chofer_id),
                event=EventType.VIAJE_CANCELADO if hasattr(EventType, 'VIAJE_CANCELADO') else 'viaje_cancelado',
                data={"viaje_id": str(viaje_id), "motivo": "cancelado_por_pasajero"}
            )
        except Exception as e:
            logger.warning(f"No se pudo notificar cancelacion al chofer {chofer_id}: {e}")

    await db.commit()

    return {
        "success": True,
        "viaje_id": str(viaje_id),
        "estado": "cancelado",
        "message": "Viaje cancelado correctamente"
    }