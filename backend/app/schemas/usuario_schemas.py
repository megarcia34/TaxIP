"""
User profile schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PerfilResponse(BaseModel):
    """User profile response"""
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    ciudad_id: Optional[UUID] = None
    foto_perfil_url: Optional[str] = None
    tipo_usuario: str
    created_at: datetime


class ActualizarPerfilRequest(BaseModel):
    """Update user profile request"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = None
    documento: Optional[str] = None
    ciudad_id: Optional[UUID] = None


class DireccionFrecuenteRequest(BaseModel):
    """Save frequent address request"""
    nombre: str = Field(..., description="casa, trabajo, gimnasio, etc")
    latitud: float
    longitud: float
    direccion_texto: str


class DireccionFrecuenteResponse(BaseModel):
    """Frequent address response"""
    id: UUID
    nombre: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion_texto: Optional[str] = None
    created_at: datetime


class TaxistaFavoritoResponse(BaseModel):
    """Favorite driver response"""
    id: UUID
    chofer_id: UUID
    nombre_chofer: Optional[str] = None
    calificacion_promedio: Optional[float] = None
    created_at: datetime