"""
Broadcast Service - Motor de publicacion de viajes a choferes cercanos.

Responsabilidades:
- Publicar un viaje a choferes dentro de un radio (con ampliacion progresiva)
- Registrar cada emision en trip.broadcast_log
- Notificar a choferes excluidos (por filtros opt-in)
- Manejar timeout de publicacion (re-publicar o expirar)
- Notificar a pasajeros y choferes por WebSocket
"""
import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.geo_service import buscar_choferes_cercanos
from app.services.trip_service import TripService
from app.websocket.connection_manager import manager
from app.websocket.events import EventType

logger = logging.getLogger(__name__)


# ============================================================
# CONSTANTES DE NEGOCIO
# ============================================================

RADIO_INICIAL_METROS = 2000
RADIO_MAXIMO_METROS = 10000
FACTOR_AMPLIACION = 2
TIMEOUT_SEGUNDOS = 50
MAX_INTENTOS = 3


# ============================================================
# PUBLICACION PRINCIPAL
# ============================================================

async def publicar_viaje_a_cercanos(
    db: AsyncSession,
    viaje_id: UUID,
) -> dict:
    """
    Publica un viaje a choferes cercanos.

    Flujo:
    1. Cargar viaje
    2. Calcular radio segun intentos previos
    3. Buscar choferes elegibles (geo_service)
    4. Enviar WS 'nuevo_viaje' a elegibles
    5. Enviar WS 'excluido_de_viaje' a excluidos conectados
    6. Registrar en trip.broadcast_log
    7. Marcar viaje como 'publicado'

    Returns:
        {
            "publicados": int,        # cuantos recibieron el viaje
            "excluidos": int,         # cuantos fueron excluidos
            "sin_choferes": bool,     # True si no habia nadie en radio
            "intentos": int,          # intento actual
            "radio_metros": int,      # radio usado
        }
    """
    trip_service = TripService(db)

    # 1. Cargar viaje
    viaje = await trip_service.get_viaje(viaje_id)
    if not viaje:
        logger.warning(f"Broadcast: viaje {viaje_id} no encontrado")
        return {"error": "viaje_no_encontrado"}

    if viaje.estado not in ("pendiente", "publicado"):
        logger.info(
            f"Broadcast: viaje {viaje_id} en estado '{viaje.estado}', no se publica"
        )
        return {"error": f"estado_invalido_{viaje.estado}"}

    # 2. Calcular radio (ampliacion progresiva)
    intentos = viaje.intentos_broadcast or 0
    radio = min(RADIO_INICIAL_METROS * (FACTOR_AMPLIACION ** intentos), RADIO_MAXIMO_METROS)

    # Necesitamos lat/lng del origen. Intentamos sacarlos del campo PostGIS.
    # Si no estan, hacemos fallback a las direcciones (no deberia pasar).
    if not viaje.origen:
        logger.warning(f"Broadcast: viaje {viaje_id} sin campo origen")
        return {"error": "sin_origen"}

    # Extraer lat/lng desde el WKB de PostGIS
    # ST_X y ST_Y funcionan sobre geography/geometry
    coords_query = await db.execute(
        text("""
            SELECT
                ST_Y(origen::geometry) AS lat,
                ST_X(origen::geometry) AS lng
            FROM trip.viaje_solicitado
            WHERE id = :viaje_id
        """),
        {"viaje_id": viaje_id},
    )
    coords = coords_query.first()
    if not coords or coords.lat is None:
        logger.warning(f"Broadcast: viaje {viaje_id} sin coordenadas de origen")
        return {"error": "sin_coordenadas"}

    lat = float(coords.lat)
    lng = float(coords.lng)

    # 3. Buscar choferes elegibles
    elegibles = await buscar_choferes_cercanos(
        db=db,
        control_base_id=viaje.control_base_id,
        lat=lat,
        lng=lng,
        radio_metros=radio,
        requiere_baul_grande=bool(viaje.requiere_baul_grande),
        calidad_minima_vehiculo=viaje.calidad_minima_vehiculo,
        tipo_vehiculo_solicitado=viaje.tipo_vehiculo_solicitado,
        # TODO: excluir choferes que ya rechazaron este viaje
        excluir_chofer_ids=None,
    )

    # Sacar la lista de excluidos que vino adjunta
    excluidos = elegibles[0].get("_excluidos", []) if elegibles else []

    # 4. Marcar viaje como publicado
    await trip_service.marcar_viaje_publicado(viaje_id, radio_metros=radio)

    # 5. Preparar payload
    payload = {
        "viaje_id": str(viaje.id),
        "origen": {
            "lat": lat,
            "lng": lng,
            "direccion": viaje.direccion_origen,
        },
        "destino": {
            "direccion": viaje.direccion_destino,
        },
        "precio_estimado": float(viaje.precio_estimado) if viaje.precio_estimado else None,
        "distancia_metros": viaje.distancia_metros,
        "tiempo_estimado_segundos": viaje.tiempo_estimado_segundos,
        "nombre_pasajero": viaje.nombre_pasajero,
        "notas": viaje.notas,
        "requiere_baul_grande": bool(viaje.requiere_baul_grande),
        "calidad_minima_vehiculo": viaje.calidad_minima_vehiculo,
        "timeout_segundos": TIMEOUT_SEGUNDOS,
        "intento": intentos + 1,
        "radio_metros": radio,
    }

    # 6. Enviar WS a elegibles
    publicados = 0
    for chofer in elegibles:
        enviado = await manager.send_personal(
            str(chofer["chofer_id"]),
            EventType.NUEVO_VIAJE,
            payload,
        )
        if enviado:
            publicados += 1

        # Registrar en broadcast_log (aunque no este conectado)
        await registrar_broadcast_log(
            db=db,
            viaje_id=viaje.id,
            chofer_id=chofer["chofer_id"],
            vehiculo_id=chofer["vehiculo_id"],
            distancia_metros=chofer.get("distancia_metros"),
            control_base_id=viaje.control_base_id,
            resultado="enviado" if enviado else "sin_conexion",
        )

    # 7. Enviar WS a excluidos (motivo de exclusion)
    for exc in excluidos:
        await manager.send_personal(
            str(exc["chofer_id"]),
            EventType.EXCLUIDO_DE_VIAJE,
            {
                "viaje_id": str(viaje.id),
                "motivo": exc.get("motivo_exclusion", "no_elegible"),
                "detalle": _motivo_detalle(exc.get("motivo_exclusion")),
            },
        )

    # 8. Log final
    logger.info(
        f"Broadcast: viaje {viaje_id} publicado a {publicados} choferes "
        f"(radio={radio}m, intento={intentos + 1}, excluidos={len(excluidos)})"
    )

    return {
        "publicados": publicados,
        "excluidos": len(excluidos),
        "sin_choferes": len(elegibles) == 0,
        "intentos": intentos + 1,
        "radio_metros": radio,
    }


# ============================================================
# TIMEOUT Y RE-PUBLICACION
# ============================================================

async def manejar_timeout_broadcast(
    db: AsyncSession,
    viaje_id: UUID,
) -> str:
    """
    Maneja el timeout de un viaje publicado.

    Retorna:
        'aceptado'    -> el viaje ya fue aceptado, no hacer nada
        'republicado' -> se re-publico con radio ampliado
        'expirado'    -> se supero el maximo de intentos, viaje expirado
        'error'       -> algo salio mal
    """
    trip_service = TripService(db)
    viaje = await trip_service.get_viaje(viaje_id)

    if not viaje:
        return "error"

    # Si ya fue aceptado o esta en otro estado, no tocar
    if viaje.estado != "publicado":
        return "aceptado"

    intentos = viaje.intentos_broadcast or 0

    # Si ya superamos el maximo, expirar
    if intentos >= MAX_INTENTOS:
        await db.execute(
            text("""
                UPDATE trip.viaje_solicitado
                SET estado = 'expirado',
                    updated_at = NOW()
                WHERE id = :viaje_id
                  AND estado = 'publicado'
            """),
            {"viaje_id": viaje_id},
        )
        await db.commit()

        # Notificar al pasajero
        if viaje.pasajero_id:
            await manager.send_personal(
                str(viaje.pasajero_id),
                EventType.VIAJE_EXPIRADO,
                {"viaje_id": str(viaje_id), "intentos": intentos},
            )

        logger.warning(f"Broadcast: viaje {viaje_id} expirado tras {intentos} intentos")
        return "expirado"

    # Re-publicar con radio ampliado
    await db.execute(
        text("""
            UPDATE trip.viaje_solicitado
            SET intentos_broadcast = intentos_broadcast + 1,
                estado = 'pendiente',
                updated_at = NOW()
            WHERE id = :viaje_id
              AND estado = 'publicado'
        """),
        {"viaje_id": viaje_id},
    )
    await db.commit()

    # Notificar al pasajero que se esta re-publicando
    if viaje.pasajero_id:
        await manager.send_personal(
            str(viaje.pasajero_id),
            EventType.VIAJE_REASIGNADO,
            {"viaje_id": str(viaje_id), "intento": intentos + 1},
        )

    # Re-publicar
    resultado = await publicar_viaje_a_cercanos(db, viaje_id)

    logger.info(
        f"Broadcast: viaje {viaje_id} re-publicado (intento {intentos + 1}) "
        f"-> {resultado}"
    )
    return "republicado"


# ============================================================
# REGISTRO DE BROADCAST LOG
# ============================================================

async def registrar_broadcast_log(
    db: AsyncSession,
    viaje_id: UUID,
    chofer_id: UUID,
    vehiculo_id: Optional[UUID],
    distancia_metros: Optional[float],
    control_base_id: UUID,
    resultado: str,
    motivo_exclusion: Optional[str] = None,
) -> None:
    """
    Inserta una fila en trip.broadcast_log.
    """
    await db.execute(
        text("""
            INSERT INTO trip.broadcast_log (
                id, viaje_id, chofer_id, vehiculo_id,
                distancia_metros, emitido_en, respuesta,
                motivo_exclusion, control_base_id
            )
            VALUES (
                gen_random_uuid(), :viaje_id, :chofer_id, :vehiculo_id,
                :distancia, NOW(), :resultado,
                :motivo, :control_base_id
            )
        """),
        {
            "viaje_id": viaje_id,
            "chofer_id": chofer_id,
            "vehiculo_id": vehiculo_id,
            "distancia": int(distancia_metros) if distancia_metros else None,
            "resultado": resultado,
            "motivo": motivo_exclusion,
            "control_base_id": control_base_id,
        },
    )
    await db.commit()


# ============================================================
# HELPERS
# ============================================================

def _motivo_detalle(motivo: Optional[str]) -> str:
    """Texto legible del motivo de exclusion."""
    detalles = {
        "baul_insuficiente": "El viaje requiere baul grande",
        "calidad_insuficiente": "El vehiculo no cumple la calidad minima",
        "tipo_vehiculo_no_coincide": "El tipo de vehiculo no coincide",
        "no_disponible": "No estas disponible en este momento",
        "sin_turno": "No tenes turno activo",
        "no_aprobado": "Tu cuenta no esta aprobada",
        "rechazo_previo": "Ya rechazaste este viaje",
    }
    return detalles.get(motivo, "No cumples los filtros del viaje")