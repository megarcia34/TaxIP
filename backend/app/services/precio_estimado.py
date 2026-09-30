"""
Servicio de estimación de precios - MOTOR UNIFICADO TAXIP 2.1
Una sola fórmula, variables configurables por tenant, mismo resultado siempre.

Fórmula Maestra:
1. FD = ceil(distancia_m / metros_por_ficha)
2. Según modo_cobro_tiempo:
   - 'detenido': FT estimado por velocidad promedio vs velocidad_referencia
   - 'total': FT = ceil((tiempo_viaje + tiempo_espera) * 60 / seg_por_ficha)
3. FICHAS_TOTALES = FD + FT
4. PRECIO_BASE = bajada + (FICHAS_TOTALES × precio_ficha)
5. PRECIO_VEHICULO = PRECIO_BASE × factor_vehiculo (desde tabla intermedia)
6. PRECIO_RECARGOS = PRECIO_VEHICULO × Π(recargos)
7. PRECIO_FINAL = redondeo(PRECIO_RECARGOS)
"""
import logging
import math
from decimal import Decimal
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.payment import ConfiguracionTarifa, ConfiguracionTarifaVehiculo
from app.models.trip import TipoVehiculo
from app.schemas.reserva_schemas import (
    EstimacionPrecioRequest,
    EstimacionPrecioResponse,
)

logger = logging.getLogger(__name__)


# ============================================================
# EXCEPCIONES
# ============================================================
class TarifaNotFoundError(Exception):
    """No se encontró configuración de tarifa para el tenant"""
    pass


class TipoVehiculoNotFoundError(Exception):
    """No se encontró el tipo de vehículo"""
    pass


# ============================================================
# UTILIDADES
# ============================================================
def to_float(val) -> float:
    """Convierte Decimal, str, None a float de forma segura"""
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except ValueError:
            return 0.0
    return float(val)


