"""
Schemas de mantenimiento para propietario.

Cubre planes, items de plan, asignacion a vehiculos y vencimientos.
"""
from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List


# ============================================================
# PLANES
# ============================================================

class PlanCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    tipo: str = Field(..., pattern="^(preventivo|correctivo|predictivo)$")
    descripcion: Optional[str] = None
    umbrales_override: Optional[dict] = None


class PlanUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    tipo: Optional[str] = Field(None, pattern="^(preventivo|correctivo|predictivo)$")
    descripcion: Optional[str] = None
    umbrales_override: Optional[dict] = None
    activo: Optional[bool] = None


class PlanResponse(BaseModel):
    id: UUID
    nombre: str
    tipo: str
    descripcion: Optional[str]
    umbrales_override: Optional[dict]
    activo: bool
    items_count: int
    vehiculos_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ITEMS DE PLAN
# ============================================================

class PlanItemCreate(BaseModel):
    componente_id: UUID
    control_id: Optional[UUID] = None
    intervalo_km: Optional[int] = Field(None, ge=0)
    intervalo_dias: Optional[int] = Field(None, ge=0)
    intervalo_meses: Optional[int] = Field(None, ge=0)
    prioridad: Optional[str] = Field(None, pattern="^(alta|media|baja)$")
    criticidad: Optional[str] = Field(None, pattern="^(critica|importante|normal)$")
    obligatorio: bool = True
    instrucciones: Optional[str] = None
    umbrales_override: Optional[dict] = None

    @model_validator(mode="after")
    def validar_intervalo(self):
        if not (self.intervalo_km or self.intervalo_dias or self.intervalo_meses):
            raise ValueError(
                "Al menos uno de intervalo_km, intervalo_dias o intervalo_meses debe estar seteado"
            )
        return self


class PlanItemResponse(BaseModel):
    id: UUID
    plan_id: UUID
    componente_id: UUID
    componente_nombre: str
    control_id: Optional[UUID]
    intervalo_km: Optional[int]
    intervalo_dias: Optional[int]
    intervalo_meses: Optional[int]
    prioridad: Optional[str]
    criticidad: Optional[str]
    obligatorio: bool
    instrucciones: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ASIGNACION PLAN-VEHICULO
# ============================================================

class AsignarPlanRequest(BaseModel):
    vehiculo_ids: List[UUID] = Field(..., min_length=1)
    compatibilidad_override: bool = False
    compatibilidad_override_motivo: Optional[str] = None

    @model_validator(mode="after")
    def validar_override(self):
        if self.compatibilidad_override and not self.compatibilidad_override_motivo:
            raise ValueError(
                "compatibilidad_override_motivo es obligatorio si compatibilidad_override=true"
            )
        return self


class AsignarPlanResponse(BaseModel):
    asignados: int
    fallidos: int
    errores: List[dict]


class PlanVehiculoResponse(BaseModel):
    id: UUID
    plan_id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    compatibilidad_override: bool
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# VENCIMIENTOS
# ============================================================

class VencimientoResponse(BaseModel):
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    plan_item_id: UUID
    componente_nombre: str
    km_actual: Optional[float]
    km_proximo: Optional[float]
    fecha_proximo: Optional[date]
    estado: str
    vigente: bool
    calculado_en: datetime
    advertencias: List[str] = []

    class Config:
        from_attributes = True


class ResolverVencimientoRequest(BaseModel):
    km_al_resolver: int = Field(..., ge=0)
    fecha_resolucion: date
    costo: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = None


class VencimientoListResponse(BaseModel):
    total: int
    items: List[VencimientoResponse]