# app/models/fleet/vehiculo.py
"""
Vehiculos, fotos, propietarios y relaciones propietario-vehiculo.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 8.
Sin cambios funcionales.

NOTA: los comment= de las columnas se mantienen tal cual (con tildes)
porque diff.py los compara contra la DB. La correccion de encoding
en comments requiere migracion (R26+). Solo se corrigieron docstrings
y comentarios de seccion (ASCII puro segun N10).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
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
    func,
    text,
    
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehiculo(Base):
    """Vehicle information with QR fijo"""
    __tablename__ = "vehiculo"
    __table_args__ = (
        Index("idx_vehiculo_qr", "qr_uuid"),
        Index("ix_vehiculo_capacidad_baul", "capacidad_baul"),
        Index("ix_vehiculo_estado_vehiculo", "estado_vehiculo"),
        CheckConstraint(
            "estado_vehiculo IN ('regular', 'bueno', 'excelente')",
            name="ck_vehiculo_estado_vehiculo"
        ),
        CheckConstraint(
            "capacidad_baul IN ('sin_baul', 'baul_chico', 'baul_mediano', 'baul_grande', 'van_carga')",
            name="ck_vehiculo_capacidad_baul"
        ),
        CheckConstraint(
            "estado_aprobacion IN ('pendiente', 'en_revision', 'aprobado', 'rechazado')",
            name="estado_aprobacion"
        ),
        CheckConstraint(
            "estado_operativo IN ('sin_verificar', 'en_servicio', 'servicio_limitado', 'fuera_servicio')",
            name="estado_operativo"
        ),
        Index("idx_vehiculo_estado_operativo", "estado_operativo"),
        {"schema": "fleet"},
    )

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
    patente: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
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

    # ============================================================
    # COLUMNAS AGREGADAS EN R19 (aprobacion y ciclo de vida)
    # ============================================================
    estado_aprobacion: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pendiente",
        doc="Estado de aprobacion del vehiculo por el tenant",
    )
    documentacion_completa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        doc="True cuando estan cargados los 4 documentos obligatorios",
    )
    fecha_vencimiento_taxi: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Fecha de vencimiento del taxi por antiguedad maxima",
    )
    override_antiguedad: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        doc="True si el tenant aprobo por excepcion un vehiculo vencido",
    )
    en_revision_desde: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Inicio del plazo de revision tras cambio de documentos",
    )
    en_revision_expira_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Fin del plazo de revision; si vence, se bloquea el vehiculo",
    )
    aprobado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
        doc="Admin del tenant que aprobo el vehiculo",
    )
    aprobado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Fecha y hora de aprobacion",
    )
    rechazado_por: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
        doc="Admin del tenant que rechazo el vehiculo",
    )
    rechazado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Fecha y hora de rechazo",
    )
    motivo_rechazo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Motivo del rechazo del vehiculo",
    )

    # ============================================================
    # COLUMNAS AGREGADAS EN R25 (m3_037)
    # 3 columnas para estado operativo y verificacion tecnica.
    # ============================================================
    estado_operativo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="sin_verificar",
        doc="Estado operativo: sin_verificar | en_servicio | servicio_limitado | fuera_servicio"
    )
    habilitado_para_operar: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        doc="Decision administrativa del propietario. Default true para no bloquear flota existente."
    )
    verificacion_tecnica_pendiente: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        doc="True si el vehiculo nunca fue verificado tecnicamente"
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


# ============================================================
# MODELO FOTO_VEHICULO
# ============================================================

class FotoVehiculo(Base):
    """
    Vehicle photos (Cloudinary)
    Tabla: fleet.foto_vehiculo
    """
    __tablename__ = "foto_vehiculo"
    __table_args__ = (
        Index("idx_foto_vehiculo_vehiculo", "vehiculo_id"),
        Index("idx_foto_vehiculo_principal", "vehiculo_id", "es_principal"),
        {"schema": "fleet"},
    )

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


class PropietarioVehiculo(Base):
    __tablename__ = "propietario_vehiculo"
    __table_args__ = (
        Index("unique_propietario_vehiculo_activo", "propietario_id", "vehiculo_id", unique=True),
        Index("idx_propietario_vehiculo_vehiculo", "vehiculo_id", "activo"),
        Index("idx_propietario_vehiculo_propietario", "propietario_id", "activo"),
        {"schema": "fleet"},
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


class RelacionPropietarioVehiculo(Base):
    """
    Relacion propietario-vehiculo con porcentaje de participacion.
    Tabla: fleet.relacion_propietario_vehiculo

    Existente en DB, faltante en ORM (Fase 4c, R11).
    """
    __tablename__ = "relacion_propietario_vehiculo"
    __table_args__ = {"schema": "fleet"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id"),
        nullable=True,
    )
    propietario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
    )
    porcentaje_participacion: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        server_default=text("100"),
    )
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        server_default=text("true"),
    )


__all__ = [
    "Vehiculo",
    "FotoVehiculo",
    "PropietarioVehiculo",
    "RelacionPropietarioVehiculo",
]