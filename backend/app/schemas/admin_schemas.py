"""
Admin schemas (dashboard, statistics, ranking)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ============================================================
# DASHBOARD - ESTADÍSTICAS
# ============================================================

class EstadisticasResponse(BaseModel):
    """Response para estadísticas del dashboard"""
    total_choferes: int = 0
    choferes_online: int = 0
    viajes_hoy: int = 0
    viajes_mes: int = 0
    ingresos_hoy: float = 0
    ingresos_mes: float = 0
    calificacion_promedio: float = 0
    total_vehiculos: int = 0
    total_clientes: int = 0
    viajes_pendientes: int = 0
    viajes_en_curso: int = 0
    viajes_finalizados: int = 0
    viajes_cancelados: int = 0


class ChoferesOnlineResponse(BaseModel):
    """Response para choferes online"""
    id: UUID
    usuario_id: UUID
    vehiculo_id: Optional[UUID] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: str
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    estado_laboral: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    calificacion_promedio: float
    ultima_conexion: datetime


class SolicitudActivaResponse(BaseModel):
    """Response para solicitudes activas (VIAJES PENDIENTES)"""
    id: UUID
    pasajero_id: UUID
    pasajero_nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion_origen: Optional[str] = None
    direccion_destino: Optional[str] = None
    estado: str
    precio_estimado: Optional[float] = None
    created_at: datetime
    tiempo_espera: Optional[int] = None
    distancia_metros: Optional[int] = None


class RankingChoferResponse(BaseModel):
    """Response para ranking de choferes"""
    id: UUID
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: str
    calificacion_promedio: float
    total_calificaciones: int
    total_viajes: int
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None


class CierreTurnoRequest(BaseModel):
    """Request para cierre de turno"""
    chofer_id: UUID
    vehiculo_id: UUID
    fecha_inicio: datetime
    fecha_fin: datetime
    total_viajes: int
    total_recaudado: float
    observaciones: Optional[str] = None


class CierreTurnoResponse(BaseModel):
    """Response para cierre de turno"""
    success: bool
    message: str
    turno_id: Optional[UUID] = None


class DashboardDataResponse(BaseModel):
    """Response para datos del dashboard"""
    estadisticas: EstadisticasResponse
    choferes_online: List[ChoferesOnlineResponse] = []
    solicitudes_activas: List[SolicitudActivaResponse] = []
    ranking: List[RankingChoferResponse] = []


# ============================================================
# PROPIETARIOS (Admin)
# ============================================================

class PropietarioListResponse(BaseModel):
    """Response para listado de propietarios"""
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    activo: bool
    total_vehiculos: int = 0
    total_contratos: int = 0
    created_at: datetime


class PropietarioDetailResponse(BaseModel):
    """Response para detalle de propietario"""
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    activo: bool
    vehiculos: List[dict] = []
    contratos: List[dict] = []
    created_at: datetime


# ============================================================
# EMPRESAS (Admin)
# ============================================================

class EmpresaListResponse(BaseModel):
    """Response para listado de empresas"""
    id: UUID
    nombre: str
    tipo: Optional[str] = None
    email_facturacion: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool
    total_viajes: int = 0
    total_empleados: int = 0
    created_at: datetime


class EmpresaDetailResponse(BaseModel):
    """Response para detalle de empresa"""
    id: UUID
    nombre: str
    tipo: Optional[str] = None
    email_facturacion: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool
    empleados: List[dict] = []
    viajes: List[dict] = []
    created_at: datetime