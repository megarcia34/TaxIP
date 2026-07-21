"""
Trip/ride schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class SolicitarViajeRequest(BaseModel):
    """Request a taxi"""
    origen_latitud: float
    origen_longitud: float
    direccion_origen: str
    destino_latitud: Optional[float] = None
    destino_longitud: Optional[float] = None
    direccion_destino: Optional[str] = None
    metodo_pago: str = Field(default="efectivo", description="efectivo, billetera, tarjeta_credito, tarjeta_debito")


class SolicitarViajeResponse(BaseModel):
    """Taxi request response"""
    success: bool
    viaje_id: UUID
    estado: str
    mensaje: str
    tiempo_estimado_segundos: Optional[int] = None
    precio_estimado: Optional[float] = None


class CalcularCostoRequest(BaseModel):
    """Calculate estimated trip cost"""
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float


class CalcularCostoResponse(BaseModel):
    """Estimated cost response"""
    distancia_metros: int
    tiempo_estimado_segundos: int
    precio_estimado: float
    moneda: str = "ARS"
    tarifa_base: float
    costo_km: float
    costo_minuto: float


class ViajeEstadoResponse(BaseModel):
    """Trip status response"""
    id: UUID
    estado: str  # pendiente, aceptado, en_curso, finalizado, cancelado, pagado
    chofer_nombre: Optional[str] = None
    chofer_foto: Optional[str] = None
    vehiculo_patente: Optional[str] = None
    vehiculo_modelo: Optional[str] = None
    ubicacion_chofer_lat: Optional[float] = None
    ubicacion_chofer_lng: Optional[float] = None
    tiempo_espera_segundos: Optional[int] = None
    precio_final: Optional[float] = None
    url_seguimiento: Optional[str] = None
    solicitado_en: datetime
    aceptado_en: Optional[datetime] = None
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None


class CancelarViajeRequest(BaseModel):
    """Cancel trip request"""
    motivo: Optional[str] = None


class CalificarViajeRequest(BaseModel):
    """Rate a trip"""
    puntaje: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comentario: Optional[str] = None


class CalificarViajeResponse(BaseModel):
    """Rating response"""
    success: bool
    message: str


class HistorialViajeResponse(BaseModel):
    """Trip history item"""
    id: UUID
    origen: str
    destino: Optional[str] = None
    precio_final: Optional[float] = None
    estado: str
    creado_en: datetime
    calificacion_dada: Optional[int] = None


class ObjetoOlvidadoRequest(BaseModel):
    """Report lost item"""
    descripcion: str
    foto_url: Optional[str] = None


class ObjetoOlvidadoResponse(BaseModel):
    """Lost item response"""
    id: UUID
    estado: str
    descripcion: str
    created_at: datetime


class CompartirViajeResponse(BaseModel):
    """Share trip URL response"""
    url_seguimiento: str
    codigo_compartido: str

    # ============================================
# RESERVAS ANTICIPADAS
# ============================================

class ReservarViajeRequest(BaseModel):
    """Request para reservar un viaje con anticipación"""
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    fecha_programada: datetime  # Fecha y hora programada para el viaje
    notas: Optional[str] = None


class ReservarViajeResponse(BaseModel):
    """Response después de crear una reserva"""
    success: bool
    reserva_id: UUID
    estado: str
    fecha_programada: datetime
    mensaje: str


class ReservaPendienteResponse(BaseModel):
    """Response para listar reservas pendientes"""
    id: UUID
    origen_latitud: Optional[float] = None
    origen_longitud: Optional[float] = None
    destino_latitud: Optional[float] = None
    destino_longitud: Optional[float] = None
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    fecha_programada: datetime
    creado_en: datetime