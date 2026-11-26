# app/models/fleet/neumatico.py
"""
Modelos de neumaticos (vehiculo, historial, medicion, operacion,
sugerencia, imagen).

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 4.
Sin cambios funcionales (solo correccion de encoding en el
comentario de seccion: ASCII puro segun N10).
"""
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


# ============================================================
# MODELOS DE NEUMATICOS (sin cambios)
# ============================================================

class NeumaticoVehiculo(Base):
    __tablename__ = "neumatico_vehiculo"
    __table_args__ = (
        Index("uq_neumatico_codigo_interno", "control_base_id", "codigo_interno", unique=True),
        Index("idx_neumatico_vehiculo_codigo", "codigo_interno"),
        Index("idx_neumatico_vehiculo_control_base", "control_base_id"),
        Index("idx_neumatico_vehiculo_estado", "estado"),
        Index("idx_neumatico_vehiculo_vehiculo", "vehiculo_id"),
        CheckConstraint(
            "tipo_neumatico IN ('RADIAL', 'BIAS', 'TUBELESS', 'RUN_FLAT', 'TODO_TERRENO')",
            name="chk_neumatico_tipo"
        ),
        CheckConstraint(
            "estado IN ('ACTIVO', 'EN_USO', 'DESBASTADO', 'RECICLADO', 'DESECHADO', 'BAJA')",
            name="chk_neumatico_estado"
        ),
        {"schema": "fleet"},
    )

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
    fecha_alta = Column(DateTime(timezone=False), server_default=func.now())
    fecha_baja = Column(DateTime(timezone=False))
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class NeumaticoHistorialPosicion(Base):
    __tablename__ = "neumatico_historial_posicion"
    __table_args__ = (
        Index("idx_historial_pos_neumatico", "neumatico_vehiculo_id"),
        Index(
            "idx_historial_pos_activa_vehiculo",
            "vehiculo_id",
            "eje_posicion",
            postgresql_where=text("(activo = true) AND (fecha_desmontaje IS NULL)"),
        ),
        Index("idx_historial_pos_control_base", "control_base_id"),
        Index("idx_historial_pos_eje", "eje_posicion"),
        Index("idx_historial_pos_vehiculo", "vehiculo_id"),
        CheckConstraint(
            "eje_posicion ~ '^[DT][1-4]$'",
            name="chk_eje_posicion_formato"
        ),
        {"schema": "fleet"},
    )

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
    __table_args__ = (
        Index("idx_medicion_fecha", "fecha_medicion"),
        Index("idx_medicion_historial", "historial_posicion_id"),
        Index("idx_medicion_control_base", "control_base_id"),
        CheckConstraint(
            "profundidad_mm >= 0 AND profundidad_mm <= 30",
            name="chk_profundidad_rango"
        ),
        {"schema": "fleet"},
    )

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
    __table_args__ = (
        Index("idx_operacion_control_base", "control_base_id"),
        Index("idx_operacion_tipo", "tipo_operacion"),
        Index("idx_operacion_fecha", "fecha_operacion"),
        Index("idx_operacion_vehiculo", "vehiculo_id"),
        CheckConstraint(
            "tipo_operacion IN ('MONTAJE', 'DESMONTAJE', 'ROTACION', 'REPARACION', 'ALINEACION', 'BALANCEO', 'INVENTARIO', 'OTRO', 'CAMBIO', 'DESECHO')",
            name="chk_operacion_tipo"
        ),
        {"schema": "fleet"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehiculo_id = Column(UUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    control_base_id = Column(UUID(as_uuid=True), ForeignKey("tenant.control_base.id"), nullable=False)
    tipo_operacion = Column(String(30), nullable=False)
    descripcion = Column(Text)
    km_vehiculo_actual = Column(Integer, nullable=False)
    fecha_operacion = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    costo = Column(Numeric(10, 2))
    moneda = Column(String(3), default="ARS")
    proveedor = Column(String(100))
    observaciones = Column(Text)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class NeumaticoOperacionDetalle(Base):
    __tablename__ = "neumatico_operacion_detalle"
    __table_args__ = (
        Index("idx_operacion_detalle_neumatico", "neumatico_vehiculo_id"),
        Index("idx_operacion_detalle_operacion", "operacion_id"),
        {"schema": "fleet"},
    )

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
    __table_args__ = (
        Index(
            "idx_sugerencia_pendientes",
            "vehiculo_id",
            "prioridad",
            postgresql_where=text("(estado)::text = 'PENDIENTE'::text"),
        ),
        Index("idx_sugerencia_control_base", "control_base_id"),
        Index("idx_sugerencia_estado", "estado"),
        Index("idx_sugerencia_vehiculo", "vehiculo_id"),
        CheckConstraint(
            "prioridad IN ('ALTA', 'MEDIA', 'BAJA')",
            name="chk_sugerencia_prioridad"
        ),
        CheckConstraint(
            "estado IN ('PENDIENTE', 'EN_PROCESO', 'ATENDIDA', 'DESCARTADA')",
            name="chk_sugerencia_estado"
        ),
        CheckConstraint(
            "tipo_sugerencia IN ('ROTACION', 'REEMPLAZO', 'REPARACION', 'INSPECCION', 'INVENTARIO', 'OTRO')",
            name="chk_sugerencia_tipo"
        ),
        {"schema": "fleet"},
    )

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
    fecha_generacion = Column(DateTime(timezone=False), server_default=func.now())
    fecha_atendida = Column(DateTime(timezone=False))
    atendida_por = Column(UUID(as_uuid=True), ForeignKey("auth.usuario.id"))
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class NeumaticoImagen(Base):
    __tablename__ = "neumatico_imagen"
    __table_args__ = (
        Index("idx_neumatico_imagen_cloudinary", "cloudinary_public_id", unique=True),
        Index("idx_neumatico_imagen_neumatico", "neumatico_vehiculo_id"),
        Index("idx_neumatico_imagen_operacion", "operacion_id"),
        Index("idx_neumatico_imagen_control_base", "control_base_id"),
        CheckConstraint(
            "tipo_imagen IN ('NEUMATICO', 'OPERACION', 'DANO', 'MEDICION', 'INVENTARIO', 'OTRO')",
            name="chk_imagen_tipo"
        ),
        {"schema": "fleet"},
    )

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


__all__ = [
    "NeumaticoVehiculo",
    "NeumaticoHistorialPosicion",
    "NeumaticoMedicion",
    "NeumaticoOperacion",
    "NeumaticoOperacionDetalle",
    "NeumaticoSugerencia",
    "NeumaticoImagen",
]