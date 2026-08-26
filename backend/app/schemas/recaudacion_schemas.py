"""
Recaudacion Schemas - Pydantic models for income/collection operations
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field


# ============================================================
# BASE SCHEMAS
# ============================================================

class IngresoBase(BaseModel):
    """Base income schema"""
    turno_id: UUID
    viaje_id: Optional[UUID] = None
    tipo_ingreso: str = Field(..., description="efectivo | electronico | taximetro | manual | corporativo")
    medio_pago: Optional[str] = Field(None, description="efectivo | debito | credito | qr | transferencia | billetera")
    origen: str = Field(..., description="app | taximetro | manual | corporativo")
    monto: Decimal
    moneda: str = "ARS"
    fecha_hora: Optional[datetime] = None
    declarado_por: Optional[UUID] = None
    observaciones: Optional[str] = None
    referencia_pago: Optional[str] = None
    transaccion_id: Optional[UUID] = None


class IngresoCreate(IngresoBase):
    """Schema for creating an income"""
    pass


class IngresoUpdate(BaseModel):
    """Schema for updating an income"""
    monto: Optional[Decimal] = None
    observaciones: Optional[str] = None
    referencia_pago: Optional[str] = None


# ============================================================
# FILTER SCHEMAS
# ============================================================

class IngresoListFilter(BaseModel):
    """Filters for listing incomes"""
    turno_id: Optional[UUID] = None
    viaje_id: Optional[UUID] = None
    tipo_ingreso: Optional[str] = None
    medio_pago: Optional[str] = None
    origen: Optional[str] = None
    estado: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class IngresoResponse(BaseModel):
    """Income response schema"""
    id: UUID
    turno_id: UUID
    viaje_id: Optional[UUID] = None
    tipo_ingreso: str
    medio_pago: Optional[str] = None
    origen: str
    monto: Decimal
    moneda: str
    fecha_hora: datetime
    declarado_por: Optional[UUID] = None
    estado: str
    observaciones: Optional[str] = None
    referencia_pago: Optional[str] = None
    transaccion_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumenIngresosTurno(BaseModel):
    """Summary of incomes for a turno"""
    turno_id: UUID
    total_ingresos: Decimal
    total_aprobados: Decimal
    total_pendientes: Decimal
    total_rechazados: Decimal
    total_efectivo: Decimal
    total_electronico: Decimal
    total_taximetro: Decimal
    total_manual: Decimal
    total_corporativo: Decimal
    cantidad_ingresos: int