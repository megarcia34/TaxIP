"""
Fleet and Driver Management Models (PostGIS enabled)
Tablas: vehiculo, chofer_vehiculo, gasto_vehiculo, mantenimiento_vehiculo,
propietario_vehiculo, contrato_vehiculo, turno_chofer, gasto_turno,
categoria_gasto, neumatico_vehiculo, neumatico_historial_posicion, ...
"""
import uuid
from uuid import uuid4
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Integer, DECIMAL, 
    Numeric, Text, Date, Index, text, UniqueConstraint, Time, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geography
from app.database import Base

# Alias para que los modelos de neumÃ¡ticos puedan usar default=now
now = datetime.now


class Vehiculo(Base):
    """Vehicle information with QR fijo"""
    __tablename__ = "vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    control_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=True
    )    
    patente: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str] = mapped_column(String(100), nullable=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=True)
    numero_licencia: Mapped[str] = mapped_column(String(50), nullable=True)
    capacidad: Mapped[Optional[int]] = mapped_column(Integer, default=4, nullable=True)
    capacidad_baul: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default='sin_baul'
    )
    estado_vehiculo: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default='bueno'
    )
    equipamiento: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='[]'
    )
    qr_uuid: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=True,
        comment="UUID único para generar QR fijo del vehículo"
    )
    qr_activo: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        default=True,
        nullable=True,
        comment="Permite desactivar QR sin eliminar vehículo"
    )
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=True,
        comment="Fecha y hora de creación del registro del vehículo"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True,
        comment="Fecha y hora de la última actualización del registro del vehículo"
    )

# ============================================================
# COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
# 5 columnas de estado de neumaticos (D-0804 a D-0808).
# ============================================================
    desgaste_manual: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0",
        comment="% ingresado por propietario",
    )
    desgaste_neumaticos: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0",
    )
    fecha_ultimo_cambio_neumaticos: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="fecha del último cambio",
    )
    km_ultimo_cambio_neumaticos: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="km al último cambio",
    )
    parches_neumaticos: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0",
        comment="cantidad de parches",
    )


    control_base: Mapped["ControlBase"] = relationship(
        "ControlBase",
        lazy="selectin"
    )

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
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=True
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud: Mapped[float] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[float] = mapped_column(Numeric(11, 8), nullable=True)
    ubicacion: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        index=True
    )
    estado_laboral: Mapped[Optional[str]] = mapped_column(String(20), default='libre', nullable=True)
    estado_panico: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    ultima_conexion: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    calificacion_promedio: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), default=5.0, nullable=True)
    total_calificaciones: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    estado_aprobacion: Mapped[str] = mapped_column(
        String(20), nullable=True, server_default='pendiente'
    )
    total_viajes: Mapped[int] = mapped_column(
        Integer, nullable=True, server_default='0'
    )
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=True
    )

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


# ============================================================
# CATEGORÃAS DE GASTOS
# ============================================================

class CategoriaGasto(Base):
    """
    CategorÃ­as y subcategorÃ­as de gastos para vehÃ­culos y turnos.
    """
    __tablename__ = "categoria_gasto"
    __table_args__ = (
        UniqueConstraint('control_base_id', 'nombre', name='uq_categoria_gasto_tenant_nombre'),
        {"schema": "fleet"}
    )

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
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subcategorias: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb")
    )
    aplica_a: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb")
    )
    tratamiento_economico: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="configurable"
    )
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=True
    )

    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    gastos_vehiculo = relationship(
        "GastoVehiculo",
        foreign_keys="GastoVehiculo.categoria_id",
        lazy="selectin"
    )
    gastos_turno = relationship(
        "GastoTurno",
        foreign_keys="GastoTurno.categoria_id",
        lazy="selectin"
    )


    # ============================================================
    # GASTO VEHÃCULO
    # ============================================================

