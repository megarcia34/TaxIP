# app/models/liquidacion.py
"""
Modelos de Liquidación — Motor Base (D3) + D7 (Aprobación y Pagos)
Tablas: liquidacion, liquidacion_detalle, liquidacion_estado_historial, liquidacion_ajuste
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, JSON, Integer, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.database import Base


class Liquidacion(Base):
    __tablename__ = "liquidacion"
    __table_args__ = (
        Index("ix_liquidacion_turno_id", "turno_id"),
        Index("ix_liquidacion_contrato_id", "contrato_id"),
        Index("ix_liquidacion_vehiculo_id", "vehiculo_id"),
        Index("ix_liquidacion_chofer_id", "chofer_id"),
        Index("ix_liquidacion_propietario_id", "propietario_id"),
        Index("ix_liquidacion_control_base_id", "control_base_id"),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    control_base_id = Column(PGUUID(as_uuid=True), ForeignKey("tenant.control_base.id", ondelete="CASCADE"), nullable=False)

    turno_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.turno_chofer.id", ondelete="CASCADE"), nullable=False)
    contrato_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.contrato_vehiculo.id", ondelete="CASCADE"), nullable=False)
    vehiculo_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.vehiculo.id", ondelete="CASCADE"), nullable=False)
    chofer_id = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)
    propietario_id = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="CASCADE"), nullable=False)

    tipo_contrato = Column(String(20), nullable=False)
    periodo_desde = Column(DateTime, nullable=False)
    periodo_hasta = Column(DateTime, nullable=False)

    monto_bruto = Column(Numeric(12, 2), default=0)
    total_gastos = Column(Numeric(12, 2), default=0)
    comision_chofer = Column(Numeric(12, 2), default=0)
    canon = Column(Numeric(12, 2), default=0)
    
    # ============================================
    # NUEVOS CAMPOS para ALQUILER
    # ============================================
    km_excedentes = Column(Numeric(12, 2), default=0, nullable=False)
    cargo_km_excedentes = Column(Numeric(12, 2), default=0, nullable=False)
    saldo_chofer = Column(Numeric(12, 2), default=0, nullable=False)
    saldo_propietario = Column(Numeric(12, 2), default=0, nullable=False)
    
    total_chofer = Column(Numeric(12, 2), default=0)
    total_propietario = Column(Numeric(12, 2), default=0)

    estado = Column(String(20), default='BORRADOR')
    version = Column(Integer, default=1)
    calculada_en = Column(DateTime, default=datetime.now)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ============================================
    # CAMPOS PARA D7 - APROBACIÓN Y PAGOS
    # ============================================
    aprobada_por = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="SET NULL"), nullable=True)
    aprobada_en = Column(DateTime, nullable=True)
    rechazada_por = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="SET NULL"), nullable=True)
    rechazada_en = Column(DateTime, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    pagada_por = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="SET NULL"), nullable=True)
    pagada_en = Column(DateTime, nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    referencia_pago = Column(String(100), nullable=True)

    # Relaciones
    turno = relationship("TurnoChofer", lazy="selectin")
    contrato = relationship("ContratoVehiculo", lazy="selectin")
    vehiculo = relationship("Vehiculo", lazy="selectin")
    chofer = relationship("Usuario", foreign_keys=[chofer_id], lazy="selectin")
    propietario = relationship("Usuario", foreign_keys=[propietario_id], lazy="selectin")
    
    # D7 - Relaciones para aprobación y pagos
    usuario_aprobador = relationship("Usuario", foreign_keys=[aprobada_por], lazy="selectin")
    usuario_rechazador = relationship("Usuario", foreign_keys=[rechazada_por], lazy="selectin")
    usuario_pagador = relationship("Usuario", foreign_keys=[pagada_por], lazy="selectin")

    detalles = relationship("LiquidacionDetalle", lazy="selectin", cascade="all, delete-orphan")
    historial_estados = relationship("LiquidacionEstadoHistorial", lazy="selectin", cascade="all, delete-orphan")
    ajustes = relationship("LiquidacionAjuste", lazy="selectin", cascade="all, delete-orphan")


class LiquidacionDetalle(Base):
    __tablename__ = "liquidacion_detalle"
    __table_args__ = (
        Index("ix_liquidacion_detalle_liquidacion_id", "liquidacion_id"),
        Index("ix_liquidacion_detalle_fuente_id", "fuente_id"),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liquidacion_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.liquidacion.id", ondelete="CASCADE"), nullable=False)

    tipo_linea = Column(String(20), nullable=False)
    concepto = Column(String(255), nullable=True)
    fuente_tipo = Column(String(50), nullable=True)
    fuente_id = Column(PGUUID(as_uuid=True), nullable=True)
    monto = Column(Numeric(12, 2), nullable=False)
    signo = Column(String(5), nullable=False)
    meta_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    liquidacion = relationship("Liquidacion", lazy="selectin")


class LiquidacionEstadoHistorial(Base):
    __tablename__ = "liquidacion_estado_historial"
    __table_args__ = (
        Index("ix_liquidacion_estado_historial_liquidacion_id", "liquidacion_id"),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liquidacion_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.liquidacion.id", ondelete="CASCADE"), nullable=False)
    control_base_id = Column(PGUUID(as_uuid=True), ForeignKey("tenant.control_base.id", ondelete="CASCADE"), nullable=False)

    estado_anterior = Column(String(20), nullable=True)
    estado_nuevo = Column(String(20), nullable=False)
    cambiado_por = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="SET NULL"), nullable=True)
    motivo = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    liquidacion = relationship("Liquidacion", lazy="selectin")
    usuario = relationship("Usuario", foreign_keys=[cambiado_por], lazy="selectin")


class LiquidacionAjuste(Base):
    __tablename__ = "liquidacion_ajuste"
    __table_args__ = (
        Index("ix_liquidacion_ajuste_liquidacion_id", "liquidacion_id"),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liquidacion_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.liquidacion.id", ondelete="CASCADE"), nullable=False)
    control_base_id = Column(PGUUID(as_uuid=True), ForeignKey("tenant.control_base.id", ondelete="CASCADE"), nullable=False)

    tipo_ajuste = Column(String(20), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    motivo = Column(Text, nullable=True)
    usuario_id = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    liquidacion = relationship("Liquidacion", lazy="selectin")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], lazy="selectin")