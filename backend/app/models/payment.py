"""
Payment and Wallet Models for TaxIP
Tablas: metodo_pago, billetera, transaccion, configuracion_tarifa, configuracion_tarifa_vehiculo
"""
import uuid
from datetime import datetime, time
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, Date, Time, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class MetodoPago(Base):
    """Payment methods"""
    __tablename__ = "metodo_pago"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Relationships
    transacciones: Mapped[list["Transaccion"]] = relationship(
        back_populates="metodo_pago",
        lazy="selectin"
    )


class Billetera(Base):
    """Digital wallet for users"""
    __tablename__ = "billetera"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    saldo: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), default=0, nullable=True)
    moneda: Mapped[Optional[str]] = mapped_column(String(10), default="ARS", nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")
    transacciones: Mapped[list["Transaccion"]] = relationship(
        back_populates="billetera",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class Transaccion(Base):
    """Transaction records"""
    __tablename__ = "transaccion"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    billetera_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.billetera.id", ondelete="CASCADE"),
        nullable=True
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="SET NULL"),
        nullable=True
    )
    metodo_pago_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.metodo_pago.id"),
        nullable=True
    )
    tipo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    monto: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    saldo_despues: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, default='COMPLETADO')
    external_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    billetera: Mapped["Billetera"] = relationship(back_populates="transacciones")
    viaje: Mapped[Optional["ViajeSolicitado"]] = relationship(lazy="selectin")
    metodo_pago: Mapped[Optional["MetodoPago"]] = relationship(back_populates="transacciones")


