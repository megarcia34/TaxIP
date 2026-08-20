"""
Optimización - Endpoints para análisis de optimización
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from uuid import UUID
from datetime import date, timedelta
import logging

from app.database import get_db
from app.dependencies import get_current_user, get_filtros_reporte
from app.services.optimizacion import (
    analizar_medios_pago,
    calcular_benchmarking
)
from app.services.rentabilidad import obtener_configuracion_tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/optimizacion", tags=["Optimización"])


# ============================================
# ANÁLISIS POR MEDIO DE PAGO
# ============================================

@router.get("/medios-pago")
async def get_analisis_medios_pago(
    vehiculo_id: Optional[UUID] = Query(None, description="Filtrar por vehículo"),
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    filtros: dict = Depends(get_filtros_reporte),
    db: AsyncSession = Depends(get_db)
):
    """
    Analiza el costo por medio de pago
    
    - Super Admin: Todos los medios de pago de todos los tenants
    - Admin Tenant: Todos los medios de pago de su tenant
    - Propietario: Medios de pago de sus vehículos
    """
    # Definir fechas
    hoy = date.today()
    
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Construir condiciones WHERE según rol
    condiciones = []
    params = {"fecha_desde": fecha_desde_obj, "fecha_hasta": fecha_hasta_obj}
    
    if not filtros["is_super_admin"]:
        if filtros["control_base_id"]:
            condiciones.append("vs.control_base_id = :control_base_id")
            params["control_base_id"] = filtros["control_base_id"]
    
    if filtros["is_propietario"] and filtros["propietario_id"]:
        condiciones.append("pv.propietario_id = :propietario_id")
        params["propietario_id"] = filtros["propietario_id"]
    
    if vehiculo_id:
        condiciones.append("vs.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    where_clause = " AND ".join(condiciones) if condiciones else "1=1"
    
    # ✅ CORREGIDO: JOIN con metodo_pago
    query = text(f"""
        SELECT 
            COALESCE(mp.nombre, 'efectivo') as medio_pago,
            COUNT(vs.id) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_ingresos,
            COALESCE(SUM(vs.precio_estimado), 0) as total_estimado
        FROM trip.viaje_solicitado vs
        LEFT JOIN payment.transaccion t ON t.viaje_id = vs.id
        LEFT JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE vs.estado = 'finalizado'
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            AND {where_clause}
        GROUP BY medio_pago
        ORDER BY total_ingresos DESC
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    # Obtener configuración del tenant para comisiones
    config = None
    if filtros["control_base_id"]:
        config = await obtener_configuracion_tenant(db, filtros["control_base_id"])
    
    total_ingresos = sum(float(r[2] or 0) for r in rows)
    
    medios = []
    for row in rows:
        medio = row[0]
        viajes = row[1] or 0
        ingresos = float(row[2] or 0)
        
        # Calcular comisión según medio
        comision_porcentaje = 0
        if config and medio == "qr":
            comision_porcentaje = config["comision_qr"] / 100
        elif config and medio == "debito":
            comision_porcentaje = config["comision_debito"] / 100
        elif config and medio == "credito":
            comision_porcentaje = config["comision_credito"] / 100
        
        costo_comisiones = ingresos * comision_porcentaje
        if config:
            costo_comisiones = costo_comisiones * (1 + config["iva"] / 100)
        
        medios.append({
            "medio_pago": medio,
            "total_viajes": viajes,
            "total_ingresos": round(ingresos, 2),
            "porcentaje_ingresos": round((ingresos / total_ingresos * 100), 2) if total_ingresos > 0 else 0,
            "comision_porcentaje": round(comision_porcentaje * 100, 2),
            "costo_comisiones": round(costo_comisiones, 2),
            "costo_porcentaje": round((costo_comisiones / ingresos * 100), 2) if ingresos > 0 else 0
        })
    
    return {
        "success": True,
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "total_ingresos": round(total_ingresos, 2),
        "total_comisiones": round(sum(m["costo_comisiones"] for m in medios), 2),
        "medios": medios
    }


# ============================================
# BENCHMARKING
# ============================================

