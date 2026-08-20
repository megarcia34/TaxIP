# app/services/calculators/autogestion.py
"""
Calculador de liquidación para AUTO_GESTION — D6
"""

from decimal import Decimal
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.services.calculators.base import LiquidacionCalculator


class AutoGestionCalculator(LiquidacionCalculator):
    """
    Calculador de liquidación para AUTO_GESTION.
    
    Reglas de negocio (D6 + modelo económico):
    1. Ingresos = viajes + ticketera
    2. Gastos del turno los paga el propietario (porque es el chofer)
    3. Gastos del vehículo los absorbe el propietario (mantenimiento, neumáticos)
    4. Comisión chofer = 0 (no hay chofer)
    5. Canon = 0 (no hay alquiler)
    6. Total propietario = Ingresos - Gastos_turno - Gastos_vehiculo
    """

    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        # DEBUG: Verificar valores recibidos
        print("🔍 DEBUG AUTO_GESTION:")
        print(f"   viajes: {len(contexto.viajes)}")
        print(f"   gastos_turno: {len(contexto.gastos_turno)}")
        print(f"   gastos_vehiculo: {len(contexto.gastos_vehiculo)}")
        print(f"   recaudacion_ticketera: {contexto.recaudacion_ticketera}")

        # 1. Sumar ingresos (viajes)
        monto_bruto = Decimal(0)
        lineas = []
        for viaje in contexto.viajes:
            monto_bruto += viaje["precio_final"]
            lineas.append(self._crear_linea_ingreso(viaje))

        # 2. Agregar recaudación de ticketera (si existe)
        if contexto.recaudacion_ticketera and contexto.recaudacion_ticketera > 0:
            monto_bruto += contexto.recaudacion_ticketera
            lineas.append(self._crear_linea_ingreso_ticketera(contexto))

        # 3. Sumar gastos del turno (los paga el propietario)
        total_gastos_turno = Decimal(0)
        for gasto in contexto.gastos_turno:
            total_gastos_turno += gasto["monto"]
            lineas.append(self._crear_linea_gasto_turno(gasto))
        
        # 4. Sumar gastos del vehículo (los absorbe el propietario) - NUEVO
        total_gastos_vehiculo = Decimal(0)
        for gasto in contexto.gastos_vehiculo:
            total_gastos_vehiculo += gasto["monto"]
            lineas.append(self._crear_linea_gasto_vehiculo(gasto))

        # 5. Calcular utilidad (ingresos - gastos totales)
        total_gastos = total_gastos_turno + total_gastos_vehiculo
        utilidad = monto_bruto - total_gastos
        
        # Si la utilidad es negativa, se muestra como 0 (el propietario asume la pérdida)
        if utilidad < 0:
            utilidad = Decimal(0)

        # 6. En AUTO_GESTION, el propietario es el chofer
        #    No hay comisión ni canon
        return LiquidacionResultado(
            monto_bruto=monto_bruto,
            total_gastos=total_gastos,
            comision_chofer=Decimal(0),  # No hay chofer
            canon=Decimal(0),            # No hay alquiler
            total_chofer=Decimal(0),     # No hay chofer
            total_propietario=utilidad,  # Toda la utilidad es del propietario
            detalles=lineas
        )