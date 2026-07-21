"""
Schemas para gestión de configuraciones de tarifa
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime, time
import re


class ConfiguracionTarifaBase(BaseModel):
    """Base para configuración de tarifa"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='ignore',
        from_attributes=True
    )
    
    control_base_id: UUID = Field(..., description="ID del tenant")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre de la configuración")
    
    modo_calculo: str = Field(default="por_km", description="Modo de cálculo: ficha_argentina, por_km, por_minuto, mixto")
    
    tarifa_base: float = Field(default=0, ge=0, description="Tarifa base (bajada)")
    precio_por_km: float = Field(default=0, ge=0, description="Precio por kilómetro")
    precio_por_minuto: float = Field(default=0, ge=0, description="Precio por minuto")
    
    distancia_por_ficha: float = Field(default=100, ge=1, description="Distancia en metros por ficha")
    precio_por_ficha: float = Field(default=0, ge=0, description="Precio por ficha")
    precio_por_minuto_espera: float = Field(default=0, ge=0, description="Precio por minuto de espera")
    
    recargo_nocturno: float = Field(default=1.0, ge=1.0, description="Factor de recargo nocturno")
    recargo_feriado: float = Field(default=1.0, ge=1.0, description="Factor de recargo feriado")
    recargo_domingo: float = Field(default=1.0, ge=1.0, description="Factor de recargo domingo")
    
    hora_inicio_nocturno: str = Field(default="22:00", description="Hora de inicio del recargo nocturno (HH:MM)")
    hora_fin_nocturno: str = Field(default="06:00", description="Hora de fin del recargo nocturno (HH:MM)")
    
    moneda: str = Field(default="ARS", max_length=3, description="Moneda")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")
    activo: bool = Field(default=True, description="Si está activo")

    @field_validator('hora_inicio_nocturno', 'hora_fin_nocturno', mode='before')
    @classmethod
    def convertir_hora_a_string(cls, v):
        if v is None:
            return "00:00"
        if isinstance(v, time):
            return v.strftime("%H:%M")
        if isinstance(v, str):
            if len(v) > 5 and v[2] == ':':
                v = v[:5]
            if re.match(r'^\d{2}:\d{2}$', v):
                return v
            parts = v.split(':')
            if len(parts) >= 2:
                return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        return "00:00"


class ConfiguracionTarifaCreate(ConfiguracionTarifaBase):
    """Schema para crear configuración"""
    pass


class ConfiguracionTarifaUpdate(BaseModel):
    """Schema para actualizar configuración"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='ignore'
    )
    
    nombre: Optional[str] = Field(None, max_length=100)
    modo_calculo: Optional[str] = Field(None, description="Modo de cálculo")
    tarifa_base: Optional[float] = Field(None, ge=0)
    precio_por_km: Optional[float] = Field(None, ge=0)
    precio_por_minuto: Optional[float] = Field(None, ge=0)
    distancia_por_ficha: Optional[float] = Field(None, ge=1)
    precio_por_ficha: Optional[float] = Field(None, ge=0)
    precio_por_minuto_espera: Optional[float] = Field(None, ge=0)
    recargo_nocturno: Optional[float] = Field(None, ge=1.0)
    recargo_feriado: Optional[float] = Field(None, ge=1.0)
    recargo_domingo: Optional[float] = Field(None, ge=1.0)
    
    # ✅ CAMBIADO: Acepta str o time
    hora_inicio_nocturno: Optional[Union[str, time]] = Field(None)
    hora_fin_nocturno: Optional[Union[str, time]] = Field(None)
    
    moneda: Optional[str] = Field(None, max_length=3)
    descripcion: Optional[str] = Field(None)
    activo: Optional[bool] = Field(None)

    @field_validator('hora_inicio_nocturno', 'hora_fin_nocturno', mode='before')
    @classmethod
    def convertir_a_time(cls, v):
        """Convierte string HH:MM o HH:MM:SS a time object"""
        if v is None:
            return None
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            # ✅ Recortar segundos si existen
            if len(v) > 5 and ':' in v:
                v = v[:5]
            parts = v.split(':')
            if len(parts) >= 2:
                try:
                    hora = int(parts[0])
                    minuto = int(parts[1])
                    if 0 <= hora <= 23 and 0 <= minuto <= 59:
                        return time(hora, minuto)
                except ValueError:
                    pass
        # ✅ Si no se pudo convertir, devolver None
        return None


class ConfiguracionTarifaResponse(ConfiguracionTarifaBase):
    """Schema para respuesta de configuración"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    tenant_nombre: Optional[str] = Field(None, description="Nombre del tenant")


class ConfiguracionTarifaListResponse(BaseModel):
    """Schema para lista paginada de configuraciones"""
    model_config = ConfigDict(from_attributes=True)
    
    items: List[ConfiguracionTarifaResponse]
    total: int
    limit: int
    offset: int