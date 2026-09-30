"""
Trip Models
Tablas: viaje_solicitado, calificacion, historial_estado_viaje, objeto_olvidado, panico, tipo_vehiculo, foto_viaje, reserva
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, DECIMAL, Integer, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geography
from app.database import Base


class ViajeSolicitado(Base):
    """
    Viaje solicitado por cualquier canal (calle, landing, qr, corporativo, despacho).

    Usa PostGIS para los puntos de origen y destino.

    SEMANTICA DE TIMESTAMPS (deuda B9 cerrada 2026-09-30):

    - solicitado_en: fecha y hora en que se solicito el viaje.
      Snapshot del momento de la solicitud. Es el timestamp de NEGOCIO.
      Fuente de verdad: COMMENT ON COLUMN en Postgres, agregado por la
      migracion 4fa1ae56e7e7. Para reportes, liquidaciones y
      ordenamiento historico usar SIEMPRE este campo.

    - created_at: timestamp TECNICO de insercion de la fila en la DB.
      Sin semantica de negocio. Sin COMMENT en Postgres. Lo setea
      SQLAlchemy via default=datetime.now. Usar solo para auditoria
      tecnica y debugging.

    - updated_at: fecha y hora de la ultima actualizacion del viaje.
      Ver COMMENT ON COLUMN en Postgres.

    En el flujo normal (trip_service.py) solicitado_en y created_at
    coinciden salvo microsegundos, porque ambos usan datetime.now() al
    construir el objeto. En filas legacy (pre-migracion 4fa1ae56e7e7)
    solicitado_en se poblo igual a created_at. No asumir que pueden
    diferir en el flujo actual, pero NO usar created_at para logica de
    negocio: la semantica la define solicitado_en.
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
    chofer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    chofer_vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.chofer_vehiculo.id", ondelete="SET NULL"),
        nullable=True,
        comment="Asignación específica chofer-vehículo al momento del viaje (snapshot inmutable)"
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="SET NULL"),
        nullable=True
    )
    turno_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id", ondelete="SET NULL"),
        nullable=True,
        comment="Turno al que pertenece el viaje; puede ser NULL para viajes históricos no atribuibles o pendientes de inicio"
    )

    # PostGIS Geography points
    origen: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        index=True
    )
    destino: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        index=True
    )
    direccion_origen: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direccion_destino: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default='pendiente', nullable=False, index=True)

    # Pricing
    precio_estimado: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    precio_final: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS", nullable=False)

    # Time and distance
    tiempo_estimado_segundos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distancia_metros: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Sharing/Follow Me feature
    url_seguimiento: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    codigo_compartido: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    # Timestamps
     # Timestamp de NEGOCIO. Ver docstring de clase. No confundir con created_at.
    solicitado_en: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="Fecha y hora en que se solicito el viaje (snapshot del momento de la solicitud)"
    )
    aceptado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    iniciado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finalizado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelado_por: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    motivo_cancelacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reservas anticipadas
    fecha_programada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reserva_procesada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    procesado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamp TECNICO de insercion. Ver docstring de clase.
    # Para logica de negocio usar solicitado_en.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    # Timestamp de ultima actualizacion. Ver docstring de clase.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="Fecha y hora de la última actualización del viaje"
    )

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 2 (COMPLETAR ORM)
    # ============================================================
    comercio_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comercio.id"),
        nullable=True
    )
    empresa_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.empresa.id"),
        nullable=True
    )
    nombre_pasajero: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    facturado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    finalizado_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    pasajero: Mapped["Usuario"] = relationship(
        foreign_keys=[pasajero_id],
        back_populates="viajes_como_pasajero"
    )
    chofer: Mapped[Optional["Usuario"]] = relationship(
        foreign_keys=[chofer_id],
        back_populates="viajes_como_chofer"
    )
    chofer_vehiculo: Mapped[Optional["ChoferVehiculo"]] = relationship(back_populates="viajes")
    vehiculo: Mapped[Optional["Vehiculo"]] = relationship(back_populates="viajes")
    turno: Mapped[Optional["TurnoChofer"]] = relationship(lazy="selectin")
    comercio: Mapped[Optional["Comercio"]] = relationship("Comercio", lazy="selectin")
    empresa: Mapped[Optional["Empresa"]] = relationship("Empresa", lazy="selectin")
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
    latitud: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud: Mapped[Optional[float]] = mapped_column(DECIMAL(11, 8), nullable=True)
    observacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

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
    ubicacion: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    resuelto_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

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
    comentario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

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
    estado: Mapped[str] = mapped_column(String(20), default='reportado', nullable=False)
    foto_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    viaje: Mapped["ViajeSolicitado"] = relationship(back_populates="objetos_olvidados")
    pasajero: Mapped["Usuario"] = relationship(foreign_keys=[pasajero_id])
    chofer: Mapped["Usuario"] = relationship(foreign_keys=[chofer_id])


