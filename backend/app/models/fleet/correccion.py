# app/models/fleet/correccion.py
"""
Correcciones manuales de kilometraje con trazabilidad.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 7.
Sin cambios funcionales.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# MODELOS DE SOPORTE (R25 / m3_039)
# ============================================================

class KilometrajeCorreccion(Base):
    """
    Correcciones manuales de kilometraje con trazabilidad.
    El turno original se marca km_sospechoso=true.
    Tabla: fleet.kilometraje_correccion (m3_039)
    """
    __tablename__ = "kilometraje_correccion"
    __table_args__ = (
        Index("idx_kilometraje_correccion_control_base", "control_base_id"),
        Index("idx_kilometraje_correccion_fecha", "created_at"),
        Index("idx_kilometraje_correccion_vehiculo", "vehiculo_id"),
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
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    turno_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id", ondelete="SET NULL"),
        nullable=True
    )
    km_anterior: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    km_nuevo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    control_base = relationship("ControlBase", lazy="selectin")
    vehiculo = relationship("Vehiculo", lazy="selectin")
    turno = relationship("TurnoChofer", lazy="selectin")
    autor = relationship("Usuario", foreign_keys=[autor_id], lazy="selectin")


__all__ = ["KilometrajeCorreccion"]