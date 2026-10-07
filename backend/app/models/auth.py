"""
Authentication and User Profile Models
Tablas: tipo_usuario, usuario, perfil_general, direccion_frecuente, taxista_favorito, reset_token,
       usuario_rol, refresh_token, usuario_empresa, autorizacion_inicio, turno_empleado, auditoria_email
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, Integer, Date, Numeric, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TipoUsuario(Base):
    """User roles: admin, pasajero, chofer, propietario, forense_tenant, forense_maestro"""
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
    roles: Mapped[list["UsuarioRol"]] = relationship(
        "UsuarioRol",
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
    tipo_usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.tipo_usuario.id"),
        nullable=True
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    fecha_suspension: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    motivo_suspension: Mapped[str] = mapped_column(Text, nullable=True)
    suspendido_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

    # Relationships
    tipo_usuario: Mapped["TipoUsuario"] = relationship(back_populates="usuarios")
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        foreign_keys=[control_base_id],
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
    
    # ============================================================
    # RELACIONES AGREGADAS PARA MODELOS EXTENDIDOS
    # ============================================================
    
    roles: Mapped[list["UsuarioRol"]] = relationship(
        "UsuarioRol",
        back_populates="usuario",
        lazy="selectin"
    )
    
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="usuario",
        lazy="selectin"
    )
    
    empresas: Mapped[list["UsuarioEmpresa"]] = relationship(
        "UsuarioEmpresa",
        back_populates="usuario",
        lazy="selectin"
    )
    
    autorizaciones_inicio: Mapped[list["AutorizacionInicio"]] = relationship(
        "AutorizacionInicio",
        foreign_keys="AutorizacionInicio.chofer_id",
        lazy="selectin"
    )
    
    turnos_empleado: Mapped[list["TurnoEmpleado"]] = relationship(
        "TurnoEmpleado",
        foreign_keys="TurnoEmpleado.empleado_id",
        lazy="selectin"
    )
    
    billetera: Mapped["Billetera"] = relationship(
        "Billetera",
        lazy="selectin",
        uselist=False
    )
    
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
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=True
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
    fecha_nacimiento: Mapped[datetime] = mapped_column(Date, nullable=True)
    barrio: Mapped[str] = mapped_column(String(100), nullable=True)
    codigo_postal: Mapped[str] = mapped_column(String(20), nullable=True)
    tipo_conductor: Mapped[str] = mapped_column(String(50), nullable=True)
    agencia: Mapped[str] = mapped_column(String(100), nullable=True)    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="perfil")
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
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=True)
    direccion_texto: Mapped[str] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    usuario: Mapped["Usuario"] = relationship(back_populates="reset_tokens")


# ============================================================
# MODELOS AGREGADOS PARA COMPLETAR EL ESQUEMA AUTH
# ============================================================

class UsuarioRol(Base):
    """User roles (multiple roles per user)"""
    __tablename__ = "usuario_rol"
    __table_args__ = (
        Index("idx_usuario_rol_usuario", "usuario_id", "activo"),
        Index("idx_usuario_rol_vigencia", "usuario_id", "fecha_inicio", "fecha_fin"),
        Index("idx_usuario_rol_tipo", "tipo_usuario_id", "activo"),
        Index(
            "uq_usuario_rol_activo",
            "usuario_id", "tipo_usuario_id",
            unique=True,
            postgresql_where=text("activo = true"),
        ),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False
    )
    tipo_usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.tipo_usuario.id"),
        nullable=False
    )
    # ELIMINADO: control_base_id NO debe estar aquí
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")
    tipo_usuario: Mapped["TipoUsuario"] = relationship("TipoUsuario", lazy="selectin")


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_token"
    __table_args__ = (
        Index("unique_usuario_token", "usuario_id", "token", unique=True),
        {"schema": "auth"}
    )
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
    token: Mapped[str] = mapped_column(String(500), nullable=False)
    expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


class UsuarioEmpresa(Base):
    """User-company relationship for corporate employees"""
    __tablename__ = "usuario_empresa"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id"),
        nullable=False
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False
    )
    rol: Mapped[Optional[str]] = mapped_column(String(20), default="recepcionista", nullable=True)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


class AutorizacionInicio(Base):
    """Driver shift authorization (QR-based)"""
    __tablename__ = "autorizacion_inicio"
    __table_args__ = (
        Index("idx_autorizacion_inicio_chofer", "chofer_id"),
        Index("idx_autorizacion_inicio_contrato", "contrato_id"),
        Index("idx_autorizacion_inicio_expires", "expires_at"),
        Index("idx_autorizacion_inicio_token", "token"),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    contrato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.contrato_vehiculo.id"),
        nullable=False
    )
    chofer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id"),
        nullable=False
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id"),
        nullable=False
    )
    tipo_contrato: Mapped[str] = mapped_column(String(20), nullable=True)
    turno_contractual: Mapped[str] = mapped_column(String(20), nullable=True)
    dia_contractual: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    qr_referencia: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )

    chofer: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[chofer_id], lazy="selectin")
    vehiculo: Mapped["Vehiculo"] = relationship("Vehiculo", lazy="selectin")
    contrato: Mapped["ContratoVehiculo"] = relationship("ContratoVehiculo", lazy="selectin")
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        foreign_keys=[control_base_id],
        lazy="selectin"
    )


class TurnoEmpleado(Base):
    """Employee work shifts (corporate module)"""
    __tablename__ = "turno_empleado"
    __table_args__ = (
        Index("idx_turno_empleado_empleado_id", "empleado_id"),
        Index("idx_turno_empleado_empresa_id", "empresa_id"),
        Index("idx_turno_empleado_estado", "estado"),
        Index("idx_turno_empleado_fecha_inicio", "fecha_inicio"),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id"),
        nullable=False
    )
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVO",
        comment="ACTIVO (puede operar) o CERRADO (no puede operar)"
    )
    viajes_gestionados: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True, comment="Contador de viajes gestionados en el turno")
    facturado_total: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), default=0.0, nullable=True, comment="Total facturado en el turno")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    empleado: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[empleado_id], lazy="selectin")
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")


class AuditoriaEmail(Base):
    """Email validation audit"""
    __tablename__ = "auditoria_email"
    __table_args__ = (
        Index("idx_auditoria_email_created_at", "created_at"),
        Index("idx_auditoria_email_email", "email"),
        Index("idx_auditoria_email_valid", "valid"),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    valid: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(String, nullable=True)
    mx_records: Mapped[str] = mapped_column(Text, nullable=True)
    smtp_response: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)