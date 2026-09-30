"""
Schemas para el endpoint unificado del Splash Screen.
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ProgresoResponse(BaseModel):
    datos_personales: bool
    documentos_basicos: bool
    selfie: bool


class VehiculoInfoResponse(BaseModel):
    id: UUID
    patente: str


class TurnoInfoResponse(BaseModel):
    id: UUID
    inicio_turno: datetime


class ContratoInfoResponse(BaseModel):
    id: UUID
    tipo: str  # porcentaje, alquiler, autogestion


class SplashEstadoResponse(BaseModel):
    autenticado: bool
    
    # Estado de aprobación
    estado_aprobacion: str  # pendiente, en_revision, aprobado, rechazado
    estado_laboral: str     # fuera_servicio, libre, ocupado
    
    # Flags de condición
    puede_operar: bool
    tiene_vehiculo: bool
    tiene_contrato_activo: bool
    tiene_turno_activo: bool
    
    # Navegación
    etapa_actual: str  # registro, email, datos, documentos, selfie, revision, esperando_vehiculo, contrato_pendiente, listo, turno, home
    
    # Progreso M1
    documentos_faltantes: List[str]
    progreso: ProgresoResponse
    
    # Motivo de bloqueo (si aplica)
    motivo_bloqueo: Optional[str] = None
    
    # Datos contextuales
    tenant_nombre: Optional[str] = None
    vehiculo: Optional[VehiculoInfoResponse] = None
    turno: Optional[TurnoInfoResponse] = None
    contrato: Optional[ContratoInfoResponse] = None