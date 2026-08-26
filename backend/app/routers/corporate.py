"""
Corporate Routes - Endpoints para gestión corporativa
Cuentas corrientes, movimientos, facturas y pagos
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.dependencies import (
    get_current_user,
    get_admin_tenant_user,
    get_super_admin_user,
    get_empresa_context
)
from app.services.cuenta_corriente_service import CuentaCorrienteService
from app.services.facturacion_service import FacturacionService
from app.schemas.corporate_schemas import (
    CuentaCreate,
    CuentaResponse,
    MovimientoCreate,
    MovimientoResponse,
    FacturaCreate,
    FacturaResponse,
    FacturaFilter,
    PagoCreate,
    PagoResponse,
    ResumenCuenta
)
from app.core.exceptions import (
    CorporateError,
    CorporateNotFoundError,
    CorporateInvalidStateError,
    CorporatePermissionError,
    CorporateCreditLimitExceededError
)

router = APIRouter(prefix="/api/corporate", tags=["Corporate"])


# ============================================================
# CUENTAS CORRIENTES
# ============================================================

@router.post("/cuenta", response_model=CuentaResponse)
async def crear_cuenta(
    data: CuentaCreate,
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una cuenta corriente para una empresa
    Solo Admin Tenant puede crear cuentas
    """
    try:
        service = CuentaCorrienteService(db)
        cuenta = await service.crear_cuenta(data)
        return cuenta
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/cuenta/{empresa_id}", response_model=CuentaResponse)
async def get_cuenta(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener cuenta corriente de una empresa
    """
    try:
        service = CuentaCorrienteService(db)
        cuenta = await service.get_cuenta(empresa_id)
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta para empresa {empresa_id} no encontrada"
            )
        return cuenta
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/cuenta/{empresa_id}/resumen", response_model=ResumenCuenta)
async def get_resumen_cuenta(
    empresa_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener resumen de cuenta corriente
    """
    try:
        service = CuentaCorrienteService(db)
        return await service.get_resumen_cuenta(empresa_id)
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# MOVIMIENTOS
# ============================================================

@router.post("/movimiento", response_model=MovimientoResponse)
async def registrar_movimiento(
    data: MovimientoCreate,
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un movimiento en una cuenta corriente
    Solo Admin Tenant puede registrar movimientos
    """
    try:
        service = CuentaCorrienteService(db)
        movimiento = await service.registrar_movimiento(data)
        return movimiento
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CorporateCreditLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/movimientos/{cuenta_id}", response_model=List[MovimientoResponse])
async def get_movimientos(
    cuenta_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tipo: Optional[str] = Query(None, description="credito | debito | ajuste"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener movimientos de una cuenta
    """
    try:
        service = CuentaCorrienteService(db)
        movimientos = await service.get_movimientos(cuenta_id, limit, offset, tipo)
        return movimientos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# FACTURAS
# ============================================================

@router.post("/factura", response_model=FacturaResponse)
async def crear_factura(
    data: FacturaCreate,
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una factura corporativa
    Solo Admin Tenant puede crear facturas
    """
    try:
        service = FacturacionService(db)
        factura = await service.generar_factura_corporativa(data)
        return factura
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/facturas/{empresa_id}", response_model=List[FacturaResponse])
async def get_facturas(
    empresa_id: UUID,
    estado: Optional[str] = Query(None, description="pendiente | pagada | vencida | cancelada"),
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener facturas de una empresa
    """
    try:
        filters = FacturaFilter(
            empresa_id=empresa_id,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=limit,
            offset=offset
        )
        service = FacturacionService(db)
        facturas = await service.get_facturas(filters)
        return facturas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/factura/generar-periodica")
async def generar_factura_periodica(
    empresa_id: UUID,
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generar factura periódica para una empresa
    """
    try:
        service = FacturacionService(db)
        facturas = await service.generar_facturas_periodicas(empresa_id)
        return {
            "success": True,
            "message": f"Factura generada correctamente",
            "facturas": facturas
        }
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/factura/actualizar-vencidas")
async def actualizar_facturas_vencidas(
    current_user: tuple = Depends(get_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar facturas vencidas (solo Super Admin)
    """
    try:
        service = FacturacionService(db)
        cantidad = await service.actualizar_estados_vencidos()
        return {
            "success": True,
            "message": f"{cantidad} facturas actualizadas a estado 'vencida'",
            "cantidad": cantidad
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# PAGOS
# ============================================================

@router.post("/pago", response_model=PagoResponse)
async def procesar_pago(
    data: PagoCreate,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Procesar pago de una factura
    """
    try:
        service = FacturacionService(db)
        pago = await service.procesar_pago(data)
        return pago
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pagos/{factura_id}", response_model=List[PagoResponse])
async def get_pagos(
    factura_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener pagos de una factura
    """
    try:
        service = FacturacionService(db)
        pagos = await service.get_pagos(factura_id)
        return pagos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================
# REPORTES
# ============================================================

@router.get("/reporte/facturacion/{empresa_id}")
async def get_reporte_facturacion(
    empresa_id: UUID,
    fecha_desde: datetime,
    fecha_hasta: datetime,
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener reporte de facturación
    """
    try:
        service = FacturacionService(db)
        reporte = await service.generar_reporte_facturacion(
            empresa_id=empresa_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        return reporte
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tenant/{control_base_id}/factura-periodica")
async def generar_factura_tenant_periodica(
    control_base_id: UUID,
    periodo: str = Query(..., description="YYYY-MM"),
    current_user: tuple = Depends(get_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generar factura periódica de tenant (canon por vehículo)
    Solo Super Admin puede generar facturas de tenant
    """
    try:
        service = FacturacionService(db)
        factura = await service.generar_factura_tenant(control_base_id, periodo)
        return {
            "success": True,
            "message": "Factura de tenant generada correctamente",
            "factura": factura
        }
    except CorporateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CorporateInvalidStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))