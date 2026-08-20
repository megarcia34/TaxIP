# app/schemas/rentabilidad_schemas.py
"""
Schemas para el módulo de Rentabilidad
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


# ============================================================
# SCHEMAS PARA RESPUESTAS
# ============================================================

class RentabilidadViajeResponse(BaseModel):
    """Rentabilidad de un viaje específico"""
    viaje_id: str
    ingreso_bruto: float
    costo_combustible: float
    comision_bancaria: float
    porcentaje_taxip: float
    costo_fijo_por_viaje: float
    canon_por_viaje: float
    utilidad_neta: float
    margen: float
    distancia_km: float
    tiempo_min: float
    metodo_pago: str
    estado: str
    fecha: datetime

    class Config:
        from_attributes = True


class RentabilidadPeriodoResponse(BaseModel):
    """Rentabilidad de un vehículo en un período"""
    total_viajes: int
    ingresos_brutos: float
    costos_variables: float
    comisiones_bancarias: float
    porcentaje_taxip_total: float
    costos_fijos: float
    canon_taxip: float
    utilidad_neta: float
    margen: float
    dias_periodo: int
    viajes: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class RentabilidadVehiculoDetalleResponse(BaseModel):
    """Respuesta detallada de rentabilidad de vehículo"""
    success: bool
    vehiculo: Dict[str, Any]
    periodo: Dict[str, Any]
    resumen: Dict[str, Any]
    promedios: Dict[str, float]
    benchmarking: Dict[str, Any]
    viajes: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class RentabilidadTenantResponse(BaseModel):
    """Rentabilidad consolidada del tenant"""
    success: bool
    periodo: Dict[str, Any]
    consolidado: Dict[str, Any]

    class Config:
        from_attributes = True


class AnalisisMediosPagoResponse(BaseModel):
    """Análisis de medios de pago"""
    medio_pago: str
    total_viajes: int
    total_ingresos: float
    costo_comisiones: float
    porcentaje_ingresos: float

    class Config:
        from_attributes = True


class BenchmarkingResponse(BaseModel):
    """Benchmarking de vehículo vs flota"""
    vehiculo_id: str
    patente: str
    viajes_totales: int
    ingreso_promedio: float
    utilidad_promedio: float
    margen_promedio: float
    posicion_ranking: int
    total_vehiculos: int
    percentil: float

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS PARA RECALCULO
# ============================================================

class RecalcularRentabilidadRequest(BaseModel):
    """Request para recalcular rentabilidad"""
    mes: int = Field(..., ge=1, le=12)
    anio: int = Field(..., ge=2020)
    vehiculo_id: UUID

    class Config:
        from_attributes = True


class RecalcularRentabilidadResponse(BaseModel):
    """Respuesta de recalculo"""
    success: bool
    mensaje: str
    vehiculo_id: str
    mes: int
    anio: int

    class Config:
        from_attributes = True