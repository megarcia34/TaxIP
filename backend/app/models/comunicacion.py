"""
Communication Models
Tablas: conversacion, email_enviado, mensaje (schema: comunicacion)

Existente en DB, faltante en ORM (Fase 4c, R11).
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, Integer,
    Index, UniqueConstraint, text, func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Conversacion(Base):
    """Conversacion 1-a-1 entre dos usuarios."""
    __tablename__ = "conversacion"
    __table_args__ = (
        UniqueConstraint(
            "participante_1", "participante_2",
            name="uq_participantes_unicos",
        ),
        {"schema": "comunicacion"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    participante_1: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    participante_2: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    ultimo_mensaje: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ultimo_mensaje_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )


class EmailEnviado(Base):
    """Registro de emails enviados."""
    __tablename__ = "email_enviado"
    __table_args__ = {"schema": "comunicacion"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True,
    )
    destinatario_email: Mapped[str] = mapped_column(String, nullable=False)
    asunto: Mapped[str] = mapped_column(String, nullable=False)
    template_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estado: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'pendiente'"),
    )
    error_mensaje: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    enviado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )


class Mensaje(Base):
    """Mensaje dentro de una conversacion."""
    __tablename__ = "mensaje"
    __table_args__ = {"schema": "comunicacion"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    conversacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comunicacion.conversacion.id", ondelete="CASCADE"),
        nullable=False,
    )
    remitente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="SET NULL"),
        nullable=True,
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    leido: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    leido_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )