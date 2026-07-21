"""
WebSocket Event Handlers
"""

import json
import logging
from fastapi import WebSocket
from typing import Dict, Any
from uuid import UUID

from app.websocket.connection_manager import manager
from app.database import AsyncSessionLocal
from app.core.route_monitor import RouteMonitor
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def handle_websocket(websocket: WebSocket, user_id: str):
    """Main WebSocket handler for a connected user"""
    await manager.connect(websocket, user_id, "unknown")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await process_message(user_id, message, websocket)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "data": {"message": "Invalid JSON"}})
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    finally:
        manager.disconnect(user_id)


async def process_message(user_id: str, message: Dict[str, Any], websocket: WebSocket):
    """Route incoming messages to appropriate handlers"""
    msg_type = message.get("type")
    
    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    
    elif msg_type == "set_role":
        role = message.get("data", {}).get("role")
        if role in ["pasajero", "chofer"]:
            manager.user_roles[user_id] = role
            if role == "chofer":
                manager.available_drivers.add(user_id)
            await websocket.send_json({"type": "role_set", "data": {"role": role}})
    
    elif msg_type == "location_update" and manager.user_roles.get(user_id) == "chofer":
        data = message.get("data", {})
        lat = data.get("latitud")
        lng = data.get("longitud")
        viaje_id = data.get("viaje_id")
        
        if lat and lng:
            async with AsyncSessionLocal() as db:
                # Update driver location
                query = text("""
                    UPDATE fleet.chofer_vehiculo
                    SET latitud = :lat, longitud = :lng,
                        ubicacion = ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                        ultima_conexion = NOW()
                    WHERE usuario_id = :user_id
                """)
                await db.execute(query, {"lat": lat, "lng": lng, "user_id": UUID(user_id)})
                
                # Log GPS if in active trip
                if viaje_id:
                    log_query = text("""
                        INSERT INTO audit.log_gps (id, viaje_id, usuario_id, latitud, longitud, ubicacion, created_at)
                        VALUES (gen_random_uuid(), :viaje_id, :user_id, :lat, :lng,
                                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, NOW())
                    """)
                    await db.execute(log_query, {
                        "viaje_id": UUID(viaje_id),
                        "user_id": UUID(user_id),
                        "lat": lat,
                        "lng": lng
                    })
                    
                    # Check route deviation
                    deviation = await RouteMonitor.check_deviation(UUID(viaje_id), lat, lng)
                    if deviation and deviation > 100:
                        await RouteMonitor.alert_deviation(UUID(viaje_id), lat, lng, deviation)
                
                await db.commit()
            
            if viaje_id:
                await manager.send_driver_location_to_passenger(viaje_id, lat, lng)
    
    elif msg_type == "subscribe_trip":
        data = message.get("data", {})
        viaje_id = data.get("viaje_id")
        if viaje_id:
            manager.trip_passengers[viaje_id] = user_id
            await websocket.send_json({"type": "subscribed", "data": {"viaje_id": viaje_id}})
    
    elif msg_type == "arrived":
        data = message.get("data", {})
        viaje_id = data.get("viaje_id")
        if viaje_id:
            passenger_id = manager.trip_passengers.get(viaje_id)
            if passenger_id:
                await manager.notify_driver_arrived(passenger_id)