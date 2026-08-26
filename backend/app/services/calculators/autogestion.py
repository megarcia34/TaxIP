# app/services/calculators/autogestion.py
"""
Calculador de liquidación para AUTO_GESTION — D6
ACTUALIZADO CON INGRESO_TURNO
"""

from decimal import Decimal
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.services.calculators.base import LiquidacionCalculator


class AutoGestionCalculator(LiquidacionCalculator):
    """
    Calculador de liquidación para AUTO_GESTION.
    
    Reglas de negocio (D6 + modelo económico):
    1. Ingresos = viajes + ticketera + todos los ingresos aprobados
    2. Gastos del turno los paga el propietario (porque es el chofer)
    3. Gastos del vehículo los absorbe el propietario (mantenimiento, neumáticos)
    4. Comisión chofer = 0 (no hay chofer)
    5. Canon = 0 (no hay alquiler)
    6. Total propietario = Ingresos - Gastos_turno - Gastos_vehiculo
    """

    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        # DEBUG
        print("🔍 DEBUG AUTO_GESTION:")
        print(f"   viajes: {len(contexto.viajes)}")
        print(f"   gastos_turno: {len(contexto.gastos_turno)}")
        print(f"   gastos_vehiculo: {len(contexto.gastos_vehiculo)}")
        print(f"   ingresos: {len(contexto.ingresos)}")
        print(f"   total_ingresos_aprobados: {contexto.total_ingresos_aprobados}")

        # 1. Calcular monto bruto usando el nuevo método
        monto_bruto, lineas = self._calcular_monto_bruto_desde_ingresos(contexto)

        # 2. Sumar gastos del turno (los paga el propietario)
        total_gastos_turno = Decimal(0)
        for gasto in contexto.gastos_turno:
            total_gastos_turno += gasto["monto"]
            lineas.append(self._crear_linea_gasto_turno(gasto))
        
        # 3. Sumar gastos del vehículo (los absorbe el propietario)
        total_gastos_vehiculo = Decimal(0)
        for gasto in contexto.gastos_vehiculo:
            total_gastos_vehiculo += gasto["monto"]
            lineas.append(self._crear_linea_gasto_vehiculo(gasto))

        # 4. Calcular utilidad (ingresos - gastos totales)
        total_gastos = total_gastos_turno + total_gastos_vehiculo
        utilidad = monto_bruto - total_gastos
        
        # Si la utilidad es negativa, se muestra como 0 (el propietario asume la pérdida)
        if utilidad < 0:
            utilidad = Decimal(0)

        # 5. En AUTO_GESTION, el propietario es el chofer
        return LiquidacionResultado(
            monto_bruto=monto_bruto,
            total_gastos=total_gastos,
            comision_chofer=Decimal(0),
            canon=Decimal(0),
            total_chofer=Decimal(0),
            total_propietario=utilidad,
            detalles=lineas
        )