class GastoVehiculo(Base):
    """Vehicle expenses. Coincide con fleet.gasto_vehiculo."""
    __tablename__ = "gasto_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=True
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.categoria_gasto.id", ondelete="SET NULL"),
        nullable=True
    )
    subcategoria: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    km_registro: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    tipo_gasto: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    moneda: Mapped[Optional[str]] = mapped_column(String(10), server_default="ARS", nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comprobante_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_gasto: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("now()"), nullable=True)

    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="gastos"
    )
    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )
    categoria = relationship(
        "CategoriaGasto",
        foreign_keys=[categoria_id],
        lazy="selectin"
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
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=True
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_servicio: Mapped[str] = mapped_column(String(100), nullable=True)
    taller_nombre: Mapped[str] = mapped_column(String(150), nullable=True)
    taller_direccion: Mapped[str] = mapped_column(Text, nullable=True)
    costo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    kilometraje: Mapped[int] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_servicio: Mapped[datetime] = mapped_column(Date, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

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
    porcentaje_participacion: Mapped[Optional[float]] = mapped_column(Numeric(5,2), default=100, nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(Date, default=datetime.now)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # ============================================================
    # COLUMNA AGREGADA EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 1 columna faltante (D-0766).
    # ============================================================
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )

    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )
    vehiculo = relationship(
        "Vehiculo",
        foreign_keys=[vehiculo_id],
        back_populates="propietarios"
    )

# app/models/fleet.py

class ContratoVehiculo(Base):
    __tablename__ = "contrato_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    control_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id", ondelete="CASCADE"), nullable=False)
    propietario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"), nullable=False)
    chofer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    
    tipo_contrato: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Horarios flexibles
    hora_inicio: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    duracion_minima_horas: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    permite_extension: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hora_fin_extension: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)
    
    porcentaje_chofer: Mapped[Optional[float]] = mapped_column(Numeric(5,2), nullable=True)
    monto_diario: Mapped[Optional[float]] = mapped_column(Numeric(10,2), nullable=True)
    
    estado_contrato: Mapped[Optional[str]] = mapped_column(String(30), default='PENDIENTE_CONFIGURACION', nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    canon_diario: Mapped[Optional[float]] = mapped_column(Numeric(10,2), nullable=True)
    km_incluidos_dia: Mapped[Optional[float]] = mapped_column(Numeric(10,2), nullable=True)
    valor_km_excedente: Mapped[Optional[float]] = mapped_column(Numeric(10,2), nullable=True)
    modalidad_computo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default='DIARIO')
    tratamiento_dia_no_trabajado: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, default='POR_DISPONIBILIDAD')
    dias_contractuales: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    dia_inicio_semana: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # ============================================
    # NUEVO: CompensaciÃ³n de KM
    # ============================================
    compensacion_km: Mapped[str] = mapped_column(String(20), nullable=False, default='DIARIA')
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()"))

    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    turnos = relationship("TurnoChofer", lazy="selectin", cascade="all, delete-orphan")
    propietario = relationship("Usuario", foreign_keys=[propietario_id])
    chofer = relationship("Usuario", foreign_keys=[chofer_id])
    vehiculo = relationship("Vehiculo", foreign_keys=[vehiculo_id], back_populates="contratos")

    # ============================================================
    # DOCUMENTOS (Fase 7) - ALINEADOS CON LA BASE DE DATOS
    # ============================================================

class DocumentoVehiculo(Base):
    """Documentos del vehÃ­culo (seguro, VTV, patente, cÃ©dula, etc.)"""
    __tablename__ = "documento_vehiculo"
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
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_archivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # âœ… CAMPOS AGREGADOS
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    notificar_dias: Mapped[int] = mapped_column(Integer, server_default="30")
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # ============================================================
    # COLUMNAS AGREGADAS EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 16 columnas faltantes (D-0404 a D-0419).
    # ============================================================
    chasis: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    dominio: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    marca: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    motor: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    seguro_cobertura: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_compania: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    seguro_fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    seguro_poliza: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seguro_suma_asegurada: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seguro_tomador: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seguro_vehiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tipo_vehiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uso: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    vtv_fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relaciones
    vehiculo = relationship("Vehiculo", foreign_keys=[vehiculo_id], lazy="selectin")


