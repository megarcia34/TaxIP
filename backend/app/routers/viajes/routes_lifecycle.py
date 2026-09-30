"""
Viajes - Endpoints del ciclo de vida del viaje.
Extraído de routes.py (refactor 2026-09-24).

Incluye: aceptar, llegar, rechazar, iniciar, finalizar, cancelar.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import (
    get_current_user,
    get_current_driver_user,
)

from .services import actualizar_estado_viaje
from .schemas import CancelarViajeRequest

from datetime import datetime
from app.services.precio_estimado import calcular_precio_estimado
from app.schemas.reserva_schemas import (
    EstimacionPrecioRequest,
    TipoVehiculoEnum,
)

from .services import calcular_distancia, calcular_tiempo_estimado

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# ACEPTAR VIAJE
# ============================================

@router.post("/{viaje_id}/aceptar")
async def aceptar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """Aceptar un viaje (chofer)"""
    driver_id, control_base_id, _, _ = current_user

    try:
        result = await actualizar_estado_viaje(
            db, viaje_id, control_base_id, "aceptado", "aceptado_en"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    await db.commit()
    return {"success": True, "message": "Viaje aceptado"}


# ============================================
# LLEGAR AL ORIGEN (M3 - Etapa 10.2)
# ============================================

@router.post("/{viaje_id}/llegar")
async def llegar_viaje(
    viaje_id: UUID,
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    El chofer marca que llegó al origen del pasajero.

    Solo aplica a viajes no-vía-pública (landing, QR, corporativo,
    despacho manual). En viajes de vía pública, el pasajero ya está
    a bordo y no tiene sentido marcar llegada.

    Requisitos:
    - Chofer autenticado.
    - El chofer debe ser el asignado al viaje.
    - El viaje debe estar en estado 'aceptado'.
    - El viaje NO debe ser 'via_publica'.

    Efectos:
    - Registra `llegado_en` en el viaje.
    - Inserta evento en trip.historial_estado_viaje.
    - Actualiza fleet.chofer_vehiculo.updated_at.
    - Notifica al pasajero (in-app + WS) si no es anónimo.
    """
    chofer_id, control_base_id, _, _ = current_user

    # 1. Leer el viaje
    query = text("""
        SELECT id, estado, origen_tipo, chofer_id, control_base_id,
               pasajero_id, es_anonimo, nombre_pasajero
        FROM trip.viaje_solicitado
        WHERE id = :viaje_id AND control_base_id = :control_base_id
        LIMIT 1
    """)
    viaje = (await db.execute(query, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })).first()

    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viaje no encontrado",
        )

    (id_viaje, estado, origen_tipo, chofer_asignado,
     cb_id, pasajero_id, es_anonimo, nombre_pasajero) = viaje

    # 2. Validar canal
    if origen_tipo == "via_publica":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este viaje no requiere marcar llegada (el pasajero ya está a bordo).",
        )

    # 3. Validar estado
    if estado != "aceptado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Solo se puede marcar llegada desde estado 'aceptado'. "
                f"Estado actual: '{estado}'."
            ),
        )

    # 4. Validar chofer
    if chofer_asignado != chofer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No sos el chofer asignado a este viaje.",
        )

    # 5. Actualizar viaje
    await db.execute(
        text("""
            UPDATE trip.viaje_solicitado
            SET llegado_en = NOW(), updated_at = NOW()
            WHERE id = :viaje_id
        """),
        {"viaje_id": viaje_id},
    )

    # 6. Historial
    await db.execute(
        text("""
            INSERT INTO trip.historial_estado_viaje (
                id, viaje_id, estado, latitud, longitud, observacion, created_at
            )
            VALUES (
                gen_random_uuid(), :viaje_id, 'aceptado',
                :lat, :lng,
                'Chofer llegó al origen del pasajero', NOW()
            )
        """),
        {"viaje_id": viaje_id, "lat": lat, "lng": lng},
    )

    # 7. Actualizar chofer_vehiculo.updated_at
    await db.execute(
        text("""
            UPDATE fleet.chofer_vehiculo
            SET updated_at = NOW()
            WHERE usuario_id = :chofer_id AND control_base_id = :cb_id
        """),
        {"chofer_id": chofer_id, "cb_id": cb_id},
    )

    # 8. Notificar al pasajero (si no es anónimo)
    if not es_anonimo and pasajero_id:
        # 8.1. Notificación in-app
        await db.execute(
            text("""
                INSERT INTO notification.notificacion (
                    id, usuario_id, titulo, mensaje, tipo, leida, created_at
                )
                VALUES (
                    gen_random_uuid(), :pasajero_id,
                    '🚕 Tu chofer llegó',
                    'Tu chofer está en el punto de origen. Por favor subí al vehículo.',
                    'viaje',
                    false,
                    NOW()
                )
            """),
            {"pasajero_id": pasajero_id},
        )

        # 8.2. Notificar por WebSocket (best effort)
        try:
            from app.websocket.connection_manager import manager
            await manager.notify_driver_arrived(
                passenger_id=str(pasajero_id),
                viaje_id=str(viaje_id),
            )
        except Exception as e:
            logger.warning(f"No se pudo notificar por WS al pasajero: {e}")

    # 9. Commit
    await db.commit()

    return {
        "success": True,
        "message": "Llegada registrada",
        "viaje_id": str(viaje_id),
    }


