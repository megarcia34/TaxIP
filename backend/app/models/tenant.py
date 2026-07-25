"""
Multi-tenant (Company/Fleet) Models
Tablas: control_base, configuracion_tenant
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ControlBase(Base):
    """Company/Fleet that operates taxis"""
    __tablename__ = "control_base"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=True)  # ✅ NUEVO
    latitud: Mapped[str] = mapped_column(String(50), nullable=True)    # Cambiado a String por compatibilidad
    longitud: Mapped[str] = mapped_column(String(50), nullable=True)   # Cambiado a String por compatibilidad
    ciudad_id: Mapped[uuid.UUID] = mapped_column(                      # ✅ NUEVO
        UUID(as_uuid=True),
        ForeignKey("geo.ciudad.id", ondelete="SET NULL"),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    fecha_suspension: Mapped[datetime] = mapped_column(DateTime, nullable=True)    # ✅ NUEVO
    motivo_suspension: Mapped[str] = mapped_column(String(255), nullable=True)     # ✅ NUEVO
    suspendido_por: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)  # ✅ NUEVO

    # Relationships
    # NOTA: Las relaciones inversas a modelos de dominio se eliminan 
    # para evitar ciclos de mapeo en SQLAlchemy.
    # Las consultas se hacen explicitamente desde los modelos de dominio.
    
    configuracion: Mapped["Configuracion"] = relationship(
        back_populates="control_base",
        uselist=False,
        lazy="selectin"
    )
    
    # ✅ NUEVA RELACIÓN CON CIUDAD
    ciudad: Mapped["Ciudad"] = relationship(
        "Ciudad",
        lazy="selectin"
    )


class Configuracion(Base):
    """Tenant configuration (currency, timezone, features)"""
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
    moneda_default: Mapped[str] = mapped_column(String(10), default="ARS")
    timezone: Mapped[str] = mapped_column(String(100), default="America/Argentina/Tucuman")
    idioma: Mapped[str] = mapped_column(String(20), default="es")
    habilitar_fidelizacion: Mapped[bool] = mapped_column(Boolean, default=False)
    habilitar_pagos_online: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship(back_populates="configuracion")