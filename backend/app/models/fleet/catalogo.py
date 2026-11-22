# app/models/fleet/catalogo.py
"""
Catalogo de marcas y modelos de vehiculos.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 1.
Sin cambios funcionales.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# MODELOS MARCA Y MODELO - CATALOGO DE VEHICULOS
# ============================================================

class Marca(Base):
    """
    Vehicle brands catalog
    Tabla: fleet.marca
    """
    __tablename__ = "marca"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    modelos: Mapped[list["Modelo"]] = relationship(
        "Modelo",
        back_populates="marca",
        lazy="selectin"
    )


class Modelo(Base):
    """
    Vehicle models catalog
    Tabla: fleet.modelo
    """
    __tablename__ = "modelo"
    __table_args__ = (
        Index(
            "modelo_marca_id_nombre_key",
            "marca_id", "nombre",
            unique=True,
        ),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    marca_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.marca.id"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    marca: Mapped["Marca"] = relationship("Marca", back_populates="modelos", lazy="selectin")


__all__ = ["Marca", "Modelo"]