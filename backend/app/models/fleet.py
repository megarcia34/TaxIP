"""
Fleet and Driver Management Models (PostGIS enabled)
Tablas: vehiculo, chofer_vehiculo, gasto_vehiculo, mantenimiento_vehiculo,
       propietario_vehiculo, contrato_vehiculo, turno_chofer, gasto_turno
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Integer, DECIMAL, Text, Date, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.database import Base


class Vehiculo(Base):
    """Vehicle information with QR fijo"""
    __tablename__ = "vehiculo"
    __table_args__ = {"schema": "fleet"}

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
    patente: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str] = mapped_column(String(100), nullable=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=True)
    numero_licencia: Mapped[str] = mapped_column(String(50), nullable=True)
    capacidad: Mapped[int] = mapped_column(Integer, default=4)
    
    qr_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    qr_activo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # NOTA: Sin back_populates para evitar ciclo de mapeo con ControlBase
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    
    # Relaciones con modelos del mismo archivo (fleet.py) - OK con back_populates
    choferes_asignaciones = relationship(
        "ChoferVehiculo",
        foreign_keys="ChoferVehiculo.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )
    gastos = relationship(
        "GastoVehiculo",
        foreign_keys="GastoVehiculo.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )
    mantenimientos = relationship(
        "MantenimientoVehiculo",
        foreign_keys="MantenimientoVehiculo.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )
    propietarios = relationship(
        "PropietarioVehiculo",
        foreign_keys="PropietarioVehiculo.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )
    contratos = relationship(
        "ContratoVehiculo",
        foreign_keys="ContratoVehiculo.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con TurnoChofer (turno.py)
    turnos = relationship(
        "TurnoChofer",
        foreign_keys="TurnoChofer.vehiculo_id",
        lazy="selectin"
    )
    
    viajes = relationship(
        "ViajeSolicitado",
        foreign_keys="ViajeSolicitado.vehiculo_id",
        back_populates="vehiculo",
        lazy="selectin"
    )


class ChoferVehiculo(Base):
    """Active driver-vehicle assignment with real-time GPS"""
    __tablename__ = "chofer_vehiculo"
    __table_args__ = {"schema": "fleet"}

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
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=False
    )
    
    latitud: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=True)
    ubicacion: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        index=True
    )
    
    estado_laboral: Mapped[str] = mapped_column(String(20), default='libre')
    estado_panico: Mapped[bool] = mapped_column(Boolean, default=False)
    ultima_conexion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    calificacion_promedio: Mapped[float] = mapped_column(DECIMAL(3, 2), default=5.0)
    total_calificaciones: Mapped[int] = mapped_column(Integer, default=0)
    
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # NOTA: Sin back_populates para evitar ciclo de mapeo con ControlBase
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    
    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        back_populates="chofer_vehiculos"
    )
    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="choferes_asignaciones"
    )
    viajes = relationship(
        "ViajeSolicitado",
        foreign_keys="ViajeSolicitado.chofer_vehiculo_id",
        back_populates="chofer_vehiculo",
        lazy="selectin"
    )


class GastoVehiculo(Base):
    """Vehicle expenses"""
    __tablename__ = "gasto_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_gasto: Mapped[str] = mapped_column(String(50), nullable=True)
    monto: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS")
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    kilometraje: Mapped[int] = mapped_column(Integer, nullable=True)
    comprobante_url: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_gasto: Mapped[datetime] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="gastos"
    )
    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )


class MantenimientoVehiculo(Base):
    """Vehicle maintenance records"""
    __tablename__ = "mantenimiento_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_servicio: Mapped[str] = mapped_column(String(100), nullable=True)
    taller_nombre: Mapped[str] = mapped_column(String(150), nullable=True)
    taller_direccion: Mapped[str] = mapped_column(Text, nullable=True)
    costo: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=True)
    kilometraje: Mapped[int] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_servicio: Mapped[datetime] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="mantenimientos"
    )
    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )


class PropietarioVehiculo(Base):
    __tablename__ = "propietario_vehiculo"
    __table_args__ = (
        Index("unique_propietario_vehiculo_activo", "propietario_id", "vehiculo_id"),
        {"schema": "fleet"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    propietario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"), nullable=False)
    porcentaje_participacion: Mapped[float] = mapped_column(DECIMAL(5,2), default=100)
    fecha_inicio: Mapped[datetime] = mapped_column(Date, default=datetime.now)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )
    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="propietarios"
    )


class ContratoVehiculo(Base):
    __tablename__ = "contrato_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    control_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id", ondelete="CASCADE"), nullable=False)
    propietario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"), nullable=False)
    chofer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    
    tipo_contrato: Mapped[str] = mapped_column(String(20), nullable=False)
    turno_asignado: Mapped[str] = mapped_column(String(10), nullable=False)
    
    porcentaje_chofer: Mapped[Optional[float]] = mapped_column(DECIMAL(5,2), nullable=True)
    monto_diario: Mapped[Optional[float]] = mapped_column(DECIMAL(10,2), nullable=True)
    
    estado_contrato: Mapped[str] = mapped_column(String(30), default='PENDIENTE_CONFIGURACION')
    
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # NOTA: Sin back_populates para evitar ciclo de mapeo con ControlBase
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    
    # NOTA: Sin back_populates para evitar ciclo de mapeo con TurnoChofer (turno.py)
    turnos = relationship(
        "TurnoChofer",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )
    chofer = relationship(
        "Usuario",
        foreign_keys=[chofer_id]
    )
    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="contratos"
    )