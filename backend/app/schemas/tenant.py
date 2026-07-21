"""
Schemas para la gestión de Tenants (Control Base)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class TenantBase(BaseModel):
    """Base para Tenant"""
    nombre: str = Field(..., description="Nombre del tenant", max_length=255)
    email: Optional[str] = Field(None, description="Email de contacto", max_length=255)
    telefono: Optional[str] = Field(None, description="Teléfono", max_length=50)
    latitud: Optional[float] = Field(None, description="Latitud")
    longitud: Optional[float] = Field(None, description="Longitud")


class TenantCreate(TenantBase):
    """Schema para crear un nuevo tenant"""
    pass


class TenantUpdate(BaseModel):
    """Schema para actualizar un tenant"""
    nombre: Optional[str] = Field(None, description="Nombre del tenant", max_length=255)
    email: Optional[str] = Field(None, description="Email de contacto", max_length=255)
    telefono: Optional[str] = Field(None, description="Teléfono", max_length=50)
    latitud: Optional[float] = Field(None, description="Latitud")
    longitud: Optional[float] = Field(None, description="Longitud")
    activo: Optional[bool] = Field(None, description="Estado del tenant")


class TenantSuspender(BaseModel):
    """Schema para suspender un tenant"""
    motivo: str = Field(..., description="Motivo de la suspensión", min_length=3)


class TenantResponse(BaseModel):
    """Schema para respuesta de tenant"""
    id: UUID
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
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