# app/models/fleet/chofer.py
"""
Choferes asignados a vehiculos, historial de asignaciones y documentos.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 9.
Sin cambios funcionales.

NOTA: los comment= de tabla y columnas se mantienen tal cual
(con tildes donde corresponde) porque diff.py los compara contra
la DB. Solo se corrigieron docstrings y comentarios de seccion
(ASCII puro segun N10).
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
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from app.database import Base


class ChoferVehiculo(Base):
    """Active driver-vehicle assignment with real-time GPS"""
    __tablename__ = "chofer_vehiculo"
    __table_args__ = (
        CheckConstraint(
            "estado_aprobacion IN ('pendiente', 'en_revision', 'aprobado', 'rechazado')",
            name="chk_estado_aprobacion"
        ),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=True
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=True)
    ubicacion: Mapped[Geography] = mapped_column(
        Geography(geometry_type='Point', srid=4326),
        nullable=True,
    )
    estado_laboral: Mapped[Optional[str]] = mapped_column(String(20), default='libre', nullable=True)
    estado_panico: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    ultima_conexion: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    calificacion_promedio: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), default=5.0, nullable=True)
    total_calificaciones: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    estado_aprobacion: Mapped[str] = mapped_column(
        String(20), nullable=True, server_default='pendiente'
    )
    total_viajes: Mapped[int] = mapped_column(
        Integer, nullable=True, server_default='0'
    )

    # ============================================
    # RECHAZO
    # ============================================
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Motivo del rechazo de la postulacion del chofer"
    )
    rechazado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    rechazado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )

    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        back_populates="chofer_vehiculos"
    )
    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="choferes_asignaciones"
    )
    viajes = relationship(
        "ViajeSolicitado",
        foreign_keys="ViajeSolicitado.chofer_vehiculo_id",
        back_populates="chofer_vehiculo",
        lazy="selectin"
    )


class HistorialChoferVehiculo(Base):
    """
    Historial de asignaciones chofer-vehiculo.
    Tabla: fleet.historial_chofer_vehiculo

    Existente en DB, faltante en ORM (Fase 4c, R11).
    """
    __tablename__ = "historial_chofer_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id"),
        nullable=True,
    )
    chofer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
    )
    fecha_inicio: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)


class DocumentosChofer(Base):
    """
    Driver documents (license, insurance, background checks)
    Tabla: fleet.documentos_chofer
    """
    __tablename__ = "documentos_chofer"
    __table_args__ = (
        Index(
            "documentos_chofer_usuario_id_tipo_documento_key",
            "usuario_id",
            "tipo_documento",
            unique=True,
        ),
        Index("idx_documentos_chofer_usuario", "usuario_id"),
        Index("idx_documentos_chofer_tipo", "tipo_documento"),
        {
            "schema": "fleet",
            "comment": "Documentos subidos por choferes para aprobacion municipal",
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_documento: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Valores: licencia, seguro, antecedentes"
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="URL del documento almacenado (local, S3, etc)"
    )
    numero: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Numero del documento (DNI, licencia, etc). Opcional."
    )
    subido_en: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    fecha_vencimiento: Mapped[datetime] = mapped_column(Date, nullable=True)
    notificar_dias: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


__all__ = ["ChoferVehiculo", "HistorialChoferVehiculo", "DocumentosChofer"]