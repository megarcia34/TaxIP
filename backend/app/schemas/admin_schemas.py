"""
Admin/Dashboard schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class EstadisticasResponse(BaseModel):
    """Dashboard statistics"""
    total_viajes_hoy: int
    total_viajes_mes: int
    choferes_online: int
    choferes_totales: int
    pasajeros_totales: int
    ingresos_hoy: float
    ingresos_mes: float
    calificacion_promedio: float


class RankingChoferResponse(BaseModel):
    """Driver ranking item"""
    chofer_id: UUID
    nombre: str
    calificacion_promedio: float
    total_viajes: int
    imagen_url: Optional[str] = None


class SolicitudActivaResponse(BaseModel):
    """Active ride request response"""
    viaje_id: UUID
    pasajero_nombre: str
    origen: str
    destino: Optional[str] = None
    solicitado_en: datetime
    tiempo_espera_segundos: int