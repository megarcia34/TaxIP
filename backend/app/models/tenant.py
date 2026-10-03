"""
Multi-tenant (Company/Fleet) Models
Tablas: control_base, configuracion_tenant, empresa
"""

import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, DECIMAL, Numeric, Text, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ControlBase(Base):
    """Operating company (tenant)"""
    __tablename__ = "control_base"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    ciudad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("geo.ciudad.id", ondelete="SET NULL"),
        nullable=True
    )
    direccion: Mapped[str] = mapped_column(String(255), nullable=True)
    latitud: Mapped[str] = mapped_column(String(50), nullable=True)
    longitud: Mapped[str] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_suspension: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    motivo_suspension: Mapped[str] = mapped_column(String(255), nullable=True)
    suspendido_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    ciudad: Mapped["Ciudad"] = relationship("Ciudad", lazy="selectin")
    configuracion: Mapped["Configuracion"] = relationship(
        "Configuracion",
        back_populates="control_base",
        uselist=False,
        lazy="selectin"
    )


class Configuracion(Base):
    """Tenant configuration"""
    __tablename__ = "configuracion_tenant"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    moneda_default: Mapped[str] = mapped_column(String(10), default="ARS", nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), default="America/Argentina/Tucuman", nullable=False)
    idioma: Mapped[str] = mapped_column(String(20), default="es", nullable=False)
    habilitar_fidelizacion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    habilitar_pagos_online: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship("ControlBase", back_populates="configuracion")


class Empresa(Base):
    """Corporate companies"""
    __tablename__ = "empresa"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="hotel", nullable=True)
    email_facturacion: Mapped[str] = mapped_column(String(200), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    direccion: Mapped[str] = mapped_column(Text, nullable=True)
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=True)
    tarifa_preferencial: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    condiciones_pago: Mapped[str] = mapped_column(String(20), default="mensual", nullable=True)
    limite_credito: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=True)
    contacto_nombre: Mapped[str] = mapped_column(String(200), nullable=True)
    contacto_telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    contacto_email: Mapped[str] = mapped_column(String(200), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    fecha_suspension: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    motivo_suspension: Mapped[str] = mapped_column(Text, nullable=True)
    suspendido_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")

# ============================================================
# MODELO FACTURA - FACTURACIÓN DE TENANT
# ============================================================

class Factura(Base):
    """
    Tenant invoices (canon mensual por vehículo)
    Tabla: tenant.factura
    """
    __tablename__ = "factura"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id"),
        nullable=False
    )
    periodo: Mapped[datetime] = mapped_column(Date, nullable=False)
    vehiculos_activos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    canon_total: Mapped[float] = mapped_column(DECIMAL, default=0, nullable=False)
    porcentaje_plataforma: Mapped[float] = mapped_column(DECIMAL, default=15, nullable=False)
    total_a_pagar: Mapped[float] = mapped_column(DECIMAL, default=0, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    pagada_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    pagada_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )
    numero_factura: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    observaciones: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    pagado_por_usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")