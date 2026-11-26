"""
MantenimientoEngine: motor de calculo de vencimientos.

Lee los planes asignados a un vehiculo, calcula el estado de cada item
(normal, proximo, critico, vencido) y persiste el resultado en
fleet.mantenimiento_vencimiento.

Usa KilometrajeService para obtener el km actual (fuente unica de verdad).
"""
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.fleet import (
    MantenimientoPlan,
    MantenimientoPlanItem,
    MantenimientoPlanVehiculo,
    MantenimientoVencimiento,
)
from app.services.kilometraje_service import KilometrajeService, LecturaKilometraje

logger = logging.getLogger(__name__)


@dataclass
class VencimientoCalculado:
    """
    Resultado puro del calculo de un vencimiento (sin persistir).
    """
    # --- Identificadores ---
    control_base_id: UUID
    vehiculo_id: UUID
    plan_id: UUID
    plan_item_id: UUID

    # --- Datos del calculo ---
    km_actual: Optional[float]
    km_proximo: Optional[float]
    fecha_proximo: Optional[date]
    estado: str  # normal | proximo | critico | vencido
    vigente: bool
    requiere_verificacion: bool
    advertencias: List[str] = field(default_factory=list)

    # --- Datos de contexto (para UI) ---
    componente_nombre: Optional[str] = None
    intervalo_km: Optional[int] = None
    intervalo_dias: Optional[int] = None
    prioridad: Optional[str] = None
    criticidad: Optional[str] = None
    km_para_vencer: Optional[float] = None
    dias_para_vencer: Optional[int] = None


