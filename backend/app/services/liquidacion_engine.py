# app/services/liquidacion_engine.py
"""
Motor de liquidaciones - Orquesta el cálculo y persistencia
"""

from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.liquidacion_context import LiquidacionContext
from app.services.calculators import (
    AlquilerCalculator,
    PorcentajeCalculator,
    AutoGestionCalculator,
    LiquidacionCalculator
)
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.core.exceptions import LiquidacionError


class LiquidacionEngine:
    """
    Motor principal de liquidaciones.
    Orquesta la carga de contexto, selección de calculador y persistencia.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.context_loader = LiquidacionContext(db)
        self.repository = LiquidacionRepository(db)

    async def calcular(self, turno_id: UUID) -> UUID:
        """
        Calcula y persiste la liquidación para un turno.
        Retorna el ID de la liquidación creada.
        """
        # 1. Cargar contexto
        contexto = await self.context_loader.cargar(turno_id)

        # 2. Seleccionar calculador según tipo de contrato
        calculador = self._seleccionar_calculador(contexto.tipo_contrato)

        # 3. Ejecutar cálculo
        resultado = await calculador.calcular(contexto)

        # 4. Persistir liquidación
        liquidacion_id = await self.repository.crear_liquidacion(
            contexto=contexto,
            resultado=resultado
        )

        # 5. Registrar historial de estado (BORRADOR → CALCULADA)
        await self.repository.registrar_cambio_estado(
            liquidacion_id=liquidacion_id,
            estado_anterior="BORRADOR",
            estado_nuevo="CALCULADA",
            motivo="Cálculo automático por motor",
            usuario_id=None  # Puede ser el usuario autenticado si se pasa
        )

        return liquidacion_id

    def _seleccionar_calculador(self, tipo_contrato: str) -> LiquidacionCalculator:
        """Selecciona el calculador adecuado según el tipo de contrato"""
        if tipo_contrato == "ALQUILER":
            return AlquilerCalculator()
        elif tipo_contrato == "PORCENTAJE":
            return PorcentajeCalculator()
        elif tipo_contrato == "AUTO_GESTION":
            return AutoGestionCalculator()
        else:
            raise LiquidacionError(f"Tipo de contrato no soportado: {tipo_contrato}")

    async def recalcular(self, liquidacion_id: UUID) -> UUID:
        """
        Recalcula una liquidación existente (crea una nueva versión)
        """
        # Obtener la liquidación existente para obtener el turno_id
        liquidacion = await self.repository.obtener_por_id(liquidacion_id)
        if not liquidacion:
            raise LiquidacionError(f"Liquidación no encontrada: {liquidacion_id}")

        # Si la liquidación está en estado CALCULADA o BORRADOR, se puede recalcular
        if liquidacion.estado not in ["BORRADOR", "CALCULADA"]:
            raise LiquidacionError(f"No se puede recalcular una liquidación en estado {liquidacion.estado}")

        # Calcular nueva liquidación (crea una nueva versión con el mismo turno)
        nuevo_id = await self.calcular(liquidacion.turno_id)

        # Opcional: marcar la anterior como obsoleta (si se requiere)
        # await self.repository.actualizar_estado(liquidacion_id, "OBSOLETA")

        return nuevo_id