class DocumentoPropietario(Base):
    """Documentos personales del propietario (DNI, Licencia, CUIT, etc.)"""
    __tablename__ = "documento_propietario"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_archivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    
    # ============================================================
    # COLUMNA AGREGADA EN FASE 4b (Ronda 7, reconciliacion ORM)
    # 1 columna faltante (D-0766).
    # ============================================================
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        server_default=func.now(),
    )

    propietario = relationship(
        "Usuario",
        foreign_keys=[propietario_id]
    )


    # ============================================================
    #  MODELOS DE NEUMÃTICOS (sin cambios)
    # ============================================================

class NeumaticoVehiculo(Base):
    __tablename__ = "neumatico_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    codigo_interno = Column(String(20), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo_dibujo = Column(String(50))
    medida = Column(String(20))
    tipo_neumatico = Column(String(20), nullable=False)
    fecha_fabricacion = Column(Date)
    estado = Column(String(20), nullable=False, default="ACTIVO")
    km_totales_acumulados = Column(Integer, default=0)
    fecha_alta = Column(DateTime(timezone=True), default=now)
    fecha_baja = Column(DateTime(timezone=True))
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class NeumaticoHistorialPosicion(Base):
    __tablename__ = "neumatico_historial_posicion"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    neumatico_vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_vehiculo.id"), nullable=False)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    eje_posicion = Column(String(5), nullable=False)
    km_montaje = Column(Integer, nullable=False)
    km_desmontaje = Column(Integer)
    fecha_montaje = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    fecha_desmontaje = Column(DateTime(timezone=False))
    operacion_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_operacion.id"))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())


class NeumaticoMedicion(Base):
    __tablename__ = "neumatico_medicion"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    historial_posicion_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_historial_posicion.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    profundidad_mm = Column(Numeric(3, 1), nullable=False)
    fecha_medicion = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    medido_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())


class NeumaticoOperacion(Base):
    __tablename__ = "neumatico_operacion"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    tipo_operacion = Column(String(30), nullable=False)
    descripcion = Column(Text)
    km_vehiculo_actual = Column(Integer, nullable=False)
    fecha_operacion = Column(DateTime(timezone=True), nullable=False, default=now)
    costo = Column(Numeric(10, 2))
    moneda = Column(String(3), default="ARS")
    proveedor = Column(String(100))
    observaciones = Column(Text)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class NeumaticoOperacionDetalle(Base):
    __tablename__ = "neumatico_operacion_detalle"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    operacion_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_operacion.id"), nullable=False)
    neumatico_vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_vehiculo.id"), nullable=False)
    posicion_antes = Column(String(5))
    posicion_despues = Column(String(5))
    km_neumatico_en_operacion = Column(Integer)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())


class NeumaticoSugerencia(Base):
    __tablename__ = "neumatico_sugerencia"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    tipo_sugerencia = Column(String(30), nullable=False)
    neumatico_vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_vehiculo.id"))
    mensaje = Column(Text, nullable=False)
    prioridad = Column(String(10), nullable=False)
    km_actual = Column(Integer)
    km_umbral = Column(Integer)
    estado = Column(String(20), default="PENDIENTE")
    fecha_generacion = Column(DateTime(timezone=True), default=now)
    fecha_atendida = Column(DateTime(timezone=True))
    atendida_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)


class NeumaticoImagen(Base):
    __tablename__ = "neumatico_imagen"
    __table_args__ = {"schema": "fleet"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    neumatico_vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_vehiculo.id"))
    operacion_id = Column(UUID(as_uuid=True), ForeignKey("fleet.neumatico_operacion.id"))
    cloudinary_public_id = Column(String(255), nullable=False)
    cloudinary_url = Column(String(500), nullable=False)
    cloudinary_secure_url = Column(String(500))
    tipo_imagen = Column(String(30), nullable=False)
    descripcion = Column(Text)
    peso_bytes = Column(Integer)
    dimensiones = Column(String(20))
    subido_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    fecha_subida = Column(DateTime(timezone=False), server_default=func.now())
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # ============================================================
    # MODELO CONTRATO_QR - AGREGADO PARA COMPLETAR EL ESQUEMA FLEET
    # ============================================================

class ContratoQr(Base):
    """
    QR codes generated for vehicle contracts
    Used for shift start authorization and traceability
    Tabla: fleet.contrato_qr
    """
    __tablename__ = "contrato_qr"
    __table_args__ = ({"schema": "fleet"},)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    contrato_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.contrato_vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    usos: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)

    # Relationships
    contrato: Mapped["ContratoVehiculo"] = relationship("ContratoVehiculo", lazy="selectin")
    creador: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")

    # ============================================================
    # MODELO DOCUMENTOS_CHOFER
    # ============================================================

