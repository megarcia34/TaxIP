# app/schemas/turno_schemas.py
"""
Schemas para gestión de turnos de choferes.

DECISIÓN DE ARQUITECTURA:
- Los schemas de RESPONSE usan camelCase (alias_generator=to_camel).
- Los schemas de REQUEST mantienen snake_case (es lo que el frontend envía).

Esto alinea el backend con el frontend (TypeScript usa camelCase por convención)
y elimina la necesidad de mapear en el cliente.
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ============================================
# MODELO BASE CON CAMELCASE
# ============================================

class CamelCaseModel(BaseModel):
    """Modelo base que convierte snake_case a camelCase en la salida JSON."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# ============================================
# SCHEMAS DE REQUEST (snake_case)
# ============================================

class CheckInRequest(BaseModel):
    """Solicitud de Check-in con código de autorización"""
    auth_token: str
    km_inicial: float = Field(..., gt=0)
    combustible_inicial: str = Field(
        ..., pattern='^(RESERVA|1/4|1/2|3/4|LLENO)$'
    )


class CheckInDirectoRequest(BaseModel):
    """Solicitud de Check-in directo (propietario-chofer)"""
    vehiculo_id: UUID
    km_inicial: float = Field(..., gt=0)
    combustible_inicial: str = Field(
        ..., pattern='^(RESERVA|1/4|1/2|3/4|LLENO)$'
    )


class CheckOutRequest(BaseModel):
    """Solicitud de Check-out"""
    km_final: float = Field(..., gt=0)
    combustible_final: str = Field(
        ..., pattern='^(RESERVA|1/4|1/2|3/4|LLENO)$'
    )
    recaudacion_ticketera: float = Field(0, ge=0)


class ValidarCodigoRequest(BaseModel):
    """Solicitud de validación de código"""
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class GastoRequest(BaseModel):
    """Registro de gasto durante turno"""
    turno_id: UUID
    tipo_gasto: str = Field(
        ..., description="COMBUSTIBLE, LUBRICANTE, LAVADO, REPARACION, OTROS"
    )
    monto: float = Field(..., gt=0)
    km_registro: Optional[float] = None
    url_comprobante: Optional[str] = None


class IniciarJornadaRequest(BaseModel):
    """Solicitud para iniciar jornada usando auth_token"""
    auth_token: str
    km_inicial: float = Field(..., gt=0)
    combustible_inicial: str = Field(
        ..., pattern='^(RESERVA|1/4|1/2|3/4|LLENO)$'
    )


class GenerarCodigoRequest(BaseModel):
    """Solicitud de generación de código"""
    dias_validez: int = Field(30, ge=1, le=90)


class GenerarQrRequest(BaseModel):
    """Solicitud para generar QR operativo"""
    contrato_id: UUID
    dias_validez: Optional[int] = 30


class EscaneoQrRequest(BaseModel):
    """Solicitud de escaneo QR"""
    token: str


class AutorizacionTurnoRequest(BaseModel):
    """Solicitud para autorizar inicio de jornada"""
    contrato_id: UUID
    fecha_referencia: Optional[datetime] = None


# ============================================
# SCHEMAS DE RESPONSE (camelCase)
# ============================================

class VehiculoInfo(CamelCaseModel):
    """Información del vehículo"""
    id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None


class VehiculoDisponibleInfo(CamelCaseModel):
    """Información de vehículo disponible para iniciar turno"""
    id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None


class ValidarCodigoResponse(CamelCaseModel):
    """Respuesta de validación de código"""
    success: bool
    message: str
    auth_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    contrato_id: Optional[UUID] = None
    vehiculo: Optional[VehiculoInfo] = None
    licencia: Optional[str] = None


class CheckInResponse(CamelCaseModel):
    """Respuesta de check-in (con código o directo)"""
    success: bool
    message: str
    turno_id: UUID
    vehiculo_id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    inicio_turno: datetime
    estado_laboral: str
    km_inicial: float
    combustible_inicial: str
    duracion_minutos: int = 0
    duracion_formateada: str = "00:00:00"


