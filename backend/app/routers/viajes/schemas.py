"""
Viajes - Schemas Pydantic
"""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Union
from datetime import datetime


# ============================================
# NUEVOS SCHEMAS PARA EL DASHBOARD
# ============================================

class ViajeDashboardResponse(BaseModel):
    """
    Respuesta para el dashboard de viajes
    CON TODOS LOS DATOS MEJORADOS
    """
    viaje_id: UUID
    estado: str
    direccion_origen: str = ""
    direccion_destino: str = ""
    precio_estimado: Optional[float] = None
    precio_final: Optional[float] = None
    created_at: datetime
    aceptado_en: Optional[datetime] = None
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None
    distancia_metros: Optional[int] = None
    tiempo_estimado_segundos: Optional[int] = None
    
    # NUEVOS CAMPOS MEJORADOS
    pasajero: str  # nombre completo o email
    chofer: str    # nombre completo o "Sin asignar"
    fecha: str     # DD/MM/YYYY
    hora: str      # HH:MI AM
    precio: Optional[float]  # estimado o final según estado
    empresa: Optional[str] = None  # control_base.nombre
    propietario: Optional[str] = None  # propietario del vehículo
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    
    # Coordenadas
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None

    class Config:
        from_attributes = True


class DashboardEstadisticasResponse(BaseModel):
    """Estadísticas rápidas para el dashboard"""
    total: int
    por_estado: Dict[str, int]
    hoy: Dict[str, Union[int, float]]

    class Config:
        from_attributes = True


class DashboardViajesResponse(BaseModel):
    """Respuesta paginada del dashboard"""
    total: int
    limit: int
    offset: int
    viajes: List[ViajeDashboardResponse]

    class Config:
        from_attributes = True


# ============================================
# ESTADO DEL VIAJE (MEJORADO)
# ============================================

class ViajeEstadoResponse(BaseModel):
    """Estado de un viaje específico"""
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
    
    # NUEVOS CAMPOS (opcionales para compatibilidad)
    empresa: Optional[str] = None
    patente: Optional[str] = None
    propietario: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# HISTORIAL DEL VIAJE (MEJORADO)
# ============================================

class HistorialViajeResponse(BaseModel):
    """Historial de viajes con detalles mejorados"""
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
    
    # NUEVOS CAMPOS
    fecha_hora: Optional[str] = None  # DD/MM/YYYY HH24:MI
    empresa: Optional[str] = None
    patente: Optional[str] = None
    propietario: Optional[str] = None

    class Config:
        from_attributes = True


class HistorialViajesResponse(BaseModel):
    """Respuesta paginada del historial"""
    total: int
    limit: int
    offset: int
    viajes: List[HistorialViajeResponse]

    class Config:
        from_attributes = True


# ============================================
# SOLICITAR VIAJE
# ============================================

class SolicitarViajeRequest(BaseModel):
    """Solicitar un nuevo viaje"""
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

    class Config:
        from_attributes = True


class SolicitarViajeResponse(BaseModel):
    """Respuesta al solicitar un viaje"""
    success: bool
    viaje_id: UUID
    estado: str
    mensaje: str
    tiempo_estimado_segundos: Optional[int] = None
    precio_estimado: Optional[float] = None

    class Config:
        from_attributes = True


# ============================================
# CALCULAR COSTO
# ============================================

class CalcularCostoRequest(BaseModel):
    """Calcular costo estimado de un viaje"""
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float
    tipo_vehiculo: Optional[str] = "standard"

    class Config:
        from_attributes = True


class CalcularCostoResponse(BaseModel):
    """Respuesta del cálculo de costo"""
    distancia_metros: int
    tiempo_estimado_segundos: int
    precio_estimado: float
    tarifa_base: float
    costo_km: float
    costo_minuto: float

    class Config:
        from_attributes = True


# ============================================
# CANCELAR VIAJE
# ============================================

class CancelarViajeRequest(BaseModel):
    """Cancelar un viaje"""
    motivo: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# CALIFICAR VIAJE
# ============================================

class CalificarViajeRequest(BaseModel):
    """Calificar un viaje"""
    puntaje: int = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comentario: Optional[str] = None

    class Config:
        from_attributes = True


class CalificarViajeResponse(BaseModel):
    """Respuesta al calificar un viaje"""
    success: bool
    message: str

    class Config:
        from_attributes = True


# ============================================
# OBJETOS OLVIDADOS
# ============================================

class ObjetoOlvidadoRequest(BaseModel):
    """Reportar objeto olvidado"""
    descripcion: str
    foto_url: Optional[str] = None

    class Config:
        from_attributes = True


class ObjetoOlvidadoResponse(BaseModel):
    """Respuesta de objeto olvidado"""
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

    class Config:
        from_attributes = True


# ============================================
# COMPARTIR VIAJE
# ============================================

class CompartirViajeResponse(BaseModel):
    """Respuesta para compartir viaje"""
    url_seguimiento: str
    codigo_compartido: str

    class Config:
        from_attributes = True


# ============================================
# RESERVAS
# ============================================

class ReservarViajeRequest(BaseModel):
    """Reservar un viaje programado"""
    origen_latitud: float
    origen_longitud: float
    destino_latitud: float
    destino_longitud: float
    direccion_origen: str
    direccion_destino: str
    fecha_programada: datetime
    tipo_vehiculo: Optional[str] = "standard"

    class Config:
        from_attributes = True


class ReservarViajeResponse(BaseModel):
    """Respuesta al reservar un viaje"""
    success: bool
    reserva_id: UUID
    estado: str
    fecha_programada: datetime
    mensaje: str

    class Config:
        from_attributes = True


class ReservaPendienteResponse(BaseModel):
    """Reserva pendiente"""
    id: UUID
    origen_latitud: Optional[float] = None
    origen_longitud: Optional[float] = None
    destino_latitud: Optional[float] = None
    destino_longitud: Optional[float] = None
    direccion_origen: str
    direccion_destino: str
    fecha_programada: datetime
    creado_en: datetime

    class Config:
        from_attributes = True


# ============================================
# SOLICITAR VIAJE PÚBLICO
# ============================================

class SolicitarViajePublicoRequest(BaseModel):
    """Solicitar viaje desde endpoint público"""
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

    class Config:
        from_attributes = True


class SolicitarViajePublicoResponse(BaseModel):
    """Respuesta de viaje público"""
    success: bool
    viaje_id: UUID
    mensaje: str
    chofer_asignado: Optional[dict] = None
    tiempo_espera_estimado: Optional[int] = None

    class Config:
        from_attributes = True