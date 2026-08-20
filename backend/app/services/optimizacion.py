"""
Servicios de Optimización y Análisis
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID


async def analizar_medios_pago(
    db: AsyncSession,
    vehiculo_id: Optional[UUID],
    fecha_desde: date,
    fecha_hasta: date
) -> Dict[str, Any]:
    """
    Analiza el costo por medio de pago
    """
    params = {"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta}
    
    query_where = """
        WHERE vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
    """
    
    if vehiculo_id:
        query_where += " AND vs.vehiculo_id = :vehiculo_id"
        params["vehiculo_id"] = vehiculo_id
    
    # ✅ CORREGIDO: JOIN con metodo_pago
    query = text(f"""
        SELECT 
            COALESCE(mp.nombre, 'efectivo') as medio_pago,
            COUNT(vs.id) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_ingresos
        FROM trip.viaje_solicitado vs
        LEFT JOIN payment.transaccion t ON t.viaje_id = vs.id
        LEFT JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id
        {query_where}
            AND vs.estado = 'finalizado'
        GROUP BY medio_pago
        ORDER BY total_ingresos DESC
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    total_ingresos = sum(float(r[2] or 0) for r in rows)
    
    return {
        "total_ingresos": round(total_ingresos, 2),
        "por_medio": [
            {
                "medio_pago": row[0],
                "total_viajes": row[1] or 0,
                "total_ingresos": round(float(row[2] or 0), 2),
                "porcentaje": round((float(row[2] or 0) / total_ingresos * 100), 2) if total_ingresos > 0 else 0
            }
            for row in rows
        ]
    }


async def calcular_benchmarking(
    db: AsyncSession,
    vehiculo_id: UUID,
    control_base_id: UUID,
    fecha_desde: date,
    fecha_hasta: date
) -> Dict[str, Any]:
    """
    Calcula el benchmarking del vehículo vs la flota del tenant
    """
    # Rentabilidad del vehículo
    from app.services.rentabilidad import calcular_rentabilidad_periodo
    rentabilidad_vehiculo = await calcular_rentabilidad_periodo(
        db, vehiculo_id, fecha_desde, fecha_hasta, control_base_id
    )
    
    # Promedios de la flota
    query_flota = text("""
        SELECT 
            AVG(vs.precio_final) as avg_ingreso,
            COUNT(vs.id) as total_viajes,
            AVG(vs.distancia_metros) as avg_distancia
        FROM trip.viaje_solicitado vs
        WHERE vs.control_base_id = :control_base_id
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            AND vs.estado = 'finalizado'
    """)
    
    result = await db.execute(query_flota, {
        "control_base_id": control_base_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta
    })
    row = result.first()
    
    avg_ingreso = float(row[0] or 0)
    total_viajes_flota = int(row[1] or 0)
    avg_distancia = float(row[2] or 0) / 1000
    
    ingreso_vehiculo = rentabilidad_vehiculo["ingresos_brutos"]
    total_viajes_vehiculo = rentabilidad_vehiculo["total_viajes"]
    
    # Determinar comparación
    if ingreso_vehiculo > avg_ingreso * total_viajes_vehiculo:
        comparacion = "superior"
        mensaje = "Este vehículo está por encima del promedio en ingresos"
    elif ingreso_vehiculo < avg_ingreso * total_viajes_vehiculo:
        comparacion = "inferior"
        mensaje = "Este vehículo está por debajo del promedio en ingresos"
    else:
        comparacion = "similar"
        mensaje = "Este vehículo está en el promedio de ingresos"
    
    return {
        "vehiculo": {
            "ingresos": round(ingreso_vehiculo, 2),
            "viajes": total_viajes_vehiculo,
            "promedio_por_viaje": round(ingreso_vehiculo / total_viajes_vehiculo, 2) if total_viajes_vehiculo > 0 else 0
        },
        "flota": {
            "promedio_ingresos": round(avg_ingreso, 2),
            "total_viajes": total_viajes_flota,
            "promedio_por_viaje": round(avg_ingreso, 2) if avg_ingreso > 0 else 0,
            "promedio_distancia_km": round(avg_distancia, 2)
        },
        "comparacion": comparacion,
        "mensaje": mensaje
    }