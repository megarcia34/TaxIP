"""
Notifications Model
Tablas: notificacion
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Notificacion(Base):
    """
    In-app notifications for users
    Types: 'viaje', 'alerta', 'sistema', 'promocion'
    """
    __tablename__ = "notificacion"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=True)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

    # Relationships
    # NOTA: Sin back_populates para evitar ciclo de mapeo con Usuario
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")