class TipoVehiculo(Base):
    """
    Vehicle types - Catálogo puro
    
    ⚠️ IMPORTANTE: Los campos tarifarios están DEPRECADOS.
    Los precios reales viven en payment.configuracion_tarifa y
    payment.configuracion_tarifa_vehiculo (factores por tipo).
    Estos campos se mantienen en 0 por compatibilidad y NO deben
    usarse en el motor unificado TaxIP 2.1.
    """
    __tablename__ = "tipo_vehiculo"
    __table_args__ = {"schema": "trip"}

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ⚠️ DEPRECATED: Los campos tarifarios quedan deprecados.
    # Los precios reales viven en payment.configuracion_tarifa.
    # Estos campos se mantienen en 0 por compatibilidad y no deben usarse en el motor unificado.
    tarifa_base: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.tarifa_base"
    )
    tarifa_por_km: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha con metros_por_ficha=1000"
    )
    tarifa_por_minuto: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha con metros_por_ficha=0"
    )
    
    capacidad_pasajeros: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    capacidad_equipaje: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    
    precio_por_ficha: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        nullable=False,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha"
    )
    distancia_por_ficha: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=100,
        nullable=False,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.metros_por_ficha"
    )
    precio_por_minuto_espera: Mapped[float] = mapped_column(
        DECIMAL(10, 2), 
        default=0,
        nullable=False,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.seg_por_ficha_espera"
    )

    def __repr__(self):
        return f"<TipoVehiculo {self.id} - {self.nombre}>"


# ============================================================
# MODELO RESERVA - AGREGADO PARA COMPLETAR EL ESQUEMA TRIP
# ============================================================

class Reserva(Base):
    """
    Corporate trip reservations (despacho manual)
    Tabla: trip.reserva
    """
    __tablename__ = "reserva"
    __table_args__ = {"schema": "trip"}

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
    empleado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False
    )
    turno_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.turno_empleado.id"),
        nullable=True
    )
    pasajero_nombre: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pasajero_telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direccion_origen: Mapped[str] = mapped_column(Text, nullable=False)
    latitud_origen: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud_origen: Mapped[Optional[float]] = mapped_column(DECIMAL(11, 8), nullable=True)
    direccion_destino: Mapped[str] = mapped_column(Text, nullable=False)
    latitud_destino: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 8), nullable=True)
    longitud_destino: Mapped[Optional[float]] = mapped_column(DECIMAL(11, 8), nullable=True)
    paradas_intermedias: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, server_default=text("'[]'::jsonb"), comment="JSONB array con las paradas intermedias")
    tipo_vehiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, server_default="standard")
    nota_conductor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        server_default="reservado",
        comment="Estado actual del viaje en el pipeline: reservado | despachado | vehiculo_llego | pasajero_a_bordo | completado | cancelado"
    )
    es_programado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_programada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    distancia_estimada_km: Mapped[Optional[float]] = mapped_column(DECIMAL(8, 2), nullable=True)
    tiempo_estimado_minutos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    precio_estimado: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    precio_final: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    metodo_pago: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, server_default="vehiculo")
    cantidad_pasajeros: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cantidad_equipaje: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    centro_costo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    empresa: Mapped["Empresa"] = relationship("Empresa", lazy="selectin")
    empleado: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[empleado_id], lazy="selectin")
    creador: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[creado_por], lazy="selectin")
    turno: Mapped["TurnoEmpleado"] = relationship("TurnoEmpleado", lazy="selectin")