# ============================================
# RECHAZAR VIAJE
# ============================================

@router.post("/{viaje_id}/rechazar")
async def rechazar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Rechazar un viaje (chofer).

    Registra el rechazo en trip.broadcast_log sin cambiar el estado del viaje.
    El chofer NO es penalizado. El viaje sigue publicado para otros choferes.
    """
    from app.services.broadcast_service import registrar_broadcast_log

    driver_id, control_base_id, _, _ = current_user

    # 1. Verificar que el viaje existe y esta en el tenant correcto
    viaje_query = await db.execute(
        text("""
            SELECT id, control_base_id, estado
            FROM trip.viaje_solicitado
            WHERE id = :viaje_id
              AND control_base_id = :control_base_id
            LIMIT 1
        """),
        {"viaje_id": viaje_id, "control_base_id": control_base_id},
    )
    viaje = viaje_query.first()

    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viaje no encontrado",
        )

    # 2. Registrar rechazo en broadcast_log
    await registrar_broadcast_log(
        db=db,
        viaje_id=viaje_id,
        chofer_id=driver_id,
        vehiculo_id=None,
        distancia_metros=None,
        control_base_id=control_base_id,
        resultado="rechazado",
        motivo_exclusion=None,
    )

    # 3. El viaje NO cambia de estado. Sigue publicado para otros choferes.

    return {
        "success": True,
        "message": "Viaje rechazado",
        "viaje_id": str(viaje_id),
    }


# ============================================
# INICIAR VIAJE
# ============================================

@router.post("/{viaje_id}/iniciar")
async def iniciar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """Iniciar un viaje (chofer)"""
    driver_id, control_base_id, _, _ = current_user

    try:
        result = await actualizar_estado_viaje(
            db, viaje_id, control_base_id, "en_curso", "iniciado_en"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    await db.commit()
    return {"success": True, "message": "Viaje iniciado"}


# ============================================
# FINALIZAR VIAJE
# ============================================

@router.post("/{viaje_id}/finalizar")
async def finalizar_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Finalizar un viaje (chofer).

    Calcula y persiste `precio_final` usando el MOTOR UNIFICADO TAXIP 2.1.
    Recalcula distancia y tiempo reales con Directions API (fallback a los
    persistidos si falla, luego a Haversine).

    Si el motor unificado falla (tarifa no configurada, tipo vehículo
    inactivo, etc.), cae a `precio_estimado` como fallback y lo loguea.
    El viaje se finaliza igual: no se bloquea por un problema de cálculo.

    Libera al chofer (fleet.chofer_vehiculo.estado_laboral = 'libre').
    """
    driver_id, control_base_id, _, _ = current_user

    # ------------------------------------------------------------
    # 1. Leer datos del viaje
    # ------------------------------------------------------------
    ctx_query = text("""
        SELECT
            estado,
            chofer_vehiculo_id,
            precio_estimado,
            distancia_metros,
            tiempo_estimado_segundos,
            tipo_vehiculo_solicitado,
            moneda,
            iniciado_en,
            ST_Y(origen::geometry) AS origen_lat,
            ST_X(origen::geometry) AS origen_lng,
            ST_Y(destino::geometry) AS destino_lat,
            ST_X(destino::geometry) AS destino_lng
        FROM trip.viaje_solicitado
        WHERE id = :viaje_id AND control_base_id = :control_base_id
        LIMIT 1
    """)
    ctx = (await db.execute(ctx_query, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })).first()

    if not ctx:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    (
        estado,
        chofer_vehiculo_id,
        precio_estimado_persistido,
        distancia_metros_persistida,
        tiempo_segundos_persistido,
        tipo_vehiculo_solicitado,
        moneda_persistida,
        iniciado_en,
        origen_lat,
        origen_lng,
        destino_lat,
        destino_lng,
    ) = ctx

    # ------------------------------------------------------------
    # 2. Validar transición
    # ------------------------------------------------------------
    if estado != "en_curso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Solo se puede finalizar un viaje en estado 'en_curso'. "
                f"Estado actual: '{estado}'."
            ),
        )

    # ------------------------------------------------------------
    # 3. Recalcular distancia y tiempo con Directions
    # ------------------------------------------------------------
    from app.services.directions import directions_service

    distancia_km = None
    tiempo_minutos = None

    if origen_lat and origen_lng and destino_lat and destino_lng:
        try:
            ruta = await directions_service.calcular_ruta_por_coords(
                origen_lat, origen_lng, destino_lat, destino_lng,
            )
            if ruta and ruta.get("ruta_completa") is not None:
                distancia_km = float(ruta["distancia_km"])
                tiempo_minutos = int(ruta["tiempo_minutos"])
            else:
                logger.warning(
                    f"Directions devolvió simulación para viaje {viaje_id}, "
                    f"usando datos persistidos."
                )
        except Exception as e:
            logger.warning(f"Directions falló en finalizar_viaje: {e}")

    # Fallback 1: datos persistidos del viaje
    if (distancia_km is None or tiempo_minutos is None) and (
        distancia_metros_persistida and tiempo_segundos_persistido
    ):
        distancia_km = distancia_metros_persistida / 1000.0
        tiempo_minutos = tiempo_segundos_persistido // 60
        logger.info(
            f"Usando distancia/tiempo persistidos para viaje {viaje_id}: "
            f"{distancia_km:.2f} km, {tiempo_minutos} min."
        )

    # Fallback 2: Haversine sobre las coordenadas
    if distancia_km is None or tiempo_minutos is None:
        distancia_metros_haversine = calcular_distancia(
            origen_lat, origen_lng, destino_lat, destino_lng,
        )
        distancia_km = distancia_metros_haversine / 1000.0
        tiempo_minutos = calcular_tiempo_estimado(distancia_metros_haversine) // 60
        logger.warning(
            f"Usando Haversine para viaje {viaje_id}: "
            f"{distancia_km:.2f} km, {tiempo_minutos} min."
        )

    distancia_metros_final = int(distancia_km * 1000)
    tiempo_segundos_final = tiempo_minutos * 60

    # ------------------------------------------------------------
    # 4. Calcular precio final con el motor unificado
    # ------------------------------------------------------------
    precio_final: float
    moneda_final: str = moneda_persistida or "ARS"
    desglose = None
    precio_calculado_con = "motor_unificado"

    try:
        tipo_vehiculo_str = (tipo_vehiculo_solicitado or "standard").lower()
        try:
            tipo_vehiculo_enum = TipoVehiculoEnum(tipo_vehiculo_str)
        except ValueError:
            tipo_vehiculo_enum = TipoVehiculoEnum.STANDARD

        estimacion_request = EstimacionPrecioRequest(
            tipo_vehiculo=tipo_vehiculo_enum,
            direccion_origen="",
            direccion_destino="",
            paradas_intermedias=[],
            tiempo_espera_minutos=0,
            latitud_origen=origen_lat,
            longitud_origen=origen_lng,
            latitud_destino=destino_lat,
            longitud_destino=destino_lng,
        )

        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now(),
            es_feriado=False,
        )

        precio_final = float(resultado.precio_estimado)
        moneda_final = resultado.moneda or moneda_final
        desglose = resultado.desglose

    except Exception as e:
        logger.error(
            f"Error calculando precio_final para viaje {viaje_id}: {e}. "
            f"Fallback a precio_estimado={precio_estimado_persistido}."
        )
        precio_final = (
            float(precio_estimado_persistido)
            if precio_estimado_persistido
            else 0.0
        )
        precio_calculado_con = "fallback_estimado"

    # ------------------------------------------------------------
    # 5. UPDATE atómico del viaje
    # ------------------------------------------------------------
    await db.execute(
        text("""
            UPDATE trip.viaje_solicitado
            SET estado = 'finalizado',
                finalizado_en = NOW(),
                precio_final = :precio_final,
                distancia_metros = :distancia_metros,
                tiempo_estimado_segundos = :tiempo_segundos,
                moneda = :moneda,
                updated_at = NOW()
            WHERE id = :viaje_id AND control_base_id = :control_base_id
        """),
        {
            "viaje_id": viaje_id,
            "control_base_id": control_base_id,
            "precio_final": precio_final,
            "distancia_metros": distancia_metros_final,
            "tiempo_segundos": tiempo_segundos_final,
            "moneda": moneda_final,
        },
    )

    # ------------------------------------------------------------
    # 6. Historial
    # ------------------------------------------------------------
    observacion = (
        f"Viaje finalizado. Precio final: {precio_final} {moneda_final}. "
        f"Calculado con: {precio_calculado_con}. "
        f"Distancia: {distancia_km:.2f} km. Tiempo: {tiempo_minutos} min."
    )
    await db.execute(
        text("""
            INSERT INTO trip.historial_estado_viaje (
                id, viaje_id, estado, observacion, created_at
            )
            VALUES (gen_random_uuid(), :viaje_id, 'finalizado', :obs, NOW())
        """),
        {"viaje_id": viaje_id, "obs": observacion},
    )

    # ------------------------------------------------------------
    # 7. Liberar al chofer
    # ------------------------------------------------------------
    if chofer_vehiculo_id:
        await db.execute(
            text("""
                UPDATE fleet.chofer_vehiculo
                SET estado_laboral = 'libre', updated_at = NOW()
                WHERE id = :chofer_vehiculo_id
            """),
            {"chofer_vehiculo_id": chofer_vehiculo_id},
        )

    # ------------------------------------------------------------
    # 8. Commit
    # ------------------------------------------------------------
    await db.commit()

    # ------------------------------------------------------------
    # 9. Respuesta
    # ------------------------------------------------------------
    return {
        "success": True,
        "message": "Viaje finalizado",
        "viaje_id": str(viaje_id),
        "precio_final": precio_final,
        "moneda": moneda_final,
        "desglose": desglose,
        "precio_calculado_con": precio_calculado_con,
    }


