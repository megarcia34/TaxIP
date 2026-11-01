"""
Schemas Pydantic para el modulo de conciliacion de turnos.

Usados por los endpoints del propietario y del chofer.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# ============================================================
# BANDEJA DE CONCILIACIONES (PROPIETARIO)
# ============================================================

class ConciliacionPendienteItem(BaseModel):
    """Item de la bandeja de conciliaciones pendientes."""
    turno_id: UUID
    fin_turno: Optional[datetime]
    vehiculo_patente: str
    chofer_nombre: str
    tipo_contrato: str
    recaudacion_declarada: Decimal
    efectivo_en_mano: Decimal
    gastos_declarados: Decimal
    diferencia: Decimal
    dias_restantes: int
    estado: str


class ConciliacionPendienteResponse(BaseModel):
    """Respuesta de la bandeja de conciliaciones pendientes."""
    total: int
    turnos: List[ConciliacionPendienteItem]


# ============================================================
# DETALLE DE CONCILIACION
# ============================================================

class GastoConciliacionItem(BaseModel):
    """Gasto declarado por el chofer, pendiente de aprobacion."""
    id: UUID
    tipo_gasto: str
    monto: Decimal
    descripcion: Optional[str]
    url_comprobante: Optional[str]
    created_at: datetime
    estado_aprobacion: str  # "pendiente", "aprobado", "rechazado"


class DiferenciaItem(BaseModel):
    """Diferencia detectada en la conciliacion."""
    id: UUID
    tipo: str  # "DEUDA_CHOFER", "DEUDA_PROPIETARIO", "NEUTRA"
    concepto: str
    monto: Decimal
    descripcion: Optional[str]
    estado: str  # "PENDIENTE", "SALDADA"


class ConciliacionDetalleResponse(BaseModel):
    """Detalle completo de un turno para conciliar."""
    turno_id: UUID
    fin_turno: Optional[datetime]
    vehiculo_patente: str
    chofer_nombre: str
    tipo_contrato: str
    porcentaje_chofer: Optional[Decimal]
    canon_diario: Optional[Decimal]
    tratamiento_gastos: Optional[str]
    
    # Recaudacion
    recaudacion_viajes: Decimal
    recaudacion_manual: Decimal
    recaudacion_total: Decimal
    efectivo_en_mano: Decimal
    recaudacion_electronico: Decimal
    diferencia_efectivo: Decimal
    
    # Gastos
    gastos: List[GastoConciliacionItem]
    gastos_total: Decimal
    
    # Diferencias
    diferencias: List[DiferenciaItem]
    diferencias_total: Decimal
    puede_cerrar: bool


# ============================================================
# ACCIONES
# ============================================================

class AprobarGastoRequest(BaseModel):
    """Request para aprobar un gasto."""
    pass  # No requiere body


class RechazarGastoRequest(BaseModel):
    """Request para rechazar un gasto."""
    motivo: str = Field(..., min_length=1, max_length=500)


class CerrarConciliacionRequest(BaseModel):
    """Request para cerrar la conciliacion."""
    observaciones: Optional[str] = None


class SaldarDiferenciaRequest(BaseModel):
    """Request para marcar una diferencia como saldada."""
    observaciones: Optional[str] = None


# ============================================================
# DISPUTAS
# ============================================================

class AbrirDisputaRequest(BaseModel):
    """Request para abrir una disputa."""
    motivo: str = Field(..., min_length=10, max_length=2000)


class ResolverDisputaRequest(BaseModel):
    """Request para resolver una disputa."""
    resolucion: str = Field(..., min_length=10, max_length=2000)
    a_favor_de: str = Field(..., pattern="^(chofer|propietario)$")


class DisputaResponse(BaseModel):
    """Respuesta de una disputa."""
    id: UUID
    turno_id: UUID
    abierta_por: UUID
    motivo: str
    estado: str
    resolucion: Optional[str]
    resuelta_por: Optional[UUID]
    resuelta_en: Optional[datetime]
    plazo_tenant: Optional[datetime]
    plazo_plataforma: Optional[datetime]
    created_at: datetime


# ============================================================
# HISTORIAL
# ============================================================

class ConciliacionHistorialItem(BaseModel):
    """Item del historial de conciliaciones cerradas."""
    turno_id: UUID
    fin_turno: Optional[datetime]
    conciliado_en: Optional[datetime]
    vehiculo_patente: str
    chofer_nombre: str
    recaudacion_total: Decimal
    total_chofer: Decimal
    total_propietario: Decimal
    tipo_conciliacion: str  # "MANUAL", "AUTOMATICA"
    estado: str


class ConciliacionHistorialResponse(BaseModel):
    """Respuesta del historial de conciliaciones."""
    total: int
    conciliaciones: List[ConciliacionHistorialItem]