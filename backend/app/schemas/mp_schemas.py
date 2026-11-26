from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MPAuthorizeResponse(BaseModel):
    authorization_url: str
    state: str


class MPVinculacionStatusResponse(BaseModel):
    vinculada: bool
    estado: Optional[str] = None
    mp_user_id: Optional[int] = None
    mp_email: Optional[str] = None
    mp_nickname: Optional[str] = None
    expires_at: Optional[datetime] = None


class MPCobroDirectoRequest(BaseModel):
    propietario_id: UUID = Field(..., description="ID del propietario que recibe el cobro directo")
    viaje_id: Optional[UUID] = Field(default=None, description="ID del viaje asociado si aplica")
    monto: Decimal = Field(..., gt=0, description="Monto a cobrar en ARS")
    titulo: str = Field(default="Viaje TaxIP", min_length=1, max_length=120)
    external_reference: Optional[str] = Field(default=None, max_length=255)
    payer_email: Optional[str] = Field(default=None, max_length=200)


class MPCobroDirectoResponse(BaseModel):
    preference_id: str
    init_point: str
    sandbox_init_point: Optional[str] = None
    external_reference: str
    propietario_id: UUID
    mp_user_id: int
    excluded_payment_types: list[str]
    monto: Decimal
    moneda: str = "ARS"


class MPWebhookResponse(BaseModel):
    received: bool = True
    signature_valid: bool = True
    topic: Optional[str] = None
    resource_id: Optional[str] = None
    detail: Optional[str] = None