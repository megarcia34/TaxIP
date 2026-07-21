"""
WebSocket Connection Manager
Manages active connections for passengers and drivers
"""

from fastapi import WebSocket
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_roles: Dict[str, str] = {}
        self.trip_passengers: Dict[str, str] = {}
        self.trip_drivers: Dict[str, str] = {}
        self.available_drivers: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, user_id: str, role: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_roles[user_id] = role
        
        if role == "chofer":
            self.available_drivers.add(user_id)
            logger.info(f"🚗 Driver {user_id} connected. Available: {len(self.available_drivers)}")
        else:
            logger.info(f"👤 User {user_id} ({role}) connected")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        role = self.user_roles.pop(user_id, None)
        if role == "chofer":
            self.available_drivers.discard(user_id)
        
        for trip_id, pid in list(self.trip_passengers.items()):
            if pid == user_id:
                del self.trip_passengers[trip_id]
        for trip_id, did in list(self.trip_drivers.items()):
            if did == user_id:
                del self.trip_drivers[trip_id]
        
        logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, user_id: str, message: dict) -> bool:
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"Error sending to {user_id}: {e}")
                self.disconnect(user_id)
        return False
    
    async def broadcast_to_drivers_nearby(self, message: dict) -> int:
        sent_count = 0
        for driver_id in self.available_drivers:
            if await self.send_personal_message(driver_id, message):
                sent_count += 1
        return sent_count
    
    async def send_driver_location_to_passenger(self, viaje_id: str, lat: float, lng: float):
        passenger_id = self.trip_passengers.get(viaje_id)
        if passenger_id:
            message = {
                "type": "driver_location_update",
                "data": {
                    "viaje_id": viaje_id,
                    "latitud": lat,
                    "longitud": lng
                }
            }
            await self.send_personal_message(passenger_id, message)
    
    def register_trip(self, viaje_id: str, passenger_id: str, driver_id: str):
        self.trip_passengers[viaje_id] = passenger_id
        self.trip_drivers[viaje_id] = driver_id
        self.available_drivers.discard(driver_id)
        logger.info(f"📡 Trip {viaje_id} registered: P={passenger_id}, D={driver_id}")
    
    def unregister_trip(self, viaje_id: str):
        driver_id = self.trip_drivers.pop(viaje_id, None)
        self.trip_passengers.pop(viaje_id, None)
        
        if driver_id and self.user_roles.get(driver_id) == "chofer":
            self.available_drivers.add(driver_id)
    
    async def notify_driver_arrived(self, passenger_id: str):
        message = {
            "type": "driver_arrived",
            "data": {"message": "Tu conductor ha llegado", "play_sound": True}
        }
        await self.send_personal_message(passenger_id, message)


manager = ConnectionManager()