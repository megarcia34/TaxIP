"""
Trip Models
Tablas: viaje_solicitado, calificacion, historial_estado_viaje, objeto_olvidado, panico, tipo_vehiculo, foto_viaje, reserva
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, JSON, text,
    Numeric, func, Index, UniqueConstraint, CheckConstraint,
)
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
    __table_args__ = (
        CheckConstraint(
            "((calidad_minima_vehiculo IS NULL) OR ((calidad_minima_vehiculo)::text = ANY ((ARRAY['regular'::character varying, 'bueno'::character varying, 'excelente'::character varying])::text[])))",
            name="ck_viaje_calidad_min",
        ),
        CheckConstraint(
            "((cargado_a_cuenta = false) OR (cuenta_corriente_id IS NOT NULL))",
            name="ck_viaje_cc_obligatoria",
        ),
        CheckConstraint(
            "((origen_tipo IS NULL) OR ((origen_tipo)::text <> 'despacho_manual'::text) OR (centro_costo IS NOT NULL))",
            name="ck_viaje_centro_costo_despacho",
        ),
        CheckConstraint(
            "((estado_cobro IS NULL) OR ((estado_cobro)::text = ANY ((ARRAY['pendiente'::character varying, 'cobrado'::character varying, 'facturado'::character varying, 'pagado'::character varying])::text[])))",
            name="ck_viaje_estado_cobro",
        ),
        CheckConstraint(
            "((origen_tipo IS NULL) OR ((origen_tipo)::text = ANY ((ARRAY['plataforma'::character varying, 'via_publica'::character varying, 'qr_comercio'::character varying, 'corporativo'::character varying, 'despacho_manual'::character varying])::text[])))",
            name="ck_viaje_origen_tipo",
        ),
        CheckConstraint(
            "((responsable_cobro IS NULL) OR ((responsable_cobro)::text = ANY ((ARRAY['chofer'::character varying, 'propietario'::character varying, 'tenant'::character varying, 'comercio'::character varying, 'empresa'::character varying])::text[])))",
            name="ck_viaje_responsable_cobro",
        ),
        CheckConstraint(
            "((subestado_despacho IS NULL) OR ((subestado_despacho)::text = ANY ((ARRAY['reservado'::character varying, 'despachado'::character varying, 'vehiculo_llego'::character varying, 'pasajero_a_bordo'::character varying, 'completado'::character varying])::text[])))",
            name="ck_viaje_subestado_despacho",
        ),
        CheckConstraint(
            "((metodo_pago IS NULL) OR ((metodo_pago)::text = ANY ((ARRAY['efectivo'::character varying, 'tarjeta_debito'::character varying, 'qr'::character varying, 'transferencia'::character varying])::text[])))",
            name="metodo_pago",
        ),
        Index("idx_viaje_aceptado", "aceptado_en", postgresql_where=text("(estado)::text = 'aceptado'::text")),
        Index("idx_viaje_chofer", "chofer_id"),
        Index("idx_viaje_comercio", "comercio_id"),
        Index("idx_viaje_estado", "estado"),
        Index("idx_viaje_fecha_programada", "fecha_programada", postgresql_where=text("(estado)::text = 'programada'::text")),
        # FIX R10: restaurado. La DB tiene idx_viaje_origen_gist (GIST manual).
        # El GIST auto-generado por GeoAlchemy2 se desactiva con spatial_index=False
        # en la columna origen para evitar duplicado.
        Index("idx_viaje_origen_gist", "origen", postgresql_using="gist"),
        Index("idx_viaje_pasajero", "pasajero_id"),
        Index("idx_viaje_reservas_pendientes", "fecha_programada", "reserva_procesada", postgresql_where=text("(estado)::text = 'programada'::text")),
        Index("idx_viaje_solicitado_chofer_vehiculo", "chofer_vehiculo_id"),
        Index("idx_viajes_llegado_en", "llegado_en", postgresql_where=text("llegado_en IS NOT NULL")),
        Index("ix_viaje_centro_costo", "centro_costo"),
        Index("ix_viaje_cuenta_corriente_id", "cuenta_corriente_id"),
        Index("ix_viaje_empleado_id", "empleado_id"),
        Index("ix_viaje_empresa_id", "empresa_id"),
        Index("ix_viaje_estado", "estado"),
        Index("ix_viaje_fecha_expiracion_publicado", "fecha_expiracion", postgresql_where=text("(estado)::text = 'publicado'::text")),
        Index("ix_viaje_qr_cobro_token", "qr_cobro_token"),
        Index("ix_viaje_solicitado_turno_id", "turno_id"),
        {"schema": "trip"},    
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=True
    )
    pasajero_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=True
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
    # FIX R10: spatial_index=False en origen. La DB tiene idx_viaje_origen_gist
    # (manual, declarado en __table_args__). Sin esto, GeoAlchemy2 auto-genera
    # idx_viaje_solicitado_origen, que crea un GIST duplicado sobre la misma columna.
    origen: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326, spatial_index=False),
        nullable=True,
    )
    # destino mantiene spatial_index=True (default). La DB no tiene GIST sobre
    # destino. Se creara en migracion m3_011.
    destino: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
    )
    direccion_origen: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direccion_destino: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default='pendiente', nullable=True)

    # Pricing
    precio_estimado: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    precio_final: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS", nullable=True)

    # Time and distance
    tiempo_estimado_segundos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distancia_metros: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Sharing/Follow Me feature
    url_seguimiento: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    codigo_compartido: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Timestamps
     # Timestamp de NEGOCIO. Ver docstring de clase. No confundir con created_at.
    solicitado_en: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=True,
        comment="Fecha y hora en que se solicitó el viaje (snapshot del momento de la solicitud)"
    )
    aceptado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    iniciado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finalizado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelado_por: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    motivo_cancelacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reservas anticipadas
    fecha_programada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reserva_procesada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    procesado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamp TECNICO de insercion. Ver docstring de clase.
    # Para logica de negocio usar solicitado_en.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)
    # Timestamp de ultima actualizacion. Ver docstring de clase.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True,
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

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4a (Ronda 6, reconciliacion ORM)
    # Origen: DB tiene 66 columnas, ORM tenia 37. Faltaban 29.
    # Items D-1195 a D-1223 del diff.
    # ============================================================

    calidad_minima_vehiculo: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    cantidad_pasajeros: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    cantidad_valijas: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    cargado_a_cuenta: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    centro_costo: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    cuenta_corriente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    empleado_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    es_anonimo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    es_programado: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    estado_cobro: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    fecha_cobro: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    fecha_expiracion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    fecha_publicacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    intentos_broadcast: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    llegado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    lugar_subida: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    metodo_pago: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Medio de pago del pasajero. Valores canonicos: efectivo, tarjeta_debito, qr, transferencia. NULL permitido para viajes sin info. Billetera se agregara cuando se implemente la wallet TaxIP. Deuda B7.",
    )
    movimiento_cc_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    origen_tipo: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    paradas_intermedias: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    pasajero_telefono: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )
    qr_cobro_expira: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    qr_cobro_token: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )
    radio_broadcast_metros: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    requiere_baul_grande: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    responsable_cobro: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    subestado_despacho: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )
    tipo_vehiculo_solicitado: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    turno_empleado_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

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
        nullable=True
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=True)
    latitud: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)
    observacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
        nullable=True
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=True
    )
    ubicacion: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    resuelto_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
    estado: Mapped[str] = mapped_column(String(20), default='reportado', nullable=True)
    foto_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
        Numeric(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.tarifa_base"
    )
    tarifa_por_km: Mapped[float] = mapped_column(
        Numeric(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha con metros_por_ficha=1000"
    )
    tarifa_por_minuto: Mapped[float] = mapped_column(
        Numeric(10, 2), 
        nullable=False, 
        default=0,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha con metros_por_ficha=0"
    )
    
    capacidad_pasajeros: Mapped[int] = mapped_column(Integer, default=4, nullable=True)
    capacidad_equipaje: Mapped[int] = mapped_column(Integer, default=2, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)
    
    precio_por_ficha: Mapped[float] = mapped_column(
        Numeric, 
        default=0,
        nullable=True,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.precio_por_ficha"
    )
    distancia_por_ficha: Mapped[float] = mapped_column(
        Numeric, 
        default=100,
        nullable=True,
        doc="DEPRECATED - Usar payment.configuracion_tarifa.metros_por_ficha"
    )
    precio_por_minuto_espera: Mapped[float] = mapped_column(
        Numeric, 
        default=0,
        nullable=True,
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
    latitud_origen: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitud_origen: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)
    direccion_destino: Mapped[str] = mapped_column(Text, nullable=False)
    latitud_destino: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitud_destino: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)
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
    distancia_estimada_km: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    tiempo_estimado_minutos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    precio_estimado: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    precio_final: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
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

class BroadcastLog(Base):
    """
    Log de broadcast de viajes a choferes.
    Tabla: trip.broadcast_log

    Existente en DB, faltante en ORM (Fase 4c, R11).
    """
    __tablename__ = "broadcast_log"
    __table_args__ = (
        Index("ix_bcl_cb_fecha", "control_base_id", "emitido_en"),
        Index("ix_bcl_chofer_fecha", "chofer_id", "emitido_en"),
        Index("ix_bcl_motivo", "motivo_exclusion"),
        Index("ix_bcl_respuesta", "respuesta"),
        Index("ix_bcl_viaje", "viaje_id"),
        {"schema": "trip"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id"),
        nullable=False,
    )
    chofer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=False,
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id"),
        nullable=True,
    )
    distancia_metros: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    emitido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    respondido_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    respuesta: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    motivo_exclusion: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    tiempo_respuesta_segundos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    control_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)