# app/models/fleet/ingreso_turno.py
"""
Ingresos por turno (recaudacion por jornada).

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 10.
Sin cambios funcionales.

Correccion de docstring: el original decia "(NUEVA - aun no existe
en BD)" pero la tabla SI existe en la DB desde R25 (m3_035). Se
actualizo el docstring para reflejar el estado real.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IngresoTurno(Base):
    """
    Income/collection records per shift
    Reemplaza los campos legacy de recaudacion en turno_chofer
    Tabla: fleet.ingreso_turno (existente en DB desde R25 / m3_035)
    """
    __tablename__ = "ingreso_turno"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    turno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id", ondelete="CASCADE"),
        nullable=False
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="SET NULL"),
        nullable=True,
        comment="Viaje asociado, si corresponde"
    )
    tipo_ingreso: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="efectivo | electronico | taximetro | manual | corporativo"
    )
    medio_pago: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
        comment="efectivo | debito | credito | qr | transferencia | billetera"
    )
    origen: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="app",
        comment="app | taximetro | manual | corporativo"
    )
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS", nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    declarado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True,
        comment="Usuario que declaró el ingreso (chofer)"
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="pendiente | aprobado | rechazado | disputado"
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transaccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.transaccion.id", ondelete="SET NULL"),
        nullable=True,
        comment="Referencia a transacción electrónica si aplica"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    turno: Mapped["TurnoChofer"] = relationship("TurnoChofer", lazy="selectin")
    viaje: Mapped["ViajeSolicitado"] = relationship("ViajeSolicitado", lazy="selectin")
    declarante: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[declarado_por], lazy="selectin")
    transaccion: Mapped["Transaccion"] = relationship("Transaccion", lazy="selectin")


__all__ = ["IngresoTurno"]