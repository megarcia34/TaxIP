"""
Calculador de liquidacion para PORCENTAJE - D5
ACTUALIZADO CON INGRESO_TURNO Y FASE 0
"""

from decimal import Decimal, ROUND_HALF_UP
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado
from app.services.calculators.base import LiquidacionCalculator


class PorcentajeCalculator(LiquidacionCalculator):
    """
    Calculador de liquidacion para PORCENTAJE.
    
    Reglas de negocio (D5 + modelo economico + Fase 0):
    1. Base de calculo = ingresos aprobados del turno
    2. Gastos del turno se descuentan segun tratamiento_gastos (ANTES o DESPUES)
    3. Gastos del vehiculo los absorbe el PROPIETARIO (no afectan la base)
    4. porcentaje_chofer = porcentaje que RECIBE EL CHOFER (ej. 35%)
    5. El propietario recibe el resto: 100 - porcentaje_chofer (ej. 65%)
    6. Comision de pasarela es SIEMPRE costo del propietario
    7. Si base_liquidable < 0, se usa 0
    """

    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        # 1. Validar porcentaje
        if not contexto.porcentaje_chofer:
            raise ValueError("El contrato no tiene porcentaje_chofer definido")
        
        if contexto.porcentaje_chofer < 0 or contexto.porcentaje_chofer > 100:
            raise ValueError(f"Porcentaje invalido: {contexto.porcentaje_chofer}%")

        # 2. Calcular monto bruto usando el metodo de la clase base
        monto_bruto, lineas = self._calcular_monto_bruto_desde_ingresos(contexto)
        
        # 3. Sumar gastos del turno
        total_gastos_turno = Decimal(0)
        for gasto in contexto.gastos_turno:
            total_gastos_turno += gasto["monto"]
            lineas.append(self._crear_linea_gasto_turno(gasto))
        
        # 4. Sumar gastos del vehiculo (los absorbe el propietario)
        total_gastos_vehiculo = Decimal(0)
        for gasto in contexto.gastos_vehiculo:
            total_gastos_vehiculo += gasto["monto"]
            lineas.append(self._crear_linea_gasto_vehiculo(gasto))
        
        # 5. Aplicar tratamiento de gastos (ANTES o DESPUES)
        tratamiento_gastos = contexto.tratamiento_gastos or "DESPUES"
        porcentaje = Decimal(str(contexto.porcentaje_chofer or 0))
        
        if tratamiento_gastos == "ANTES":
            # Gastos se descuentan ANTES de aplicar el porcentaje
            base_liquidable = monto_bruto - total_gastos_turno
            if base_liquidable < 0:
                base_liquidable = Decimal(0)
            
            comision_chofer = (base_liquidable * porcentaje) / Decimal(100)
            comision_propietario = (base_liquidable * (Decimal(100) - porcentaje)) / Decimal(100)
            
            lineas.append(self._crear_linea_comision(
                comision_chofer.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                f"Comision chofer {porcentaje:.0f}% sobre base liquidable (gastos descontados ANTES)"
            ))
            lineas.append(self._crear_linea_comision(
                comision_propietario.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                f"Comision propietario {100 - int(porcentaje):.0f}% sobre base liquidable"
            ))
            
        else:  # DESPUES
            # Gastos se descuentan DESPUES de aplicar el porcentaje
            comision_chofer_bruta = (monto_bruto * porcentaje) / Decimal(100)
            comision_propietario = (monto_bruto * (Decimal(100) - porcentaje)) / Decimal(100)
            
            # Redondear brutas primero (practica contable)
            comision_chofer_bruta = comision_chofer_bruta.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            comision_propietario = comision_propietario.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Los gastos se restan de la parte del chofer
            comision_chofer = comision_chofer_bruta - total_gastos_turno
            if comision_chofer < 0:
                comision_chofer = Decimal(0)
            
            lineas.append(self._crear_linea_comision(
                comision_chofer_bruta,
                f"Comision chofer {porcentaje:.0f}% sobre monto bruto"
            ))
            lineas.append(self._crear_linea_comision(
                comision_propietario,
                f"Comision propietario {100 - int(porcentaje):.0f}% sobre monto bruto"
            ))
            lineas.append(self._crear_linea_gasto_turno({
                "id": contexto.turno_id,  # ✅ UUID válido del turno
                "monto": total_gastos_turno,
                "tipo_gasto": "GASTOS_TURNO",
            }))
        
        # Redondear comisiones finales
        comision_chofer = comision_chofer.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        comision_propietario = comision_propietario.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 6. Comision de pasarela (costo del propietario)
        comision_pasarela = contexto.comision_pasarela or Decimal(0)
        
        lineas.append(self._crear_linea_comision(
            comision_pasarela,
            "Comision pasarela (costo de recaudacion electronica, absorbido por propietario)"
        ))
        
        # 7. Calcular totales
        total_chofer = comision_chofer
        
        # El propietario recibe su porcentaje menos gastos de vehiculo y comision de pasarela
        total_propietario = comision_propietario - total_gastos_vehiculo - comision_pasarela
        if total_propietario < 0:
            total_propietario = Decimal(0)
        
        # 8. Construir resultado
        return LiquidacionResultado(
            monto_bruto=monto_bruto,
            total_gastos=total_gastos_turno + total_gastos_vehiculo,
            comision_chofer=comision_chofer,
            canon=Decimal(0),
            km_excedentes=Decimal(0),
            cargo_km_excedentes=Decimal(0),
            total_chofer=total_chofer,
            total_propietario=total_propietario,
            saldo_chofer=total_chofer,
            saldo_propietario=total_propietario,
            comision_pasarela=comision_pasarela,
            detalles=lineas
        )