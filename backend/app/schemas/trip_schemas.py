"""
Trip Schemas - Pydantic models for trip operations
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field


# ============================================================
# BASE SCHEMAS
# ============================================================

class ViajeBase(BaseModel):
    """Base trip schema"""
    control_base_id: UUID
    pasajero_id: UUID
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    precio_estimado: Optional[Decimal] = None
    moneda: str = "ARS"
    tiempo_estimado_segundos: Optional[int] = None
    distancia_metros: Optional[int] = None
    fecha_programada: Optional[datetime] = None
    comercio_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    nombre_pasajero: Optional[str] = None
    notas: Optional[str] = None


class ViajeCreate(ViajeBase):
    """Schema for creating a trip"""
    pass


class ViajeUpdate(BaseModel):
    """Schema for updating a trip"""
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    precio_estimado: Optional[Decimal] = None
    precio_final: Optional[Decimal] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


# ============================================================
# CYCLE OF LIFE SCHEMAS
# ============================================================

class ViajeAceptar(BaseModel):
    """Schema for accepting a trip"""
    chofer_id: UUID
    vehiculo_id: UUID
    chofer_vehiculo_id: UUID


class ViajeIniciar(BaseModel):
    """Schema for starting a trip"""
    pass


class ViajeFinalizar(BaseModel):
    """Schema for finalizing a trip"""
    precio_final: Optional[Decimal] = None


class ViajeCancelar(BaseModel):
    """Schema for canceling a trip"""
    cancelado_por: str = "pasajero"  # pasajero | chofer | sistema
    motivo: str


# ============================================================
# FILTER SCHEMAS
# ============================================================

class ViajeListFilter(BaseModel):
    """Filters for listing trips"""
    control_base_id: Optional[UUID] = None
    pasajero_id: Optional[UUID] = None
    chofer_id: Optional[UUID] = None
    estado: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class ViajeResponse(BaseModel):
    """Trip response schema"""
    id: UUID
    control_base_id: UUID
    pasajero_id: UUID
    chofer_id: Optional[UUID] = None
    vehiculo_id: Optional[UUID] = None
    turno_id: Optional[UUID] = None
    estado: str
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    precio_estimado: Optional[Decimal] = None
    precio_final: Optional[Decimal] = None
    moneda: str
    solicitado_en: datetime
    aceptado_en: Optional[datetime] = None
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None
    cancelado_en: Optional[datetime] = None
    cancelado_por: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ViajeListResponse(BaseModel):
    """List of trips response"""
    items: List[ViajeResponse]
    total: int
    limit: int
    offset: int