# ============================================================
# MOTOR UNIFICADO DE CÁLCULO TAXIP 2.1
# ============================================================
class CalculadorTarifaUnificado:
    """
    Motor unificado de cálculo de tarifas.
    
    Ya NO usa modo_calculo (deprecado).
    Ya NO usa campos tarifarios de tipo_vehiculo (deprecados).
    Todas las variables vienen de payment.configuracion_tarifa.
    El factor por tipo de vehículo viene de payment.configuracion_tarifa_vehiculo.
    """

    def __init__(
        self,
        config: ConfiguracionTarifa,
        tipo_vehiculo: TipoVehiculo,
        factor_tipo_vehiculo: float,
        distancia_km: float,
        tiempo_minutos: int,
        tiempo_espera_minutos: int = 0,
        fecha_hora: Optional[datetime] = None,
        es_feriado: bool = False,
    ):
        self.config = config
        self.tipo_vehiculo = tipo_vehiculo
        self.factor_tipo_vehiculo = factor_tipo_vehiculo
        self.distancia_km = distancia_km
        self.distancia_metros = distancia_km * 1000
        self.tiempo_minutos = tiempo_minutos
        self.tiempo_espera_minutos = tiempo_espera_minutos
        self.fecha_hora = fecha_hora or datetime.now()
        self.es_feriado = es_feriado

        # Resultados
        self.subtotal = 0.0
        self.desglose: Dict[str, Any] = {}
        self.recargos_aplicados: List[str] = []

    def calcular(self) -> Dict[str, Any]:
        """Ejecuta la fórmula unificada completa"""

        # ================================================================
        # 1. LEER CONFIGURACIÓN DEL TENANT
        # ================================================================
        bajada = to_float(self.config.tarifa_base)
        precio_ficha = to_float(self.config.precio_por_ficha)
        metros_por_ficha = to_float(
            self.config.metros_por_ficha
            if self.config.metros_por_ficha is not None
            else self.config.distancia_por_ficha
            or 100
        )
        seg_por_ficha = to_float(
            self.config.seg_por_ficha_espera
            if self.config.seg_por_ficha_espera is not None
            else 60
        )
        velocidad_referencia = to_float(self.config.velocidad_referencia_kmh or 30)
        modo_cobro_tiempo = self.config.modo_cobro_tiempo or "detenido"
        redondeo = int(self.config.redondeo_comercial if self.config.redondeo_comercial is not None else 100)

        # ================================================================
        # 2. FASE 1 — FICHAS POR DISTANCIA (FD)
        # ================================================================
        if metros_por_ficha > 0:
            fichas_distancia = math.ceil(self.distancia_metros / metros_por_ficha)
        else:
            fichas_distancia = 0
            logger.warning("metros_por_ficha es 0, fichas por distancia desactivadas")

        # ================================================================
        # 3. FASE 2 — FICHAS POR TIEMPO (FT)
        # ================================================================
        if modo_cobro_tiempo == "total":
            # Modo 'total': todo el tiempo cuenta (emula por_minuto original)
            tiempo_total_seg = (self.tiempo_minutos + self.tiempo_espera_minutos) * 60
            if seg_por_ficha > 0:
                fichas_tiempo = math.ceil(tiempo_total_seg / seg_por_ficha)
            else:
                fichas_tiempo = 0
            tiempo_detenido_min = self.tiempo_minutos + self.tiempo_espera_minutos
            velocidad_promedio = None
        else:
            # Modo 'detenido' (default): taxímetro real
            if self.tiempo_minutos > 0:
                velocidad_promedio = self.distancia_km / (self.tiempo_minutos / 60)
            else:
                velocidad_promedio = 0

            if velocidad_promedio >= velocidad_referencia:
                # Viaje fluido, solo cuenta distancia
                fichas_tiempo = 0
                tiempo_detenido_min = 0
            else:
                # Hay tráfico, calcular tiempo detenido
                tiempo_fluido_min = (self.distancia_km / velocidad_referencia) * 60
                tiempo_detenido_min = self.tiempo_minutos - tiempo_fluido_min

                if tiempo_detenido_min > 0.5:  # Más de 30 segundos
                    fichas_tiempo = math.ceil(
                        (tiempo_detenido_min - 0.5) * 60 / seg_por_ficha
                    )
                else:
                    fichas_tiempo = 0

        # ================================================================
        # 4. FASE 3 — PRECIO BASE
        # ================================================================
        fichas_totales = fichas_distancia + fichas_tiempo
        monto_fichas = fichas_totales * precio_ficha
        self.subtotal = bajada + monto_fichas
        precio_base = self.subtotal

        # ================================================================
        # 5. FASE 4 — FACTOR POR TIPO DE VEHÍCULO
        # ================================================================
        factor_veh = self.factor_tipo_vehiculo
        precio_antes_vehiculo = self.subtotal
        self.subtotal *= factor_veh
        precio_despues_vehiculo = self.subtotal

        # ================================================================
        # 6. FASE 5 — RECARGOS (nocturno × domingo × feriado)
        # ================================================================
        factor_recargos = 1.0
        recargos_detalle = []

        if self._es_nocturno():
            f = to_float(self.config.recargo_nocturno)
            if f > 1.0:
                precio_antes = self.subtotal
                factor_recargos *= f
                self.subtotal *= f
                recargos_detalle.append({
                    "tipo": "nocturno",
                    "factor": f,
                    "precio_antes": round(precio_antes, 2),
                    "precio_despues": round(self.subtotal, 2),
                    "aporte": round(self.subtotal - precio_antes, 2),
                })
                self.recargos_aplicados.append(f"nocturno_{f}x")

        if self._es_domingo():
            f = to_float(self.config.recargo_domingo)
            if f > 1.0:
                precio_antes = self.subtotal
                factor_recargos *= f
                self.subtotal *= f
                recargos_detalle.append({
                    "tipo": "domingo",
                    "factor": f,
                    "precio_antes": round(precio_antes, 2),
                    "precio_despues": round(self.subtotal, 2),
                    "aporte": round(self.subtotal - precio_antes, 2),
                })
                self.recargos_aplicados.append(f"domingo_{f}x")

        if self.es_feriado:
            f = to_float(self.config.recargo_feriado)
            if f > 1.0:
                precio_antes = self.subtotal
                factor_recargos *= f
                self.subtotal *= f
                recargos_detalle.append({
                    "tipo": "feriado",
                    "factor": f,
                    "precio_antes": round(precio_antes, 2),
                    "precio_despues": round(self.subtotal, 2),
                    "aporte": round(self.subtotal - precio_antes, 2),
                })
                self.recargos_aplicados.append(f"feriado_{f}x")

        precio_con_recargos = self.subtotal

        # ================================================================
        # 7. FASE 6 — REDONDEO COMERCIAL
        # ================================================================
        precio_antes_redondeo = self.subtotal
        ajuste_redondeo = 0.0
        if redondeo > 0:
            resto = self.subtotal % redondeo
            if resto == 0:
                pass  # Ya es múltiplo
            elif resto <= redondeo / 2:
                # Baja al múltiplo anterior
                self.subtotal = self.subtotal - resto
                ajuste_redondeo = -resto
            else:
                # Sube al siguiente múltiplo
                ajuste = redondeo - resto
                self.subtotal = self.subtotal + ajuste
                ajuste_redondeo = ajuste

        precio_final = self.subtotal

        # ================================================================
        # 8. GENERAR DESGLOSE TRAZABLE
        # ================================================================
        self.desglose = {
            "tarifa_base": round(bajada, 2),
            "fichas": {
                "distancia": {
                    "cantidad": fichas_distancia,
                    "metros": round(self.distancia_metros, 2),
                    "metros_por_ficha": metros_por_ficha,
                    "precio_por_ficha": precio_ficha,
                    "subtotal": round(fichas_distancia * precio_ficha, 2),
                },
                "tiempo": {
                    "cantidad": fichas_tiempo,
                    "modo_cobro": modo_cobro_tiempo,
                    "velocidad_promedio_kmh": round(velocidad_promedio, 2) if velocidad_promedio is not None else None,
                    "velocidad_referencia_kmh": velocidad_referencia,
                    "tiempo_detenido_min": round(tiempo_detenido_min, 2),
                    "seg_por_ficha": seg_por_ficha,
                    "precio_por_ficha": precio_ficha,
                    "subtotal": round(fichas_tiempo * precio_ficha, 2),
                },
                "total": fichas_totales,
                "subtotal_fichas": round(monto_fichas, 2),
            },
            "precio_base": round(precio_base, 2),
            "factor_vehiculo": {
                "tipo": self.tipo_vehiculo.id,
                "factor": factor_veh,
                "precio_antes": round(precio_antes_vehiculo, 2),
                "precio_despues": round(precio_despues_vehiculo, 2),
            },
            "recargos": recargos_detalle,
            "precio_con_recargos": round(precio_con_recargos, 2),
            "redondeo": {
                "multiplo": redondeo,
                "ajuste": round(ajuste_redondeo, 2),
            },
            "precio_sin_redondeo": round(precio_antes_redondeo, 2),
            "distancia_km": round(self.distancia_km, 2),
            "tiempo_minutos": self.tiempo_minutos,
            "tiempo_espera_minutos": self.tiempo_espera_minutos,
            "moneda": self.config.moneda or "ARS",
        }

        logger.info(
            f"Fórmula unificada: bajada={bajada}, FD={fichas_distancia}, "
            f"FT={fichas_tiempo}, total={fichas_totales}, "
            f"factor_veh={factor_veh}, recargos={factor_recargos}, "
            f"final={precio_final}"
        )

        return {
            "precio": round(precio_final, 2),
            "desglose": self.desglose,
            "recargos_aplicados": self.recargos_aplicados,
            "modo_calculo": "unificado",
        }

    def _es_nocturno(self) -> bool:
        """Verifica si la hora está dentro del rango nocturno"""
        hora_actual = self.fecha_hora.time()

        hora_inicio_raw = self.config.hora_inicio_nocturno or "22:00"
        hora_fin_raw = self.config.hora_fin_nocturno or "06:00"

        if isinstance(hora_inicio_raw, str):
            try:
                inicio = time.fromisoformat(hora_inicio_raw)
            except ValueError:
                return False
        elif isinstance(hora_inicio_raw, time):
            inicio = hora_inicio_raw
        else:
            return False

        if isinstance(hora_fin_raw, str):
            try:
                fin = time.fromisoformat(hora_fin_raw)
            except ValueError:
                return False
        elif isinstance(hora_fin_raw, time):
            fin = hora_fin_raw
        else:
            return False

        # Caso especial: si inicio > fin (ej: 22:00 a 06:00)
        if inicio > fin:
            return hora_actual >= inicio or hora_actual <= fin
        else:
            return inicio <= hora_actual <= fin

    def _es_domingo(self) -> bool:
        """Verifica si la fecha es domingo (weekday = 6)"""
        return self.fecha_hora.weekday() == 6


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================
async def calcular_precio_estimado(
    request: EstimacionPrecioRequest,
    control_base_id: UUID,
    db: AsyncSession,
    distancia_km: float,
    tiempo_minutos: int,
    fecha_hora: Optional[datetime] = None,
    es_feriado: bool = False,
) -> EstimacionPrecioResponse:
    """
    Calcula el precio estimado usando la FÓRMULA UNIFICADA TAXIP 2.1.
    
    El motor recibe:
    - control_base_id (resuelto por el caller)
    - distancia_km y tiempo_minutos (calculados por el caller, ej: Google Maps)
    - es_feriado (determinado externamente por el caller)
    
    El motor NO:
    - Resuelve el tenant (lo recibe como parámetro)
    - Llama a Google Maps (recibe distancia/tiempo)
    - Consulta APIs de feriados (recibe el flag)
    """
    logger.info(
        f"Calculando precio para tenant {control_base_id}, "
        f"vehículo {request.tipo_vehiculo.value}"
    )

    # 1. Obtener configuración de tarifa del tenant
    stmt = select(ConfiguracionTarifa).where(
        and_(
            ConfiguracionTarifa.control_base_id == control_base_id,
            ConfiguracionTarifa.activo == True,
        )
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if not config:
        raise TarifaNotFoundError(
            f"No hay configuración de tarifa activa para este tenant."
        )

    # 2. Obtener tipo de vehículo
    stmt = select(TipoVehiculo).where(
        and_(
            TipoVehiculo.id == request.tipo_vehiculo.value,
            TipoVehiculo.activo == True,
        )
    )
    result = await db.execute(stmt)
    tipo_vehiculo = result.scalar_one_or_none()

    if not tipo_vehiculo:
        raise TipoVehiculoNotFoundError(
            f"El tipo de vehículo '{request.tipo_vehiculo.value}' no existe o está inactivo"
        )

    # 3. Obtener factor del tipo de vehículo desde tabla intermedia
    stmt = select(ConfiguracionTarifaVehiculo).where(
        and_(
            ConfiguracionTarifaVehiculo.configuracion_tarifa_id == config.id,
            ConfiguracionTarifaVehiculo.tipo_vehiculo_id == tipo_vehiculo.id,
            ConfiguracionTarifaVehiculo.activo == True,
        )
    )
    result = await db.execute(stmt)
    config_vehiculo = result.scalar_one_or_none()

    if config_vehiculo:
        factor_tipo_vehiculo = to_float(config_vehiculo.factor_precio)
    else:
        factor_tipo_vehiculo = 1.0
        logger.warning(
            f"No se encontró factor para vehículo '{tipo_vehiculo.id}' "
            f"en config '{config.nombre}'. Usando factor default 1.0"
        )

    # 4. Calcular precio con fórmula unificada
    calculador = CalculadorTarifaUnificado(
        config=config,
        tipo_vehiculo=tipo_vehiculo,
        factor_tipo_vehiculo=factor_tipo_vehiculo,
        distancia_km=distancia_km,
        tiempo_minutos=tiempo_minutos,
        tiempo_espera_minutos=request.tiempo_espera_minutos or 0,
        fecha_hora=fecha_hora,
        es_feriado=es_feriado,
    )
    resultado = calculador.calcular()

    # 5. Construir respuesta
    response = EstimacionPrecioResponse(
        distancia_km=round(distancia_km, 2),
        tiempo_minutos=tiempo_minutos,
        precio_estimado=resultado["precio"],
        desglose=resultado["desglose"],
        latitud_origen=None,
        longitud_origen=None,
        latitud_destino=None,
        longitud_destino=None,
        modo_calculo="unificado",
        moneda=config.moneda or "ARS",
        recargos_aplicados=resultado.get("recargos_aplicados", []),
    )

    logger.info(f"Precio estimado calculado: {response.precio_estimado} {response.moneda}")
    return response


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def calcular_fichas(distancia_metros: float, distancia_por_ficha: float) -> int:
    """Calcula el número de fichas para una distancia dada"""
    if distancia_por_ficha <= 0:
        return 0
    return math.ceil(distancia_metros / distancia_por_ficha)


def formatear_precio(precio: float, moneda: str = "ARS") -> str:
    """Formatea un precio con su moneda"""
    if moneda == "ARS":
        return f"${precio:,.2f}"
    return f"{moneda} {precio:,.2f}"