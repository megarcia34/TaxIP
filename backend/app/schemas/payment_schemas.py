"""
Payment and wallet schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class WalletBalanceResponse(BaseModel):
    """Wallet balance response"""
    saldo: float
    moneda: str = "ARS"


class TopUpRequest(BaseModel):
    """Request to top up wallet"""
    monto: float = Field(..., gt=0, description="Amount to add")
    metodo_pago: str = Field(default="mercadopago", description="mercadopago, tarjeta_credito, tarjeta_debito")


class TopUpResponse(BaseModel):
    """Top up response"""
    success: bool
    transaction_id: UUID
    form_url: Optional[str] = None
    monto: float
    message: str


class PaymentWebhookPayload(BaseModel):
    """Webhook from payment gateway (Paypertic)"""
    external_transaction_id: str
    status: str
    amount: float
    provider_id: Optional[str] = None
    payment_method_detail: Optional[str] = None
    authorization_code: Optional[str] = None


class TransaccionResponse(BaseModel):
    """Transaction response"""
    id: UUID
    tipo: str  # TOP_UP, TRIP_PAYMENT, REFUND
    monto: float
    saldo_despues: float
    estado: str
    descripcion: Optional[str] = None
    viaje_id: Optional[UUID] = None
    created_at: datetime


class PagarViajeConWalletRequest(BaseModel):
    """Pay trip with wallet request"""
    viaje_id: UUID


class PagarViajeConWalletResponse(BaseModel):
    """Pay trip with wallet response"""
    success: bool
    monto_pagado: float
    nuevo_saldo: float
    message: str