# ============================================
# CANCELAR VIAJE
# ============================================

@router.post("/{viaje_id}/cancelar")
async def cancelar_viaje(
    viaje_id: UUID,
    request: CancelarViajeRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancelar un viaje.
    Si el viaje estaba 'aceptado' o 'en_curso' y tenía chofer asignado,
    libera al chofer (fleet.chofer_vehiculo.estado_laboral = 'libre').
    """
    _, control_base_id, _, _ = current_user

    # 1. Obtener estado actual y chofer_vehiculo_id antes de cambiar
    ctx_query = text("""
        SELECT estado, chofer_vehiculo_id
        FROM trip.viaje_solicitado
        WHERE id = :viaje_id AND control_base_id = :control_base_id
        LIMIT 1
    """)
    ctx = (await db.execute(ctx_query, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })).first()

    if not ctx:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    estado_previo = ctx[0]
    chofer_vehiculo_id = ctx[1]

    # 2. Cambiar estado del viaje

    try:
        result = await actualizar_estado_viaje(
            db, viaje_id, control_base_id, "cancelado", "cancelado_en"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not result:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # 3. Guardar motivo
    if request.motivo:
        await db.execute(
            text("""
                UPDATE trip.viaje_solicitado
                SET motivo_cancelacion = :motivo
                WHERE id = :viaje_id
            """),
            {"viaje_id": viaje_id, "motivo": request.motivo},
        )

    # 4. Liberar al chofer solo si el viaje estaba activo con chofer asignado
    if chofer_vehiculo_id and estado_previo in ("aceptado", "en_curso"):
        await db.execute(
            text("""
                UPDATE fleet.chofer_vehiculo
                SET estado_laboral = 'libre', updated_at = NOW()
                WHERE id = :chofer_vehiculo_id
            """),
            {"chofer_vehiculo_id": chofer_vehiculo_id},
        )

    await db.commit()
    return {"success": True, "message": "Viaje cancelado"}