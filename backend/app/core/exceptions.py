# app/core/exceptions.py
"""
Excepciones personalizadas para la aplicación
"""


class TenantMismatchError(Exception):
    """Error cuando un objeto no pertenece al tenant esperado"""
    pass


class LiquidacionError(Exception):
    """Error general del módulo de liquidaciones"""
    pass


class TurnoError(Exception):
    """Error en la gestión de turnos"""
    pass


class ContratoError(Exception):
    """Error en la gestión de contratos"""
    pass


class VehiculoError(Exception):
    """Error en la gestión de vehículos"""
    pass


class ChoferError(Exception):
    """Error en la gestión de choferes"""
    pass


class AutorizacionError(Exception):
    """Error en la autorización de turnos"""
    pass