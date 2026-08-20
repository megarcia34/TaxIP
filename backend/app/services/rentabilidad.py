"""
Servicios de Cálculo de Rentabilidad
USANDO LIQUIDACIÓN COMO FUENTE DE DATOS
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from uuid import UUID
import calendar
import logging

logger = logging.getLogger(__name__)


# app/services/rentabilidad.py (agregar al principio del archivo)

def calcular_ppv(
    tarifa_base: float,
    precio_km: float,
    precio_minuto: float,
    recargo_nocturno: float,
    distancia_km: float,
    tiempo_min: float,
    es_nocturno: bool = False
) -> float:
    """
    Calcula el Precio Promedio del Viaje (PPV)
    PPV = (TB + (DP × PK) + (TP × PM)) × (1 + recargo_nocturno)
    """
    base = tarifa_base + (distancia_km * precio_km) + (tiempo_min * precio_minuto)
    if es_nocturno:
        base = base * recargo_nocturno
    return round(base, 2)


def calcular_costo_medio_ponderado_procesadoras(
    config: Dict[str, Any]
) -> float:
    """
    Calcula el Costo Promedio Ponderado de Procesadoras (CPP)
    CPP = Σ(Mix × Comisión) × (1 + IVA)
    """
    cpp = (
        (config["mix_efectivo"] / 100 * 0) +
        (config["mix_transferencia"] / 100 * 0) +
        (config["mix_qr"] / 100 * (config["comision_qr"] / 100)) +
        (config["mix_debito"] / 100 * (config["comision_debito"] / 100)) +
        (config["mix_credito"] / 100 * (config["comision_credito"] / 100))
    )
    cpp = cpp * (1 + config["iva"] / 100)
    return round(cpp, 4)

# ============================================
# CONFIGURACIÓN DEL TENANT
# ============================================

async def obtener_configuracion_tenant(
    db: AsyncSession,
    control_base_id: UUID
) -> Dict[str, Any]:
    """
    Obtiene la configuración de rentabilidad del tenant
    """
    query = text("""
        SELECT 
            canon_mensual_por_vehiculo,
            porcentaje_taxip_por_viaje,
            iva,
            iibb,
            idc,
            mix_efectivo,
            mix_transferencia,
            mix_qr,
            mix_debito,
            mix_credito,
            comision_qr,
            comision_debito,
            comision_credito,
            costo_combustible_por_km,
            costo_mantenimiento_por_dia,
            costo_seguro_por_dia,
            costo_impuesto_por_dia,
            depreciacion_vehiculo_por_dia
        FROM tenant.configuracion_tenant
        WHERE control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()
    
    if not row:
        return {
            "canon_mensual_por_vehiculo": 10000,
            "porcentaje_taxip_por_viaje": 1.5,
            "iva": 21.0,
            "iibb": 5.0,
            "idc": 0.3,
            "mix_efectivo": 40.0,
            "mix_transferencia": 20.0,
            "mix_qr": 25.0,
            "mix_debito": 15.0,
            "mix_credito": 0.0,
            "comision_qr": 0.80,
            "comision_debito": 1.00,
            "comision_credito": 3.50,
            "costo_combustible_por_km": 80.0,
            "costo_mantenimiento_por_dia": 500.0,
            "costo_seguro_por_dia": 300.0,
            "costo_impuesto_por_dia": 200.0,
            "depreciacion_vehiculo_por_dia": 400.0
        }
    
    return {
        "canon_mensual_por_vehiculo": float(row[0] or 10000),
        "porcentaje_taxip_por_viaje": float(row[1] or 1.5),
        "iva": float(row[2] or 21.0),
        "iibb": float(row[3] or 5.0),
        "idc": float(row[4] or 0.3),
        "mix_efectivo": float(row[5] or 40.0),
        "mix_transferencia": float(row[6] or 20.0),
        "mix_qr": float(row[7] or 25.0),
        "mix_debito": float(row[8] or 15.0),
        "mix_credito": float(row[9] or 0.0),
        "comision_qr": float(row[10] or 0.80),
        "comision_debito": float(row[11] or 1.00),
        "comision_credito": float(row[12] or 3.50),
        "costo_combustible_por_km": float(row[13] or 80.0),
        "costo_mantenimiento_por_dia": float(row[14] or 500.0),
        "costo_seguro_por_dia": float(row[15] or 300.0),
        "costo_impuesto_por_dia": float(row[16] or 200.0),
        "depreciacion_vehiculo_por_dia": float(row[17] or 400.0)
    }


