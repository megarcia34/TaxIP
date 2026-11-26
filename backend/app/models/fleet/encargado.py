# app/models/fleet/encargado.py
"""
Encargado o auxiliar autorizado para verificar estado de componentes
e intervenciones. Sin login en MVP (usuario_id nullable para evolucion).

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 6.
Sin cambios funcionales.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Encargado(Base):
    """
    Encargado o auxiliar autorizado para verificar estado de componentes
    e intervenciones. Sin login en MVP (usuario_id nullable para evolucion).
    Tabla: fleet.encargado (m3_038)
    """
    __tablename__ = "encargado"
    __table_args__ = (
        Index("idx_encargado_control_base", "control_base_id"),
        Index("idx_encargado_propietario", "propietario_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=True
    )
    propietario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    documento: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    matricula: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    taller_nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    taller_direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    taller_telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    control_base = relationship("ControlBase", lazy="selectin")
    propietario = relationship("Usuario", foreign_keys=[propietario_id], lazy="selectin")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], lazy="selectin")


__all__ = ["Encargado"]