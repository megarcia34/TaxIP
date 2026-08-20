# app/services/calculators/porcentaje.py
"""
Calculador de liquidación para PORCENTAJE — D5
"""

from decimal import Decimal, ROUND_HALF_UP
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.services.calculators.base import LiquidacionCalculator


class PorcentajeCalculator(LiquidacionCalculator):
    """
    Calculador de liquidación para PORCENTAJE.
    
    Reglas de negocio (D5 + modelo económico):
    1. Base de cálculo = viajes app + recaudacion_ticketera_calle
    2. Gastos del turno se descuentan ANTES de aplicar el porcentaje
    3. Gastos del vehículo los absorbe el PROPIETARIO (no afectan la base)
    4. Comisión = (monto_bruto - gastos_turno) * porcentaje / 100
    5. El chofer recibe la comisión (ya neta de gastos de turno)
    6. El propietario recibe: monto_bruto - gastos_turno - comision - gastos_vehiculo
    7. No hay mínimo garantizado
    8. Si base_liquidable < 0, se usa 0
    """

    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        # 1. Validar porcentaje
        if not contexto.porcentaje_chofer:
            raise ValueError("El contrato no tiene porcentaje_chofer definido")
        
        if contexto.porcentaje_chofer < 0 or contexto.porcentaje_chofer > 100:
            raise ValueError(f"Porcentaje inválido: {contexto.porcentaje_chofer}%")

        # 2. Sumar ingresos (viajes + ticketera)
        monto_bruto = Decimal(0)
        lineas = []
        
        # 2a. Viajes de aplicación
        for viaje in contexto.viajes:
            monto_bruto += viaje["precio_final"]
            lineas.append(self._crear_linea_ingreso(viaje))
        
        # 2b. Recaudación ticketera calle
        if contexto.recaudacion_ticketera and contexto.recaudacion_ticketera > 0:
            monto_bruto += contexto.recaudacion_ticketera
            lineas.append(self._crear_linea_ingreso_ticketera(contexto))
        
        # 3. Sumar gastos del turno (se descuentan ANTES del porcentaje)
        total_gastos_turno = Decimal(0)
        for gasto in contexto.gastos_turno:
            total_gastos_turno += gasto["monto"]
            lineas.append(self._crear_linea_gasto_turno(gasto))
        
        # 4. Sumar gastos del vehículo (los absorbe el propietario, DESPUÉS del porcentaje)
        total_gastos_vehiculo = Decimal(0)
        for gasto in contexto.gastos_vehiculo:
            total_gastos_vehiculo += gasto["monto"]
            lineas.append(self._crear_linea_gasto_vehiculo(gasto))
        
        # 5. Calcular base liquidable (ingresos - gastos de turno) ANTES del porcentaje
        base_liquidable = monto_bruto - total_gastos_turno
        
        # 6. Si base liquidable es negativa, usar 0
        if base_liquidable < 0:
            base_liquidable = Decimal(0)
        
        # 7. Calcular comisión (sobre la base liquidable)
        comision_chofer = (base_liquidable * contexto.porcentaje_chofer) / Decimal(100)
        comision_chofer = comision_chofer.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        lineas.append(self._crear_linea_comision(
            comision_chofer, 
            f"Comisión chofer {contexto.porcentaje_chofer}% sobre base liquidable"
        ))
        
        # 8. Calcular totales
        total_chofer = comision_chofer
        # El propietario absorbe: gastos de turno (ya descontados) + gastos de vehículo
        total_propietario = monto_bruto - total_gastos_turno - comision_chofer - total_gastos_vehiculo
        
        # 9. Construir resultado
        return LiquidacionResultado(
            monto_bruto=monto_bruto,
            total_gastos=total_gastos_turno + total_gastos_vehiculo,
            comision_chofer=comision_chofer,
            canon=Decimal(0),
            total_chofer=total_chofer,
            total_propietario=total_propietario,
            detalles=lineas
        )