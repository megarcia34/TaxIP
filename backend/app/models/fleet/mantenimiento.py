# app/models/fleet/mantenimiento.py
"""
Modelos de mantenimiento: catalogo global (sistema, subsistema,
componente), config por vehiculo, planes, checklist y registro
legacy de mantenimiento de vehiculo.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# MODELOS DE MANTENIMIENTO - CATALOGO GLOBAL (R25 / m3_038)
# Todos en schema fleet (movidos en m3_040).
# ============================================================

class MantenimientoCatalogoSistema(Base):
    """
    Catalogo global de sistemas de mantenimiento.
    Compartido por todos los tenants. Override por tenant en
    mantenimiento_catalogo_override.
    """
    __tablename__ = "mantenimiento_catalogo_sistema"
    __table_args__ = (
        UniqueConstraint("nombre", name="nombre"),
        Index("idx_catalogo_sistema_orden", "orden"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    subsistemas = relationship(
        "MantenimientoCatalogoSubsistema",
        back_populates="sistema",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MantenimientoCatalogoSubsistema(Base):
    """
    Catalogo global de subsistemas. Pertenece a un sistema.
    """
    __tablename__ = "mantenimiento_catalogo_subsistema"
    __table_args__ = (
        UniqueConstraint("sistema_id", "nombre", name="sistema_id"),
        Index("idx_catalogo_subsistema_sistema", "sistema_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    sistema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_sistema.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    sistema = relationship("MantenimientoCatalogoSistema", back_populates="subsistemas", lazy="selectin")
    componentes = relationship(
        "MantenimientoCatalogoComponente",
        back_populates="subsistema",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MantenimientoCatalogoComponente(Base):
    """
    Catalogo global de componentes. Pertenece a un subsistema.
    """
    __tablename__ = "mantenimiento_catalogo_componente"
    __table_args__ = (
        UniqueConstraint("subsistema_id", "nombre", name="subsistema_id"),
        Index("idx_catalogo_componente_subsistema", "subsistema_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    subsistema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_subsistema.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    subsistema = relationship("MantenimientoCatalogoSubsistema", back_populates="componentes", lazy="selectin")
    controles = relationship(
        "MantenimientoCatalogoControl",
        back_populates="componente",
        lazy="selectin"
    )
    compatibilidades = relationship(
        "MantenimientoCatalogoComponenteCompatibilidad",
        back_populates="componente",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MantenimientoCatalogoControl(Base):
    """
    Catalogo global de controles.
    - componente_id NULL: control generico (aplica a todos los componentes).
    - componente_id NOT NULL: control especifico de un componente.
    """
    __tablename__ = "mantenimiento_catalogo_control"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('visual', 'instrumental', 'documental')",
            name="tipo"
        ),
        Index("idx_catalogo_control_componente", "componente_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    componente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_componente.id", ondelete="CASCADE"),
        nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    unidad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    rango_normal: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    componente = relationship("MantenimientoCatalogoComponente", back_populates="controles", lazy="selectin")


class MantenimientoCatalogoComponenteCompatibilidad(Base):
    """
    Compatibilidad de un componente con marca/modelo/anio/motorizacion.
    Si un campo es NULL, aplica a todos.
    """
    __tablename__ = "mantenimiento_catalogo_componente_compatibilidad"
    __table_args__ = (
        Index("idx_compatibilidad_componente", "componente_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    componente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_componente.id", ondelete="CASCADE"),
        nullable=False
    )
    marca: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    anio_desde: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    anio_hasta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    motorizacion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    componente = relationship("MantenimientoCatalogoComponente", back_populates="compatibilidades", lazy="selectin")


class MantenimientoChecklistInspeccion(Base):
    """
    Checklist de inspeccion diaria (inicio/fin de turno).
    Lo consume la app chofer. Corto, curado, sin diagnosticos.
    """
    __tablename__ = "mantenimiento_checklist_inspeccion"
    __table_args__ = (
        CheckConstraint(
            "tipo_inspeccion IN ('inicio', 'fin', 'ambos')",
            name="tipo_inspeccion"
        ),
        CheckConstraint(
            "tipo_respuesta IN ('ok_novedad', 'nivel', 'estado_visual', 'si_no', 'texto_libre')",
            name="tipo_respuesta"
        ),
        CheckConstraint(
            "severidad_default IS NULL OR severidad_default IN ('baja', 'media', 'alta', 'critica')",
            name="severidad_default"
        ),
        UniqueConstraint("nombre", name="nombre"),
        Index("idx_checklist_inspeccion_orden", "orden"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_inspeccion: Mapped[str] = mapped_column(String(20), nullable=False)
    componente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_componente.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_respuesta: Mapped[str] = mapped_column(String(20), nullable=False)
    opciones: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    severidad_default: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    componente = relationship("MantenimientoCatalogoComponente", lazy="selectin")


class MantenimientoVehiculoConfig(Base):
    """
    Configuracion tecnica del vehiculo para mantenimiento.
    Tabla: fleet.mantenimiento_vehiculo_config (m3_038, movida de public en m3_039_fix)
    """
    __tablename__ = "mantenimiento_vehiculo_config"
    __table_args__ = (
        CheckConstraint(
            "motorizacion IN ('nafta', 'diesel', 'gnc', 'hibrido', 'electrico')",
            name="motorizacion"
        ),
        CheckConstraint(
            "transmision IN ('manual', 'automatica', 'cvt')",
            name="transmision"
        ),
        Index("idx_vehiculo_config_control_base", "control_base_id"),
        {"schema": "fleet"},
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
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    motorizacion: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="nafta | diesel | gnc | hibrido | electrico"
    )
    cilindrada: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transmision: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="manual | automatica | cvt"
    )
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notas_tecnicas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    control_base = relationship("ControlBase", lazy="selectin")
    vehiculo = relationship("Vehiculo", lazy="selectin")


class MantenimientoCatalogoOverride(Base):
    """
    Override del catalogo global por tenant.
    Permite agregar, ocultar o renombrar entidades del catalogo.
    Tabla: fleet.mantenimiento_catalogo_override (m3_039)
    """
    __tablename__ = "mantenimiento_catalogo_override"
    __table_args__ = (
        CheckConstraint(
            "entidad_tipo IN ('sistema', 'subsistema', 'componente', 'control')",
            name="entidad_tipo"
        ),
        CheckConstraint(
            "accion IN ('agregar', 'ocultar', 'renombrar')",
            name="accion"
        ),
        UniqueConstraint(
            "control_base_id", "entidad_tipo", "entidad_id", "accion",
            name="mantenimiento_catalogo_overri_control_base_id_entidad_tipo__key"
        ),
        Index("idx_catalogo_override_control_base", "control_base_id"),
        Index("idx_catalogo_override_entidad", "entidad_tipo", "entidad_id"),
        {"schema": "fleet"},
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
    entidad_tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    entidad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    accion: Mapped[str] = mapped_column(String(20), nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    control_base = relationship("ControlBase", lazy="selectin")


class MantenimientoPlanGrupo(Base):
    """
    Grupo de vehiculos por compatibilidad (marca, modelo, anio, motorizacion).
    Se expande a filas en mantenimiento_plan_vehiculo (R26).
    Tabla: fleet.mantenimiento_plan_grupo (m3_039)
    """
    __tablename__ = "mantenimiento_plan_grupo"
    __table_args__ = (
        UniqueConstraint(
            "control_base_id", "propietario_id", "nombre",
            name="mantenimiento_plan_grupo_control_base_id_propietario_id_nom_key"
        ),
        Index("idx_plan_grupo_control_base", "control_base_id"),
        Index("idx_plan_grupo_propietario", "propietario_id"),
        {"schema": "fleet"},
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
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criterios: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    control_base = relationship("ControlBase", lazy="selectin")
    propietario = relationship("Usuario", foreign_keys=[propietario_id], lazy="selectin")


class MantenimientoVehiculo(Base):
    """Registro de mantenimiento de vehiculo (legacy, reemplazado por mantenimiento_intervencion en R28)."""

    __tablename__ = "mantenimiento_vehiculo"
    __table_args__ = (
        Index("idx_mantenimiento_vehiculo_control_base", "control_base_id"),
        {"schema": "fleet"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    # Columna agregada en R25 (m3_037), control_base_id nullable con backfill desde vehiculo.
    control_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=True,
        doc="Tenant del mantenimiento. Nullable para compatibilidad con legacy."
    )
    tipo_servicio: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    taller_nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    taller_direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    costo: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    kilometraje: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_servicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
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

# ============================================================
# MODELOS DE MANTENIMIENTO - PLANES Y VENCIMIENTOS (R26 / m3_043)
# Tablas creadas en la migración m3_043.
# ============================================================

class MantenimientoPlan(Base):
    """
    Plan de mantenimiento configurable por tenant y propietario.
    """
    __tablename__ = "mantenimiento_plan"
    __table_args__ = (
        UniqueConstraint("control_base_id", "propietario_id", "nombre", name="uq_mantenimiento_plan_tenant_propietario_nombre"),
        CheckConstraint("tipo IN ('preventivo', 'correctivo', 'predictivo')", name="ck_mantenimiento_plan_tipo"),
        Index("idx_plan_control_base", "control_base_id"),
        Index("idx_plan_propietario", "propietario_id"),
        {"schema": "fleet"},
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
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbrales_override: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    items = relationship(
        "MantenimientoPlanItem",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    vehiculos = relationship(
        "MantenimientoPlanVehiculo",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MantenimientoPlanItem(Base):
    """
    Ítems que componen un plan de mantenimiento.
    """
    __tablename__ = "mantenimiento_plan_item"
    __table_args__ = (
        CheckConstraint("prioridad IN ('alta', 'media', 'baja')", name="ck_mantenimiento_plan_item_prioridad"),
        CheckConstraint("criticidad IN ('critica', 'importante', 'normal')", name="ck_mantenimiento_plan_item_criticidad"),
        Index("idx_plan_item_plan", "plan_id"),
        Index("idx_plan_item_componente", "componente_id"),
        {"schema": "fleet"},
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
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_plan.id", ondelete="CASCADE"),
        nullable=False
    )
    componente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_componente.id", ondelete="CASCADE"),
        nullable=False
    )
    control_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_catalogo_control.id", ondelete="SET NULL"),
        nullable=True
    )
    intervalo_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    intervalo_dias: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    intervalo_meses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prioridad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    criticidad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    obligatorio: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    instrucciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    umbrales_override: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    plan = relationship("MantenimientoPlan", back_populates="items", lazy="selectin")
    vencimientos = relationship(
        "MantenimientoVencimiento",
        back_populates="plan_item",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MantenimientoPlanVehiculo(Base):
    """
    Asignación de un plan de mantenimiento a un vehículo específico.
    """
    __tablename__ = "mantenimiento_plan_vehiculo"
    __table_args__ = (
        UniqueConstraint("control_base_id", "plan_id", "vehiculo_id", name="uq_mantenimiento_plan_vehiculo_tenant_plan_vehiculo"),
        Index("idx_plan_vehiculo_plan", "plan_id"),
        Index("idx_plan_vehiculo_vehiculo", "vehiculo_id"),
        {"schema": "fleet"},
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
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_plan.id", ondelete="CASCADE"),
        nullable=False
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    compatibilidad_override: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    compatibilidad_override_motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compatibilidad_override_autor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="SET NULL"),
        nullable=True
    )
    compatibilidad_override_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relaciones
    plan = relationship("MantenimientoPlan", back_populates="vehiculos", lazy="selectin")
    vehiculo = relationship("Vehiculo", lazy="selectin")


class MantenimientoVencimiento(Base):
    """
    Cálculo de cuándo se vence un ítem de un plan para un vehículo específico.
    """
    __tablename__ = "mantenimiento_vencimiento"
    __table_args__ = (
        UniqueConstraint("control_base_id", "vehiculo_id", "plan_item_id", name="uq_mantenimiento_vencimiento_tenant_vehiculo_plan_item"),
        CheckConstraint("estado IN ('normal', 'proximo', 'critico', 'vencido')", name="ck_mantenimiento_vencimiento_estado"),
        Index("idx_vencimiento_vehiculo", "vehiculo_id"),
        Index("idx_vencimiento_estado", "estado"),
        Index("idx_vencimiento_plan_item", "plan_item_id"),
        {"schema": "fleet"},
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
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False
    )
    plan_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.mantenimiento_plan_item.id", ondelete="CASCADE"),
        nullable=False
    )
    km_actual: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    km_proximo: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    fecha_proximo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    vigente: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    calculado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relaciones
    plan_item = relationship("MantenimientoPlanItem", back_populates="vencimientos", lazy="selectin")
    vehiculo = relationship("Vehiculo", lazy="selectin")

__all__ = [
    "MantenimientoCatalogoSistema",
    "MantenimientoCatalogoSubsistema",
    "MantenimientoCatalogoComponente",
    "MantenimientoCatalogoControl",
    "MantenimientoCatalogoComponenteCompatibilidad",
    "MantenimientoChecklistInspeccion",
    "MantenimientoVehiculoConfig",
    "MantenimientoCatalogoOverride",
    "MantenimientoPlanGrupo",
    "MantenimientoVehiculo",
    "MantenimientoPlan",
    "MantenimientoPlanItem",
    "MantenimientoPlanVehiculo",
    "MantenimientoVencimiento",
]