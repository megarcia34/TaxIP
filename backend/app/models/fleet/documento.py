# app/models/fleet/documento.py
"""
Documentos de vehiculos, propietarios y notificaciones de vencimiento.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 3.
Sin cambios funcionales (solo correccion de encoding en comentarios
y docstrings: ASCII puro segun N10).
"""
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# DOCUMENTOS (Fase 7) - ALINEADOS CON LA BASE DE DATOS
# ============================================================

class DocumentoVehiculo(Base):
    """Documentos del vehiculo (seguro, VTV, patente, cedula, etc.)"""
    __tablename__ = "documento_vehiculo"
    __table_args__ = (
        Index("idx_documento_vehiculo_fecha_vencimiento", "fecha_vencimiento"),
        Index("idx_documento_vehiculo_vehiculo_id", "vehiculo_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_archivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # CAMPOS AGREGADOS
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    notificar_dias: Mapped[int] = mapped_column(Integer, server_default="30")

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 16 columnas faltantes (D-0404 a D-0419).
    # ============================================================
    chasis: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    dominio: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    marca: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    motor: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    seguro_cobertura: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_compania: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    seguro_fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    seguro_poliza: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seguro_suma_asegurada: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seguro_tomador: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_vehiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tipo_vehiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uso: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    vtv_fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relaciones
    vehiculo = relationship("Vehiculo", foreign_keys=[vehiculo_id], lazy="selectin")


class DocumentoPropietario(Base):
    """Documentos personales del propietario (DNI, Licencia, CUIT, etc.)"""
    __tablename__ = "documento_propietario"
    __table_args__ = (
        Index("idx_documento_propietario_propietario_id", "propietario_id"),
        Index(
            "uq_documento_propietario_tipo",
            "propietario_id", "tipo_documento",
            unique=True,
        ),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_archivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # ============================================================
    # COLUMNA AGREGADA EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 1 columna faltante (D-0766).
    # ============================================================
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )

    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )


# ============================================================
# MODELO NOTIFICACION_VENCIMIENTO
# ============================================================

class NotificacionVencimiento(Base):
    """
    Expiration notifications for documents
    Tabla: fleet.notificacion_vencimiento
    """
    __tablename__ = "notificacion_vencimiento"
    __table_args__ = (
        Index(
            "idx_notificacion_email_pendiente",
            "email_enviado",
            "fecha_vencimiento",
            postgresql_where=text("email_enviado = false"),
        ),
        Index("idx_notificacion_nivel", "nivel"),
        Index("idx_notificacion_propietario", "propietario_id"),
        Index("idx_notificacion_documento", "documento_id"),
        Index("idx_notificacion_fecha_vencimiento", "fecha_vencimiento"),
        Index(
            "uq_notificacion_documento_nivel",
            "documento_id", "nivel",
            unique=True,
        ),
        CheckConstraint(
            "nivel IN ('vencido', 'critico', 'urgente', 'preventivo', 'vigente')",
            name="chk_notificacion_nivel_valido"
        ),
        CheckConstraint(
            "entidad_tipo IN ('propietario', 'vehiculo', 'chofer')",
            name="chk_notificacion_entidad_ti_fd97"
        ),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    entidad_tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="propietario | vehiculo | chofer"
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="vencido | critico | urgente | preventivo | vigente"
    )
    dias_restantes: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(Date, nullable=False)
    email_enviado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    email_enviado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sms_enviado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    sms_enviado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    propietario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


__all__ = ["DocumentoVehiculo", "DocumentoPropietario", "NotificacionVencimiento"]