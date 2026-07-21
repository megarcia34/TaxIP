"""
Schemas para gestión de reservas
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class TipoVehiculoEnum(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    VAN = "van"
    MINIVAN = "minivan"


class EstadoReservaEnum(str, Enum):
    RESERVADO = "reservado"
    DESPACHADO = "despachado"
    VEHICULO_LLEGO = "vehiculo_llego"
    PASAJERO_A_BORDO = "pasajero_a_bordo"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class MetodoPagoEnum(str, Enum):
    EFECTIVO = "efectivo"
    QR = "qr"
    TRANSFERENCIA = "transferencia"


class ParadaIntermedia(BaseModel):
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion: Optional[str] = None


class ReservaBase(BaseModel):
    """Base para reserva"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='ignore'
    )
    
    pasajero_nombre: Optional[str] = Field(None, max_length=255)
    pasajero_telefono: Optional[str] = Field(None, max_length=50)
    direccion_origen: str = Field(..., min_length=3)
    latitud_origen: Optional[float] = None
    longitud_origen: Optional[float] = None
    direccion_destino: str = Field(..., min_length=3)
    latitud_destino: Optional[float] = None
    longitud_destino: Optional[float] = None
    paradas_intermedias: Optional[List[ParadaIntermedia]] = Field(default_factory=list)
    tipo_vehiculo: TipoVehiculoEnum = TipoVehiculoEnum.STANDARD
    nota_conductor: Optional[str] = Field(None, max_length=500)
    es_programado: bool = False
    fecha_programada: Optional[datetime] = None
    metodo_pago: MetodoPagoEnum = MetodoPagoEnum.EFECTIVO
    cantidad_pasajeros: int = Field(default=1, ge=1, le=4, description="Número de pasajeros")
    cantidad_equipaje: int = Field(default=0, ge=0, le=4, description="Cantidad de equipaje mediano")
    centro_costo: Optional[str] = Field(None, max_length=255, description="Centro de costo o referencia interna")
    
    @field_validator('fecha_programada')
    @classmethod
    def validar_fecha_programada(cls, v, info):
        es_programado = info.data.get('es_programado')
        if es_programado and v is None:
            raise ValueError('Se requiere fecha programada')
        if v and v < datetime.now():
            raise ValueError('La fecha programada debe ser futura')
        return v


class ReservaCreate(ReservaBase):
    """Schema para crear reserva"""
    empresa_id: UUID


class ReservaUpdate(BaseModel):
    """Schema para actualizar reserva"""
    pasajero_nombre: Optional[str] = None
    pasajero_telefono: Optional[str] = None
    direccion_origen: Optional[str] = None
    latitud_origen: Optional[float] = None
    longitud_origen: Optional[float] = None
    direccion_destino: Optional[str] = None
    latitud_destino: Optional[float] = None
    longitud_destino: Optional[float] = None
    paradas_intermedias: Optional[List[ParadaIntermedia]] = None
    tipo_vehiculo: Optional[TipoVehiculoEnum] = None
    nota_conductor: Optional[str] = None
    estado: Optional[EstadoReservaEnum] = None
    metodo_pago: Optional[MetodoPagoEnum] = None
    precio_final: Optional[float] = None
    cantidad_pasajeros: Optional[int] = Field(None, ge=1, le=4)
    cantidad_equipaje: Optional[int] = Field(None, ge=0, le=4)
    centro_costo: Optional[str] = Field(None, max_length=255)


class ReservaResponse(ReservaBase):
    """Schema para respuesta de reserva"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    empresa_id: UUID
    empleado_id: UUID
    turno_id: Optional[UUID]
    estado: EstadoReservaEnum
    distancia_estimada_km: Optional[float]
    tiempo_estimado_minutos: Optional[int]
    precio_estimado: Optional[float]
    precio_final: Optional[float]
    created_at: datetime
    updated_at: datetime
    creado_por: Optional[UUID] = None
    
    # Campos adicionales para la vista
    empresa_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None


# ============================================================
# ✅ NUEVO SCHEMA PARA ESTIMACIÓN DE PRECIO (FASE 2)
# ============================================================

class EstimacionPrecioRequest(BaseModel):
    """Request para estimar precio - SOPORTA MÚLTIPLES MODOS DE CÁLCULO"""
    direccion_origen: str = Field(..., description="Dirección de origen")
    direccion_destino: str = Field(..., description="Dirección de destino")
    paradas_intermedias: Optional[List[ParadaIntermedia]] = Field(default_factory=list, description="Paradas intermedias")
    tipo_vehiculo: TipoVehiculoEnum = Field(default=TipoVehiculoEnum.STANDARD, description="Tipo de vehículo")
    
    # ✅ NUEVO CAMPO: tiempo de espera en minutos
    tiempo_espera_minutos: Optional[int] = Field(
        default=0, 
        ge=0,
        description="Tiempo de espera en minutos (para modo ficha_argentina y mixto)"
    )
    
    es_programado: bool = Field(default=False, description="Si es un viaje programado")
    fecha_programada: Optional[datetime] = Field(default=None, description="Fecha programada para el viaje")
    hora: Optional[int] = Field(default=None, description="Hora específica del viaje")

    model_config = {
        "json_schema_extra": {
            "example": {
                "direccion_origen": "Av. Independencia 1000, San Miguel de Tucumán",
                "direccion_destino": "Plaza Independencia, San Miguel de Tucumán",
                "paradas_intermedias": [],
                "tipo_vehiculo": "standard",
                "tiempo_espera_minutos": 0,
                "es_programado": False
            }
        }
    }


class EstimacionPrecioResponse(BaseModel):
    """Response para estimación de precio - CON DESGLOSE DETALLADO"""
    distancia_km: float = Field(..., description="Distancia en kilómetros")
    tiempo_minutos: int = Field(..., description="Tiempo estimado en minutos")
    precio_estimado: float = Field(..., description="Precio total estimado")
    desglose: Dict[str, Any] = Field(..., description="Desglose detallado del cálculo")
    latitud_origen: Optional[float] = Field(None, description="Latitud del origen")
    longitud_origen: Optional[float] = Field(None, description="Longitud del origen")
    latitud_destino: Optional[float] = Field(None, description="Latitud del destino")
    longitud_destino: Optional[float] = Field(None, description="Longitud del destino")
    
    # ✅ NUEVOS CAMPOS PARA CONTEXTO
    modo_calculo: Optional[str] = Field(None, description="Modo de cálculo utilizado")
    moneda: Optional[str] = Field(default="ARS", description="Moneda del precio")
    recargos_aplicados: Optional[List[str]] = Field(default_factory=list, description="Lista de recargos aplicados")

    model_config = {
        "json_schema_extra": {
            "example": {
                "distancia_km": 5.2,
                "tiempo_minutos": 15,
                "precio_estimado": 7440.0,
                "desglose": {
                    "bajada": 1200.0,
                    "fichas": 6240.0,
                    "total_fichas": 52,
                    "distancia_metros": 5200,
                    "distancia_por_ficha": 100,
                    "precio_por_ficha": 120,
                    "espera": 0,
                    "subtotal": 7440.0,
                    "recargo_nocturno": 1.0,
                    "recargo_domingo": 1.0,
                    "recargo_feriado": 1.0
                },
                "modo_calculo": "ficha_argentina",
                "moneda": "ARS",
                "recargos_aplicados": []
            }
        }
    }