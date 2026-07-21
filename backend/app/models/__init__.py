# app/models/__init__.py

# Importar Base
from app.database import Base

# Auth
from app.models.auth import (
    TipoUsuario,
    Usuario,
    PerfilGeneral,
    DireccionFrecuente,
    TaxistaFavorito,
    ResetToken,
)

# Tenant
from app.models.tenant import (
    ControlBase,
    Configuracion,
)

# Audit
from app.models.audit import (
    LogGps,
    AlertaDesvio,
)

# Fleet
from app.models.fleet import (
    Vehiculo,
    ChoferVehiculo,
    GastoVehiculo,
    MantenimientoVehiculo,
    PropietarioVehiculo,
    ContratoVehiculo,
)

# Geo
from app.models.geo import (
    Pais,
    Provincia,
    Ciudad,
)

# Notification
from app.models.notification import (
    Notificacion,
)

# Payment
from app.models.payment import (
    MetodoPago,
    Billetera,
    Transaccion,
    ConfiguracionTarifa,
)

# Trip
from app.models.trip import (
    ViajeSolicitado,
    HistorialEstadoViaje,
    Panico,
    Calificacion,
    ObjetoOlvidado,
    TipoVehiculo,
)

# Turno
from app.models.turno import TurnoChofer

# Gasto
from app.models.gasto_turno import GastoTurno

# Foto Viaje
from app.models.foto_viaje import FotoViaje

__all__ = [
    # Base
    "Base",

    # Auth
    "TipoUsuario",
    "Usuario",
    "PerfilGeneral",
    "DireccionFrecuente",
    "TaxistaFavorito",
    "ResetToken",

    # Tenant
    "ControlBase",
    "Configuracion",

    # Audit
    "LogGps",
    "AlertaDesvio",

    # Fleet
    "Vehiculo",
    "ChoferVehiculo",
    "GastoVehiculo",
    "MantenimientoVehiculo",
    "PropietarioVehiculo",
    "ContratoVehiculo",

    # Geo
    "Pais",
    "Provincia",
    "Ciudad",

    # Notification
    "Notificacion",

    # Payment
    "MetodoPago",
    "Billetera",
    "Transaccion",
    "ConfiguracionTarifa",

    # Trip
    "ViajeSolicitado",
    "HistorialEstadoViaje",
    "Panico",
    "Calificacion",
    "ObjetoOlvidado",
    "TipoVehiculo",

    # Turno
    "TurnoChofer",

    # Gasto
    "GastoTurno",

    # Foto Viaje
    "FotoViaje",
]