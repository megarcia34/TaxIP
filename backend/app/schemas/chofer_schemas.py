"""
Driver/Fleet management schemas (for dashboard)
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ChoferCreateRequest(BaseModel):
    """Create a new driver"""
    email: str
    password: str = Field(..., min_length=6)
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    documento: Optional[str] = None
    vehiculo_patente: str
    vehiculo_marca: Optional[str] = None
    vehiculo_modelo: Optional[str] = None
    vehiculo_anio: Optional[int] = None


class ChoferUpdateRequest(BaseModel):
    """Update driver information"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    estado_laboral: Optional[str] = Field(None, description="libre, ocupado, fuera_servicio")
    activo: Optional[bool] = None


class ChoferResponse(BaseModel):
    """Driver response"""
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    estado_laboral: str
    calificacion_promedio: float
    total_viajes: int
    vehiculo_patente: Optional[str] = None
    vehiculo_modelo: Optional[str] = None
    ubicacion_lat: Optional[float] = None
    ubicacion_lng: Optional[float] = None
    ultima_conexion: Optional[datetime] = None
    activo: bool


class ActualizarUbicacionRequest(BaseModel):
    """Update driver GPS location"""
    latitud: float
    longitud: float


class CambiarEstadoLaboralRequest(BaseModel):
    """Change driver work status"""
    estado: str = Field(..., description="libre, ocupado, fuera_servicio")