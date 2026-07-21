"""
Geographic Models (PostGIS)
Tablas: pais, provincia, ciudad
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Pais(Base):
    """Country"""
    __tablename__ = "pais"
    __table_args__ = {"schema": "geo"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_iso: Mapped[str] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    provincias: Mapped[list["Provincia"]] = relationship(
        back_populates="pais",
        lazy="selectin"
    )


class Provincia(Base):
    """State/Province"""
    __tablename__ = "provincia"
    __table_args__ = {"schema": "geo"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    pais_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("geo.pais.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    pais: Mapped["Pais"] = relationship(back_populates="provincias")
    ciudades: Mapped[list["Ciudad"]] = relationship(
        back_populates="provincia",
        lazy="selectin"
    )


class Ciudad(Base):
    """City"""
    __tablename__ = "ciudad"
    __table_args__ = {"schema": "geo"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    provincia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("geo.provincia.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    provincia: Mapped["Provincia"] = relationship(back_populates="ciudades")
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con PerfilGeneral (auth.py)
    # PerfilGeneral.ciudad referencia a Ciudad, pero Ciudad no tiene back_populates
    perfiles: Mapped[list["PerfilGeneral"]] = relationship(
        "PerfilGeneral",
        foreign_keys="PerfilGeneral.ciudad_id"
    )