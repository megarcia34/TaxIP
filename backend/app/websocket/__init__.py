"""
WebSocket module for real-time communication in TaxIP.

Exporta:
- ConnectionManager: gestor de conexiones
- manager: instancia singleton
- handle_websocket: handler principal del endpoint WS
- EventType: enum de eventos
- WsCloseCode: códigos de cierre
- authenticate_ws: validación JWT para WS
"""
from app.websocket.connection_manager import ConnectionManager, manager
from app.websocket.events import EventType, WsCloseCode
from app.websocket.handlers import handle_websocket

__all__ = [
    "ConnectionManager",
    "manager",
    "handle_websocket",
    "EventType",
    "WsCloseCode",
]
