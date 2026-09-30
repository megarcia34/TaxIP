"""
Enumeración de eventos WebSocket del sistema TaxIP.
"""
from enum import Enum


class EventType(str, Enum):
    # Cliente -> Servidor
    PING = "ping"
    SET_ROLE = "set_role"
    LOCATION_UPDATE = "location_update"
    SUBSCRIBE_TRIP = "subscribe_trip"
    ARRIVED = "arrived"

    # Servidor -> Cliente (genéricos)
    PONG = "pong"
    ERROR = "error"

    # Servidor -> Choferes
    NUEVO_VIAJE = "nuevo_viaje"
    VIAJE_TOMADO = "viaje_tomado"
    EXCLUIDO_DE_VIAJE = "excluido_de_viaje"

    # Servidor -> Pasajero / Empleado
    VIAJE_ASIGNADO = "viaje_asignado"
    VEHICULO_LLEGO = "vehiculo_llego"
    VIAJE_INICIADO = "viaje_iniciado"
    VIAJE_FINALIZADO = "viaje_finalizado"
    VIAJE_CANCELADO = "viaje_cancelado"
    VIAJE_REASIGNADO = "viaje_reasignado"
    VIAJE_EXPIRADO = "viaje_expirado"
    DESVIO_RUTA = "desvio_ruta"

    # Chofer (cobro)
    COBRO_PENDIENTE = "cobro_pendiente"
    PAGO_CONFIRMADO = "pago_confirmado"

    # Empleado (despacho manual)
    RESERVA_PUBLICADA = "reserva_publicada"
    RESERVA_ACEPTADA = "reserva_aceptada"
    RESERVA_EN_CURSO = "reserva_en_curso"
    RESERVA_COMPLETADA = "reserva_completada"
    RESERVA_CANCELADA = "reserva_cancelada"

    # Legacy
    ROLE_SET = "role_set"
    SUBSCRIBED = "subscribed"
    DRIVER_ARRIVED = "driver_arrived"
    DRIVER_LOCATION_UPDATE = "driver_location_update"


class WsCloseCode:
    NORMAL = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    POLICY_VIOLATION = 1008
    INTERNAL_ERROR = 1011
    UNAUTHORIZED = 4001
    FORBIDDEN = 4003
    TOO_MANY_CONNECTIONS = 4008
    INVALID_ROLE = 4009


WS_HEARTBEAT_INTERVAL_SECONDS = 30
WS_HEARTBEAT_TIMEOUT_SECONDS = 90
WS_AUTH_TIMEOUT_SECONDS = 5
