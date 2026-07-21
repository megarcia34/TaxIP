"""
Trip/Viaje Models (PostGIS enabled)
Tablas: viaje_solicitado, historial_estado_viaje, panico, calificacion, objeto_olvidado
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Integer, DECIMAL, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.database import Base


class ViajeSolicitado(Base):
    """
    Main trip/ride table - Core business entity
    Uses PostGIS for origin/destination points
    """
    __tablename__ = "viaje_solicitado"
    __table_args__ = {"schema": "trip"}

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
    pasajero_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    chofer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    chofer_vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.chofer_vehiculo.id", ondelete="SET NULL"),
        nullable=True
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # PostGIS Geography points
    origen: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        index=True
    )
    destino: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    direccion_origen: Mapped[str] = mapped_column(Text, nullable=True)
    direccion_destino: Mapped[str] = mapped_column(Text, nullable=True)
    
    estado: Mapped[str] = mapped_column(String(20), default='pendiente', index=True)
    
    # Pricing
    precio_estimado: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=True)
    precio_final: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS")
    
    # Time and distance
    tiempo_estimado_segundos: Mapped[int] = mapped_column(Integer, nullable=True)
    distancia_metros: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Sharing/Follow Me feature
    url_seguimiento: Mapped[str] = mapped_column(String(255), nullable=True)
    codigo_compartido: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    
    # Timestamps
    solicitado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    aceptado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    iniciado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    finalizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelado_por: Mapped[str] = mapped_column(String(20), nullable=True)
    motivo_cancelacion: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Reservas anticipadas
    fecha_programada: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reserva_procesada: Mapped[bool] = mapped_column(default=False)
    procesado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # Relationships
    # NOTA: Sin back_populates para evitar ciclo de mapeo con ControlBase
    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )
    pasajero: Mapped["Usuario"] = relationship(
        foreign_keys=[pasajero_id],
        back_populates="viajes_como_pasajero"
    )
    chofer: Mapped["Usuario"] = relationship(
        foreign_keys=[chofer_id],
        back_populates="viajes_como_chofer"
    )
    chofer_vehiculo: Mapped["ChoferVehiculo"] = relationship(back_populates="viajes")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="viajes")
    historial_estados: Mapped[list["HistorialEstadoViaje"]] = relationship(
        back_populates="viaje",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    alertas_panico: Mapped[list["Panico"]] = relationship(
        back_populates="viaje",
        lazy="selectin"
    )
    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="viaje",
        lazy="selectin"
    )
    objetos_olvidados: Mapped[list["ObjetoOlvidado"]] = relationship(
        back_populates="viaje",
        lazy="selectin"
    )
    transacciones: Mapped[list["Transaccion"]] = relationship(
        "Transaccion",
        back_populates="viaje",
        lazy="selectin"
    )
    # NOTA: Sin back_populates porque FotoViaje no tiene relationship inversa
    fotos: Mapped[list["FotoViaje"]] = relationship(
        "FotoViaje",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class HistorialEstadoViaje(Base):
    """Trip state change history"""
    __tablename__ = "historial_estado_viaje"
    __table_args__ = {"schema": "trip"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=False
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    latitud: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=True)
    observacion: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    viaje: Mapped["ViajeSolicitado"] = relationship(back_populates="historial_estados")


class Panico(Base):
    """Panic button alerts"""
    __tablename__ = "panico"
    __table_args__ = {"schema": "trip"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=False
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    ubicacion: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    resuelto_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    viaje: Mapped["ViajeSolicitado"] = relationship(back_populates="alertas_panico")
    usuario: Mapped["Usuario"] = relationship(lazy="selectin")


class Calificacion(Base):
    """Ratings for drivers and passengers"""
    __tablename__ = "calificacion"
    __table_args__ = {"schema": "trip"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    calificador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    calificado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    viaje: Mapped["ViajeSolicitado"] = relationship(back_populates="calificaciones")
    calificador: Mapped["Usuario"] = relationship(
        foreign_keys=[calificador_id],
        back_populates="calificaciones_emitidas"
    )
    calificado: Mapped["Usuario"] = relationship(
        foreign_keys=[calificado_id],
        back_populates="calificaciones_recibidas"
    )


class ObjetoOlvidado(Base):
    """Lost and found items reporting"""
    __tablename__ = "objeto_olvidado"
    __table_args__ = {"schema": "trip"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=False
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
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default='reportado')
    foto_url: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    viaje: Mapped["ViajeSolicitado"] = relationship(back_populates="objetos_olvidados")
    pasajero: Mapped["Usuario"] = relationship(foreign_keys=[pasajero_id])
    chofer: Mapped["Usuario"] = relationship(foreign_keys=[chofer_id])


class TipoVehiculo(Base):
    """Tipos de vehículos disponibles"""
    __tablename__ = "tipo_vehiculo"
    __table_args__ = {"schema": "trip"}

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    
    tarifa_base: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    tarifa_por_km: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    tarifa_por_minuto: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    
    capacidad_pasajeros: Mapped[int] = mapped_column(Integer, default=4)
    capacidad_equipaje: Mapped[int] = mapped_column(Integer, default=2)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Nuevos campos para modo ficha
    precio_por_ficha: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        doc="Precio por ficha para este tipo de vehículo"
    )
    distancia_por_ficha: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=100,
        doc="Distancia en metros por ficha para este tipo de vehículo"
    )
    precio_por_minuto_espera: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        doc="Precio por minuto de espera para este tipo de vehículo"
    )

    def __repr__(self):
        return f"<TipoVehiculo {self.id} - {self.nombre}>"