"""
Owner module schemas (vehicle expenses and maintenance)
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class GastoVehiculoRequest(BaseModel):
    """Register vehicle expense"""
    vehiculo_id: UUID
    tipo_gasto: str = Field(..., description="combustible, mantenimiento, reparacion, seguro, impuesto")
    monto: float = Field(..., gt=0)
    descripcion: Optional[str] = None
    kilometraje: Optional[int] = None
    comprobante_url: Optional[str] = None
    fecha_gasto: date


class GastoVehiculoResponse(BaseModel):
    """Vehicle expense response"""
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    tipo_gasto: Optional[str] = None
    monto: float
    descripcion: Optional[str] = None
    kilometraje: Optional[int] = None
    comprobante_url: Optional[str] = None
    fecha_gasto: Optional[date] = None
    created_at: datetime


class MantenimientoVehiculoRequest(BaseModel):
    """Register vehicle maintenance"""
    vehiculo_id: UUID
    tipo_servicio: str
    taller_nombre: str
    taller_direccion: Optional[str] = None
    costo: Optional[float] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_servicio: date


class MantenimientoVehiculoResponse(BaseModel):
    """Vehicle maintenance response"""
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    tipo_servicio: Optional[str] = None
    taller_nombre: Optional[str] = None
    taller_direccion: Optional[str] = None
    costo: Optional[float] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_servicio: Optional[date] = None
    created_at: datetime


class ResumenGastosResponse(BaseModel):
    """Expense summary response"""
    total_gastos: float
    por_tipo: dict
    por_vehiculo: list
    periodo_desde: date
    periodo_hasta: date

    # =====================================================
# CONTRATOS
# =====================================================
from pydantic import BaseModel, Field, condecimal
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class ContratoCreate(BaseModel):
    vehiculo_id: UUID
    chofer_id: UUID
    tipo_contrato: str = Field(..., pattern="^(AUTO_GESTION|PORCENTAJE|CANON_FIJO)$")
    turno_asignado: str = Field(..., pattern="^(DIURNO|NOCTURNO|COMPLETO)$")
    porcentaje_chofer: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    monto_diario: Optional[condecimal(max_digits=10, decimal_places=2)] = None

class ContratoResponse(BaseModel):
    id: UUID
    vehiculo_id: UUID
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    chofer_id: UUID
    chofer_nombre: Optional[str] = None
    chofer_apellido: Optional[str] = None
    tipo_contrato: str
    turno_asignado: str
    porcentaje_chofer: Optional[Decimal] = None
    monto_diario: Optional[Decimal] = None
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    activo: bool

    class Config:
        from_attributes = True

class ChoferDisponibleResponse(BaseModel):
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    calificacion_promedio: Optional[Decimal] = None
    total_calificaciones: Optional[int] = None

# ============================================
# FASE 2: INGRESOS
# ============================================

class RecaudacionManualRequest(BaseModel):
    vehiculo_id: UUID
    monto: float = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = None

class RegistrarCanonRequest(BaseModel):
    contrato_id: UUID
    fecha_pago: date
    monto: float = Field(..., gt=0)

class IngresoResponse(BaseModel):
    id: UUID
    tipo: str  # viaje, recaudacion_manual, canon
    monto: float
    fecha: str
    descripcion: Optional[str] = None
    vehiculo_patente: Optional[str] = None
    chofer_nombre: Optional[str] = None