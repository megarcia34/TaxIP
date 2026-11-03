import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Numeric, Text, 
    CheckConstraint, Index, text # <-- text es necesario para server_default
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base

class GastoTurno(Base):
    __tablename__ = "gasto_turno"
    __table_args__ = (
        CheckConstraint("monto > 0", name="monto_check"),
        Index("idx_gasto_turno_turno", "turno_id"),
        Index("ix_gasto_turno_categoria_id", "categoria_id"),
        {"schema": "fleet"},
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turno_id = Column(PGUUID(as_uuid=True), ForeignKey("fleet.turno_chofer.id"), nullable=False)

    categoria_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fleet.categoria_gasto.id", ondelete="SET NULL"),
        nullable=True
    )
    subcategoria = Column(String(50), nullable=True)

    tipo_gasto = Column(String(30), nullable=False)
    monto = Column(Numeric, nullable=False)
    km_registro = Column(Numeric, nullable=True)
    url_comprobante = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # NUEVOS R24 (Alineados a la migracion m3_030)
    estado_aprobacion = Column(
        String(20), 
        nullable=True, 
        server_default=text("'pendiente'"),
        comment="Estado de aprobacion del gasto por parte del propietario: pendiente, aprobado, rechazado"
    )
    descripcion = Column(Text, nullable=True)

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