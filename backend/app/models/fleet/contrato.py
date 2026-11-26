# app/models/fleet/contrato.py
"""
Contratos de vehiculos y QRs de contrato.

Movido desde fleet/_legacy.py en R25.5 Fase 2 paso 2.

NOTA: ContratoVehiculo tenia un duplicado interno de columnas en
_legacy.py (version Column clasico + version Mapped). Se consolido
en este archivo dejando solo la version Mapped + la columna
tratamiento_gastos (que solo existia en la version Column) + el
__table_args__ completo (11 CHECKs + 6 indices).

Sin cambios funcionales: el resultado final del ORM es identico
(columnas Mapped + tratamiento_gastos + CHECKs/indices del
__table_args__ + FKs con CASCADE).
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContratoVehiculo(Base):
    __tablename__ = "contrato_vehiculo"
    __table_args__ = (
        Index("idx_contrato_estado", "estado_contrato"),
        Index("ix_contrato_vehiculo_hora_inicio", "hora_inicio"),
        Index("ix_contrato_vehiculo_hora_fin", "hora_fin"),
        Index("idx_contrato_chofer_historial", "chofer_id", "fecha_inicio"),
        Index("idx_contrato_vehiculo_historial", "vehiculo_id", "fecha_inicio"),
        Index(
            "idx_contrato_propietario_activo",
            "propietario_id",
            "activo",
            postgresql_where=text("activo = true"),
        ),
        CheckConstraint(
            "tratamiento_dia_no_trabajado IN ('POR_DISPONIBILIDAD', 'NO_COBRA', 'DESCUENTO_PROPORCIONAL')",
            name="chk_contrato_tratamiento_dia",
        ),
        CheckConstraint(
            "modalidad_computo IN ('DIARIO', 'SEMANAL', 'MENSUAL')",
            name="chk_contrato_modalidad_computo",
        ),
        CheckConstraint(
            "compensacion_km IN ('DIARIA', 'ACUMULADA', 'COMPENSADA')",
            name="compensacion_km",
        ),
        CheckConstraint(
            "estado_contrato IN ('PENDIENTE_CONFIGURACION', 'PROGRAMADO', 'ACTIVO', 'FINALIZADO')",
            name="estado",
        ),
        CheckConstraint(
            "(permite_extension = false AND hora_fin_extension IS NULL) OR (permite_extension = true AND hora_fin_extension IS NOT NULL)",
            name="extension_valida",
        ),
        CheckConstraint(
            "dia_inicio_semana IN ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo') OR dia_inicio_semana IS NULL",
            name="dia_inicio_semana",
        ),
        CheckConstraint(
            "(tipo_contrato = 'PORCENTAJE' AND porcentaje_chofer IS NOT NULL AND porcentaje_chofer >= 0 AND porcentaje_chofer <= 100) OR (tipo_contrato <> 'PORCENTAJE' AND porcentaje_chofer IS NULL)",
            name="porcentaje",
        ),
        CheckConstraint(
            "(estado_contrato = 'ACTIVO' AND activo = true) OR (estado_contrato IN ('PENDIENTE_CONFIGURACION', 'PROGRAMADO', 'FINALIZADO') AND activo = false)",
            name="activo_estado",
        ),
        CheckConstraint(
            "hora_fin IS NULL OR hora_inicio IS NULL OR hora_fin <> hora_inicio",
            name="horario_valido",
        ),
        CheckConstraint(
            "duracion_minima_horas IS NULL OR duracion_minima_horas >= 1",
            name="duracion_minima",
        ),
        CheckConstraint(
            "tipo_contrato <> 'AUTO_GESTION' OR propietario_id = chofer_id",
            name="auto_gestion",
        ),
        {"schema": "fleet"},
    )

    # --- Columnas (version Mapped consolidada) ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id", ondelete="CASCADE"),
        nullable=False,
    )
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"),
        nullable=False,
    )
    chofer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )

    tipo_contrato: Mapped[str] = mapped_column(String(20), nullable=False)

    # Horarios flexibles
    hora_inicio: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    duracion_minima_horas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=6
    )
    permite_extension: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    hora_fin_extension: Mapped[Optional[datetime.time]] = mapped_column(
        Time, nullable=True
    )

    porcentaje_chofer: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    monto_diario: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    estado_contrato: Mapped[Optional[str]] = mapped_column(
        String(30),
        default="PENDIENTE_CONFIGURACION",
        nullable=True,
        comment="PENDIENTE_CONFIGURACION | ACTIVO | INACTIVO | RECHAZADO",
    )
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, nullable=True
    )

    canon_diario: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    km_incluidos_dia: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    valor_km_excedente: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    modalidad_computo: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default="DIARIO"
    )
    tratamiento_dia_no_trabajado: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, default="POR_DISPONIBILIDAD"
    )
    dias_contractuales: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    dia_inicio_semana: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    compensacion_km: Mapped[str] = mapped_column(
        String(20), nullable=False, default="DIARIA"
    )

    # Columna presente solo en la version Column clasico del _legacy.py.
    # Se conserva para mantener alineacion con la DB (varchar(50), nullable).
    tratamiento_gastos: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="DESPUES"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    # --- Relationships ---
    control_base: Mapped["ControlBase"] = relationship("ControlBase", lazy="selectin")
    turnos = relationship("TurnoChofer", lazy="selectin", cascade="all, delete-orphan")
    propietario = relationship("Usuario", foreign_keys=[propietario_id])
    chofer = relationship("Usuario", foreign_keys=[chofer_id])
    vehiculo = relationship(
        "Vehiculo", foreign_keys=[vehiculo_id], back_populates="contratos"
    )


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
    __table_args__ = (
        Index("idx_contrato_qr_contrato", "contrato_id"),
        Index("idx_contrato_qr_token", "token"),
        Index(
            "idx_contrato_qr_activos",
            "contrato_id",
            "fecha_expiracion",
            postgresql_where=text("activo = true"),
        ),
        {
            "schema": "fleet",
            "comment": "QRs generados para pagos y trazabilidad de viajes",
        },
    )

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


__all__ = ["ContratoVehiculo", "ContratoQr"]