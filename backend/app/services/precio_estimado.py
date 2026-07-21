"""
Servicio de estimación de precios - Multi-tenant con múltiples modos de cálculo
Soporta: ficha_argentina, por_km, por_minuto, mixto
"""

import logging
import math
from decimal import Decimal
from datetime import datetime, time
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.payment import ConfiguracionTarifa
from app.models.trip import TipoVehiculo
from app.schemas.reserva_schemas import (
    EstimacionPrecioRequest,
    EstimacionPrecioResponse,
    ParadaIntermedia
)

logger = logging.getLogger(__name__)


# ============================================================
# CONSTANTES Y ENUMS
# ============================================================

class ModoCalculo:
    """Modos de cálculo de tarifa"""
    FICHA_ARGENTINA = "ficha_argentina"
    POR_KM = "por_km"
    POR_MINUTO = "por_minuto"
    MIXTO = "mixto"

    @classmethod
    def list(cls) -> List[str]:
        return [cls.FICHA_ARGENTINA, cls.POR_KM, cls.POR_MINUTO, cls.MIXTO]

    @classmethod
    def is_valid(cls, modo: str) -> bool:
        return modo in cls.list()


# ============================================================
# EXCEPCIONES
# ============================================================

class TarifaNotFoundError(Exception):
    """No se encontró configuración de tarifa para el tenant"""
    pass


class TipoVehiculoNotFoundError(Exception):
    """No se encontró el tipo de vehículo"""
    pass


class ModoCalculoInvalidoError(Exception):
    """El modo de cálculo no es válido"""
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
# CALCULADOR DE TARIFA
# ============================================================

