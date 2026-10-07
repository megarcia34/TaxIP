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
    UsuarioRol,
    RefreshToken,
    UsuarioEmpresa,
    AutorizacionInicio,
    TurnoEmpleado,
    AuditoriaEmail,
    CodigoMetadatos,
    CodigoVerificacion,
    PlantillaViaje,
    PrestadoraTelefonica,
)

# Corporate
from app.models.corporate import (
    CuentaCorriente,
    MovimientoCuenta,
    FacturaCorporativa,
    PagoCorporativo,
)

# Public
from app.models.public import (
    Comercio,
    EscaneoQr,
)

# Tenant
from app.models.tenant import (
    ControlBase,
    Configuracion,
    Empresa,
    Factura as FacturaTenant,
)

# Audit
from app.models.audit import (
    LogGps,
    AlertaDesvio,
    LogAcciones,
    AlertasVencimiento,
)

# Fleet
from app.models.fleet import (
    Vehiculo,
    ChoferVehiculo,
    GastoVehiculo,
    MantenimientoVehiculo,
    PropietarioVehiculo,
    ContratoVehiculo,
    CategoriaGasto,
    DocumentoVehiculo,
    DocumentoPropietario,
    HistorialChoferVehiculo,
    RelacionPropietarioVehiculo,
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
    ConfiguracionTarifaVehiculo,
    ConfiguracionPasarela,
    QrCobro,
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

# Liquidacion
from app.models.liquidacion import (
    Liquidacion,
    LiquidacionDetalle,
    LiquidacionEstadoHistorial,
    LiquidacionAjuste,
)

# Turno
from app.models.turno import TurnoChofer

# Gasto
from app.models.gasto_turno import GastoTurno

# Foto Viaje
from app.models.foto_viaje import FotoViaje

# Comunicacion (nuevo, Fase 4c)
from app.models.comunicacion import (
    Conversacion,
    EmailEnviado,
    Mensaje,
)

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
    "UsuarioRol",
    "RefreshToken",
    "UsuarioEmpresa",
    "AutorizacionInicio",
    "TurnoEmpleado",
    "AuditoriaEmail",
    "CodigoMetadatos",
    "CodigoVerificacion",
    "PlantillaViaje",
    "PrestadoraTelefonica",

    # Corporate
    "CuentaCorriente",
    "MovimientoCuenta",
    "FacturaCorporativa",
    "PagoCorporativo",

    # Public
    "Comercio",
    "EscaneoQr",

    # Tenant
    "ControlBase",
    "Configuracion",
    "Empresa",
    "FacturaTenant",

    # Audit
    "LogGps",
    "AlertaDesvio",
    "LogAcciones",
    "AlertasVencimiento",

    # Fleet
    "Vehiculo",
    "ChoferVehiculo",
    "GastoVehiculo",
    "MantenimientoVehiculo",
    "PropietarioVehiculo",
    "ContratoVehiculo",
    "CategoriaGasto",
    "DocumentoVehiculo",
    "DocumentoPropietario",
    "HistorialChoferVehiculo",
    "RelacionPropietarioVehiculo",

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
    "ConfiguracionTarifaVehiculo",
    "ConfiguracionPasarela",
    "QrCobro",

    # Trip
    "ViajeSolicitado",
    "HistorialEstadoViaje",
    "Panico",
    "Calificacion",
    "ObjetoOlvidado",
    "TipoVehiculo",

    # Liquidacion
    "Liquidacion",
    "LiquidacionDetalle",
    "LiquidacionEstadoHistorial",
    "LiquidacionAjuste",

    # Turno
    "TurnoChofer",

    # Gasto
    "GastoTurno",

    # Foto Viaje
    "FotoViaje",

    # Comunicacion
    "Conversacion",
    "EmailEnviado",
    "Mensaje",
]