# app/services/calculators/base.py
"""
Interfaz base para calculadores de liquidación
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from decimal import Decimal
from app.schemas.liquidacion import LiquidacionContextSchema, LiquidacionResultado


class LiquidacionCalculator(ABC):
    """Interfaz común para todos los calculadores de liquidación"""

    @abstractmethod
    async def calcular(self, contexto: LiquidacionContextSchema) -> LiquidacionResultado:
        """
        Calcula la liquidación a partir del contexto.
        Retorna un objeto LiquidacionResultado con los totales y detalles.
        """
        pass

    def _crear_linea_ingreso(self, viaje: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una línea de detalle para un viaje"""
        return {
            "tipo_linea": "INGRESO",
            "concepto": f"Viaje {viaje['id']}",
            "fuente_tipo": "viaje_solicitado",
            "fuente_id": viaje["id"],
            "monto": viaje["precio_final"],
            "signo": "HABER",
            "meta_data": {
                "fecha": viaje["finalizado_en"].isoformat() if viaje["finalizado_en"] else None,
                "vehiculo_id": str(viaje["vehiculo_id"]) if viaje["vehiculo_id"] else None,
                "chofer_id": str(viaje["chofer_id"]) if viaje["chofer_id"] else None,
            }
        }

    def _crear_linea_ingreso_ticketera(self, contexto: LiquidacionContextSchema) -> Dict[str, Any]:
        """Crea una línea de ingreso para recaudación de ticketera"""
        return {
            "tipo_linea": "INGRESO",
            "concepto": "Recaudación ticketera calle",
            "fuente_tipo": "turno_chofer",
            "fuente_id": contexto.turno_id,
            "monto": contexto.recaudacion_ticketera or Decimal(0),
            "signo": "HABER",
            "meta_data": {
                "fecha": contexto.fecha_fin.isoformat() if contexto.fecha_fin else None,
                "vehiculo_id": str(contexto.vehiculo_id),
                "chofer_id": str(contexto.chofer_id),
                "tipo": "ticketera_calle"
            }
        }

    def _crear_linea_gasto_turno(self, gasto: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una línea de detalle para un gasto de turno"""
        return {
            "tipo_linea": "GASTO_TURNO",
            "concepto": f"Gasto turno: {gasto['tipo_gasto']}",
            "fuente_tipo": "gasto_turno",
            "fuente_id": gasto["id"],
            "monto": gasto["monto"],
            "signo": "DEBE",
            "meta_data": {
                "tipo": gasto["tipo_gasto"],
                "categoria_id": str(gasto.get("categoria_id")) if gasto.get("categoria_id") else None,
                "subcategoria": gasto.get("subcategoria"),
                "km_registro": gasto.get("km_registro"),
            }
        }

    def _crear_linea_gasto_vehiculo(self, gasto: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una línea de detalle para un gasto de vehículo (NUEVO)"""
        return {
            "tipo_linea": "GASTO_VEHICULO",
            "concepto": f"Gasto vehículo: {gasto.get('tipo_gasto', 'sin_tipo')}",
            "fuente_tipo": "gasto_vehiculo",
            "fuente_id": gasto["id"],
            "monto": gasto["monto"],
            "signo": "DEBE",
            "meta_data": {
                "tipo": gasto.get("tipo_gasto"),
                "categoria_id": str(gasto.get("categoria_id")) if gasto.get("categoria_id") else None,
                "subcategoria": gasto.get("subcategoria"),
                "km_registro": gasto.get("km_registro"),
                "fecha_gasto": gasto.get("fecha_gasto").isoformat() if gasto.get("fecha_gasto") else None,
                "descripcion": gasto.get("descripcion"),
            }
        }

    def _crear_linea_comision(self, monto: Decimal, concepto: str) -> Dict[str, Any]:
        return {
            "tipo_linea": "COMISION",
            "concepto": concepto,
            "fuente_tipo": None,
            "fuente_id": None,
            "monto": monto,
            "signo": "DEBE",
            "meta_data": {}
        }

    def _crear_linea_canon(self, monto: Decimal, concepto: str) -> Dict[str, Any]:
        return {
            "tipo_linea": "CANON",
            "concepto": concepto,
            "fuente_tipo": None,
            "fuente_id": None,
            "monto": monto,
            "signo": "DEBE",
            "meta_data": {}
        }

    def _crear_linea_km_excedente(self, km_excedentes: Decimal, costo: Decimal, valor_km: Decimal) -> Dict[str, Any]:
        """Crea una línea de detalle para KM excedentes"""
        return {
            "tipo_linea": "CANON",
            "concepto": f"KM excedentes ({km_excedentes:.2f} km x ${valor_km:.2f})",
            "fuente_tipo": None,
            "fuente_id": None,
            "monto": costo,
            "signo": "DEBE",
            "meta_data": {
                "km_excedentes": float(km_excedentes),
                "valor_km": float(valor_km)
            }
        }