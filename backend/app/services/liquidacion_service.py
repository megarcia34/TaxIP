# app/services/liquidacion_service.py
"""
Servicio de liquidación de turnos
"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo
from app.models.turno import TurnoChofer
from app.models.gasto_turno import GastoTurno
from app.models.trip import ViajeSolicitado


class LiquidacionService:
    """Servicio para cálculo de liquidaciones"""

    @staticmethod
    async def calcular_liquidacion(
        db: AsyncSession,
        turno_id: str
    ) -> dict:
        """
        Calcular liquidación completa del turno
        """
        # Obtener turno
        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        # Obtener contrato
        contrato = await db.get(ContratoVehiculo, turno.contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato no encontrado"
            )

        # 1. Calcular recaudación de la app
        viajes_app = await db.execute(
            select(
                func.sum(ViajeSolicitado.precio_final)
            )
            .where(
                and_(
                    ViajeSolicitado.vehiculo_id == turno.vehiculo_id,
                    ViajeSolicitado.finalizado_en >= turno.inicio_turno,
                    ViajeSolicitado.finalizado_en <= turno.fin_turno,
                    ViajeSolicitado.estado == 'finalizado'
                )
            )
        )
        recaudacion_app_total = viajes_app.scalar() or 0

        # 2. Obtener gastos del turno
        gastos = await db.execute(
            select(func.sum(GastoTurno.monto))
            .where(GastoTurno.turno_id == turno.id)
        )
        total_gastos = gastos.scalar() or 0

        # 3. Calcular monto bruto total
        monto_bruto = recaudacion_app_total + (turno.recaudacion_ticketera_calle or 0)

        # 4. Calcular comisión del chofer según tipo de contrato
        comision_chofer = 0
        if contrato.tipo_contrato == 'PORCENTAJE':
            comision_chofer = monto_bruto * (contrato.porcentaje_chofer / 100)
        elif contrato.tipo_contrato == 'MONTO_FIJO':
            comision_chofer = contrato.monto_diario or 0
        # AUTO_GESTION: comisión 0

        # 5. Calcular utilidad del propietario
        utilidad_propietario = monto_bruto - comision_chofer - total_gastos

        # 6. Actualizar turno con valores calculados
        turno.recaudacion_app_efectivo = recaudacion_app_total  # Simplificado
        turno.recaudacion_app_debito = 0  # Por ahora
        turno.monto_bruto_calculado = monto_bruto
        turno.comision_chofer_calculada = comision_chofer
        turno.utilidad_propietario_calculada = utilidad_propietario
        await db.commit()

        return {
            "turno_id": turno.id,
            "recaudacion_app": recaudacion_app_total,
            "recaudacion_ticketera": turno.recaudacion_ticketera_calle,
            "total_gastos": total_gastos,
            "monto_bruto": monto_bruto,
            "comision_chofer": comision_chofer,
            "utilidad_propietario": utilidad_propietario,
            "tipo_contrato": contrato.tipo_contrato,
            "porcentaje_chofer": contrato.porcentaje_chofer,
            "monto_diario": contrato.monto_diario
        }