class CalculadorTarifa:
    """
    Calculador de tarifa que soporta múltiples modos de cálculo
    """
    
    def __init__(
        self,
        config: ConfiguracionTarifa,
        tipo_vehiculo: TipoVehiculo,
        distancia_km: float,
        tiempo_minutos: int,
        tiempo_espera_minutos: int = 0,
        fecha_hora: Optional[datetime] = None
    ):
        self.config = config
        self.tipo_vehiculo = tipo_vehiculo
        self.distancia_km = distancia_km
        self.distancia_metros = distancia_km * 1000
        self.tiempo_minutos = tiempo_minutos
        self.tiempo_espera_minutos = tiempo_espera_minutos
        self.fecha_hora = fecha_hora or datetime.now()
        
        # Resultados del cálculo
        self.subtotal = 0.0
        self.desglose: Dict[str, Any] = {}
        self.recargos_aplicados: List[str] = []
        
        # Determinar modo de cálculo (fallback a por_km)
        self.modo = config.modo_calculo or ModoCalculo.POR_KM
        
        if not ModoCalculo.is_valid(self.modo):
            logger.warning(f"Modo de cálculo inválido: {self.modo}, usando por_km")
            self.modo = ModoCalculo.POR_KM

    def calcular(self) -> Dict[str, Any]:
        """
        Ejecuta el cálculo completo
        
        Returns:
            Dict con precio, desglose y recargos aplicados
        """
        # 1. Calcular precio base según modo
        self._calcular_base()
        
        # 2. Aplicar recargos
        self._aplicar_recargos()
        
        # 3. Generar respuesta
        return {
            "precio": round(self.subtotal, 2),
            "desglose": self.desglose,
            "recargos_aplicados": self.recargos_aplicados,
            "modo_calculado": self.modo
        }

    def _calcular_base(self):
        """Calcula el precio base según el modo configurado"""
        
        if self.modo == ModoCalculo.FICHA_ARGENTINA:
            self._calcular_ficha_argentina()
        elif self.modo == ModoCalculo.POR_KM:
            self._calcular_por_km()
        elif self.modo == ModoCalculo.POR_MINUTO:
            self._calcular_por_minuto()
        elif self.modo == ModoCalculo.MIXTO:
            self._calcular_mixto()
        else:
            # Fallback a por_km
            self._calcular_por_km()

    def _calcular_ficha_argentina(self):
        """
        Modo Ficha Argentina:
        Precio = Bajada + (distancia_metros / distancia_por_ficha) * precio_por_ficha + espera * precio_espera
        """
        # Convertir todos los valores a float
        distancia_por_ficha = to_float(
            self.tipo_vehiculo.distancia_por_ficha or 
            self.config.distancia_por_ficha or 
            100
        )
        precio_por_ficha = to_float(
            self.tipo_vehiculo.precio_por_ficha or 
            self.config.precio_por_ficha or 
            0
        )
        precio_espera = to_float(
            self.tipo_vehiculo.precio_por_minuto_espera or 
            self.config.precio_por_minuto_espera or 
            0
        )
        tarifa_base = to_float(self.tipo_vehiculo.tarifa_base or self.config.tarifa_base or 0)

        # Calcular número de fichas (redondear hacia arriba)
        if distancia_por_ficha > 0:
            total_fichas = math.ceil(self.distancia_metros / distancia_por_ficha)
        else:
            total_fichas = 0
            logger.warning("distancia_por_ficha es 0, no se pueden calcular fichas")

        # Calcular subtotal
        monto_fichas = total_fichas * precio_por_ficha
        monto_espera = self.tiempo_espera_minutos * precio_espera
        self.subtotal = tarifa_base + monto_fichas + monto_espera

        # Desglose
        self.desglose = {
            "bajada": round(tarifa_base, 2),
            "fichas": round(monto_fichas, 2),
            "total_fichas": total_fichas,
            "distancia_metros": self.distancia_metros,
            "distancia_por_ficha": distancia_por_ficha,
            "precio_por_ficha": precio_por_ficha,
            "espera": round(monto_espera, 2),
            "tiempo_espera_minutos": self.tiempo_espera_minutos,
            "precio_por_minuto_espera": precio_espera,
            "subtotal": round(self.subtotal, 2)
        }

        logger.info(f"Ficha Argentina: bajada={tarifa_base}, fichas={total_fichas}, "
                   f"espera={self.tiempo_espera_minutos}min, subtotal={self.subtotal}")

    def _calcular_por_km(self):
        """
        Modo Por KM:
        Precio = Bajada + (km * precio_por_km) + (minutos * precio_por_minuto)
        """
        tarifa_base = to_float(self.tipo_vehiculo.tarifa_base or self.config.tarifa_base or 0)
        precio_por_km = to_float(self.tipo_vehiculo.tarifa_por_km or self.config.precio_por_km or 0)
        precio_por_minuto = to_float(self.tipo_vehiculo.tarifa_por_minuto or self.config.precio_por_minuto or 0)

        monto_km = self.distancia_km * precio_por_km
        monto_minutos = self.tiempo_minutos * precio_por_minuto
        self.subtotal = tarifa_base + monto_km + monto_minutos

        self.desglose = {
            "bajada": round(tarifa_base, 2),
            "km": round(monto_km, 2),
            "distancia_km": round(self.distancia_km, 2),
            "precio_por_km": precio_por_km,
            "minutos": round(monto_minutos, 2),
            "tiempo_minutos": self.tiempo_minutos,
            "precio_por_minuto": precio_por_minuto,
            "subtotal": round(self.subtotal, 2)
        }

        logger.info(f"Por KM: bajada={tarifa_base}, km={self.distancia_km}, "
                   f"min={self.tiempo_minutos}, subtotal={self.subtotal}")

    def _calcular_por_minuto(self):
        """
        Modo Por Minuto:
        Precio = minutos * precio_por_minuto (sin distancia)
        """
        precio_por_minuto = to_float(self.tipo_vehiculo.tarifa_por_minuto or self.config.precio_por_minuto or 0)
        
        # Incluir tiempo de espera en el cálculo
        tiempo_total = self.tiempo_minutos + self.tiempo_espera_minutos
        self.subtotal = tiempo_total * precio_por_minuto

        self.desglose = {
            "tiempo_total_minutos": tiempo_total,
            "tiempo_viaje_minutos": self.tiempo_minutos,
            "tiempo_espera_minutos": self.tiempo_espera_minutos,
            "precio_por_minuto": precio_por_minuto,
            "subtotal": round(self.subtotal, 2)
        }

        logger.info(f"Por Minuto: tiempo={tiempo_total}min, precio/min={precio_por_minuto}, "
                   f"subtotal={self.subtotal}")

    def _calcular_mixto(self):
        """
        Modo Mixto:
        Precio = Bajada + (km * precio_por_km) + (espera * precio_espera)
        """
        tarifa_base = to_float(self.tipo_vehiculo.tarifa_base or self.config.tarifa_base or 0)
        precio_por_km = to_float(self.tipo_vehiculo.tarifa_por_km or self.config.precio_por_km or 0)
        precio_espera = to_float(
            self.tipo_vehiculo.precio_por_minuto_espera or 
            self.config.precio_por_minuto_espera or 
            0
        )

        monto_km = self.distancia_km * precio_por_km
        monto_espera = self.tiempo_espera_minutos * precio_espera
        self.subtotal = tarifa_base + monto_km + monto_espera

        self.desglose = {
            "bajada": round(tarifa_base, 2),
            "km": round(monto_km, 2),
            "distancia_km": round(self.distancia_km, 2),
            "precio_por_km": precio_por_km,
            "espera": round(monto_espera, 2),
            "tiempo_espera_minutos": self.tiempo_espera_minutos,
            "precio_por_minuto_espera": precio_espera,
            "subtotal": round(self.subtotal, 2)
        }

        logger.info(f"Mixto: bajada={tarifa_base}, km={self.distancia_km}, "
                   f"espera={self.tiempo_espera_minutos}min, subtotal={self.subtotal}")

    def _aplicar_recargos(self):
        """
        Aplica recargos según:
        - Horario nocturno (configurable)
        - Domingo
        - Feriado (se determina externamente)
        """
        recargo_total = 1.0
        recargos = []

        # 1. Recargo nocturno
        if self._es_nocturno():
            factor = to_float(self.config.recargo_nocturno or 1.0)
            recargo_total *= factor
            recargos.append(f"nocturno_{factor}x")
            logger.info(f"Recargo nocturno aplicado: {factor}x")

        # 2. Recargo domingo
        if self._es_domingo():
            factor = to_float(self.config.recargo_domingo or 1.0)
            recargo_total *= factor
            recargos.append(f"domingo_{factor}x")
            logger.info(f"Recargo domingo aplicado: {factor}x")

        # 3. Recargo feriado (si se pasa como parámetro o se calcula)
        # Por ahora lo dejamos como configurable, se aplica desde el servicio principal
        # ya que la verificación de feriados requiere API externa

        # Aplicar recargo
        if recargo_total > 1.0:
            self.subtotal *= recargo_total
            self.recargos_aplicados = recargos
            self.desglose["recargo_total"] = round(recargo_total, 2)
            self.desglose["subtotal_con_recargos"] = round(self.subtotal, 2)
            logger.info(f"Recargos aplicados: {recargos}, total={recargo_total}x")
        else:
            self.recargos_aplicados = []
            self.desglose["recargo_total"] = 1.0
            self.desglose["subtotal_con_recargos"] = round(self.subtotal, 2)

    def _es_nocturno(self) -> bool:
        """Verifica si la hora está dentro del rango nocturno"""
        hora_actual = self.fecha_hora.time()
        
        # Obtener horas del config (pueden ser time objects o strings)
        hora_inicio_raw = self.config.hora_inicio_nocturno or "22:00"
        hora_fin_raw = self.config.hora_fin_nocturno or "06:00"
        
        # Convertir a time si es string, usar directamente si ya es time
        if isinstance(hora_inicio_raw, str):
            try:
                inicio = time.fromisoformat(hora_inicio_raw)
            except ValueError:
                logger.warning(f"Formato de hora inválido: inicio={hora_inicio_raw}")
                return False
        elif isinstance(hora_inicio_raw, time):
            inicio = hora_inicio_raw
        else:
            logger.warning(f"Tipo de hora no soportado: inicio={type(hora_inicio_raw)}")
            return False
            
        if isinstance(hora_fin_raw, str):
            try:
                fin = time.fromisoformat(hora_fin_raw)
            except ValueError:
                logger.warning(f"Formato de hora inválido: fin={hora_fin_raw}")
                return False
        elif isinstance(hora_fin_raw, time):
            fin = hora_fin_raw
        else:
            logger.warning(f"Tipo de hora no soportado: fin={type(hora_fin_raw)}")
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
    es_feriado: bool = False
) -> EstimacionPrecioResponse:
    """
    Calcula el precio estimado de un viaje
    """
    logger.info(f"Calculando precio para tenant {control_base_id}, "
               f"vehículo {request.tipo_vehiculo.value}")
    
    # 1. Obtener configuración de tarifa del tenant
    stmt = select(ConfiguracionTarifa).where(
        and_(
            ConfiguracionTarifa.control_base_id == control_base_id,
            ConfiguracionTarifa.activo == True
        )
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        logger.error(f"No se encontró configuración de tarifa para tenant {control_base_id}")
        raise TarifaNotFoundError(
            f"No hay configuración de tarifa activa para este tenant. "
            f"Contacte al administrador."
        )

    logger.info(f"Configuración encontrada: {config.nombre}, "
               f"modo={config.modo_calculo}")

    # 2. Obtener tipo de vehículo
    stmt = select(TipoVehiculo).where(
        and_(
            TipoVehiculo.id == request.tipo_vehiculo.value,
            TipoVehiculo.activo == True
        )
    )
    result = await db.execute(stmt)
    tipo_vehiculo = result.scalar_one_or_none()
    
    if not tipo_vehiculo:
        logger.error(f"Tipo de vehículo no encontrado: {request.tipo_vehiculo.value}")
        raise TipoVehiculoNotFoundError(
            f"El tipo de vehículo '{request.tipo_vehiculo.value}' no existe o está inactivo"
        )

    logger.info(f"Tipo vehículo encontrado: {tipo_vehiculo.id}")

    # 3. Calcular precio
    calculador = CalculadorTarifa(
        config=config,
        tipo_vehiculo=tipo_vehiculo,
        distancia_km=distancia_km,
        tiempo_minutos=tiempo_minutos,
        tiempo_espera_minutos=request.tiempo_espera_minutos or 0,
        fecha_hora=fecha_hora
    )
    
    resultado = calculador.calcular()

    # 4. Aplicar recargo feriado si corresponde
    if es_feriado and config.recargo_feriado:
        factor = to_float(config.recargo_feriado)
        precio_final = resultado["precio"] * factor
        resultado["desglose"]["recargo_feriado"] = round(factor, 2)
        resultado["desglose"]["subtotal_con_feriado"] = round(precio_final, 2)
        resultado["precio"] = round(precio_final, 2)
        resultado["recargos_aplicados"].append(f"feriado_{factor}x")
        logger.info(f"Recargo feriado aplicado: {factor}x")

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
        modo_calculo=config.modo_calculo,
        moneda=config.moneda or "ARS",
        recargos_aplicados=resultado.get("recargos_aplicados", [])
    )

    logger.info(f"Precio estimado calculado: {response.precio_estimado} {response.moneda}")
    return response


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def calcular_fichas(distancia_metros: float, distancia_por_ficha: float) -> int:
    """
    Calcula el número de fichas para una distancia dada
    """
    if distancia_por_ficha <= 0:
        return 0
    return math.ceil(distancia_metros / distancia_por_ficha)


def formatear_precio(precio: float, moneda: str = "ARS") -> str:
    """Formatea un precio con su moneda"""
    if moneda == "ARS":
        return f"${precio:,.2f}"
    return f"{moneda} {precio:,.2f}"