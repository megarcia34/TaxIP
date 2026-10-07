"""
Rentabilidad Models
Tablas: analisis_medios_pago, rentabilidad_diaria_vehiculo,
        rentabilidad_mensual_vehiculo (schema: rentabilidad)

Existente en DB, faltante en ORM (Fase 4c, R11).
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, DateTime, Date, ForeignKey, Integer, Numeric, Index,
    UniqueConstraint, CheckConstraint, text, func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AnalisisMediosPago(Base):
    """Analisis mensual de medios de pago por vehiculo."""
    __tablename__ = "analisis_medios_pago"
    __table_args__ = (
        Index("idx_analisis_periodo", "anio", "mes"),
        Index("idx_analisis_vehiculo_periodo", "vehiculo_id", "anio", "mes"),
        {"schema": "rentabilidad"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=True,
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    medio_pago: Mapped[str] = mapped_column(String(20), nullable=False)
    total_viajes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default=text("0"),
    )
    total_ingresos: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    comision_aplicada: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    costo_comisiones: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )


class RentabilidadDiariaVehiculo(Base):
    """Rentabilidad diaria por vehiculo."""
    __tablename__ = "rentabilidad_diaria_vehiculo"
    __table_args__ = (
        Index("idx_rentabilidad_fecha", "fecha"),
        Index("idx_rentabilidad_vehiculo_fecha", "vehiculo_id", "fecha"),
        {"schema": "rentabilidad"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    total_viajes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default=text("0"),
    )
    ingresos_brutos: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    comisiones_bancarias: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    costos_variables: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    costos_fijos: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    canon_taxip: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    porcentaje_taxip: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    utilidad_neta: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    margen: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )


class RentabilidadMensualVehiculo(Base):
    """Rentabilidad mensual por vehiculo."""
    __tablename__ = "rentabilidad_mensual_vehiculo"
    __table_args__ = (
        Index("idx_rentabilidad_mensual_periodo", "anio", "mes"),
        Index("idx_rentabilidad_mensual_vehiculo", "vehiculo_id", "anio", "mes"),
        UniqueConstraint(
            "vehiculo_id", "anio", "mes",
            name="uq_rentabilidad_mensual_vehiculo_vehiculo_id",
        ),
        CheckConstraint(
            "mes >= 1 AND mes <= 12",
            name="chk_mes_rango",
        ),
        {"schema": "rentabilidad"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False,
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    total_viajes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default=text("0"),
    )
    ingresos_brutos: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    comisiones_bancarias: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    costos_variables: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    costos_fijos: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    canon_taxip: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    porcentaje_taxip: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    utilidad_neta: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    margen: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
        server_default=text("0"),
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )