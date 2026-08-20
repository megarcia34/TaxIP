# app/repositories/liquidacion_repository.py
"""
Repositorio para operaciones CRUD de liquidaciones
"""

from uuid import UUID
from decimal import Decimal
from typing import Optional, List, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.models.liquidacion import Liquidacion, LiquidacionDetalle, LiquidacionEstadoHistorial
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.core.exceptions import LiquidacionError


class LiquidacionRepository:
    """
    Repositorio para gestionar la persistencia de liquidaciones.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_liquidacion(
        self,
        contexto: LiquidacionContextSchema,
        resultado: LiquidacionResultado
    ) -> UUID:
        """
        Crea una nueva liquidación y sus detalles.
        """
        # 1. Crear cabecera
        liquidacion = Liquidacion(
            control_base_id=contexto.control_base_id,
            turno_id=contexto.turno_id,
            contrato_id=contexto.contrato_id,
            vehiculo_id=contexto.vehiculo_id,
            chofer_id=contexto.chofer_id,
            propietario_id=contexto.propietario_id,
            tipo_contrato=contexto.tipo_contrato,
            periodo_desde=contexto.fecha_inicio,
            periodo_hasta=contexto.fecha_fin,
            monto_bruto=resultado.monto_bruto,
            total_gastos=resultado.total_gastos,
            comision_chofer=resultado.comision_chofer,
            canon=resultado.canon,
            km_excedentes=resultado.km_excedentes,
            cargo_km_excedentes=resultado.cargo_km_excedentes,
            total_chofer=resultado.total_chofer,
            total_propietario=resultado.total_propietario,
            saldo_chofer=resultado.saldo_chofer,
            saldo_propietario=resultado.saldo_propietario,
            estado="CALCULADA",
            version=1,
            calculada_en=datetime.now()
        )
        self.db.add(liquidacion)
        await self.db.flush()

        # 2. Crear detalles
        for detalle_data in resultado.detalles:
            detalle = LiquidacionDetalle(
                liquidacion_id=liquidacion.id,
                tipo_linea=detalle_data.tipo_linea.value,
                concepto=detalle_data.concepto,
                fuente_tipo=detalle_data.fuente_tipo,
                fuente_id=detalle_data.fuente_id,
                monto=detalle_data.monto,
                signo=detalle_data.signo.value,
                meta_data=self._convert_decimal_to_float(detalle_data.meta_data or {})
            )
            self.db.add(detalle)

        # 3. Crear historial
        historial = LiquidacionEstadoHistorial(
            liquidacion_id=liquidacion.id,
            control_base_id=contexto.control_base_id,
            estado_anterior="BORRADOR",
            estado_nuevo="CALCULADA",
            cambiado_por=None,
            motivo="Cálculo automático por motor de liquidación"
        )
        self.db.add(historial)

        await self.db.commit()
        await self.db.refresh(liquidacion)

        return liquidacion.id

    def _convert_decimal_to_float(self, obj: Any) -> Any:
        """Convierte Decimal a float recursivamente para JSON serializable."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        else:
            return obj

    async def registrar_cambio_estado(
        self,
        liquidacion_id: UUID,
        estado_anterior: Optional[str],
        estado_nuevo: str,
        motivo: Optional[str] = None,
        usuario_id: Optional[UUID] = None
    ) -> None:
        """Registra un cambio de estado en el historial."""
        liquidacion = await self.obtener_por_id(liquidacion_id)
        if not liquidacion:
            raise LiquidacionError(f"Liquidación no encontrada: {liquidacion_id}")

        historial = LiquidacionEstadoHistorial(
            liquidacion_id=liquidacion_id,
            control_base_id=liquidacion.control_base_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            cambiado_por=usuario_id,
            motivo=motivo,
        )
        self.db.add(historial)

        liquidacion.estado = estado_nuevo
        liquidacion.updated_at = datetime.now()
        await self.db.commit()

    async def obtener_por_id(self, liquidacion_id: UUID) -> Optional[Liquidacion]:
        """Obtiene una liquidación por su ID con detalles."""
        query = select(Liquidacion).where(
            Liquidacion.id == liquidacion_id
        ).options(
            selectinload(Liquidacion.detalles),
            selectinload(Liquidacion.historial_estados),
            selectinload(Liquidacion.ajustes)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def obtener_por_turno(self, turno_id: UUID) -> Optional[Liquidacion]:
        """Obtiene la liquidación más reciente de un turno."""
        query = select(Liquidacion).where(
            Liquidacion.turno_id == turno_id
        ).order_by(
            desc(Liquidacion.version)
        ).limit(1).options(
            selectinload(Liquidacion.detalles)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def listar_por_propietario(
        self,
        propietario_id: UUID,
        control_base_id: UUID,
        limit: int = 50,
        offset: int = 0,
        estado: Optional[str] = None
    ) -> List[Liquidacion]:
        """Lista liquidaciones de un propietario."""
        query = select(Liquidacion).where(
            and_(
                Liquidacion.propietario_id == propietario_id,
                Liquidacion.control_base_id == control_base_id
            )
        )
        if estado:
            query = query.where(Liquidacion.estado == estado)
        
        query = query.order_by(desc(Liquidacion.created_at)).limit(limit).offset(offset).options(
            selectinload(Liquidacion.detalles)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def listar_por_tenant(
        self,
        control_base_id: UUID,
        limit: int = 50,
        offset: int = 0,
        estado: Optional[str] = None
    ) -> List[Liquidacion]:
        """Lista liquidaciones de un tenant."""
        query = select(Liquidacion).where(
            Liquidacion.control_base_id == control_base_id
        )
        if estado:
            query = query.where(Liquidacion.estado == estado)
        
        query = query.order_by(desc(Liquidacion.created_at)).limit(limit).offset(offset).options(
            selectinload(Liquidacion.detalles)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def existe_para_turno(self, turno_id: UUID) -> bool:
        """Verifica si ya existe una liquidación para el turno."""
        query = select(Liquidacion).where(Liquidacion.turno_id == turno_id).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def obtener_historial(self, liquidacion_id: UUID) -> List[dict]:
        """Obtiene el historial de cambios de estado."""
        query = select(LiquidacionEstadoHistorial).where(
            LiquidacionEstadoHistorial.liquidacion_id == liquidacion_id
        ).order_by(LiquidacionEstadoHistorial.created_at)
        result = await self.db.execute(query)
        historial = result.scalars().all()
        
        return [
            {
                "id": h.id,
                "estado_anterior": h.estado_anterior,
                "estado_nuevo": h.estado_nuevo,
                "cambiado_por": h.cambiado_por,
                "motivo": h.motivo,
                "created_at": h.created_at
            }
            for h in historial
        ]