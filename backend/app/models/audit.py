"""
Audit/Logging Models
Tablas: log_gps, alerta_desvio, log_acciones (schema: audit)
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Numeric, JSON, Index, Date, UniqueConstraint, text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB

from app.database import Base


class LogGps(Base):
    """
    GPS position history for drivers during trips
    Used to replay routes on web dashboard
    """
    __tablename__ = "log_gps"
    __table_args__ = (
        Index("idx_log_gps_usuario_id", "usuario_id"),
        Index("idx_log_gps_viaje_id", "viaje_id"),
        {"schema": "audit"},
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=True
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)


class AlertaDesvio(Base):
    """
    Route deviation alerts (security feature)
    Triggered when driver deviates from expected route
    """
    __tablename__ = "alerta_desvio"
    __table_args__ = (
        Index("idx_alerta_desvio_viaje_id", "viaje_id"),
        Index("idx_alerta_desvio_created_at", "created_at"),
        {"schema": "audit"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=True
    )
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    distancia_desvio_metros: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ruta_esperada_json: Mapped[str] = mapped_column(Text, nullable=True)
    notificado: Mapped[Optional[bool]] = mapped_column(default=False, nullable=True)
    resuelto: Mapped[Optional[bool]] = mapped_column(default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)


# ============================================================
# MODELO AGREGADO PARA AUDITORÍA FORENSE
# ============================================================

class LogAcciones(Base):
    """
    Audit log for all user actions
    Critical for forensic roles and judicial requirements
    """
    __tablename__ = "log_acciones"
    __table_args__ = (
        Index("idx_log_acciones_usuario", "usuario_id"),
        Index("idx_log_acciones_accion", "accion"),
        Index("idx_log_acciones_created", "created_at"),
         Index("idx_log_acciones_tenant", "control_base_id"),
        {"schema": "audit"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    tabla_afectada: Mapped[str] = mapped_column(String(100), nullable=True)
    registro_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    datos_anteriores: Mapped[dict] = mapped_column(JSONB, nullable=True)
    datos_nuevos: Mapped[dict] = mapped_column(JSONB, nullable=True)
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="SET NULL"),
        nullable=True
    )
    ip_address: Mapped[str] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

class AlertasVencimiento(Base):
    """
    Alertas de vencimiento de documentos.
    Tabla: audit.alertas_vencimiento

    Existente en DB, faltante en ORM (Fase 4c, R11).
    """
    __tablename__ = "alertas_vencimiento"
    __table_args__ = (
        Index("idx_alertas_entidad", "entidad_id", "entidad_tipo"),
        Index("idx_alertas_fecha", "fecha_vencimiento"),
        UniqueConstraint("documento_id", name="uq_alertas_documento"),
        {"schema": "audit"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    entidad_tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    documento_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    nivel: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )