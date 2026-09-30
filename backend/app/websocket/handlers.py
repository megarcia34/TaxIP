"""
WebSocket Event Handlers
"""

import json
import logging
from fastapi import WebSocket
from typing import Dict, Any, Optional
from uuid import UUID

from app.websocket.connection_manager import manager
from app.database import AsyncSessionLocal
from app.core.route_monitor import RouteMonitor
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def _resolver_rol_y_tenant(user_id: str) -> tuple[str, Optional[str]]:
    """
    Consulta la DB para resolver rol y control_base_id de un usuario.
    Devuelve ("unknown", None) si no se puede resolver.
    """
    try:
        async with AsyncSessionLocal() as db:
            query = text("""
                SELECT tu.nombre, u.control_base_id
                FROM auth.usuario u
                JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
                WHERE u.id = :user_id AND u.activo = true
            """)
            result = await db.execute(query, {"user_id": UUID(user_id)})
            row = result.first()
            if row:
                rol = row[0] or "unknown"
                tenant = str(row[1]) if row[1] else None
                return rol, tenant
    except Exception as e:
        logger.error(f"WS: no se pudo resolver rol/tenant para {user_id}: {e}")
    return "unknown", None


async def handle_websocket(
    websocket: WebSocket,
    user_id: str,
    rol: str = "unknown",
):
    """
    Main WebSocket handler for a connected user.

    Args:
        websocket: el socket.
        user_id: id del usuario autenticado.
        rol: tipo de usuario, si viene del JWT. Si no, se resuelve de la DB.
    """
    # Si no vino el rol, resolverlo de la DB. Siempre resolver el tenant.
    if rol == "unknown":
        rol, control_base_id = await _resolver_rol_y_tenant(user_id)
    else:
        # Aunque tengamos el rol del JWT, el tenant no viene ahí.
        _, control_base_id = await _resolver_rol_y_tenant(user_id)

    await manager.connect(websocket, user_id, rol, control_base_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await process_message(user_id, message, websocket)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "data": {"message": "Invalid JSON"}}
                )
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    finally:
        manager.disconnect(user_id)


async def process_message(
    user_id: str, message: Dict[str, Any], websocket: WebSocket
):
    """Route incoming messages to appropriate handlers"""
    msg_type = message.get("type")

    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})

    elif msg_type == "set_role":
        role = message.get("data", {}).get("role")
        if role in ["pasajero", "chofer"]:
            if user_id in manager.metadata:
                manager.metadata[user_id]["rol"] = role
            await websocket.send_json(
                {"type": "role_set", "data": {"role": role}}
            )

    elif msg_type == "location_update":
        # Chequear rol desde metadata (no existe manager.user_roles).
        user_meta = manager.metadata.get(user_id, {})
        if user_meta.get("rol") != "chofer":
            return

        data = message.get("data", {})
        # Alineado al frontend: el cliente manda lat/lng en camelCase.
        lat = data.get("lat")
        lng = data.get("lng")
        viaje_id = data.get("viaje_id")

        if lat and lng:
            async with AsyncSessionLocal() as db:
                query = text("""
                    UPDATE fleet.chofer_vehiculo
                    SET latitud = :lat, longitud = :lng,
                        ubicacion = ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                        ultima_conexion = NOW()
                    WHERE usuario_id = :user_id
                """)
                await db.execute(
                    query,
                    {"lat": lat, "lng": lng, "user_id": UUID(user_id)},
                )

                if viaje_id:
                    log_query = text("""
                        INSERT INTO audit.log_gps
                            (id, viaje_id, usuario_id, latitud, longitud, ubicacion, created_at)
                        VALUES
                            (gen_random_uuid(), :viaje_id, :user_id, :lat, :lng,
                             ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, NOW())
                    """)
                    await db.execute(
                        log_query,
                        {
                            "viaje_id": UUID(viaje_id),
                            "user_id": UUID(user_id),
                            "lat": lat,
                            "lng": lng,
                        },
                    )

                    deviation = await RouteMonitor.check_deviation(
                        UUID(viaje_id), lat, lng
                    )
                    if deviation and deviation > 100:
                        await RouteMonitor.alert_deviation(
                            UUID(viaje_id), lat, lng, deviation
                        )

                await db.commit()

            if viaje_id:
                await manager.send_driver_location_to_passenger(
                    viaje_id, lat, lng
                )

    elif msg_type == "subscribe_trip":
        data = message.get("data", {})
        viaje_id = data.get("viaje_id")
        if viaje_id:
            manager.subscribe_passenger_to_trip(viaje_id, user_id)
            await websocket.send_json(
                {"type": "subscribed", "data": {"viaje_id": viaje_id}}
            )

    elif msg_type == "arrived":
        data = message.get("data", {})
        viaje_id = data.get("viaje_id")
        if viaje_id:
            passenger_id = manager.get_passenger_of_trip(viaje_id)
            if passenger_id:
                await manager.notify_driver_arrived(passenger_id, viaje_id)