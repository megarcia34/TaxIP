"""
Authentication and User Profile Models
Tablas: tipo_usuario, usuario, perfil_general, direccion_frecuente, taxista_favorito, reset_token
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, DECIMAL, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TipoUsuario(Base):
    """User roles: admin, pasajero, chofer, propietario"""
    __tablename__ = "tipo_usuario"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relationships
    usuarios: Mapped[list["Usuario"]] = relationship(
        "Usuario",
        back_populates="tipo_usuario",
        lazy="selectin"
    )


class Usuario(Base):
    """System users (all roles)"""
    __tablename__ = "usuario"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.tipo_usuario.id"),
        nullable=False
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # Relationships
    tipo_usuario: Mapped["TipoUsuario"] = relationship(back_populates="usuarios")
    
    # NOTA: Sin back_populates para evitar ciclos de mapeo con modelos de otros archivos
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    
    perfil: Mapped["PerfilGeneral"] = relationship(
        back_populates="usuario",
        uselist=False,
        lazy="selectin"
    )
    direcciones_frecuentes: Mapped[list["DireccionFrecuente"]] = relationship(
        back_populates="usuario",
        lazy="selectin"
    )
    taxistas_favoritos: Mapped[list["TaxistaFavorito"]] = relationship(
        foreign_keys="TaxistaFavorito.pasajero_id",
        back_populates="pasajero",
        lazy="selectin"
    )
    reset_tokens: Mapped[list["ResetToken"]] = relationship(
        back_populates="usuario",
        lazy="selectin"
    )
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con Billetera (payment.py)
    billetera: Mapped["Billetera"] = relationship(
        "Billetera",
        lazy="selectin",
        uselist=False
    )
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con Notificacion (notification.py)
    notificaciones: Mapped[list["Notificacion"]] = relationship(
        "Notificacion",
        lazy="selectin"
    )
    
    chofer_vehiculos: Mapped[list["ChoferVehiculo"]] = relationship(
        "ChoferVehiculo",
        back_populates="usuario",
        lazy="selectin"
    )
    viajes_como_pasajero: Mapped[list["ViajeSolicitado"]] = relationship(
        "ViajeSolicitado",
        foreign_keys="ViajeSolicitado.pasajero_id",
        back_populates="pasajero",
        lazy="selectin"
    )
    viajes_como_chofer: Mapped[list["ViajeSolicitado"]] = relationship(
        "ViajeSolicitado",
        foreign_keys="ViajeSolicitado.chofer_id",
        back_populates="chofer",
        lazy="selectin"
    )
    calificaciones_emitidas: Mapped[list["Calificacion"]] = relationship(
        "Calificacion",
        foreign_keys="Calificacion.calificador_id",
        back_populates="calificador"
    )
    calificaciones_recibidas: Mapped[list["Calificacion"]] = relationship(
        "Calificacion",
        foreign_keys="Calificacion.calificado_id",
        back_populates="calificado"
    )
    gastos_vehiculo: Mapped[list["GastoVehiculo"]] = relationship(
        "GastoVehiculo",
        foreign_keys="GastoVehiculo.propietario_id",
        back_populates="propietario"
    )
    mantenimientos: Mapped[list["MantenimientoVehiculo"]] = relationship(
        "MantenimientoVehiculo",
        foreign_keys="MantenimientoVehiculo.propietario_id",
        back_populates="propietario"
    )


class PerfilGeneral(Base):
    """Extended user profile information"""
    __tablename__ = "perfil_general"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=True)
    apellido: Mapped[str] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    documento: Mapped[str] = mapped_column(String(50), nullable=True)
    direccion: Mapped[str] = mapped_column(Text, nullable=True)
    ciudad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("geo.ciudad.id"),
        nullable=True
    )
    foto_perfil_url: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="perfil")
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con Ciudad (geo.py)
    ciudad: Mapped["Ciudad"] = relationship("Ciudad", lazy="selectin")


class DireccionFrecuente(Base):
    """Saved addresses for passengers"""
    __tablename__ = "direccion_frecuente"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(50), nullable=True)
    latitud: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=True)
    direccion_texto: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    usuario: Mapped["Usuario"] = relationship(back_populates="direcciones_frecuentes")


class TaxistaFavorito(Base):
    """Favorite drivers for passengers"""
    __tablename__ = "taxista_favorito"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    pasajero_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    chofer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    pasajero: Mapped["Usuario"] = relationship(
        foreign_keys=[pasajero_id],
        back_populates="taxistas_favoritos"
    )
    chofer: Mapped["Usuario"] = relationship(
        foreign_keys=[chofer_id],
        lazy="selectin"
    )


class ResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "reset_token"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    usuario: Mapped["Usuario"] = relationship(back_populates="reset_tokens")