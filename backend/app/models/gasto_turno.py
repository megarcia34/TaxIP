# app/models/gasto_turno.py
"""
Modelo de Gastos Operativos durante el Turno
Coincide con fleet.gasto_turno
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class GastoTurno(Base):
    __tablename__ = "gasto_turno"
    __table_args__ = (
        CheckConstraint("monto > 0", name="check_monto_positivo"),
        {"schema": "fleet"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turno_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.turno_chofer.id"), nullable=False)
    
    # NUEVOS CAMPOS (Fase 5.1) - coinciden con la BD
    categoria_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fleet.categoria_gasto.id", ondelete="SET NULL"),
        nullable=True
    )
    subcategoria = Column(String(50), nullable=True)
    
    # Campos existentes
    tipo_gasto = Column(String(30), nullable=False)  # Legacy
    monto = Column(Numeric(10,2), nullable=False)
    km_registro = Column(Numeric(10,2), nullable=True)
    url_comprobante = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    turno = relationship(
        "TurnoChofer",
        lazy="selectin"
    )
    categoria = relationship(
        "CategoriaGasto",
        foreign_keys=[categoria_id],
        lazy="selectin"
    )