@router.get("/benchmarking/{vehiculo_id}")
async def get_benchmarking(
    vehiculo_id: UUID,
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    filtros: dict = Depends(get_filtros_reporte),
    db: AsyncSession = Depends(get_db)
):
    """
    Compara el rendimiento de un vehículo vs la flota del tenant
    """
    hoy = date.today()
    
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # Verificar que el vehículo existe y pertenece al usuario
    query_vehiculo = text("""
        SELECT v.id, v.control_base_id, v.patente
        FROM fleet.vehiculo v
        WHERE v.id = :vehiculo_id AND v.activo = true
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    control_base_id = row[1]
    patente = row[2]
    
    # Validar permisos
    if not filtros["is_super_admin"] and not filtros["is_admin_tenant"]:
        if filtros["is_propietario"]:
            query_prop = text("""
                SELECT id FROM fleet.propietario_vehiculo
                WHERE vehiculo_id = :vehiculo_id 
                  AND propietario_id = :propietario_id 
                  AND activo = true
            """)
            prop_result = await db.execute(query_prop, {
                "vehiculo_id": vehiculo_id,
                "propietario_id": filtros["propietario_id"]
            })
            if not prop_result.first():
                raise HTTPException(status_code=403, detail="No tienes permiso para este vehículo")
        else:
            raise HTTPException(status_code=403, detail="No tienes permiso para este vehículo")
    
    # Calcular benchmarking
    resultado = await calcular_benchmarking(
        db, vehiculo_id, control_base_id, fecha_desde_obj, fecha_hasta_obj
    )
    
    return {
        "success": True,
        "vehiculo": {
            "id": str(vehiculo_id),
            "patente": patente
        },
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "resultado": resultado
    }


# ============================================
# RECOMENDACIONES DE OPTIMIZACIÓN
# ============================================

@router.get("/recomendaciones")
async def get_recomendaciones(
    vehiculo_id: Optional[UUID] = Query(None, description="Filtrar por vehículo"),
    filtros: dict = Depends(get_filtros_reporte),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera recomendaciones de optimización basadas en análisis de datos
    """
    recomendaciones = []
    
    # ✅ Usar objetos date
    hoy = date.today()
    fecha_desde = hoy - timedelta(days=30)
    fecha_hasta = hoy
    
    # 1. Análisis de medios de pago
    try:
        analisis_medios = await analizar_medios_pago(
            db, vehiculo_id, fecha_desde, fecha_hasta
        )
        
        for medio in analisis_medios.get("por_medio", []):
            if medio["medio_pago"] in ["qr", "debito", "credito"] and medio["total_ingresos"] > 0:
                recomendaciones.append({
                    "tipo": "medios_pago",
                    "prioridad": "media",
                    "titulo": f"Optimizar pagos con {medio['medio_pago'].upper()}",
                    "descripcion": f"Los pagos con {medio['medio_pago']} representan {medio['porcentaje']}% de los ingresos. Considera incentivar el pago en efectivo o transferencia.",
                    "accion_sugerida": "Implementar descuentos por pago en efectivo o transferencia bancaria",
                    "impacto_estimado": "Reducción de comisiones bancarias hasta un 50%"
                })
    except Exception as e:
        logger.warning(f"Error en análisis de medios de pago: {e}")
    
    # 2. Costos de combustible
    if filtros.get("control_base_id"):
        try:
            config = await obtener_configuracion_tenant(db, filtros["control_base_id"])
            
            # ✅ CORREGIDO: usar objetos date
            query_combustible = text("""
                SELECT COALESCE(SUM(monto), 0) as total_combustible
                FROM fleet.gasto_vehiculo
                WHERE tipo_gasto = 'combustible'
                  AND fecha_gasto::date BETWEEN :fecha_desde AND :fecha_hasta
            """)
            result = await db.execute(query_combustible, {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            })
            total_combustible = float(result.scalar() or 0)
            
            if total_combustible > 0:
                recomendaciones.append({
                    "tipo": "gastos",
                    "prioridad": "alta",
                    "titulo": "Optimizar costos de combustible",
                    "descripcion": f"El combustible representa una parte significativa de los gastos (${total_combustible:,.0f} en el último mes). Considera optimizar rutas y monitorear consumo.",
                    "accion_sugerida": "Implementar sistema de monitoreo de consumo y optimización de rutas",
                    "impacto_estimado": "Reducción de costos de combustible hasta 15%"
                })
        except Exception as e:
            logger.warning(f"Error en análisis de gastos: {e}")
    
    # 3. Volumen de viajes
    if vehiculo_id:
        try:
            query_viajes = text("""
                SELECT COUNT(*) as total_viajes
                FROM trip.viaje_solicitado
                WHERE vehiculo_id = :vehiculo_id
                  AND estado = 'finalizado'
                  AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            """)
            result = await db.execute(query_viajes, {
                "vehiculo_id": vehiculo_id,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            })
            total_viajes = result.scalar() or 0
            
            if total_viajes == 0:
                recomendaciones.append({
                    "tipo": "volumen",
                    "prioridad": "alta",
                    "titulo": "Aumentar volumen de viajes",
                    "descripcion": "El vehículo no ha realizado viajes en el último mes. El promedio de la flota es superior.",
                    "accion_sugerida": "Implementar campañas de promoción y mejorar tiempos de respuesta",
                    "impacto_estimado": "Incremento de ingresos a partir de $1,500 por viaje"
                })
            elif total_viajes < 100:
                recomendaciones.append({
                    "tipo": "volumen",
                    "prioridad": "media",
                    "titulo": f"Aumentar volumen de viajes ({total_viajes} viajes/mes)",
                    "descripcion": f"El vehículo realizó {total_viajes} viajes en el último mes. El promedio de la flota es superior.",
                    "accion_sugerida": "Implementar campañas de promoción y mejorar tiempos de respuesta",
                    "impacto_estimado": "Incremento de ingresos hasta 30%"
                })
        except Exception as e:
            logger.warning(f"Error en análisis de volumen: {e}")
    
    # 4. Margen de rentabilidad
    if vehiculo_id and filtros.get("control_base_id"):
        try:
            resultado = await calcular_benchmarking(
                db, vehiculo_id, filtros["control_base_id"], fecha_desde, fecha_hasta
            )
            
            if resultado.get("comparacion") == "inferior" and resultado.get("vehiculo", {}).get("viajes", 0) > 0:
                recomendaciones.append({
                    "tipo": "rentabilidad",
                    "prioridad": "alta",
                    "titulo": "Mejorar rentabilidad del vehículo",
                    "descripcion": f"El vehículo está por debajo del promedio de la flota. {resultado.get('mensaje', '')}",
                    "accion_sugerida": "Revisar costos operativos y estrategias de precios",
                    "impacto_estimado": "Alinear rentabilidad con el promedio de la flota"
                })
        except Exception as e:
            logger.warning(f"Error en análisis de benchmarking: {e}")
    
    # Ordenar por prioridad
    prioridad_orden = {"alta": 0, "media": 1, "baja": 2}
    recomendaciones.sort(key=lambda x: prioridad_orden.get(x.get("prioridad", "baja"), 2))
    
    return {
        "success": True,
        "total_recomendaciones": len(recomendaciones),
        "recomendaciones": recomendaciones
    }