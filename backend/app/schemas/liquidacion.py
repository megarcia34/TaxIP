# app/schemas/liquidacion.py
"""
Schemas para el módulo de liquidaciones
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum


class EstadoLiquidacion(str, Enum):
    BORRADOR = "BORRADOR"
    CALCULADA = "CALCULADA"
    CONCILIADA = "CONCILIADA"
    CERRADA = "CERRADA"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    PAGADA = "PAGADA"
    OBSOLETA = "OBSOLETA"


class EstadoSaldo(str, Enum):
    PENDIENTE = "PENDIENTE"
    PARCIALMENTE_CANCELADO = "PARCIALMENTE_CANCELADO"
    CANCELADO = "CANCELADO"


class TipoLinea(str, Enum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"
    GASTO_TURNO = "GASTO_TURNO"
    GASTO_VEHICULO = "GASTO_VEHICULO"
    COMISION = "COMISION"
    CANON = "CANON"
    KM_EXCEDENTE = "KM_EXCEDENTE"
    AJUSTE = "AJUSTE"


class SignoLinea(str, Enum):
    DEBE = "DEBE"
    HABER = "HABER"


class TipoAjuste(str, Enum):
    CORRECCION = "CORRECCION"
    REEMBOLSO = "REEMBOLSO"
    RECARGO = "RECARGO"
    MULTA = "MULTA"


# ============================================================
# SCHEMAS PARA CREACIÓN
# ============================================================

class LiquidacionDetalleCreate(BaseModel):
    tipo_linea: TipoLinea
    concepto: Optional[str] = None
    fuente_tipo: Optional[str] = None
    fuente_id: Optional[UUID] = None
    monto: Decimal = Field(..., ge=0)
    signo: SignoLinea
    meta_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class LiquidacionCreate(BaseModel):
    turno_id: UUID
    contrato_id: UUID
    vehiculo_id: UUID
    chofer_id: UUID
    propietario_id: UUID
    tipo_contrato: str
    periodo_desde: datetime
    periodo_hasta: datetime
    monto_bruto: Decimal = Field(default=0)
    total_gastos: Decimal = Field(default=0)
    comision_chofer: Decimal = Field(default=0)
    canon: Decimal = Field(default=0)
    km_excedentes: Decimal = Field(default=0)
    cargo_km_excedentes: Decimal = Field(default=0)
    total_chofer: Decimal = Field(default=0)
    total_propietario: Decimal = Field(default=0)
    saldo_chofer: Decimal = Field(default=0)
    saldo_propietario: Decimal = Field(default=0)
    estado: EstadoLiquidacion = EstadoLiquidacion.BORRADOR
    detalles: List[LiquidacionDetalleCreate] = []

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS PARA RESPUESTA
# ============================================================

class LiquidacionDetalleResponse(BaseModel):
    id: UUID
    liquidacion_id: UUID
    tipo_linea: str
    concepto: Optional[str]
    fuente_tipo: Optional[str]
    fuente_id: Optional[UUID]
    monto: Decimal
    signo: str
    meta_data: Optional[Dict[str, Any]] = Field(None, alias="meta_data")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class LiquidacionEstadoHistorialResponse(BaseModel):
    id: UUID
    estado_anterior: Optional[str]
    estado_nuevo: str
    cambiado_por: Optional[UUID]
    motivo: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LiquidacionAjusteResponse(BaseModel):
    id: UUID
    liquidacion_id: UUID
    control_base_id: UUID
    tipo_ajuste: str
    monto: Decimal
    motivo: Optional[str]
    usuario_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class LiquidacionResponse(BaseModel):
    id: UUID
    control_base_id: UUID
    turno_id: UUID
    contrato_id: UUID
    vehiculo_id: UUID
    chofer_id: UUID
    propietario_id: UUID
    tipo_contrato: str
    periodo_desde: datetime
    periodo_hasta: datetime
    monto_bruto: Decimal
    total_gastos: Decimal
    comision_chofer: Decimal
    canon: Decimal
    km_excedentes: Decimal
    cargo_km_excedentes: Decimal
    total_chofer: Decimal
    total_propietario: Decimal
    saldo_chofer: Decimal
    saldo_propietario: Decimal
    estado: str
    version: int
    calculada_en: datetime
    created_at: datetime
    updated_at: datetime
    detalles: Optional[List[LiquidacionDetalleResponse]] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS PARA CONTEXTO INTERNO
# ============================================================

class LiquidacionContextSchema(BaseModel):
    turno_id: UUID
    contrato_id: UUID
    vehiculo_id: UUID
    chofer_id: UUID
    propietario_id: UUID
    control_base_id: UUID
    tipo_contrato: str
    fecha_inicio: datetime
    fecha_fin: datetime
    viajes: List[Dict[str, Any]]
    gastos_turno: List[Dict[str, Any]]
    gastos_vehiculo: List[Dict[str, Any]] = []
    
    # PORCENTAJE
    porcentaje_chofer: Optional[Decimal] = None
    recaudacion_ticketera: Optional[Decimal] = None
    
    # ALQUILER
    canon_diario: Optional[Decimal] = None
    canon_calculado: Optional[Decimal] = None
    km_inicial: Optional[Decimal] = None
    km_final: Optional[Decimal] = None
    km_recorridos: Optional[Decimal] = None
    km_incluidos_dia: Optional[Decimal] = None
    km_incluidos_totales: Optional[Decimal] = None
    km_excedentes: Optional[Decimal] = None
    cargo_km_excedentes: Optional[Decimal] = None
    valor_km_excedente: Optional[Decimal] = None
    modalidad_computo: Optional[str] = None
    dias_contractuales: Optional[List[str]] = None
    dias_trabajados: Optional[int] = None
    tratamiento_dia_no_trabajado: Optional[str] = None
    
    # HORARIOS FLEXIBLES
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    duracion_minima_horas: Optional[int] = None
    permite_extension: Optional[bool] = None
    hora_fin_extension: Optional[str] = None
    dia_inicio_semana: Optional[str] = None
    duracion_turno_horas: Optional[Decimal] = None


# ============================================================
# SCHEMAS PARA RESULTADO DEL CÁLCULO
# ============================================================

class LiquidacionResultado(BaseModel):
    monto_bruto: Decimal
    total_gastos: Decimal
    comision_chofer: Decimal
    canon: Decimal
    km_excedentes: Decimal = Field(default=0)
    cargo_km_excedentes: Decimal = Field(default=0)
    total_chofer: Decimal
    total_propietario: Decimal
    saldo_chofer: Decimal = Field(default=0)
    saldo_propietario: Decimal = Field(default=0)
    detalles: List[LiquidacionDetalleCreate]


# ============================================================
# SCHEMAS PARA D7 - APROBACIÓN Y PAGOS
# ============================================================

class AprobarLiquidacionRequest(BaseModel):
    pass


class RechazarLiquidacionRequest(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=500)


class RegistrarPagoRequest(BaseModel):
    metodo_pago: str = Field(..., description="EFECTIVO, TRANSFERENCIA, DEBITO, CREDITO, QR")
    referencia: Optional[str] = Field(None, max_length=100)


class LiquidacionEstadoResponse(BaseModel):
    id: UUID
    estado: str
    historial: List[LiquidacionEstadoHistorialResponse]


class LiquidacionConSaldoResponse(LiquidacionResponse):
    saldo_pendiente: Decimal
    estado_saldo: str
    pagos_realizados: List[Dict[str, Any]]