class MantenimientoEngine:
    """
    Motor de calculo de vencimientos de mantenimiento.
    """

    # Umbrales por defecto (si el plan no define override).
    UMBRALES_DEFAULT = {
        "umbral_proximo_km": 2000,
        "umbral_proximo_dias": 30,
        "umbral_critico_km": 500,
        "umbral_critico_dias": 7,
    }

    # Claves validas para el JSONB de override.
    CLAVES_UMBRALES_VALIDAS = {
        "umbral_proximo_km",
        "umbral_proximo_dias",
        "umbral_critico_km",
        "umbral_critico_dias",
    }

    # ========================================================
    # 1. METODOS PUROS (sin DB)
    # ========================================================

    @staticmethod
    def calcular_estado(
        km_actual: Optional[float],
        km_proximo: Optional[float],
        hoy: date,
        fecha_proximo: Optional[date],
        umbrales: dict,
    ) -> str:
        """
        Calcula el estado del vencimiento comparando km y fecha.
        Aplica la regla "vence primero": el peor de los dos.

        Returns:
            normal | proximo | critico | vencido
        """
        # Si no hay datos para calcular, no se puede vencer.
        if km_proximo is None and fecha_proximo is None:
            return "normal"

        # --- 1. Verificar vencido ---
        if km_actual is not None and km_proximo is not None and km_actual >= km_proximo:
            return "vencido"
        if fecha_proximo is not None and hoy >= fecha_proximo:
            return "vencido"

        # --- 2. Verificar critico ---
        if km_actual is not None and km_proximo is not None:
            if (km_proximo - km_actual) <= umbrales["umbral_critico_km"]:
                return "critico"
        if fecha_proximo is not None:
            if (fecha_proximo - hoy).days <= umbrales["umbral_critico_dias"]:
                return "critico"

        # --- 3. Verificar proximo ---
        if km_actual is not None and km_proximo is not None:
            if (km_proximo - km_actual) <= umbrales["umbral_proximo_km"]:
                return "proximo"
        if fecha_proximo is not None:
            if (fecha_proximo - hoy).days <= umbrales["umbral_proximo_dias"]:
                return "proximo"

        # --- 4. Normal ---
        return "normal"

    @classmethod
    def _leer_umbrales(
        cls,
        plan: MantenimientoPlan,
        item: MantenimientoPlanItem,
    ) -> dict:
        """
        Hace el merge de umbrales: default -> plan -> item.
        Valida que las claves del JSONB sean conocidas.
        """
        umbrales = dict(cls.UMBRALES_DEFAULT)

        if plan.umbrales_override:
            for k, v in plan.umbrales_override.items():
                if k in cls.CLAVES_UMBRALES_VALIDAS:
                    umbrales[k] = v

        if item.umbrales_override:
            for k, v in item.umbrales_override.items():
                if k in cls.CLAVES_UMBRALES_VALIDAS:
                    umbrales[k] = v

        return umbrales

    @staticmethod
    def _dias_desde_intervalo(item: MantenimientoPlanItem) -> Optional[int]:
        """
        Convierte los intervalos del item a dias.
        Regla: si hay intervalo_dias, gana. Si solo hay meses, multiplica x 30.
        """
        if item.intervalo_dias is not None:
            return item.intervalo_dias
        if item.intervalo_meses is not None:
            return item.intervalo_meses * 30
        return None

    @classmethod
    def calcular_vencimientos(
        cls,
        vehiculo_id: UUID,
        control_base_id: UUID,
        km_actual: float,
        hoy: date,
        plan_vehiculos: List[MantenimientoPlanVehiculo],
        advertencias_km: List[str],
        requiere_verificacion_km: bool,
    ) -> List[VencimientoCalculado]:
        """
        Calcula los vencimientos en memoria (sin tocar la DB).
        """
        resultados: List[VencimientoCalculado] = []

        for pv in plan_vehiculos:
            plan = pv.plan

            # Si el plan esta inactivo, no calculamos nada.
            if not plan.activo:
                continue

            for item in plan.items:
                # Calcular dias de intervalo (puede ser None si solo hay km).
                dias_intervalo = cls._dias_desde_intervalo(item)

                # Si no tiene ningun intervalo, es un error de configuracion.
                # El CHECK constraint de la DB deberia prevenirlo, pero por
                # seguridad salteamos.
                if item.intervalo_km is None and dias_intervalo is None:
                    logger.warning(
                        f"PlanItem {item.id} sin intervalo configurado, se saltea."
                    )
                    continue

                # --- Calcular km_proximo ---
                km_proximo = None
                if item.intervalo_km is not None:
                    km_proximo = float(km_actual) + float(item.intervalo_km)

                # --- Calcular fecha_proximo ---
                fecha_proximo = None
                if dias_intervalo is not None:
                    fecha_proximo = hoy + timedelta(days=dias_intervalo)

                # --- Calcular umbrales (merge) ---
                umbrales = cls._leer_umbrales(plan, item)

                # --- Calcular estado ---
                estado = cls.calcular_estado(
                    km_actual=km_actual,
                    km_proximo=km_proximo,
                    hoy=hoy,
                    fecha_proximo=fecha_proximo,
                    umbrales=umbrales,
                )

                # --- Vigencia ---
                # Si el km no es confiable (stale o cero), el vencimiento
                # existe pero no es "vigente" para disparar acciones.
                vigente = not requiere_verificacion_km

                # --- Calcular distancia al vencimiento (para UI) ---
                km_para_vencer = None
                if km_proximo is not None:
                    km_para_vencer = km_proximo - float(km_actual)

                dias_para_vencer = None
                if fecha_proximo is not None:
                    dias_para_vencer = (fecha_proximo - hoy).days

                # --- Armar resultado ---
                resultados.append(
                    VencimientoCalculado(
                        control_base_id=control_base_id,
                        vehiculo_id=vehiculo_id,
                        plan_id=plan.id,
                        plan_item_id=item.id,
                        km_actual=km_actual,
                        km_proximo=km_proximo,
                        fecha_proximo=fecha_proximo,
                        estado=estado,
                        vigente=vigente,
                        requiere_verificacion=requiere_verificacion_km,
                        advertencias=advertencias_km.copy(),
                        componente_nombre=item.componente.nombre if item.componente else None,
                        intervalo_km=item.intervalo_km,
                        intervalo_dias=dias_intervalo,
                        prioridad=item.prioridad,
                        criticidad=item.criticidad,
                        km_para_vencer=km_para_vencer,
                        dias_para_vencer=dias_para_vencer,
                    )
                )

        return resultados

    # ========================================================
    # 2. METODO ORQUESTADOR (con DB)
    # ========================================================

    @classmethod
    async def refrescar_vencimientos(
        cls,
        db: AsyncSession,
        vehiculo_id: UUID,
    ) -> List[MantenimientoVencimiento]:
        """
        Orquesta la lectura de DB, el calculo y la persistencia.

        Pasos:
        1. Lee el km actual desde KilometrajeService.
        2. Lee los planes activos del vehiculo (con items y componente).
        3. Calcula los vencimientos.
        4. Hace upsert en mantenimiento_vencimiento.
        5. Devuelve los vencimientos persistidos.
        """
        # --- 1. KM ACTUAL ---
        lectura_km = await KilometrajeService.obtener_km_actual(db, vehiculo_id)
        km_actual = float(lectura_km.km_actual)
        hoy = date.today()

        # --- 2. PLANES DEL VEHICULO ---
        query = (
            select(MantenimientoPlanVehiculo)
            .where(
                MantenimientoPlanVehiculo.vehiculo_id == vehiculo_id,
                MantenimientoPlanVehiculo.activo == True,  # noqa: E712
            )
            .options(
                selectinload(MantenimientoPlanVehiculo.plan)
                .selectinload(MantenimientoPlan.items)
                .selectinload(MantenimientoPlanItem.componente),
            )
        )
        result = await db.execute(query)
        plan_vehiculos = result.scalars().all()

        if not plan_vehiculos:
            # Sin planes asignados, no hay nada que calcular.
            return []

        control_base_id = plan_vehiculos[0].control_base_id

        # --- 3. CALCULAR ---
        calculados = cls.calcular_vencimientos(
            vehiculo_id=vehiculo_id,
            control_base_id=control_base_id,
            km_actual=km_actual,
            hoy=hoy,
            plan_vehiculos=plan_vehiculos,
            advertencias_km=lectura_km.advertencias,
            requiere_verificacion_km=lectura_km.requiere_verificacion,
        )

        # --- 4. UPSERT ---
        # Buscar existentes por (vehiculo_id, plan_item_id).
        query_existentes = (
            select(MantenimientoVencimiento)
            .where(MantenimientoVencimiento.vehiculo_id == vehiculo_id)
        )
        result = await db.execute(query_existentes)
        existentes = {v.plan_item_id: v for v in result.scalars().all()}

        ahora = datetime.now()
        persistidos = []

        for calc in calculados:
            venc = existentes.get(calc.plan_item_id)

            if venc is None:
                # --- INSERT ---
                venc = MantenimientoVencimiento(
                    control_base_id=calc.control_base_id,
                    vehiculo_id=calc.vehiculo_id,
                    plan_item_id=calc.plan_item_id,
                    km_actual=calc.km_actual,
                    km_proximo=calc.km_proximo,
                    fecha_proximo=calc.fecha_proximo,
                    estado=calc.estado,
                    vigente=calc.vigente,
                    advertencias=calc.advertencias,
                    calculado_en=ahora,
                )
                db.add(venc)
            else:
                # --- UPDATE ---
                # NO tocamos km_proximo ni fecha_proximo (regla de negocio).
                venc.km_actual = calc.km_actual
                venc.estado = calc.estado
                venc.vigente = calc.vigente
                venc.advertencias = calc.advertencias
                venc.calculado_en = ahora

            persistidos.append(venc)

        await db.commit()

        for venc in persistidos:
            await db.refresh(venc)

        return persistidos