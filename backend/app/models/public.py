"""
Public Models (no schema)
Tablas: comercio, escaneo_qr
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Comercio(Base):
    """
    Adhered businesses for QR-based taxi requests
    Un comercio adherido genera un QR para que los clientes pidan taxis sin app.
    """
    __tablename__ = "comercio"
    __table_args__ = (
        Index("idx_comercio_codigo_qr", "codigo_qr"),
    )

    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rubro: Mapped[str] = mapped_column(String(50), nullable=True)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    codigo_qr: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email_contacto: Mapped[str] = mapped_column(String(200), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id"),
        nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    escaneos: Mapped[list["EscaneoQr"]] = relationship(
        "EscaneoQr",
        back_populates="comercio",
        lazy="selectin"
    )


class EscaneoQr(Base):
    """
    QR scan audit log
    Registra cada escaneo de QR para trazabilidad, seguridad y estadísticas.
    """
    __tablename__ = "escaneo_qr"
    __table_args__ = (
        Index("idx_escaneo_created", "created_at"),
        Index("idx_escaneo_qr_contrato", "contrato_id"),
        Index("idx_escaneo_comercio", "comercio_id"),
        Index("idx_escaneo_qr_tipo", "tipo_qr"),
        Index("idx_escaneo_qr_autorizacion", "autorizacion_id"),
    )

    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    comercio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comercio.id"),
        nullable=True,
        comment="ID del comercio escaneado. NULL para QRs de tipo OPERATIVO o VEHICULO."
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id"),
        nullable=True
    )
    contrato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.contrato_vehiculo.id", ondelete="SET NULL"),
        nullable=True
    )
    autorizacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.autorizacion_inicio.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_qr: Mapped[Optional[str]] = mapped_column(
        String(20),
        default="OPERATIVO",
        nullable=True,
        comment="OPERATIVO | COMERCIO | VEHICULO | OTRO"
    )
    resultado: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="EXITO | RECHAZADO | EXPIRADO | ERROR"
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    comercio: Mapped["Comercio"] = relationship("Comercio", back_populates="escaneos", lazy="selectin")
    viaje: Mapped["ViajeSolicitado"] = relationship("ViajeSolicitado", lazy="selectin")
    contrato: Mapped["ContratoVehiculo"] = relationship("ContratoVehiculo", lazy="selectin")
    autorizacion: Mapped["AutorizacionInicio"] = relationship("AutorizacionInicio", lazy="selectin")