"""
Payment and Wallet Models for TaxIP
Tablas: metodo_pago, billetera, transaccion, configuracion_tarifa
"""
import uuid
from datetime import datetime, time
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Integer, DECIMAL, Text, Time
)
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
        nullable=False,
        index=True
    )
    saldo: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
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
    billetera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.billetera.id", ondelete="CASCADE"),
        nullable=False
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
    monto: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    saldo_despues: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, default='COMPLETADO')
    
    # ✅ ESTA ES LA COLUMNA REAL EN LA BD
    external_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    billetera: Mapped["Billetera"] = relationship(back_populates="transacciones")
    viaje: Mapped[Optional["ViajeSolicitado"]] = relationship(lazy="selectin")
    metodo_pago: Mapped[Optional["MetodoPago"]] = relationship(back_populates="transacciones")


class ConfiguracionTarifa(Base):
    """Fare configuration per tenant"""
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
        nullable=False,
        index=True
    )
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tarifa_base: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    precio_por_km: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    precio_por_minuto: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    recargo_nocturno: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), default=1.0)
    recargo_feriado: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), default=1.0)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    
    # Nuevos campos para soporte multi-tenant
    modo_calculo: Mapped[Optional[str]] = mapped_column(
        String(20), 
        default='por_km',
        doc="Modo de cálculo: ficha_argentina, por_km, por_minuto, mixto"
    )
    distancia_por_ficha: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2), 
        default=100,
        doc="Distancia en metros por cada ficha"
    )
    precio_por_ficha: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        doc="Precio por cada ficha"
    )
    precio_por_minuto_espera: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        doc="Precio por minuto de espera"
    )
    recargo_domingo: Mapped[Optional[float]] = mapped_column(
        DECIMAL(3, 2), 
        default=1.0,
        doc="Factor de recargo para domingos"
    )
    hora_inicio_nocturno: Mapped[Optional[time]] = mapped_column(
        Time, 
        default=time(22, 0),
        doc="Hora de inicio del recargo nocturno"
    )
    hora_fin_nocturno: Mapped[Optional[time]] = mapped_column(
        Time, 
        default=time(6, 0),
        doc="Hora de fin del recargo nocturno"
    )
    moneda: Mapped[Optional[str]] = mapped_column(
        String(3), 
        default='ARS',
        doc="Moneda de la tarifa"
    )
    descripcion: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        doc="Descripción adicional de la configuración"
    )

    # Relationships
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )