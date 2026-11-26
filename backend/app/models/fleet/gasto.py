# app/models/fleet/gasto.py
"""
Categorias y gastos de vehiculos.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 5.
Sin cambios funcionales (solo correccion de encoding en
docstrings y comentarios de seccion: ASCII puro segun N10).
"""
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# CATEGORIAS DE GASTOS
# ============================================================

class CategoriaGasto(Base):
    """
    Categorias y subcategorias de gastos para vehiculos y turnos.
    """
    __tablename__ = "categoria_gasto"
    __table_args__ = (
        UniqueConstraint('control_base_id', 'nombre', name='uq_categoria_gasto_tenant_nombre'),
        Index("ix_categoria_gasto_control_base_id", "control_base_id"),
        {"schema": "fleet"},
    )

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
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subcategorias: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb")
    )
    aplica_a: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb")
    )
    tratamiento_economico: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="configurable"
    )
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False
    )

    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    gastos_vehiculo = relationship(
        "GastoVehiculo",
        foreign_keys="GastoVehiculo.categoria_id",
        lazy="selectin"
    )
    gastos_turno = relationship(
        "GastoTurno",
        foreign_keys="GastoTurno.categoria_id",
        lazy="selectin"
    )


# ============================================================
# GASTO VEHICULO
# ============================================================

class GastoVehiculo(Base):
    """Vehicle expenses. Coincide con fleet.gasto_vehiculo."""
    __tablename__ = "gasto_vehiculo"
    __table_args__ = (
        Index("ix_gasto_vehiculo_categoria_id", "categoria_id"),
        Index("ix_gasto_vehiculo_km_registro", "km_registro"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )

    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.categoria_gasto.id", ondelete="SET NULL"),
        nullable=True
    )
    subcategoria: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    km_registro: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    tipo_gasto: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    moneda: Mapped[Optional[str]] = mapped_column(String(10), server_default="ARS", nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comprobante_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_gasto: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("now()"), nullable=True)

    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="gastos"
    )
    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )
    categoria = relationship(
        "CategoriaGasto",
        foreign_keys=[categoria_id],
        lazy="selectin"
    )


__all__ = ["CategoriaGasto", "GastoVehiculo"]