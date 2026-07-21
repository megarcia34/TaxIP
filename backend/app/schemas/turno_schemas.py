# app/schemas/turno_schemas.py
"""
Schemas para gestión de turnos de choferes
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CheckInRequest(BaseModel):
    """Solicitud de Check-in"""
    vehiculo_id: UUID
    km_inicial: float = Field(..., gt=0, description="Kilometraje inicial")
    combustible_inicial: str = Field(..., description="RESERVA, 1/4, 1/2, 3/4, LLENO")


class CheckOutRequest(BaseModel):
    """Solicitud de Check-out"""
    turno_id: UUID
    km_final: float = Field(..., gt=0, description="Kilometraje final")
    combustible_final: str = Field(..., description="RESERVA, 1/4, 1/2, 3/4, LLENO")
    recaudacion_ticketera_calle: float = Field(0, ge=0, description="Efectivo recaudado fuera de la app")


class GastoRequest(BaseModel):
    """Registro de gasto durante turno"""
    turno_id: UUID
    tipo_gasto: str = Field(..., description="COMBUSTIBLE, LUBRICANTE, LAVADO, REPARACION, OTROS")
    monto: float = Field(..., gt=0)
    km_registro: Optional[float] = None
    url_comprobante: Optional[str] = None


class TurnoActivoResponse(BaseModel):
    """Respuesta de turno activo"""
    tiene_turno_activo: bool
    mensaje: str
    turno_id: Optional[str] = None
    vehiculo_id: Optional[str] = None
    patente: Optional[str] = None
    inicio_turno: Optional[datetime] = None
    km_inicial: Optional[float] = None
    combustible_inicial: Optional[str] = None
    estado: Optional[str] = None
    contrato_id: Optional[str] = None


class TurnoResponse(BaseModel):
    """Respuesta de turno"""
    id: str
    vehiculo_id: str
    patente: str
    estado: str
    km_inicial: float
    km_final: Optional[float]
    combustible_inicial: str
    combustible_final: Optional[str]
    inicio_turno: datetime
    fin_turno: Optional[datetime]
    monto_bruto: float
    comision_chofer: float
    utilidad_propietario: float