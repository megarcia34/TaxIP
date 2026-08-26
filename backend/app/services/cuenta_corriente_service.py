"""
Cuenta Corriente Service - Gestión de cuentas corrientes corporativas
Maneja créditos, débitos, saldos y facturación
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func
from sqlalchemy.orm import selectinload

from app.models.corporate import (
    CuentaCorriente,
    MovimientoCuenta,
    FacturaCorporativa,
    PagoCorporativo
)
from app.models.tenant import Empresa
from app.models.trip import ViajeSolicitado
from app.models.auth import Usuario
from app.schemas.corporate_schemas import (
    CuentaCreate,
    CuentaResponse,
    MovimientoCreate,
    MovimientoResponse,
    FacturaCreate,
    FacturaResponse,
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


class CuentaCorrienteService:
    """
    Servicio centralizado para la gestión de cuentas corrientes corporativas
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # GESTIÓN DE CUENTAS
    # ============================================================

    async def crear_cuenta(self, data: CuentaCreate) -> CuentaCorriente:
        """
        Crear una cuenta corriente para una empresa
        """
        # Validar que la empresa existe
        empresa = await self.db.get(Empresa, data.empresa_id)
        if not empresa:
            raise CorporateNotFoundError(f"Empresa {data.empresa_id} no encontrada")

        # Validar que la empresa no tenga ya una cuenta
        query = select(CuentaCorriente).where(CuentaCorriente.empresa_id == data.empresa_id)
        result = await self.db.execute(query)
        if result.first():
            raise CorporateInvalidStateError(f"La empresa {data.empresa_id} ya tiene una cuenta corriente")

        # Crear cuenta
        cuenta = CuentaCorriente(
            id=uuid.uuid4(),
            empresa_id=data.empresa_id,
            saldo_actual=Decimal(0),
            saldo_disponible=data.limite_credito or Decimal(0),
            limite_credito=data.limite_credito or Decimal(0),
            moneda=data.moneda or "ARS",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(cuenta)
        await self.db.commit()
        await self.db.refresh(cuenta)

        return cuenta

    async def get_cuenta(self, empresa_id: UUID) -> Optional[CuentaCorriente]:
        """
        Obtener cuenta corriente por empresa
        """
        query = select(CuentaCorriente).where(
            CuentaCorriente.empresa_id == empresa_id
        ).options(
            selectinload(CuentaCorriente.empresa),
            selectinload(CuentaCorriente.movimientos)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_cuenta_by_id(self, cuenta_id: UUID) -> Optional[CuentaCorriente]:
        """
        Obtener cuenta por ID
        """
        return await self.db.get(CuentaCorriente, cuenta_id)

    async def get_resumen_cuenta(self, empresa_id: UUID) -> ResumenCuenta:
        """
        Obtener resumen de la cuenta
        """
        cuenta = await self.get_cuenta(empresa_id)
        if not cuenta:
            raise CorporateNotFoundError(f"Cuenta para empresa {empresa_id} no encontrada")

        # Contar movimientos recientes
        fecha_limite = datetime.now() - timedelta(days=30)
        query = select(MovimientoCuenta).where(
            and_(
                MovimientoCuenta.cuenta_id == cuenta.id,
                MovimientoCuenta.created_at >= fecha_limite
            )
        )
        result = await self.db.execute(query)
        movimientos_recientes = result.scalars().all()

        # Contar facturas pendientes
        query = select(FacturaCorporativa).where(
            and_(
                FacturaCorporativa.empresa_id == empresa_id,
                FacturaCorporativa.estado.in_(["pendiente", "vencida"])
            )
        )
        result = await self.db.execute(query)
        facturas_pendientes = result.scalars().all()

        total_pendiente = sum(f.total for f in facturas_pendientes)

        return ResumenCuenta(
            empresa_id=empresa_id,
            saldo_actual=cuenta.saldo_actual,
            saldo_disponible=cuenta.saldo_disponible,
            limite_credito=cuenta.limite_credito,
            total_pendiente=total_pendiente,
            cantidad_movimientos_recientes=len(movimientos_recientes),
            cantidad_facturas_pendientes=len(facturas_pendientes)
        )

    # ============================================================
    # MOVIMIENTOS
    # ============================================================

    async def registrar_movimiento(self, data: MovimientoCreate) -> MovimientoCuenta:
        """
        Registrar un movimiento en la cuenta
        """
        # Validar que la cuenta existe
        cuenta = await self.get_cuenta_by_id(data.cuenta_id)
        if not cuenta:
            raise CorporateNotFoundError(f"Cuenta {data.cuenta_id} no encontrada")

        # Validar que la empresa está activa
        empresa = await self.db.get(Empresa, cuenta.empresa_id)
        if not empresa or not empresa.activo:
            raise CorporateInvalidStateError("La empresa no está activa")

        # Calcular saldos
        saldo_anterior = cuenta.saldo_actual

        if data.tipo_movimiento == "credito":
            saldo_nuevo = saldo_anterior + data.monto
        elif data.tipo_movimiento == "debito":
            # Verificar que no exceda el saldo disponible
            if data.monto > cuenta.saldo_disponible:
                raise CorporateCreditLimitExceededError(
                    f"Saldo insuficiente. Disponible: {cuenta.saldo_disponible}, "
                    f"Debito: {data.monto}"
                )
            saldo_nuevo = saldo_anterior - data.monto
            # Actualizar saldo disponible
            cuenta.saldo_disponible = cuenta.saldo_disponible - data.monto
        else:
            # Ajuste
            saldo_nuevo = saldo_anterior + data.monto

        # Si es un débito, verificar que sea por un viaje
        if data.tipo_movimiento == "debito" and data.viaje_id:
            viaje = await self.db.get(ViajeSolicitado, data.viaje_id)
            if not viaje:
                raise CorporateNotFoundError(f"Viaje {data.viaje_id} no encontrado")

        # Crear movimiento
        movimiento = MovimientoCuenta(
            id=uuid.uuid4(),
            cuenta_id=data.cuenta_id,
            viaje_id=data.viaje_id,
            tipo_movimiento=data.tipo_movimiento,
            concepto=data.concepto,
            monto=data.monto,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            referencia=data.referencia,
            meta_data=data.meta_data,
            created_at=datetime.now()
        )

        self.db.add(movimiento)

        # Actualizar saldo de la cuenta
        cuenta.saldo_actual = saldo_nuevo
        cuenta.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(movimiento)

        return movimiento

    async def get_movimientos(
        self,
        cuenta_id: UUID,
        limit: int = 100,
        offset: int = 0,
        tipo: Optional[str] = None
    ) -> List[MovimientoCuenta]:
        """
        Obtener movimientos de una cuenta
        """
        query = select(MovimientoCuenta).where(
            MovimientoCuenta.cuenta_id == cuenta_id
        )

        if tipo:
            query = query.where(MovimientoCuenta.tipo_movimiento == tipo)

        query = query.order_by(MovimientoCuenta.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    # ============================================================
    # FACTURACIÓN
    # ============================================================

    async def generar_factura(self, data: FacturaCreate) -> FacturaCorporativa:
        """
        Generar una factura corporativa
        """
        # Validar que la empresa existe
        empresa = await self.db.get(Empresa, data.empresa_id)
        if not empresa:
            raise CorporateNotFoundError(f"Empresa {data.empresa_id} no encontrada")

        # Validar que no haya factura duplicada
        query = select(FacturaCorporativa).where(
            and_(
                FacturaCorporativa.empresa_id == data.empresa_id,
                FacturaCorporativa.numero_factura == data.numero_factura
            )
        )
        result = await self.db.execute(query)
        if result.first():
            raise CorporateInvalidStateError(f"Factura {data.numero_factura} ya existe")

        # Calcular total
        total = data.subtotal - data.descuento + data.iva

        # Crear factura
        factura = FacturaCorporativa(
            id=uuid.uuid4(),
            empresa_id=data.empresa_id,
            numero_factura=data.numero_factura,
            periodo_desde=data.periodo_desde,
            periodo_hasta=data.periodo_hasta,
            fecha_emision=datetime.now(),
            fecha_vencimiento=data.fecha_vencimiento or (datetime.now() + timedelta(days=30)),
            subtotal=data.subtotal,
            descuento=data.descuento,
            iva=data.iva,
            total=total,
            estado="pendiente",
            pdf_url=data.pdf_url,
            observaciones=data.observaciones,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(factura)

        # Registrar movimiento de débito por la factura
        if data.registrar_movimiento:
            # Buscar la cuenta
            cuenta = await self.get_cuenta(data.empresa_id)
            if cuenta:
                await self.registrar_movimiento(
                    MovimientoCreate(
                        cuenta_id=cuenta.id,
                        viaje_id=None,
                        tipo_movimiento="debito",
                        concepto=f"Factura {data.numero_factura}",
                        monto=total,
                        referencia=data.numero_factura,
                        meta_data={"factura_id": str(factura.id)}
                    )
                )

        await self.db.commit()
        await self.db.refresh(factura)

        return factura

    async def get_facturas(
        self,
        empresa_id: UUID,
        estado: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FacturaCorporativa]:
        """
        Obtener facturas de una empresa
        """
        query = select(FacturaCorporativa).where(
            FacturaCorporativa.empresa_id == empresa_id
        )

        if estado:
            query = query.where(FacturaCorporativa.estado == estado)

        query = query.order_by(FacturaCorporativa.fecha_emision.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def pagar_factura(self, data: PagoCreate) -> PagoCorporativo:
        """
        Registrar pago de una factura
        """
        # Validar que la factura existe
        factura = await self.db.get(FacturaCorporativa, data.factura_id)
        if not factura:
            raise CorporateNotFoundError(f"Factura {data.factura_id} no encontrada")

        if factura.estado == "pagada":
            raise CorporateInvalidStateError("La factura ya está pagada")

        # Validar que el usuario existe
        if data.confirmado_por:
            usuario = await self.db.get(Usuario, data.confirmado_por)
            if not usuario:
                raise CorporateNotFoundError(f"Usuario {data.confirmado_por} no encontrado")

        # Crear pago
        pago = PagoCorporativo(
            id=uuid.uuid4(),
            empresa_id=factura.empresa_id,
            factura_id=data.factura_id,
            monto=data.monto or factura.total,
            metodo_pago=data.metodo_pago,
            referencia=data.referencia,
            comprobante_url=data.comprobante_url,
            estado="confirmado",
            fecha_pago=datetime.now(),
            confirmado_por=data.confirmado_por,
            confirmado_en=datetime.now(),
            observaciones=data.observaciones,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(pago)

        # Actualizar estado de la factura
        factura.estado = "pagada"
        factura.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(pago)

        return pago

    # ============================================================
    # MÉTODOS DE CONSULTA
    # ============================================================

    async def verificar_credito(self, empresa_id: UUID, monto: Decimal) -> bool:
        """
        Verificar si hay crédito disponible para un monto
        """
        cuenta = await self.get_cuenta(empresa_id)
        if not cuenta:
            return False
        return cuenta.saldo_disponible >= monto

    async def obtener_deuda_total(self, empresa_id: UUID) -> Decimal:
        """
        Obtener deuda total de una empresa
        """
        # Sumar facturas pendientes
        query = select(func.sum(FacturaCorporativa.total)).where(
            and_(
                FacturaCorporativa.empresa_id == empresa_id,
                FacturaCorporativa.estado.in_(["pendiente", "vencida"])
            )
        )
        result = await self.db.execute(query)
        total = result.scalar() or Decimal(0)
        return total

    async def obtener_facturas_pendientes(self, empresa_id: UUID) -> List[FacturaCorporativa]:
        """
        Obtener facturas pendientes de una empresa
        """
        query = select(FacturaCorporativa).where(
            and_(
                FacturaCorporativa.empresa_id == empresa_id,
                FacturaCorporativa.estado.in_(["pendiente", "vencida"])
            )
        ).order_by(FacturaCorporativa.fecha_vencimiento)
        result = await self.db.execute(query)
        return result.scalars().all()