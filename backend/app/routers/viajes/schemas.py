"""
Viajes - Schemas Pydantic
"""
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


# ============================================
# ESTADO DEL VIAJE
# ============================================

class ViajeEstadoResponse(BaseModel):
    id: UUID
    estado: str
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    precio_estimado: Optional[float] = None
    precio_final: Optional[float] = None
    created_at: datetime
    aceptado_en: Optional[datetime] = None
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None
    distancia_metros: Optional[int] = None
    tiempo_estimado_segundos: Optional[int] = None
    pasajero_nombre: Optional[str] = None
    chofer_nombre: Optional[str] = None
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None


# ============================================
# HISTORIAL DEL VIAJE
# ============================================

class HistorialViajeResponse(BaseModel):
    id: UUID
    pasajero_nombre: Optional[str] = None
    chofer_nombre: Optional[str] = None
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    precio_final: Optional[float] = None
    precio_estimado: Optional[float] = None
    estado: str
    creado_en: datetime
    distancia_metros: Optional[int] = None
    tiempo_estimado_segundos: Optional[int] = None
    calificacion_dada: Optional[int] = None
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None
    aceptado_en: Optional[datetime] = None
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None


# ============================================
# SOLICITAR VIAJE
# ============================================

class SolicitarViajeRequest(BaseModel):
    direccion_origen: str
    direccion_destino: str
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None
    metodo_pago: str = "efectivo"
    tipo_vehiculo: Optional[str] = "standard"
    notas: Optional[str] = None
    pasajero_nombre: Optional[str] = None


class SolicitarViajeResponse(BaseModel):
    success: bool
    viaje_id: UUID
    estado: str
    mensaje: str
    tiempo_estimado_segundos: Optional[int] = None
    precio_estimado: Optional[float] = None


# ============================================
# CALCULAR COSTO
# ============================================

class CalcularCostoRequest(BaseModel):
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float
    tipo_vehiculo: Optional[str] = "standard"


class CalcularCostoResponse(BaseModel):
    distancia_metros: int
    tiempo_estimado_segundos: int
    precio_estimado: float
    tarifa_base: float
    costo_km: float
    costo_minuto: float


# ============================================
# CANCELAR VIAJE
# ============================================

class CancelarViajeRequest(BaseModel):
    motivo: Optional[str] = None


# ============================================
# CALIFICAR VIAJE
# ============================================

class CalificarViajeRequest(BaseModel):
    puntaje: int
    comentario: Optional[str] = None


class CalificarViajeResponse(BaseModel):
    success: bool
    message: str


# ============================================
# OBJETOS OLVIDADOS
# ============================================

class ObjetoOlvidadoRequest(BaseModel):
    descripcion: str
    foto_url: Optional[str] = None


class ObjetoOlvidadoResponse(BaseModel):
    id: UUID
    viaje_id: UUID
    descripcion: str
    estado: str
    created_at: datetime
    fecha_entrega: Optional[datetime] = None
    foto_url: Optional[str] = None
    pasajero_nombre: Optional[str] = None
    pasajero_email: Optional[str] = None
    chofer_nombre: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    observaciones: Optional[str] = None


# ============================================
# COMPARTIR VIAJE
# ============================================

class CompartirViajeResponse(BaseModel):
    url_seguimiento: str
    codigo_compartido: str


# ============================================
# RESERVAS
# ============================================

class ReservarViajeRequest(BaseModel):
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float
    direccion_origen: str
    direccion_destino: str
    fecha_programada: datetime
    tipo_vehiculo: Optional[str] = "standard"


class ReservarViajeResponse(BaseModel):
    success: bool
    reserva_id: UUID
    estado: str
    fecha_programada: datetime
    mensaje: str


class ReservaPendienteResponse(BaseModel):
    id: UUID
    origen_latitud: Optional[float] = None
    origen_longitud: Optional[float] = None
    destino_latitud: Optional[float] = None
    destino_longitud: Optional[float] = None
    direccion_origen: str
    direccion_destino: str
    fecha_programada: datetime
    creado_en: datetime


# ============================================
# SOLICITAR VIAJE PÚBLICO
# ============================================

class SolicitarViajePublicoRequest(BaseModel):
    direccion_origen: str
    origen_lat: float
    origen_lng: float
    direccion_destino: str
    destino_lat: float
    destino_lng: float
    metodo_pago: str = "efectivo"
    precio_estimado: Optional[float] = None
    nombre_pasajero: Optional[str] = None
    telefono_pasajero: Optional[str] = None


class SolicitarViajePublicoResponse(BaseModel):
    success: bool
    viaje_id: UUID
    mensaje: str
    chofer_asignado: Optional[dict] = None
    tiempo_espera_estimado: Optional[int] = None