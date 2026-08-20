# app/schemas/turno_schemas.py
"""
Schemas para gestión de turnos de choferes
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CheckInRequest(BaseModel):
    """Solicitud de Check-in"""
    vehiculo_id: UUID
    km_inicial: float = Field(..., gt=0, description="Kilometraje inicial")
    combustible_inicial: str = Field(..., description="RESERVA, 1/4, 1/2, 3/4, LLENO")


class CheckOutRequest(BaseModel):
    """Solicitud de Check-out"""
    turno_id: UUID
    km_final: float = Field(..., gt=0, description="Kilometraje final")
    combustible_final: str = Field(..., description="RESERVA, 1/4, 1/2, 3/4, LLENO")
    recaudacion_ticketera_calle: float = Field(0, ge=0, description="Efectivo recaudado fuera de la app")


class GastoRequest(BaseModel):
    """Registro de gasto durante turno"""
    turno_id: UUID
    tipo_gasto: str = Field(..., description="COMBUSTIBLE, LUBRICANTE, LAVADO, REPARACION, OTROS")
    monto: float = Field(..., gt=0)
    km_registro: Optional[float] = None
    url_comprobante: Optional[str] = None


class TurnoActivoResponse(BaseModel):
    """Respuesta de turno activo"""
    tiene_turno_activo: bool
    mensaje: str
    turno_id: Optional[str] = None
    vehiculo_id: Optional[str] = None
    patente: Optional[str] = None
    inicio_turno: Optional[datetime] = None
    km_inicial: Optional[float] = None
    combustible_inicial: Optional[str] = None
    estado: Optional[str] = None
    contrato_id: Optional[str] = None


class TurnoResponse(BaseModel):
    """Respuesta de turno"""
    id: str
    vehiculo_id: str
    patente: str
    estado: str
    km_inicial: float
    km_final: Optional[float]
    combustible_inicial: str
    combustible_final: Optional[str]
    inicio_turno: datetime
    fin_turno: Optional[datetime]
    monto_bruto: float
    comision_chofer: float
    utilidad_propietario: float


# ============================================
# NUEVOS SCHEMAS PARA AUTORIZACIÓN Y QR (C1/C2)
# ============================================

class AutorizacionTurnoRequest(BaseModel):
    """Solicitud para autorizar inicio de jornada (fase de pruebas)"""
    contrato_id: UUID
    fecha_referencia: Optional[datetime] = None  # Para pruebas


class AutorizacionTurnoResult(BaseModel):
    """Resultado de la autorización (respuesta del motor)"""
    autorizado: bool
    mensaje: Optional[str] = None
    
    # Contexto operativo (solo si autorizado)
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


class GenerarQrRequest(BaseModel):
    """Solicitud para generar QR operativo (C2)"""
    contrato_id: UUID
    dias_validez: Optional[int] = 30  # Días de vigencia del QR


class GenerarQrResponse(BaseModel):
    """Respuesta de generación de QR operativo"""
    token: str
    qr_url: Optional[str] = None
    contrato_id: UUID
    expires_at: Optional[datetime] = None
    mensaje: Optional[str] = None


class EscaneoQrRequest(BaseModel):
    """Solicitud de escaneo QR (C2)"""
    token: str


class EscaneoQrResponse(BaseModel):
    """Respuesta de escaneo de QR operativo"""
    autorizado: bool
    mensaje: str
    auth_token: Optional[str] = None
    expires_at: Optional[datetime] = None


# ============================================
# NUEVOS SCHEMAS PARA C3 — INICIO DE JORNADA
# ============================================

class IniciarJornadaRequest(BaseModel):
    """Solicitud para iniciar jornada usando auth_token (C3)"""
    auth_token: str
    km_inicial: float = Field(..., gt=0, description="Kilometraje inicial")
    combustible_inicial: str = Field(..., description="RESERVA, 1/4, 1/2, 3/4, LLENO")


class IniciarJornadaResponse(BaseModel):
    """Respuesta de inicio de jornada (C3)"""
    success: bool
    turno_id: UUID
    mensaje: str
    contrato_id: UUID
    vehiculo_id: UUID
    patente: str