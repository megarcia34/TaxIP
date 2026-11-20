# app/models/turno.py
"""
Modelo de Turno/Jornada Laboral del Chofer
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, Time, Integer, Index,CheckConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base

class TurnoChofer(Base):
    __tablename__ = "turno_chofer"
    __table_args__ = (
        Index("idx_turno_chofer_chofer_fecha", "chofer_id", "inicio_turno"),
        Index("idx_turno_chofer_estado", "estado"),
        Index("idx_turno_chofer_fin", "fin_turno"),
        Index(
            "idx_turno_chofer_vehiculo_activo",
            "vehiculo_id",
            postgresql_where=text("(estado)::text = 'ACTIVO'::text"),
        ),
                Index(
            "idx_turno_chofer_km_sospechoso",
            "km_sospechoso",
            postgresql_where=text("km_sospechoso = true"),
        ),

        CheckConstraint(
            "estado IN ('ACTIVO', 'PENDIENTE_CONFIRMACION', 'CON_DIFERENCIAS_PENDIENTES', 'EN_DISPUTA', 'CONCILIADO', 'CONCILIADO_AUTOMATICO', 'LIQUIDADO', 'CERRADO', 'CANCELADO')",
            name="estado",
        ),
        {"schema": "fleet"},
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    contrato_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.contrato_vehiculo.id"), nullable=False)
    chofer_id = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id"), nullable=False)
    vehiculo_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)

    # Estado del turno
    estado = Column(String(30), nullable=False, default='ACTIVO')

    # Control de kilometraje y combustible
    km_inicial = Column(Numeric, nullable=False)
    km_final = Column(Numeric, nullable=True)
    combustible_inicial = Column(String(20), nullable=False)
    combustible_final = Column(String(20), nullable=True)

    # Efectivo declarado por el chofer al cerrar el turno
    efectivo_declarado = Column(
        Numeric,
        nullable=True,
        comment="Efectivo que el chofer declara haber entregado al propietario al cerrar el turno",
    )

    # ============================================
    # SNAPSHOTS DE HORARIOS
    # ============================================
    snapshot_hora_inicio = Column(Time, nullable=True)
    snapshot_hora_fin = Column(Time, nullable=True)
    snapshot_duracion_minima_horas = Column(Integer, nullable=True)
    snapshot_permite_extension = Column(Boolean, nullable=True)
    snapshot_hora_fin_extension = Column(Time, nullable=True)
    snapshot_dia_contractual = Column(
        String(20),
        nullable=True,
        comment="Día contractual al inicio del turno (ej. LUNES, MARTES). Snapshot inmutable."
    )

    # ============================================
    # MARCAS DE TIEMPO
    # ============================================
    inicio_turno = Column(DateTime, default=datetime.now, nullable=False)
    fin_turno = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ============================================
    # CONCILIACION (m3_031 / m3_036)
    # ============================================
    conciliado_por = Column(
        PGUUID(as_uuid=True),
        ForeignKey("auth.usuario.id"),
        nullable=True,
        comment="Usuario que concilió el turno (propietario o sistema)"
    )
    conciliado_en = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora en que se cerró la conciliación"
    )
    tipo_conciliacion = Column(
        String(30),
        nullable=True,
        server_default="AUTOMATICA",
        comment="Tipo de conciliación aplicada al cerrar el turno (AUTOMATICA, MANUAL, etc.)"
    )

    # ============================================
    # MANTENIMIENTO (m3_037)
    # ============================================
    km_sospechoso = Column(
        Boolean,
        nullable=False,
        server_default="false",
        doc="True si el turno tiene km inconsistente. El motor de km lo excluye.",
    )

    # ============================================
    # RELATIONSHIPS
    # ============================================
    contrato = relationship(
        "ContratoVehiculo",
        lazy="selectin"
    )

    chofer = relationship(
        "Usuario",
        foreign_keys=[chofer_id],
        lazy="selectin"
    )

    vehiculo = relationship(
        "Vehiculo",
        lazy="selectin"
    )

    gastos = relationship(
        "GastoTurno",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # ============================================
    # NUEVAS RELATIONSHIPS
    # ============================================
    ingresos = relationship(
        "IngresoTurno",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    viajes = relationship(
        "ViajeSolicitado",
        lazy="selectin"
    )

    liquidaciones = relationship(
        "Liquidacion",
        lazy="selectin"
    )