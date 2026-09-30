"""
WebSocket Connection Manager para TaxIP.

Gestiona conexiones WebSocket activas con:
- Multi-tenant por control_base_id
- Metadata por usuario (rol, control_base_id, viaje activo)
- Envío personal, por rol y a múltiples destinatarios
- Compatibilidad con métodos legacy
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket

from app.websocket.events import EventType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gestiona conexiones WebSocket para comunicación en tiempo real.
    """

    def __init__(self):
        # user_id -> WebSocket
        self.active: Dict[str, WebSocket] = {}

        # user_id -> metadata
        # metadata[user_id] = {
        #     "rol": "chofer",
        #     "control_base_id": "uuid" | None,
        #     "conectado_en": datetime,
        #     "viaje_activo": "uuid" | None,
        # }
        self.metadata: Dict[str, dict] = {}

        # viaje_id -> user_id del pasajero suscrito al viaje
        # Sirve para saber a quién notificar sobre el viaje.
        self.trip_passengers: Dict[str, str] = {}

    # ============================================
    # CONEXIÓN / DESCONEXIÓN
    # ============================================

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        rol: str,
        control_base_id: Optional[str] = None,
    ) -> None:
        """
        Registra una conexión WebSocket.
        El websocket debe venir YA AUTENTICADO (ver auth.py).

        IMPORTANTE: el primer await sobre el WebSocket debe ser accept().
        Si no, Starlette responde 500 al upgrade.
        """
        # Aceptar el handshake ANTES de cualquier otra operación.
        await websocket.accept()

        # Si el usuario ya tenía una conexión, cerrarla
        if user_id in self.active:
            old_ws = self.active[user_id]
            try:
                await old_ws.close(code=1000)
            except Exception:
                pass
            logger.info(f"WS: conexión previa de {user_id} reemplazada")

        self.active[user_id] = websocket
        self.metadata[user_id] = {
            "rol": rol,
            "control_base_id": control_base_id,
            "conectado_en": datetime.utcnow(),
            "viaje_activo": None,
        }

        logger.info(
            f"WS: {rol} {user_id} conectado (tenant={control_base_id}). "
            f"Total conexiones: {len(self.active)}"
        )

    def disconnect(self, user_id: str) -> None:
        """Elimina una conexión y limpia su metadata."""
        self.active.pop(user_id, None)
        self.metadata.pop(user_id, None)
        # Limpiar suscripciones a viajes donde este usuario era pasajero
        viajes_a_limpiar = [
            viaje_id
            for viaje_id, pasajero_id in self.trip_passengers.items()
            if pasajero_id == user_id
        ]
        for viaje_id in viajes_a_limpiar:
            self.trip_passengers.pop(viaje_id, None)
        logger.info(f"WS: {user_id} desconectado. Total: {len(self.active)}")

    def is_connected(self, user_id: str) -> bool:
        """Devuelve True si el usuario tiene conexión activa."""
        return user_id in self.active

    # ============================================
    # ENVÍO DE MENSAJES
    # ============================================

    async def send_personal(
        self,
        user_id: str,
        event: EventType,
        data: Optional[dict] = None,
    ) -> bool:
        """
        Envía un evento a un usuario específico.
        Retorna True si se envió OK, False si no estaba conectado o falló.
        """
        ws = self.active.get(user_id)
        if not ws:
            return False

        mensaje = {
            "type": event.value if isinstance(event, EventType) else event,
            "data": data or {},
        }

        try:
            await ws.send_json(mensaje)
            return True
        except Exception as e:
            logger.error(f"WS: error enviando a {user_id}: {e}")
            self.disconnect(user_id)
            return False

    async def broadcast_a_rol(
        self,
        rol: str,
        event: EventType,
        data: Optional[dict] = None,
        control_base_id: Optional[str] = None,
    ) -> int:
        """
        Envía un evento a todos los usuarios de un rol.

        Args:
            rol: "chofer", "pasajero", "empleado", "propietario"
            event: EventType
            data: payload
            control_base_id: si se especifica, solo envía a ese tenant

        Returns:
            Cantidad de envíos exitosos.
        """
        destinatarios = self.get_connected_by_rol(rol, control_base_id)
        enviados = 0
        for uid in destinatarios:
            if await self.send_personal(uid, event, data):
                enviados += 1
        return enviados

    async def broadcast_a_usuarios(
        self,
        user_ids: List[str],
        event: EventType,
        data: Optional[dict] = None,
    ) -> int:
        """Envía un evento a una lista de usuarios."""
        enviados = 0
        for uid in user_ids:
            if await self.send_personal(uid, event, data):
                enviados += 1
        return enviados

    # ============================================
    # CONSULTAS
    # ============================================

    def get_connected_by_rol(
        self,
        rol: str,
        control_base_id: Optional[str] = None,
    ) -> List[str]:
        """Devuelve user_ids de un rol (opcionalmente filtrado por tenant)."""
        resultado = []
        for uid, meta in self.metadata.items():
            if meta.get("rol") != rol:
                continue
            if control_base_id and meta.get("control_base_id") != control_base_id:
                continue
            resultado.append(uid)
        return resultado

    def get_metadata(self, user_id: str) -> Optional[dict]:
        """Devuelve la metadata de un usuario conectado."""
        return self.metadata.get(user_id)

    def get_choferes_disponibles(
        self,
        control_base_id: Optional[str] = None,
    ) -> List[str]:
        """Choferes conectados y sin viaje activo."""
        return [
            uid
            for uid, meta in self.metadata.items()
            if meta.get("rol") == "chofer"
            and not meta.get("viaje_activo")
            and (
                not control_base_id
                or meta.get("control_base_id") == control_base_id
            )
        ]

    # ============================================
    # VIAJE ACTIVO
    # ============================================

    def set_viaje_activo(self, user_id: str, viaje_id: Optional[str]) -> None:
        """Marca (o limpia) el viaje activo de un usuario."""
        if user_id in self.metadata:
            self.metadata[user_id]["viaje_activo"] = viaje_id

    # ============================================
    # SUSCRIPCIÓN A VIAJES (pasajero)
    # ============================================

    def subscribe_passenger_to_trip(self, viaje_id: str, passenger_id: str) -> None:
        """Suscribe un pasajero a las notificaciones de un viaje."""
        self.trip_passengers[viaje_id] = passenger_id

    def unsubscribe_passenger_from_trip(self, viaje_id: str) -> None:
        """Desuscribe al pasajero de un viaje."""
        self.trip_passengers.pop(viaje_id, None)

    def get_passenger_of_trip(self, viaje_id: str) -> Optional[str]:
        """Devuelve el user_id del pasajero suscrito a un viaje."""
        return self.trip_passengers.get(viaje_id)

    # ============================================
    # NOTIFICACIONES ESPECÍFICAS DE VIAJE
    # ============================================

    async def notify_driver_arrived(
        self, passenger_id: str, viaje_id: str
    ) -> bool:
        """
        Notifica al pasajero que el chofer llegó al punto de origen.
        """
        return await self.send_personal(
            passenger_id,
            EventType.VEHICULO_LLEGO,
            {"viaje_id": viaje_id},
        )

    async def send_driver_location_to_passenger(
        self, viaje_id: str, lat: float, lng: float
    ) -> bool:
        """
        Envía la ubicación actual del chofer al pasajero suscrito al viaje.
        """
        passenger_id = self.trip_passengers.get(viaje_id)
        if not passenger_id:
            return False
        return await self.send_personal(
            passenger_id,
            EventType.DRIVER_LOCATION_UPDATE,
            {"viaje_id": viaje_id, "lat": lat, "lng": lng},
        )

    # ============================================
    # LEGACY (compatibilidad)
    # ============================================

    async def send_personal_message(self, user_id: str, message: dict) -> bool:
        """
        LEGACY: envía un dict crudo sin tipar con EventType.
        Mantenido para compatibilidad con app/routers/propietario/mantenimientos.py
        """
        ws = self.active.get(user_id)
        if not ws:
            return False
        try:
            await ws.send_json(message)
            return True
        except Exception as e:
            logger.error(f"WS legacy: error enviando a {user_id}: {e}")
            self.disconnect(user_id)
            return False

    async def broadcast_to_drivers_nearby(self, message: dict) -> int:
        """
        LEGACY: envía un dict crudo a todos los choferes conectados.
        Equivalente al viejo 'broadcast_to_drivers_nearby'.
        """
        enviados = 0
        for uid in self.get_connected_by_rol("chofer"):
            if await self.send_personal_message(uid, message):
                enviados += 1
        return enviados


# Singleton global
manager = ConnectionManager()