class ConfiguracionTarifa(Base):
    """
    Fare configuration per tenant - Motor Unificado TaxIP 2.1

    Campos legacy (deprecados):
    - modo_calculo: el motor unificado no usa este campo
    - distancia_por_ficha: reemplazado por metros_por_ficha
    - precio_por_minuto_espera: reemplazado por seg_por_ficha_espera
    - precio_por_km, precio_por_minuto: reemplazados por precio_por_ficha + configuración
    """
    __tablename__ = "configuracion_tarifa"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ============================================================
    # CAMPOS LEGACY (DEPRECADOS - Mantener por compatibilidad)
    # ============================================================
    tarifa_base: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        default=0,
        doc="Bajada de bandera"
    )
    precio_por_km: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        default=0,
        doc="DEPRECATED - Usar precio_por_ficha con metros_por_ficha=1000"
    )
    precio_por_minuto: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        default=0,
        doc="DEPRECATED - Usar precio_por_ficha con metros_por_ficha=0"
    )
    modo_calculo: Mapped[Optional[str]] = mapped_column(
        String(20),
        default='por_km',
        doc="DEPRECATED - Motor unificado no usa este campo"
    )
    distancia_por_ficha: Mapped[Optional[float]] = mapped_column(
        Numeric,
        default=100,
        doc="DEPRECATED - Usar metros_por_ficha",
        comment="Distancia en metros por cada ficha (ej: 100m)"
    )
    precio_por_ficha: Mapped[Optional[float]] = mapped_column(
        Numeric,
        default=0,
        doc="Precio por cada ficha",
        comment="Precio por cada ficha"
    )
    precio_por_minuto_espera: Mapped[Optional[float]] = mapped_column(
        Numeric,
        default=0,
        doc="DEPRECATED - Usar seg_por_ficha_espera",
        comment="Precio por minuto de espera"
    )

    # Recargos
    recargo_nocturno: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        default=1.0,
        doc="Factor de recargo nocturno (1.0 = sin recargo)"
    )
    recargo_feriado: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        default=1.0,
        doc="Factor de recargo feriado (1.0 = sin recargo)"
    )
    recargo_domingo: Mapped[Optional[float]] = mapped_column(
        Numeric,
        default=1.0,
        doc="Factor de recargo para domingos (1.0 = sin recargo)",
        comment="Factor de recargo para domingos (1.0 = sin recargo)"
    )
    hora_inicio_nocturno: Mapped[Optional[time]] = mapped_column(
        Time,
        default=time(22, 0),
        doc="Hora de inicio del recargo nocturno",
        comment="Hora de inicio del recargo nocturno (ej: 22:00)"
    )
    hora_fin_nocturno: Mapped[Optional[time]] = mapped_column(
        Time,
        default=time(6, 0),
        doc="Hora de fin del recargo nocturno",
        comment="Hora de fin del recargo nocturno (ej: 06:00)"
    )

    # Metadata
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    moneda: Mapped[Optional[str]] = mapped_column(
        String(3),
        default='ARS',
        doc="Moneda de la tarifa",
        comment="Moneda de la tarifa (ARS, USD, etc.)"
    )
    descripcion: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Descripción adicional de la configuración"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

    # ============================================================
    # NUEVAS COLUMNAS - MOTOR UNIFICADO TAXIP 2.1
    # ============================================================
    metros_por_ficha: Mapped[float] = mapped_column(
        Numeric,
        default=100,
        nullable=False,
        doc="Metros que equivalen a 1 ficha. 0 = desactiva fichas por distancia"
    )
    seg_por_ficha_espera: Mapped[float] = mapped_column(
        Numeric,
        default=60,
        nullable=False,
        doc="Segundos detenido = 1 ficha. 0 = desactiva fichas por tiempo"
    )
    velocidad_referencia_kmh: Mapped[float] = mapped_column(
        Numeric,
        default=30,
        nullable=False,
        doc="Velocidad urbana típica para estimar tiempo detenido en cotización"
    )
    velocidad_umbral_kmh: Mapped[float] = mapped_column(
        Numeric,
        default=15,
        nullable=False,
        doc="Velocidad por debajo de la cual se considera 'detenido' (solo liquidación futura)"
    )
    modo_cobro_tiempo: Mapped[str] = mapped_column(
        String,
        default='detenido',
        nullable=False,
        doc="'detenido' = solo tiempo detenido estimado; 'total' = todo el tiempo del viaje"
    )
    redondeo_comercial: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        doc="Múltiplo de redondeo comercial. 0 = sin redondeo"
    )

    # Relationships
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    factores_vehiculo: Mapped[list["ConfiguracionTarifaVehiculo"]] = relationship(
        "ConfiguracionTarifaVehiculo",
        back_populates="configuracion_tarifa",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class ConfiguracionTarifaVehiculo(Base):
    """
    Factores por tipo de vehículo para cada configuración de tarifa.
    Tabla: payment.configuracion_tarifa_vehiculo

    Permite definir factores de precio específicos por tipo de vehículo
    para cada configuración de tarifa del tenant.

    Ejemplo:
    - standard: factor_precio = 1.0 (sin cambio)
    - premium: factor_precio = 1.30 (+30%)
    - van: factor_precio = 1.40 (+40%)
    - minivan: factor_precio = 1.50 (+50%)
    """
    __tablename__ = "configuracion_tarifa_vehiculo"
    __table_args__ = (
        Index(
            "uq_config_tarifa_vehiculo",
            "configuracion_tarifa_id", "tipo_vehiculo_id",
            unique=True,
        ),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    configuracion_tarifa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.configuracion_tarifa.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_vehiculo_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("trip.tipo_vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    factor_precio: Mapped[float] = mapped_column(
        Numeric,
        default=1.0,
        nullable=False,
        doc="Multiplicador directo del precio (1.0 = sin cambio, 1.30 = +30%)"
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False
    )

    # Relationships
    configuracion_tarifa: Mapped["ConfiguracionTarifa"] = relationship(
        back_populates="factores_vehiculo"
    )
    tipo_vehiculo: Mapped["TipoVehiculo"] = relationship("TipoVehiculo", lazy="selectin")

    def __repr__(self):
        return f"<ConfiguracionTarifaVehiculo {self.configuracion_tarifa_id} - {self.tipo_vehiculo_id} = {self.factor_precio}>"


# ============================================================
# MODELOS FACTURA_EMPRESA Y PAGO_EMPRESA
# ============================================================

class FacturaEmpresa(Base):
    """
    Corporate invoices
    Tabla: payment.factura_empresa
    """
    __tablename__ = "factura_empresa"
    __table_args__ = {"schema": "payment"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id"),
        nullable=False
    )
    periodo: Mapped[datetime] = mapped_column(Date, nullable=False)
    total: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    descuento: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0.0, nullable=True)
    total_final: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(20), default="pendiente", nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    pagada_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    pagos: Mapped[list["PagoEmpresa"]] = relationship(
        "PagoEmpresa",
        back_populates="factura",
        lazy="selectin"
    )


class PagoEmpresa(Base):
    """
    Corporate payments
    Tabla: payment.pago_empresa
    """
    __tablename__ = "pago_empresa"
    __table_args__ = (
        Index("idx_pago_empresa_estado", "estado"),
        Index("idx_pago_empresa_fecha", "fecha_pago"),
        Index("idx_pago_empresa_empresa", "empresa_id"),
        Index("idx_pago_empresa_factura", "factura_id"),
        {"schema": "payment"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id", ondelete="CASCADE"),
        nullable=False
    )
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    referencia: Mapped[str] = mapped_column(String(100), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(20), default="pendiente", nullable=True)
    comprobante_url: Mapped[str] = mapped_column(Text, nullable=True)
    factura_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.factura_empresa.id"),
        nullable=True
    )
    observaciones: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_pago: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    confirmado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    confirmado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    factura: Mapped["FacturaEmpresa"] = relationship("FacturaEmpresa", back_populates="pagos", lazy="selectin")
    confirmado_por_usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")