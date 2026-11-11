"""
Schemas para la gestión de Tenants (Control Base)
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class TenantBase(BaseModel):
    """Base para Tenant"""
    nombre: str = Field(..., description="Nombre del tenant", max_length=255)
    email: Optional[str] = Field(None, description="Email de contacto", max_length=255)
    telefono: Optional[str] = Field(None, description="Teléfono", max_length=50)
    direccion: Optional[str] = Field(None, description="Dirección", max_length=255)
    latitud: Optional[float] = Field(None, description="Latitud")
    longitud: Optional[float] = Field(None, description="Longitud")
    ciudad_nombre: Optional[str] = Field(None, description="Nombre de la ciudad", max_length=100)
    codigo_postal: Optional[str] = Field(None, description="Código postal", max_length=20)


class TenantCreate(TenantBase):
    """Schema para crear un nuevo tenant (Super Admin)"""
    email: EmailStr = Field(..., description="Email del admin del tenant")
    ciudad_nombre: str = Field(..., description="Nombre de la ciudad de operación", min_length=2)
    
    # ============================================================
    # NUEVOS CAMPOS DE SEGURIDAD Y CONFIGURACIÓN
    # ============================================================
    admin_password: str = Field(
        ..., 
        min_length=8, 
        description="Contraseña inicial para el administrador del tenant"
    )
    timezone: str = Field(
        default="America/Argentina/Tucuman",
        description="Zona horaria del tenant"
    )
    moneda_default: str = Field(
        default="ARS",
        max_length=3,
        description="Moneda por defecto (ARS, USD, etc.)"
    )

    @field_validator('admin_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class TenantUpdate(BaseModel):
    """Schema para actualizar un tenant"""
    nombre: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=255)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activo: Optional[bool] = None
    ciudad_nombre: Optional[str] = Field(None, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=20)


class TenantSuspender(BaseModel):
    """Schema para suspender un tenant"""
    motivo: str = Field(..., description="Motivo de la suspensión", min_length=3)


class TenantResponse(BaseModel):
    """Schema para respuesta de tenant"""
    id: UUID
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    ciudad_id: Optional[UUID]
    ciudad_nombre: Optional[str]
    codigo_postal: Optional[str]
    activo: bool
    fecha_suspension: Optional[datetime]
    motivo_suspension: Optional[str]
    suspendido_por: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantListResponse(TenantResponse):
    """Schema para listado de tenants con estadísticas"""
    total_empresas: int = 0
    total_usuarios: int = 0
    total_viajes: int = 0


# ============================================================
# RESPUESTA DE CREACIÓN (SIN temp_password)
# ============================================================

class TenantCreateResponse(BaseModel):
    """Respuesta para la creación de un tenant"""
    success: bool
    tenant_id: UUID
    tenant_nombre: str
    ciudad_id: Optional[UUID] = None
    ciudad_nombre: str
    admin_email: str
    message: str