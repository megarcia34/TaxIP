"""
Facturacion Service - Gestión de facturación corporativa y de tenant
Genera facturas, procesa pagos y administra ciclos de facturación
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
from app.models.tenant import Empresa, ControlBase
from app.models.fleet import Vehiculo
from app.models.auth import Usuario
from app.schemas.corporate_schemas import (
    FacturaCreate,
    FacturaResponse,
    PagoCreate,
    PagoResponse,
    FacturaFilter
)
from app.core.exceptions import (
    CorporateError,
    CorporateNotFoundError,
    CorporateInvalidStateError,
    CorporatePermissionError
)
from app.services.cuenta_corriente_service import CuentaCorrienteService


class FacturacionService:
    """
    Servicio centralizado para la gestión de facturación
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cuenta_service = CuentaCorrienteService(db)

    # ============================================================
    # GENERACIÓN DE FACTURAS CORPORATIVAS
    # ============================================================

    async def generar_factura_corporativa(self, data: FacturaCreate) -> FacturaCorporativa:
        """
        Generar una factura corporativa para una empresa
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
            cuenta = await self.cuenta_service.get_cuenta(data.empresa_id)
            if cuenta:
                from app.schemas.corporate_schemas import MovimientoCreate
                await self.cuenta_service.registrar_movimiento(
                    MovimientoCreate(
                        cuenta_id=cuenta.id,
                        viaje_id=None,
                        tipo_movimiento="debito",
                        concepto=f"Factura {data.numero_factura} - {data.periodo_desde.strftime('%m/%Y')}",
                        monto=total,
                        referencia=data.numero_factura,
                        meta_data={"factura_id": str(factura.id)}
                    )
                )

        await self.db.commit()
        await self.db.refresh(factura)

        return factura

    async def generar_facturas_periodicas(self, empresa_id: UUID) -> List[FacturaCorporativa]:
        """
        Generar facturas periódicas para una empresa
        (basado en consumos del período)
        """
        # Obtener empresa
        empresa = await self.db.get(Empresa, empresa_id)
        if not empresa:
            raise CorporateNotFoundError(f"Empresa {empresa_id} no encontrada")

        # Determinar período (último mes)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)

        # Obtener consumos del período
        consumos = await self._obtener_consumos_periodo(empresa_id, fecha_inicio, fecha_fin)

        if not consumos:
            return []

        # Generar factura
        numero_factura = await self._generar_numero_factura(empresa_id)
        subtotal = sum(c["monto"] for c in consumos)
        iva = subtotal * Decimal("0.21")
        total = subtotal + iva

        factura = await self.generar_factura_corporativa(
            FacturaCreate(
                empresa_id=empresa_id,
                numero_factura=numero_factura,
                periodo_desde=fecha_inicio,
                periodo_hasta=fecha_fin,
                subtotal=subtotal,
                descuento=Decimal(0),
                iva=iva,
                fecha_vencimiento=fecha_fin + timedelta(days=15),
                observaciones=f"Factura período {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
                registrar_movimiento=True
            )
        )

        # Actualizar viajes como facturados
        await self._marcar_viajes_facturados(empresa_id, fecha_inicio, fecha_fin)

        return [factura]

    # ============================================================
    # GENERACIÓN DE FACTURAS DE TENANT
    # ============================================================

    async def generar_factura_tenant(
        self,
        control_base_id: UUID,
        periodo: str
    ) -> Dict[str, Any]:
        """
        Generar factura de tenant (canon mensual por vehículo)
        """
        # Validar tenant
        tenant = await self.db.get(ControlBase, control_base_id)
        if not tenant:
            raise CorporateNotFoundError(f"Tenant {control_base_id} no encontrado")

        # Obtener vehículos activos del tenant
        query = select(Vehiculo).where(
            and_(
                Vehiculo.control_base_id == control_base_id,
                Vehiculo.activo == True
            )
        )
        result = await self.db.execute(query)
        vehiculos = result.scalars().all()
        cantidad_vehiculos = len(vehiculos)

        if cantidad_vehiculos == 0:
            raise CorporateInvalidStateError("El tenant no tiene vehículos activos")

        # Calcular canon (ejemplo: $5000 por vehículo)
        canon_por_vehiculo = Decimal(5000)
        total_canon = canon_por_vehiculo * Decimal(str(cantidad_vehiculos))

        # Calcular porcentaje plataforma (ejemplo: 15%)
        porcentaje_plataforma = Decimal("15")
        comision_plataforma = total_canon * (porcentaje_plataforma / Decimal(100))
        total_a_pagar = total_canon + comision_plataforma

        # Generar número de factura
        numero_factura = f"TEN-{control_base_id.hex[:8].upper()}-{datetime.now().strftime('%Y%m')}"

        # Crear registro de factura (en tenant.factura)
        query = text("""
            INSERT INTO tenant.factura (
                id, control_base_id, periodo, vehiculos_activos, 
                canon_total, porcentaje_plataforma, total_a_pagar,
                estado, fecha_emision, numero_factura, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), :control_base_id, :periodo, :vehiculos_activos,
                :canon_total, :porcentaje_plataforma, :total_a_pagar,
                'pendiente', NOW(), :numero_factura, NOW(), NOW()
            )
            RETURNING id, numero_factura
        """)

        result = await self.db.execute(query, {
            "control_base_id": control_base_id,
            "periodo": periodo,
            "vehiculos_activos": cantidad_vehiculos,
            "canon_total": float(total_canon),
            "porcentaje_plataforma": float(porcentaje_plataforma),
            "total_a_pagar": float(total_a_pagar),
            "numero_factura": numero_factura
        })

        row = result.first()
        await self.db.commit()

        return {
            "id": row[0],
            "numero_factura": row[1],
            "control_base_id": control_base_id,
            "periodo": periodo,
            "vehiculos_activos": cantidad_vehiculos,
            "canon_total": total_canon,
            "porcentaje_plataforma": porcentaje_plataforma,
            "total_a_pagar": total_a_pagar,
            "estado": "pendiente"
        }

    # ============================================================
    # PROCESAMIENTO DE PAGOS
    # ============================================================

    async def procesar_pago(self, data: PagoCreate) -> PagoCorporativo:
        """
        Procesar pago de una factura
        """
        # Validar factura
        factura = await self.db.get(FacturaCorporativa, data.factura_id)
        if not factura:
            raise CorporateNotFoundError(f"Factura {data.factura_id} no encontrada")

        if factura.estado == "pagada":
            raise CorporateInvalidStateError("La factura ya está pagada")

        # Validar usuario
        if data.confirmado_por:
            usuario = await self.db.get(Usuario, data.confirmado_por)
            if not usuario:
                raise CorporateNotFoundError(f"Usuario {data.confirmado_por} no encontrado")

        # Calcular monto
        monto = data.monto or factura.total

        # Crear pago
        pago = PagoCorporativo(
            id=uuid.uuid4(),
            empresa_id=factura.empresa_id,
            factura_id=data.factura_id,
            monto=monto,
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

        # Registrar movimiento de crédito en la cuenta
        cuenta = await self.cuenta_service.get_cuenta(factura.empresa_id)
        if cuenta:
            from app.schemas.corporate_schemas import MovimientoCreate
            await self.cuenta_service.registrar_movimiento(
                MovimientoCreate(
                    cuenta_id=cuenta.id,
                    viaje_id=None,
                    tipo_movimiento="credito",
                    concepto=f"Pago factura {factura.numero_factura}",
                    monto=monto,
                    referencia=data.referencia,
                    meta_data={"factura_id": str(factura.id), "pago_id": str(pago.id)}
                )
            )

        await self.db.commit()
        await self.db.refresh(pago)

        return pago

    # ============================================================
    # MÉTODOS DE CONSULTA
    # ============================================================

    async def get_facturas(
        self,
        filters: FacturaFilter
    ) -> List[FacturaCorporativa]:
        """
        Obtener facturas con filtros
        """
        query = select(FacturaCorporativa)

        if filters.empresa_id:
            query = query.where(FacturaCorporativa.empresa_id == filters.empresa_id)
        if filters.estado:
            query = query.where(FacturaCorporativa.estado == filters.estado)
        if filters.fecha_desde:
            query = query.where(FacturaCorporativa.fecha_emision >= filters.fecha_desde)
        if filters.fecha_hasta:
            query = query.where(FacturaCorporativa.fecha_emision <= filters.fecha_hasta)

        query = query.order_by(FacturaCorporativa.fecha_emision.desc())

        if filters.limit:
            query = query.limit(filters.limit)
        if filters.offset:
            query = query.offset(filters.offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_pagos(self, factura_id: UUID) -> List[PagoCorporativo]:
        """
        Obtener pagos de una factura
        """
        query = select(PagoCorporativo).where(
            PagoCorporativo.factura_id == factura_id
        ).order_by(PagoCorporativo.fecha_pago)
        result = await self.db.execute(query)
        return result.scalars().all()

    # ============================================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ============================================================

    async def actualizar_estados_vencidos(self) -> int:
        """
        Actualizar facturas vencidas a estado 'vencida'
        """
        ahora = datetime.now()
        query = select(FacturaCorporativa).where(
            and_(
                FacturaCorporativa.fecha_vencimiento < ahora,
                FacturaCorporativa.estado == "pendiente"
            )
        )
        result = await self.db.execute(query)
        facturas = result.scalars().all()

        for factura in facturas:
            factura.estado = "vencida"
            factura.updated_at = datetime.now()

        await self.db.commit()
        return len(facturas)

    # ============================================================
    # REPORTES
    # ============================================================

    async def generar_reporte_facturacion(
        self,
        empresa_id: UUID,
        fecha_desde: datetime,
        fecha_hasta: datetime
    ) -> Dict[str, Any]:
        """
        Generar reporte de facturación para una empresa
        """
        # Obtener facturas del período
        query = select(FacturaCorporativa).where(
            and_(
                FacturaCorporativa.empresa_id == empresa_id,
                FacturaCorporativa.fecha_emision >= fecha_desde,
                FacturaCorporativa.fecha_emision <= fecha_hasta
            )
        )
        result = await self.db.execute(query)
        facturas = result.scalars().all()

        # Calcular totales
        total_facturado = sum(f.total for f in facturas)
        total_pagado = sum(f.total for f in facturas if f.estado == "pagada")
        total_pendiente = sum(f.total for f in facturas if f.estado in ["pendiente", "vencida"])
        cantidad_facturas = len(facturas)

        return {
            "empresa_id": empresa_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "total_facturado": total_facturado,
            "total_pagado": total_pagado,
            "total_pendiente": total_pendiente,
            "cantidad_facturas": cantidad_facturas,
            "facturas": facturas
        }

    # ============================================================
    # MÉTODOS PRIVADOS
    # ============================================================

    async def _obtener_consumos_periodo(
        self,
        empresa_id: UUID,
        fecha_desde: datetime,
        fecha_hasta: datetime
    ) -> List[Dict[str, Any]]:
        """
        Obtener consumos de viajes de una empresa en un período
        """
        query = text("""
            SELECT 
                v.id,
                v.precio_final as monto,
                v.finalizado_en,
                v.control_base_id
            FROM trip.viaje_solicitado v
            WHERE v.empresa_id = :empresa_id
                AND v.estado = 'finalizado'
                AND v.finalizado_en >= :fecha_desde
                AND v.finalizado_en <= :fecha_hasta
                AND (v.facturado IS NULL OR v.facturado = false)
            ORDER BY v.finalizado_en
        """)
        result = await self.db.execute(query, {
            "empresa_id": empresa_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        })
        rows = result.all()
        return [{"id": row[0], "monto": row[1], "fecha": row[2], "control_base_id": row[3]} for row in rows]

    async def _marcar_viajes_facturados(
        self,
        empresa_id: UUID,
        fecha_desde: datetime,
        fecha_hasta: datetime
    ) -> None:
        """
        Marcar viajes como facturados
        """
        query = text("""
            UPDATE trip.viaje_solicitado
            SET facturado = true, updated_at = NOW()
            WHERE empresa_id = :empresa_id
                AND estado = 'finalizado'
                AND finalizado_en >= :fecha_desde
                AND finalizado_en <= :fecha_hasta
                AND (facturado IS NULL OR facturado = false)
        """)
        await self.db.execute(query, {
            "empresa_id": empresa_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        })

    async def _generar_numero_factura(self, empresa_id: UUID) -> str:
        """
        Generar número de factura secuencial
        """
        # Obtener el último número de factura
        query = text("""
            SELECT numero_factura
            FROM corporate.factura_corporativa
            WHERE empresa_id = :empresa_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        result = await self.db.execute(query, {"empresa_id": empresa_id})
        row = result.first()

        if row:
            # Incrementar el número
            numero = row[0]
            if numero.startswith("FAC-"):
                try:
                    secuencia = int(numero.split("-")[-1])
                    secuencia += 1
                    return f"FAC-{secuencia:06d}"
                except:
                    pass

        # Si no hay facturas previas
        return f"FAC-000001"