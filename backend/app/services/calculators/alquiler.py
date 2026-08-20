# app/services/calculators/alquiler.py
"""
Calculador de liquidación para ALQUILER — D4
Alineado con la ESPECIFICACIÓN FUNCIONAL DE NEGOCIO
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Dict, Any

from app.schemas.liquidacion import (
    LiquidacionContextSchema,
    LiquidacionResultado,
    LiquidacionDetalleCreate,
    TipoLinea,
    SignoLinea
)
from app.services.calculators.base import LiquidacionCalculator


class AlquilerCalculator(LiquidacionCalculator):
    """
    Calculador de liquidación para ALQUILER.
    
    Reglas de negocio (basadas en la especificación funcional):
    1. Canon = canon_diario (DIARIO) o canon_diario * 7 (SEMANAL)
    2. Si día no trabajado y tratamiento = POR_USO_EFECTIVO → canon = 0
    3. KM excedentes = max(0, km_final - km_inicial - km_incluidos_dia)
    4. Costo km excedente = km_excedentes * valor_km_excedente
    5. Los gastos del turno los paga el chofer
    6. Los gastos del vehículo los absorbe el PROPIETARIO
    7. Total chofer = canon + costo_km_excedente + gastos_turno
    8. Total propietario = canon + costo_km_excedente - gastos_vehiculo
    """

    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        """
        Ejecuta el cálculo completo para un contrato ALQUILER.
        """
        # 1. Validar campos requeridos
        self._validar_contexto(contexto)

        # 2. Sumar ingresos
        monto_bruto = Decimal(0)
        lineas = []
        
        # 2a. Viajes (HABER)
        for viaje in contexto.viajes:
            monto_bruto += viaje["precio_final"]
            lineas.append(self._crear_linea_ingreso(viaje))
        
        # 2b. Ticketera (HABER)
        if contexto.recaudacion_ticketera and contexto.recaudacion_ticketera > 0:
            monto_bruto += contexto.recaudacion_ticketera
            lineas.append(self._crear_linea_ingreso_ticketera(contexto))
        
        # 3. Calcular gastos (DEBE)
        total_gastos_turno = Decimal(0)
        for gasto in contexto.gastos_turno:
            total_gastos_turno += gasto["monto"]
            lineas.append(self._crear_linea_gasto_turno(gasto))
        
        total_gastos_vehiculo = Decimal(0)
        for gasto in contexto.gastos_vehiculo:
            total_gastos_vehiculo += gasto["monto"]
            lineas.append(self._crear_linea_gasto_vehiculo(gasto))
        
        total_gastos = total_gastos_turno + total_gastos_vehiculo

        # 4. Calcular canon (DEBE)
        canon = self._calcular_canon(contexto)
        if canon > 0:
            modalidad_texto = "semanal" if contexto.modalidad_computo == "SEMANAL" else "diario"
            dias_texto = f" ({contexto.dias_trabajados} días)" if contexto.dias_trabajados else ""
            lineas.append(self._crear_linea_canon(canon, f"Canon {modalidad_texto}{dias_texto}"))
        
        # 5. Calcular KM excedentes (DEBE)
        km_excedentes, costo_km_excedente = self._calcular_km_excedentes(contexto)
        if costo_km_excedente > 0:
            lineas.append(self._crear_linea_km_excedente(
                km_excedentes, 
                costo_km_excedente, 
                contexto.valor_km_excedente or Decimal(0)
            ))
        
        # 6. Calcular totales
        total_chofer = canon + costo_km_excedente + total_gastos_turno
        total_propietario = canon + costo_km_excedente - total_gastos_vehiculo
        
        # 7. Construir resultado
        return LiquidacionResultado(
            monto_bruto=monto_bruto,
            total_gastos=total_gastos,
            comision_chofer=Decimal(0),
            canon=canon,
            km_excedentes=km_excedentes,
            cargo_km_excedentes=costo_km_excedente,
            total_chofer=total_chofer,
            total_propietario=total_propietario,
            saldo_chofer=Decimal(0),
            saldo_propietario=Decimal(0),
            detalles=self._convertir_a_detalles(lineas)
        )

    def _validar_contexto(self, contexto: LiquidacionContextSchema) -> None:
        """Valida que todos los campos necesarios estén presentes"""
        
        # Validar turno finalizado
        if not contexto.fecha_fin:
            raise ValueError("El turno no está finalizado")
        
        # Validar canon diario
        if contexto.canon_diario is None or contexto.canon_diario < 0:
            raise ValueError("canon_diario es requerido para contratos ALQUILER")
        
        # Validar KM inicial y final
        if contexto.km_inicial is None:
            raise ValueError("km_inicial es requerido para ALQUILER")
        if contexto.km_final is None:
            raise ValueError("km_final es requerido para ALQUILER")
        
        # Validar que km_final >= km_inicial
        if contexto.km_final < contexto.km_inicial:
            raise ValueError(
                f"km_final ({contexto.km_final}) no puede ser menor que km_inicial ({contexto.km_inicial})"
            )

    def _calcular_canon(self, contexto: LiquidacionContextSchema) -> Decimal:
        """
        Calcula el canon según modalidad y tratamiento de día no trabajado.
        
        Reglas:
        - DIARIO: canon_diario * días_trabajados
        - SEMANAL: canon_diario * 7 (o según días contractuales de la semana)
        - POR_USO_EFECTIVO: si no hubo uso, canon = 0
        """
        if not contexto.canon_diario:
            return Decimal(0)
        
        canon = Decimal(0)
        
        # 1. Calcular canon base según modalidad
        if contexto.modalidad_computo == "SEMANAL":
            # SEMANAL: usar días contractuales de la semana
            dias_semana = len(contexto.dias_contractuales) if contexto.dias_contractuales else 7
            canon = Decimal(str(contexto.canon_diario)) * Decimal(str(dias_semana))
        else:
            # DIARIO: usar días trabajados
            dias_trabajados = contexto.dias_trabajados or 1
            canon = Decimal(str(contexto.canon_diario)) * Decimal(str(dias_trabajados))
        
        # 2. Tratamiento: día no trabajado (POR_USO_EFECTIVO)
        if contexto.tratamiento_dia_no_trabajado == "POR_USO_EFECTIVO":
            if not self._es_dia_trabajado(contexto):
                return Decimal(0)
        
        return canon

    def _es_dia_trabajado(self, contexto: LiquidacionContextSchema) -> bool:
        """
        Verifica si el día fue trabajado.
        
        Criterio: existe al menos un viaje completado en el turno
        o el turno tiene recaudación.
        """
        if contexto.viajes and len(contexto.viajes) > 0:
            return True
        if contexto.recaudacion_ticketera and contexto.recaudacion_ticketera > 0:
            return True
        if contexto.fecha_fin:
            return True
        return False

    def _calcular_km_excedentes(self, contexto: LiquidacionContextSchema) -> tuple:
        """
        Calcula KM excedentes según el modo de compensación.
        
        Modos:
        - DIARIA: Excedente calculado por día (sin compensación)
        - ACUMULADA: Excedente sobre total del período
        - COMPENSADA: Compensación entre días
        """
        if contexto.km_inicial is None or contexto.km_final is None:
            return Decimal(0), Decimal(0)
        
        km_incluidos = contexto.km_incluidos_dia or Decimal(0)
        
        # Calcular km recorridos
        km_recorridos = Decimal(str(contexto.km_final - contexto.km_inicial))
        
        if km_recorridos <= 0:
            return Decimal(0), Decimal(0)
        
        # Obtener modo de compensación (default: DIARIA)
        compensacion = getattr(contexto, 'compensacion_km', 'DIARIA')
        
        if compensacion == "DIARIA":
            # Cálculo diario (sin compensación)
            km_incluidos_totales = km_incluidos
            km_excedentes = max(Decimal(0), km_recorridos - km_incluidos_totales)
            
        elif compensacion == "ACUMULADA":
            # Cálculo sobre total del período
            dias_periodo = contexto.dias_trabajados or 1
            km_incluidos_totales = km_incluidos * Decimal(str(dias_periodo))
            km_excedentes = max(Decimal(0), km_recorridos - km_incluidos_totales)
            
        elif compensacion == "COMPENSADA":
            # Compensación entre días
            # Usamos el mismo cálculo que ACUMULADA pero con compensación
            dias_periodo = contexto.dias_trabajados or 1
            km_incluidos_totales = km_incluidos * Decimal(str(dias_periodo))
            km_excedentes = max(Decimal(0), km_recorridos - km_incluidos_totales)
        else:
            # Fallback: DIARIA
            km_excedentes = max(Decimal(0), km_recorridos - km_incluidos)
        
        # Calcular costo
        valor_km = contexto.valor_km_excedente or Decimal(0)
        costo = (km_excedentes * valor_km).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return km_excedentes, costo

    def _convertir_a_detalles(self, lineas: list) -> list:
        """
        Convierte las líneas en diccionario a objetos LiquidacionDetalleCreate.
        """
        detalles = []
        for linea in lineas:
            try:
                if isinstance(linea, LiquidacionDetalleCreate):
                    detalles.append(linea)
                    continue
                
                if isinstance(linea, dict):
                    tipo_linea = linea.get("tipo_linea")
                    tipo_linea_enum = None
                    if tipo_linea == "INGRESO":
                        tipo_linea_enum = TipoLinea.INGRESO
                    elif tipo_linea in ["GASTO_TURNO", "GASTO"]:
                        tipo_linea_enum = TipoLinea.GASTO
                    elif tipo_linea == "GASTO_VEHICULO":
                        tipo_linea_enum = TipoLinea.GASTO
                    elif tipo_linea == "CANON":
                        tipo_linea_enum = TipoLinea.CANON
                    elif tipo_linea == "KM_EXCEDENTE":
                        tipo_linea_enum = TipoLinea.KM_EXCEDENTE
                    elif tipo_linea == "COMISION":
                        tipo_linea_enum = TipoLinea.COMISION
                    else:
                        tipo_linea_enum = TipoLinea.AJUSTE
                    
                    signo = SignoLinea.HABER if linea.get("signo") == "HABER" else SignoLinea.DEBE
                    
                    detalle = LiquidacionDetalleCreate(
                        tipo_linea=tipo_linea_enum,
                        concepto=linea.get("concepto"),
                        fuente_tipo=linea.get("fuente_tipo"),
                        fuente_id=linea.get("fuente_id"),
                        monto=linea.get("monto", Decimal(0)),
                        signo=signo,
                        meta_data=linea.get("meta_data", {})
                    )
                    detalles.append(detalle)
            except Exception as e:
                print(f"⚠️ Error al convertir línea: {e}")
                continue
        
        return detalles