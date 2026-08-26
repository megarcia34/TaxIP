"""
Corporate Schemas - Pydantic models for corporate module
"""

from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field


# ============================================================
# CUENTA CORRIENTE
# ============================================================

class CuentaCreate(BaseModel):
    """Schema for creating a current account"""
    empresa_id: UUID
    limite_credito: Decimal = Field(default=0, description="Límite de crédito")
    moneda: str = "ARS"


class CuentaResponse(BaseModel):
    """Schema for current account response"""
    id: UUID
    empresa_id: UUID
    saldo_actual: Decimal
    saldo_disponible: Decimal
    limite_credito: Decimal
    moneda: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# MOVIMIENTOS
# ============================================================

class MovimientoCreate(BaseModel):
    """Schema for creating an account movement"""
    cuenta_id: UUID
    viaje_id: Optional[UUID] = None
    tipo_movimiento: str = Field(..., description="credito | debito | ajuste")
    concepto: str
    monto: Decimal
    referencia: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class MovimientoResponse(BaseModel):
    """Schema for movement response"""
    id: UUID
    cuenta_id: UUID
    viaje_id: Optional[UUID] = None
    tipo_movimiento: str
    concepto: str
    monto: Decimal
    saldo_anterior: Decimal
    saldo_nuevo: Decimal
    referencia: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# FACTURAS
# ============================================================

class FacturaCreate(BaseModel):
    """Schema for creating a corporate invoice"""
    empresa_id: UUID
    numero_factura: str
    periodo_desde: datetime
    periodo_hasta: datetime
    subtotal: Decimal
    descuento: Decimal = Decimal(0)
    iva: Decimal = Decimal(0)
    fecha_vencimiento: Optional[datetime] = None
    pdf_url: Optional[str] = None
    observaciones: Optional[str] = None
    registrar_movimiento: bool = True


class FacturaResponse(BaseModel):
    """Schema for invoice response"""
    id: UUID
    empresa_id: UUID
    numero_factura: str
    periodo_desde: datetime
    periodo_hasta: datetime
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    subtotal: Decimal
    descuento: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    pdf_url: Optional[str] = None
    observaciones: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FacturaFilter(BaseModel):
    """Filters for listing invoices"""
    empresa_id: Optional[UUID] = None
    estado: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


# ============================================================
# PAGOS
# ============================================================

class PagoCreate(BaseModel):
    """Schema for creating a corporate payment"""
    factura_id: UUID
    monto: Optional[Decimal] = None
    metodo_pago: str
    referencia: Optional[str] = None
    comprobante_url: Optional[str] = None
    confirmado_por: Optional[UUID] = None
    observaciones: Optional[str] = None


class PagoResponse(BaseModel):
    """Schema for payment response"""
    id: UUID
    empresa_id: UUID
    factura_id: Optional[UUID] = None
    monto: Decimal
    metodo_pago: str
    referencia: Optional[str] = None
    comprobante_url: Optional[str] = None
    estado: str
    fecha_pago: datetime
    confirmado_por: Optional[UUID] = None
    confirmado_en: Optional[datetime] = None
    observaciones: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# RESUMEN
# ============================================================

class ResumenCuenta(BaseModel):
    """Schema for account summary"""
    empresa_id: UUID
    saldo_actual: Decimal
    saldo_disponible: Decimal
    limite_credito: Decimal
    total_pendiente: Decimal
    cantidad_movimientos_recientes: int
    cantidad_facturas_pendientes: int