class DocumentosChofer(Base):
    """
    Driver documents (license, insurance, background checks)
    Tabla: fleet.documentos_chofer
    """
    __tablename__ = "documentos_chofer"
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
    tipo_documento: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Valores: licencia, seguro, antecedentes"
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="URL del documento almacenado (local, S3, etc)"
    )
    subido_en: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)
    fecha_vencimiento: Mapped[datetime] = mapped_column(Date, nullable=True)
    notificar_dias: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


# ============================================================
# MODELO FOTO_VEHICULO
# ============================================================

class FotoVehiculo(Base):
    """
    Vehicle photos (Cloudinary)
    Tabla: fleet.foto_vehiculo
    """
    __tablename__ = "foto_vehiculo"
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
    url: Mapped[str] = mapped_column(Text, nullable=False)
    public_id: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    orden: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    es_principal: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    subida_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    vehiculo: Mapped["Vehiculo"] = relationship("Vehiculo", lazy="selectin")
    subido_por_usuario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")


# ============================================================
# MODELO NOTIFICACION_VENCIMIENTO
# ============================================================

class NotificacionVencimiento(Base):
    """
    Expiration notifications for documents
    Tabla: fleet.notificacion_vencimiento
    """
    __tablename__ = "notificacion_vencimiento"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    entidad_tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="propietario | vehiculo | chofer"
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="vencido | critico | urgente | preventivo | vigente"
    )
    dias_restantes: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(Date, nullable=False)
    email_enviado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    email_enviado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sms_enviado: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    sms_enviado_en: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, nullable=True)

    # Relationships
    propietario: Mapped["Usuario"] = relationship("Usuario", lazy="selectin")

# ============================================================
# MODELOS MARCA Y MODELO - CATÃLOGO DE VEHÃCULOS
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
    __table_args__ = {"schema": "fleet"}

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

    # ============================================================
# MODELO INGRESO_TURNO - RECAUDACIÃ“N POR JORNADA
# ============================================================

class IngresoTurno(Base):
    """
    Income/collection records per shift
    Reemplaza los campos legacy de recaudaciÃ³n en turno_chofer
    Tabla: fleet.ingreso_turno (NUEVA - aÃºn no existe en BD)
    """
    __tablename__ = "ingreso_turno"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    turno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.turno_chofer.id", ondelete="CASCADE"),
        nullable=False
    )
    viaje_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="SET NULL"),
        nullable=True,
        comment="Viaje asociado, si corresponde"
    )
    tipo_ingreso: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="efectivo | electronico | taximetro | manual | corporativo"
    )
    medio_pago: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
        comment="efectivo | debito | qr | transferencia "
    )
    origen: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="app",
        comment="app | taximetro | manual | corporativo"
    )
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), default="ARS", nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    declarado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True,
        comment="Usuario que declarÃ³ el ingreso (chofer)"
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="pendiente",
        nullable=False,
        comment="pendiente | aprobado | rechazado | disputado"
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transaccion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment.transaccion.id", ondelete="SET NULL"),
        nullable=True,
        comment="Referencia a transacciÃ³n electrÃ³nica si aplica"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    turno: Mapped["TurnoChofer"] = relationship("TurnoChofer", lazy="selectin")
    viaje: Mapped["ViajeSolicitado"] = relationship("ViajeSolicitado", lazy="selectin")
    declarante: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[declarado_por], lazy="selectin")
    transaccion: Mapped["Transaccion"] = relationship("Transaccion", lazy="selectin")