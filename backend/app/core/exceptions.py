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


# ============================================================
# EXCEPCIONES DE TRIP
# ============================================================

class TripError(Exception):
    """Base exception for trip errors"""
    pass


class TripNotFoundError(TripError):
    """Raised when a trip is not found"""
    pass


class TripInvalidStateError(TripError):
    """Raised when a trip is in an invalid state for the operation"""
    pass


class TripPermissionError(TripError):
    """Raised when a user does not have permission to perform an operation"""
    pass


class TripDriverNotAvailableError(TripError):
    """Raised when a driver is not available for a trip"""
    pass


# ============================================================
# EXCEPCIONES DE RECAUDACIÓN
# ============================================================

class RecaudacionError(Exception):
    """Base exception for recaudacion errors"""
    pass


class RecaudacionNotFoundError(RecaudacionError):
    """Raised when a recaudacion record is not found"""
    pass


class RecaudacionInvalidStateError(RecaudacionError):
    """Raised when a recaudacion record is in an invalid state"""
    pass


class RecaudacionPermissionError(RecaudacionError):
    """Raised when a user does not have permission"""
    pass

# app/core/exceptions.py - AGREGAR AL FINAL DEL ARCHIVO

# ============================================================
# EXCEPCIONES DE CORPORATE
# ============================================================

class CorporateError(Exception):
    """Base exception for corporate module errors"""
    pass


class CorporateNotFoundError(CorporateError):
    """Raised when a corporate record is not found"""
    pass


class CorporateInvalidStateError(CorporateError):
    """Raised when a corporate record is in an invalid state"""
    pass


class CorporatePermissionError(CorporateError):
    """Raised when a user does not have permission"""
    pass


class CorporateCreditLimitExceededError(CorporateError):
    """Raised when a credit limit is exceeded"""
    pass