class CheckOutResponse(CamelCaseModel):
    """Respuesta de check-out"""
    success: bool
    message: str
    turno_id: UUID
    estado: str
    km_recorridos: float = 0
    duracion_horas: float = 0
    ingresos_registrados: int = 0
    liquidacion_id: Optional[UUID] = None


class TurnoActivoResponse(CamelCaseModel):
    """Respuesta de turno activo (con TODOS los datos para el frontend)"""
    tiene_turno_activo: bool
    turno_id: Optional[UUID] = None
    estado: Optional[str] = None
    inicio_turno: Optional[datetime] = None
    vehiculo_id: Optional[UUID] = None
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    estado_laboral: Optional[str] = None
    km_inicial: Optional[float] = None
    combustible_inicial: Optional[str] = None
    contrato_id: Optional[UUID] = None
    duracion_minutos: Optional[int] = None
    duracion_formateada: Optional[str] = None


class TurnoResponse(CamelCaseModel):
    """Respuesta genérica de turno (histórico)"""
    id: str
    vehiculo_id: str
    patente: str
    estado: str
    km_inicial: float
    km_final: Optional[float] = None
    combustible_inicial: str
    combustible_final: Optional[str] = None
    inicio_turno: datetime
    fin_turno: Optional[datetime] = None
    monto_bruto: float = 0
    comision_chofer: float = 0
    utilidad_propietario: float = 0


class EstadoTurnoResponse(CamelCaseModel):
    """Respuesta del estado completo del chofer"""
    puede_operar: bool
    motivo: Optional[str] = None
    estado_aprobacion: str
    estado_laboral: str
    tiene_turno_activo: bool
    tiene_vehiculo: bool
    tiene_contrato_activo: bool


class ModoInicioResponse(CamelCaseModel):
    """Respuesta del modo de inicio de turno"""
    es_propietario: bool
    requiere_codigo: bool
    vehiculos_disponibles: List[VehiculoDisponibleInfo] = []


class ResumenResponse(CamelCaseModel):
    """Resumen de actividad del chofer"""
    fecha_inicio: str
    fecha_fin: str
    dias: int
    viajes: int
    recaudado: float
    km_recorridos: float
    duracion_minutos: int
    viaje_mas_caro: float
    viaje_mas_bajo: float
    promedio_viaje: float


class IniciarJornadaResponse(CamelCaseModel):
    """Respuesta de inicio de jornada (con auth_token)"""
    success: bool
    turno_id: UUID
    mensaje: str
    contrato_id: UUID
    vehiculo_id: UUID
    patente: str


class GenerarCodigoResponse(CamelCaseModel):
    """Respuesta de generación de código"""
    success: bool
    codigo: str
    contrato_id: UUID
    vehiculo_id: UUID
    patente: str
    expira_en: datetime
    mensaje: str


class GenerarQrResponse(CamelCaseModel):
    """Respuesta de generación de QR"""
    token: str
    qr_url: Optional[str] = None
    contrato_id: UUID
    expires_at: Optional[datetime] = None
    mensaje: Optional[str] = None


class EscaneoQrResponse(CamelCaseModel):
    """Respuesta de escaneo de QR"""
    autorizado: bool
    mensaje: str
    auth_token: Optional[str] = None
    expires_at: Optional[datetime] = None


class AutorizacionTurnoResult(CamelCaseModel):
    """Resultado de la autorización de inicio de jornada"""
    autorizado: bool
    mensaje: Optional[str] = None
    contrato_id: Optional[UUID] = None
    vehiculo_id: Optional[UUID] = None
    chofer_id: Optional[UUID] = None
    propietario_id: Optional[UUID] = None
    control_base_id: Optional[UUID] = None
    tipo_contrato: Optional[str] = None
    turno_contractual: Optional[str] = None
    dia_contractual: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    detalles_validacion: Optional[dict] = None