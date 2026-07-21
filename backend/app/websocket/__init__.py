"""
WebSocket module for real-time communication
"""

from app.websocket.connection_manager import ConnectionManager, manager
from app.websocket.handlers import handle_websocket

__all__ = ["ConnectionManager", "manager", "handle_websocket"]