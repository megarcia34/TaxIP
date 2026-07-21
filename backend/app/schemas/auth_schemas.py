"""
Authentication schemas (login, register, password recovery)
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from uuid import UUID


class RegistroRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: Optional[str] = None
    tipo: str = Field(..., description="pasajero, chofer, propietario")
    
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
    
    @field_validator("tipo")
    def validate_tipo(cls, v):
        valid_types = ["pasajero", "chofer", "propietario"]
        if v.lower() not in valid_types:
            raise ValueError(f"Tipo must be one of: {valid_types}")
        return v.lower()


class RegistroResponse(BaseModel):
    """User registration response"""
    success: bool
    user_id: UUID
    email: str
    message: str


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens"""
    success: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    tipo_usuario: str
    nombre_completo: Optional[str] = None
    # ✅ NUEVO: control_base_id para Admin Tenant
    control_base_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"


class RecuperarSolicitarRequest(BaseModel):
    """Request password recovery email"""
    email: EmailStr


class RecuperarConfirmarRequest(BaseModel):
    """Confirm password recovery with token"""
    token: str
    new_password: str = Field(..., min_length=6)
    
    @field_validator("new_password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class RecuperarConfirmarResponse(BaseModel):
    """Password recovery confirmation response"""
    success: bool
    message: str


class CambiarContraseniaRequest(BaseModel):
    """Change password request (authenticated user)"""
    current_password: str
    new_password: str = Field(..., min_length=6)
    
    @field_validator("new_password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class CambiarContraseniaResponse(BaseModel):
    """Change password response"""
    success: bool
    message: str


# ============================================
# GET /me - Current user info
# ============================================

class UserProfileSchema(BaseModel):
    """User profile data"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    foto_perfil_url: Optional[str] = None


class TenantInfoSchema(BaseModel):
    """Tenant (control_base) info"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None


class UserMeResponse(BaseModel):
    """Current user info response"""
    id: str
    email: str
    tipo_usuario: str
    control_base_id: Optional[str] = None
    perfil: Optional[UserProfileSchema] = None
    tenant: Optional[TenantInfoSchema] = None


# ============================================
# Owner (Propietario) Login Schemas
# ============================================

class OwnerVehiculoInfo(BaseModel):
    """Vehicle summary for owner response"""
    id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    porcentaje_participacion: float
    fecha_inicio: str


class PropietarioLoginResponse(BaseModel):
    """Owner login response with additional owner data"""
    success: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    tipo_usuario: str
    nombre_completo: Optional[str] = None
    control_base_id: Optional[UUID] = None
    tiene_vehiculos_activos: bool
    total_vehiculos: int
    vehiculos: Optional[List[OwnerVehiculoInfo]] = None