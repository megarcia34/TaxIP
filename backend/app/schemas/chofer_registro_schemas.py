"""
Schemas específicos para el flujo progresivo de registro de choferes (Módulo 1)
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import date
import re


# ==========================================
# ETAPA 1: INICIO DE REGISTRO
# ==========================================
class ChoferInicioRegistroRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")


class ChoferInicioRegistroResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID
    requiere_validacion_email: bool = True
    es_reanudacion: bool = False


# ==========================================
# ETAPA 2: VALIDACIÓN EMAIL (OTP)
# ==========================================
class ValidarEmailRequest(BaseModel):
    email: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class ValidarEmailResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    message: str
    user_id: UUID


# ==========================================
# ETAPA 3: DATOS PERSONALES Y TENANT
# ==========================================
class ActualizarDatosChoferRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    dni: str = Field(..., pattern=r'^\d{7,8}[A-Z]?$', description="DNI formato argentino")
    telefono: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    prestadora_id: UUID
    direccion: str = Field(..., min_length=5)
    ciudad_id: UUID      # Determina tenant automáticamente
    codigo_postal: str = Field(..., pattern=r'^[A-Za-z0-9\s-]{4,10}$')


class DatosChoferResponse(BaseModel):
    success: bool
    tenant_nombre: str
    pasos_completados: dict


# ==========================================
# ETAPA 4: DOCUMENTACIÓN INDIVIDUAL
# ==========================================
class DocumentoChoferUploadRequest(BaseModel):
    tipo_documento: str = Field(..., pattern='^(dni|licencia|sanidad|buena_conducta)$')
    fecha_vencimiento: Optional[date] = None


class DocumentoChoferResponse(BaseModel):
    success: bool
    tipo_documento: str
    url: str
    documentos_pendientes: List[str]


# ==========================================
# ETAPA 5: SELFIE FINAL
# ==========================================
class SelfieChoferRequest(BaseModel):
    foto_url: str = Field(..., description="URL segura devuelta por Cloudinary")


class FinalizarRegistroResponse(BaseModel):
    success: bool
    estado_aprobacion: str  # 'en_revision'
    mensaje: str


# ==========================================
# ESTADO DEL EXPEDIENTE / REANUDACIÓN
# ==========================================
class EstadoExpedienteResponse(BaseModel):
    estado_aprobacion: str  # pendiente, en_revision, aprobado, rechazado
    motivo_rechazo: Optional[str] = None
    progreso_etapas: dict   # {'datos': True, 'documentos': False, ...}
    puede_operar: bool      # Solo true si aprobado AND tiene vehículo
    tenant_nombre: Optional[str] = None
    documentos_faltantes: List[str] = []