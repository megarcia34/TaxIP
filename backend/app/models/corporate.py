"""
Corporate Module Models
Tablas: cuenta_corriente, movimiento_cuenta, factura_corporativa
"""

import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, Date, Enum as SQLEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class CuentaCorriente(Base):
    """
    Corporate current account for companies
    Tabla: corporate.cuenta_corriente
    """
    __tablename__ = "cuenta_corriente"
    __table_args__ = (
        Index("idx_cuenta_corriente_empresa", "empresa_id"),
        {"schema": "corporate"},
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    saldo_disponible: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    limite_credito: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS", nullable=False)
    ultima_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 10 columnas faltantes (D-0197 a D-0206).
    # ============================================================
    dia_cierre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fecha_apertura: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )
    fecha_proximo_vencimiento: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    fecha_ultimo_pago: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    periodo_facturacion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    propietario_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    responsable_cobro: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    titular_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    titular_tipo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    
    

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    movimientos: Mapped[list["MovimientoCuenta"]] = relationship(
        "MovimientoCuenta",
        back_populates="cuenta",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class MovimientoCuenta(Base):
    """
    Account movements (debits and credits)
    Tabla: corporate.movimiento_cuenta
    """
    __tablename__ = "movimiento_cuenta"
    __table_args__ = (
        Index("idx_movimiento_cuenta_cuenta", "cuenta_id"),
        Index("idx_movimiento_cuenta_fecha", "created_at"),
        {"schema": "corporate"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    cuenta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corporate.cuenta_corriente.id", ondelete="CASCADE"),
        nullable=False
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_movimiento: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="credito | debito | ajuste"
    )
    concepto: Mapped[str] = mapped_column(String(200), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saldo_anterior: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saldo_nuevo: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 6 columnas faltantes (D-0256 a D-0261).
    # ============================================================
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    metodo_pago: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    cuenta: Mapped["CuentaCorriente"] = relationship("CuentaCorriente", back_populates="movimientos")
    viaje: Mapped["ViajeSolicitado"] = relationship("ViajeSolicitado", lazy="selectin")


class FacturaCorporativa(Base):
    """
    Corporate invoices
    Tabla: corporate.factura_corporativa
    """
    __tablename__ = "factura_corporativa"
    __table_args__ = (
        Index("idx_factura_corporativa_empresa", "empresa_id"),
        Index("idx_factura_corporativa_fecha", "fecha_emision"),
        Index("idx_factura_corporativa_estado", "estado"),
        {"schema": "corporate"},
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
    numero_factura: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    periodo_desde: Mapped[datetime] = mapped_column(Date, nullable=False)
    periodo_hasta: Mapped[datetime] = mapped_column(Date, nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    descuento: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    iva: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="pendiente | pagada | vencida | cancelada"
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 4 columnas faltantes (D-0226 a D-0229).
    # ============================================================
    saldo_anterior: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    saldo_final: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_cargos: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_pagos: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    pagos: Mapped[list["PagoCorporativo"]] = relationship(
        "PagoCorporativo",
        back_populates="factura",
        lazy="selectin"
    )


class PagoCorporativo(Base):
    """
    Corporate payments
    Tabla: corporate.pago_corporativo
    """
    __tablename__ = "pago_corporativo"
    __table_args__ = (
        Index("idx_pago_corporativo_factura", "factura_id"),
        Index("idx_pago_corporativo_fecha", "fecha_pago"),
        {"schema": "corporate"},
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
    factura_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corporate.factura_corporativa.id", ondelete="SET NULL"),
        nullable=True
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    comprobante_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="pendiente | confirmado | rechazado"
    )
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    confirmado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    confirmado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ============================================================
    # COLUMNA AGREGADA EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 1 columna faltante (D-0280). Con FK a corporate.movimiento_cuenta.
    # ============================================================
    movimiento_cc_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corporate.movimiento_cuenta.id"),
        nullable=True,
    )

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    factura: Mapped["FacturaCorporativa"] = relationship("FacturaCorporativa", back_populates="pagos", lazy="selectin")
    confirmado_por_usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")