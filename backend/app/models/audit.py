"""
Audit/Logging Models
Tablas: log_gps, alerta_desvio (schema: audit)
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.database import Base


class LogGps(Base):
    """
    GPS position history for drivers during trips
    Used to replay routes on web dashboard
    """
    __tablename__ = "log_gps"
    __table_args__ = {"schema": "audit"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=False
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.usuario.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    longitud: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    ubicacion: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    velocidad_kmh: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class AlertaDesvio(Base):
    """
    Route deviation alerts (security feature)
    Triggered when driver deviates from expected route
    """
    __tablename__ = "alerta_desvio"
    __table_args__ = {"schema": "audit"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    viaje_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip.viaje_solicitado.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    longitud: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    distancia_desvio_metros: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    ruta_esperada_json: Mapped[str] = mapped_column(Text, nullable=True)
    notificado: Mapped[bool] = mapped_column(default=False)
    resuelto: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)