def calcular_ppv(
    tarifa_base: float,
    precio_km: float,
    precio_minuto: float,
    recargo_nocturno: float,
    distancia_km: float,
    tiempo_min: float,
    es_nocturno: bool = False
) -> float:
    """
    Calcula el Precio Promedio del Viaje (PPV)
    """
    base = tarifa_base + (distancia_km * precio_km) + (tiempo_min * precio_minuto)
    if es_nocturno:
        base = base * recargo_nocturno
    return round(base, 2)


async def calcular_rentabilidad_viaje(
    db: AsyncSession,
    viaje_id: UUID,
    config: Dict[str, Any],
    tarifa_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula la rentabilidad de un viaje específico
    USANDO LIQUIDACIÓN
    """
    # Obtener datos del viaje desde liquidacion
    query = text("""
        SELECT 
            vs.id,
            vs.precio_final,
            vs.precio_estimado,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            vs.created_at,
            vs.estado,
            vs.vehiculo_id,
            l.monto_bruto,
            l.total_gastos,
            l.total_propietario,
            l.utilidad_propietario,
            COALESCE(
                (SELECT mp.nombre 
                 FROM payment.transaccion t 
                 JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id 
                 WHERE t.viaje_id = vs.id LIMIT 1),
                'efectivo'
            ) as metodo_pago
        FROM trip.viaje_solicitado vs
        LEFT JOIN fleet.liquidacion l ON l.turno_id = vs.turno_id
        WHERE vs.id = :viaje_id
    """)
    
    result = await db.execute(query, {"viaje_id": viaje_id})
    row = result.first()
    
    if not row:
        return {"error": "Viaje no encontrado"}
    
    # Datos del viaje
    ingreso_bruto = float(row[1] or row[2] or 0)
    distancia_km = float(row[3] or 0) / 1000
    tiempo_min = float(row[4] or 0) / 60
    created_at = row[5]
    estado = row[6]
    vehiculo_id = row[7]
    metodo_pago = row[13] or "efectivo"
    
    # Datos de liquidación (si existen)
    monto_bruto = float(row[8] or 0)
    total_gastos = float(row[9] or 0)
    total_propietario = float(row[10] or 0)
    utilidad_propietario = float(row[11] or 0)
    
    if not vehiculo_id:
        return {
            "error": "El viaje no tiene vehículo asignado",
            "viaje_id": str(viaje_id),
            "ingreso_bruto": round(ingreso_bruto, 2),
            "estado": estado,
            "metodo_pago": metodo_pago
        }
    
    # Si hay liquidación, usar esos datos
    if monto_bruto > 0:
        return {
            "viaje_id": str(row[0]),
            "ingreso_bruto": round(monto_bruto, 2),
            "total_gastos": round(total_gastos, 2),
            "utilidad_propietario": round(utilidad_propietario, 2),
            "margen": round((utilidad_propietario / monto_bruto * 100) if monto_bruto > 0 else 0, 2),
            "distancia_km": round(distancia_km, 2),
            "tiempo_min": round(tiempo_min, 2),
            "metodo_pago": metodo_pago,
            "estado": estado,
            "fecha": created_at,
            "fuente": "liquidacion"
        }
    
    # Si no hay liquidación, calcular con valores estimados
    costo_combustible = distancia_km * config["costo_combustible_por_km"]
    
    comision_porcentaje = 0
    if metodo_pago == "qr":
        comision_porcentaje = config["comision_qr"] / 100
    elif metodo_pago == "debito":
        comision_porcentaje = config["comision_debito"] / 100
    elif metodo_pago == "credito":
        comision_porcentaje = config["comision_credito"] / 100
    
    comision_bancaria = ingreso_bruto * comision_porcentaje * (1 + config["iva"] / 100)
    porcentaje_taxip = ingreso_bruto * (config["porcentaje_taxip_por_viaje"] / 100)
    
    viajes_por_dia = 20
    costos_fijos_diarios = (
        config["costo_mantenimiento_por_dia"] +
        config["costo_seguro_por_dia"] +
        config["costo_impuesto_por_dia"] +
        config["depreciacion_vehiculo_por_dia"]
    )
    costo_fijo_por_viaje = costos_fijos_diarios / viajes_por_dia
    
    dias_mes = 30
    canon_por_viaje = config["canon_mensual_por_vehiculo"] / (viajes_por_dia * dias_mes)
    
    utilidad_neta = (
        ingreso_bruto -
        costo_combustible -
        comision_bancaria -
        porcentaje_taxip -
        costo_fijo_por_viaje -
        canon_por_viaje
    )
    
    return {
        "viaje_id": str(row[0]),
        "ingreso_bruto": round(ingreso_bruto, 2),
        "costo_combustible": round(costo_combustible, 2),
        "comision_bancaria": round(comision_bancaria, 2),
        "porcentaje_taxip": round(porcentaje_taxip, 2),
        "costo_fijo_por_viaje": round(costo_fijo_por_viaje, 2),
        "canon_por_viaje": round(canon_por_viaje, 2),
        "utilidad_neta": round(utilidad_neta, 2),
        "margen": round((utilidad_neta / ingreso_bruto * 100) if ingreso_bruto > 0 else 0, 2),
        "distancia_km": round(distancia_km, 2),
        "tiempo_min": round(tiempo_min, 2),
        "metodo_pago": metodo_pago,
        "estado": estado,
        "fecha": created_at,
        "fuente": "estimado"
    }


async def calcular_rentabilidad_periodo(
    db: AsyncSession,
    vehiculo_id: UUID,
    fecha_desde: date,
    fecha_hasta: date,
    control_base_id: UUID
) -> Dict[str, Any]:
    """
    Calcula la rentabilidad de un vehículo en un período
    USANDO LIQUIDACIÓN
    """
    config = await obtener_configuracion_tenant(db, control_base_id)
    
    # Obtener viajes del período CON LIQUIDACIÓN
    query = text("""
        SELECT 
            vs.id,
            vs.precio_final,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            vs.created_at,
            vs.estado,
            EXTRACT(HOUR FROM vs.created_at) as hora,
            l.monto_bruto,
            l.total_gastos,
            l.total_propietario,
            l.canon,
            l.km_excedentes,
            l.cargo_km_excedentes,
            COALESCE(
                (SELECT mp.nombre 
                 FROM payment.transaccion t 
                 JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id 
                 WHERE t.viaje_id = vs.id LIMIT 1),
                'efectivo'
            ) as metodo_pago
        FROM trip.viaje_solicitado vs
        LEFT JOIN fleet.liquidacion l ON l.turno_id = vs.turno_id
        WHERE vs.vehiculo_id = :vehiculo_id
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            AND vs.estado IN ('finalizado', 'en_curso', 'aceptado')
        ORDER BY vs.created_at
    """)
    
    result = await db.execute(query, {
        "vehiculo_id": vehiculo_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta
    })
    rows = result.all()
    
    if not rows:
        return {
            "total_viajes": 0,
            "ingresos_brutos": 0,
            "costos_variables": 0,
            "comisiones_bancarias": 0,
            "porcentaje_taxip_total": 0,
            "costos_fijos": 0,
            "canon_taxip": 0,
            "utilidad_neta": 0,
            "margen": 0,
            "dias_periodo": (fecha_hasta - fecha_desde).days + 1,
            "viajes": []
        }
    
    total_viajes = 0
    total_ingresos = 0
    total_gastos = 0
    total_utilidad = 0
    total_canon = 0
    total_km_excedentes = 0
    
    viajes_detalle = []
    
    for row in rows:
        ingreso = float(row[7] or row[1] or 0)
        gastos = float(row[8] or 0)
        utilidad = float(row[9] or 0)
        canon = float(row[10] or 0)
        km_excedentes = float(row[11] or 0)
        cargo_km = float(row[12] or 0)
        created_at = row[4]
        estado = row[5]
        metodo_pago = row[13] or "efectivo"
        
        total_viajes += 1
        total_ingresos += ingreso
        total_gastos += gastos
        total_utilidad += utilidad
        total_canon += canon
        total_km_excedentes += km_excedentes
        
        viajes_detalle.append({
            "id": str(row[0]),
            "ingreso": round(ingreso, 2),
            "gastos": round(gastos, 2),
            "utilidad": round(utilidad, 2),
            "canon": round(canon, 2),
            "km_excedentes": round(km_excedentes, 2),
            "cargo_km": round(cargo_km, 2),
            "metodo_pago": metodo_pago,
            "estado": estado,
            "fecha": created_at,
            "fuente": "liquidacion" if row[7] else "estimado"
        })
    
    dias_periodo = (fecha_hasta - fecha_desde).days + 1
    
    margen = (total_utilidad / total_ingresos * 100) if total_ingresos > 0 else 0
    
    return {
        "total_viajes": total_viajes,
        "ingresos_brutos": round(total_ingresos, 2),
        "gastos_totales": round(total_gastos, 2),
        "utilidad_neta": round(total_utilidad, 2),
        "canon_total": round(total_canon, 2),
        "km_excedentes_total": round(total_km_excedentes, 2),
        "margen": round(margen, 2),
        "dias_periodo": dias_periodo,
        "viajes": viajes_detalle
    }


async def recalcular_tablas_rentabilidad(
    db: AsyncSession,
    vehiculo_id: UUID,
    mes: int,
    anio: int
) -> Dict[str, Any]:
    """
    Recalcula y actualiza las tablas de rentabilidad precomputadas
    """
    fecha_inicio = date(anio, mes, 1)
    if mes == 12:
        fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
    
    query_vehiculo = text("""
        SELECT control_base_id FROM fleet.vehiculo WHERE id = :vehiculo_id
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
    row = result.first()
    if not row:
        return {"error": "Vehículo no encontrado"}
    control_base_id = row[0]
    
    rentabilidad = await calcular_rentabilidad_periodo(
        db, vehiculo_id, fecha_inicio, fecha_fin, control_base_id
    )
    
    # Guardar en tabla mensual
    insert_mensual = text("""
        INSERT INTO rentabilidad.rentabilidad_mensual_vehiculo (
            vehiculo_id, anio, mes,
            total_viajes, ingresos_brutos,
            costos_variables, costos_fijos,
            utilidad_neta, margen,
            created_at, updated_at
        )
        VALUES (
            :vehiculo_id, :anio, :mes,
            :total_viajes, :ingresos_brutos,
            :costos_variables, :costos_fijos,
            :utilidad_neta, :margen,
            NOW(), NOW()
        )
        ON CONFLICT (vehiculo_id, anio, mes) DO UPDATE SET
            total_viajes = EXCLUDED.total_viajes,
            ingresos_brutos = EXCLUDED.ingresos_brutos,
            costos_variables = EXCLUDED.costos_variables,
            costos_fijos = EXCLUDED.costos_fijos,
            utilidad_neta = EXCLUDED.utilidad_neta,
            margen = EXCLUDED.margen,
            updated_at = NOW()
    """)
    
    await db.execute(insert_mensual, {
        "vehiculo_id": vehiculo_id,
        "anio": anio,
        "mes": mes,
        "total_viajes": rentabilidad["total_viajes"],
        "ingresos_brutos": rentabilidad["ingresos_brutos"],
        "costos_variables": rentabilidad.get("costos_variables", 0),
        "costos_fijos": rentabilidad.get("costos_fijos", 0),
        "utilidad_neta": rentabilidad["utilidad_neta"],
        "margen": rentabilidad["margen"]
    })
    
    await db.commit()
    
    return {
        "success": True,
        "mensaje": f"Rentabilidad recalculada para {fecha_inicio.strftime('%B %Y')}",
        "vehiculo_id": str(vehiculo_id),
        "mes": mes,
        "anio": anio
    }