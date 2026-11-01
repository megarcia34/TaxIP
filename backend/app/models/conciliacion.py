"""
Modelos de Conciliacion de Turnos
Tablas: conciliacion_diferencia, conciliacion_disputa (schema: fleet)

Creadas en m3_028 (R24).
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Numeric, Text,
    Index, CheckConstraint, text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class ConciliacionDiferencia(Base):
    """
    Diferencias detectadas durante la conciliacion de un turno.
    Tabla: fleet.conciliacion_diferencia
    """
    __tablename__ = "conciliacion_diferencia"
    __table_args__ = (
        Index("ix_conciliacion_diferencia_turno_estado", "turno_id", "estado"),
        CheckConstraint(
            "tipo IN ('DEUDA_CHOFER', 'DEUDA_PROPIETARIO', 'NEUTRA')",
            name="tipo",
        ),
        CheckConstraint(
            "estado IN ('PENDIENTE', 'SALDADA')",
            name="estado",
        ),
        {"schema": "fleet"},
    )

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    turno_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id"),
        nullable=False,
    )
    liquidacion_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fleet.liquidacion.id"),
        nullable=True,
    )
    tipo = Column(
        String(30),
        nullable=False,
        comment="DEUDA_CHOFER: el chofer debe al propietario. DEUDA_PROPIETARIO: el propietario debe al chofer. NEUTRA: saldada automáticamente",
    )
    concepto = Column(String(50), nullable=False)
    monto = Column(Numeric, nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, server_default=text("'PENDIENTE'"))
    saldada_en = Column(DateTime, nullable=True)
    saldada_por = Column(
        PGUUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relaciones (usar string para evitar import circular)
    turno = relationship("TurnoChofer", lazy="selectin")
    liquidacion = relationship("Liquidacion", lazy="selectin")
    usuario_saldada = relationship(
        "Usuario",
        foreign_keys=[saldada_por],
        lazy="selectin",
    )


class ConciliacionDisputa(Base):
    """
    Disputas abiertas por chofer o propietario sobre una conciliacion.
    Tabla: fleet.conciliacion_disputa
    """
    __tablename__ = "conciliacion_disputa"
    __table_args__ = (
        Index("ix_conciliacion_disputa_turno_estado", "turno_id", "estado"),
        CheckConstraint(
            "estado IN ('ABIERTA', 'EN_TENANT', 'EN_PLATAFORMA', 'RESUELTA', 'CERRADA_AUTOMATICA')",
            name="estado",
        ),
        {"schema": "fleet"},
    )

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    turno_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id"),
        nullable=False,
    )
    abierta_por = Column(
        PGUUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False,
    )
    motivo = Column(Text, nullable=False)
    estado = Column(String(30), nullable=False, server_default=text("'ABIERTA'"))
    resolucion = Column(Text, nullable=True)
    resuelta_por = Column(
        PGUUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
    )
    resuelta_en = Column(DateTime, nullable=True)
    plazo_tenant = Column(DateTime, nullable=True)
    plazo_plataforma = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relaciones
    turno = relationship("TurnoChofer", lazy="selectin")
    usuario_abierta = relationship(
        "Usuario",
        foreign_keys=[abierta_por],
        lazy="selectin",
    )
    usuario_resuelta = relationship(
        "Usuario",
        foreign_keys=[resuelta_por],
        lazy="selectin",
    )