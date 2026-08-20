# app/models/turno.py
"""
Modelo de Turno/Jornada Laboral del Chofer
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, CheckConstraint, Time, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class TurnoChofer(Base):
    __tablename__ = "turno_chofer"
    __table_args__ = (
        CheckConstraint(
            "EXTRACT(EPOCH FROM (fin_turno - inicio_turno))/3600 <= 24",
            name="check_horas_turno"
        ),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relaciones
    contrato_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.contrato_vehiculo.id"), nullable=False)
    chofer_id = Column(PGUUID(as_uuid=True), ForeignKey("auth.usuario.id"), nullable=False)
    vehiculo_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.vehiculo.id"), nullable=False)
    
    # Estado del turno
    estado = Column(String(20), nullable=False, default='ACTIVO')
    
    # Control de kilometraje y combustible
    km_inicial = Column(Numeric(10,2), nullable=False)
    km_final = Column(Numeric(10,2), nullable=True)
    combustible_inicial = Column(String(20), nullable=False)
    combustible_final = Column(String(20), nullable=True)
    
    # Recaudación
    recaudacion_app_efectivo = Column(Numeric(10,2), default=0)
    recaudacion_app_debito = Column(Numeric(10,2), default=0)
    recaudacion_ticketera_calle = Column(Numeric(10,2), default=0)
    
    # Liquidación calculada
    monto_bruto_calculado = Column(Numeric(10,2), default=0)
    comision_chofer_calculada = Column(Numeric(10,2), default=0)
    utilidad_propietario_calculada = Column(Numeric(10,2), default=0)
    
    # ============================================
    # SNAPSHOTS DE HORARIOS (reemplazan snapshot_turno_contractual)
    # ============================================
    snapshot_hora_inicio = Column(Time, nullable=True)
    snapshot_hora_fin = Column(Time, nullable=True)
    snapshot_duracion_minima_horas = Column(Integer, nullable=True)
    snapshot_permite_extension = Column(Boolean, nullable=True)
    snapshot_hora_fin_extension = Column(Time, nullable=True)
    
    # Se mantiene para compatibilidad
    snapshot_dia_contractual = Column(String(20), nullable=True)
    
    # ⚠️ DEPRECADO: Ya no existe en la base de datos
    # snapshot_turno_contractual = Column(String(20), nullable=True)  # ELIMINADO
    
    # Marcas de tiempo
    inicio_turno = Column(DateTime, default=datetime.now, nullable=False)
    fin_turno = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
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