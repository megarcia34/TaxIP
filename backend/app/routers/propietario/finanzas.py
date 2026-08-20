from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, date

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.routers.propietario.utils import verificar_vehiculo_propietario

router = APIRouter()


# ============================================================
# ENDPOINTS EXISTENTES (se mantienen igual)
# ============================================================

@router.get("/rentabilidad")
async def obtener_rentabilidad(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    vehiculo_id: Optional[UUID] = None,
    periodo: str = Query("mes", pattern="^(dia|semana|mes|ano)$"),
):
    hoy = datetime.now().date()
    if periodo == "dia":
        fecha_desde = hoy
    elif periodo == "semana":
        fecha_desde = hoy - timedelta(days=7)
    elif periodo == "ano":
        fecha_desde = hoy - timedelta(days=365)
    else:
        fecha_desde = hoy - timedelta(days=30)
    
    query_vehiculos = text("""
        SELECT DISTINCT v.id, v.patente
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id AND v.activo = true
    """)
    result = await db.execute(query_vehiculos, {"propietario_id": propietario_id})
    vehiculos = result.all()
    
    resultados = []
    for vehiculo in vehiculos:
        vid = vehiculo[0]
        patente = vehiculo[1]
        
        query_ingresos = text("""
            SELECT COALESCE(SUM(v.precio_final), 0)
            FROM trip.viaje_solicitado v
            WHERE v.vehiculo_id = :vehiculo_id AND v.estado = 'finalizado'
              AND v.created_at::date BETWEEN :desde AND :hasta
        """)
        result_ing = await db.execute(query_ingresos, {"vehiculo_id": vid, "desde": fecha_desde, "hasta": hoy})
        ingresos = float(result_ing.scalar() or 0)
        
        query_gastos = text("""
            SELECT COALESCE(SUM(g.monto), 0)
            FROM fleet.gasto_vehiculo g
            WHERE g.vehiculo_id = :vehiculo_id AND g.fecha_gasto BETWEEN :desde AND :hasta
        """)
        result_gast = await db.execute(query_gastos, {"vehiculo_id": vid, "desde": fecha_desde, "hasta": hoy})
        gastos = float(result_gast.scalar() or 0)
        
        query_canones = text("""
            SELECT COALESCE(SUM(t.monto), 0)
            FROM payment.transaccion t
            WHERE t.tipo = 'canon' AND t.created_at::date BETWEEN :desde AND :hasta
              AND t.id IN (
                  SELECT t2.id FROM payment.transaccion t2
                  JOIN fleet.contrato_vehiculo c ON c.id = t2.id
                  WHERE c.vehiculo_id = :vehiculo_id
              )
        """)
        result_can = await db.execute(query_canones, {"vehiculo_id": vid, "desde": fecha_desde, "hasta": hoy})
        canones = float(result_can.scalar() or 0)
        
        total_ingresos = ingresos + canones
        ganancia_neta = total_ingresos - gastos
        
        resultados.append({
            "vehiculo_id": str(vid),
            "patente": patente,
            "ingresos": round(ingresos, 2),
            "gastos": round(gastos, 2),
            "canones_recibidos": round(canones, 2),
            "total_ingresos": round(total_ingresos, 2),
            "ganancia_neta": round(ganancia_neta, 2),
            "margen": round((ganancia_neta / total_ingresos * 100) if total_ingresos > 0 else 0, 2)
        })
    
    resultados.sort(key=lambda x: x["ganancia_neta"], reverse=True)
    
    return {
        "periodo": periodo,
        "desde": fecha_desde.isoformat(),
        "hasta": hoy.isoformat(),
        "vehiculos": resultados,
        "resumen_total": {
            "total_ingresos": sum(v["total_ingresos"] for v in resultados),
            "total_gastos": sum(v["gastos"] for v in resultados),
            "total_ganancia_neta": sum(v["ganancia_neta"] for v in resultados),
            "promedio_margen": round(sum(v["margen"] for v in resultados) / len(resultados) if resultados else 0, 2)
        }
    }


@router.get("/resumen-financiero")
async def resumen_financiero(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("mes", pattern="^(dia|semana|mes|ano)$"),
):
    hoy = datetime.now().date()
    if periodo == "dia":
        fecha_desde = hoy
    elif periodo == "semana":
        fecha_desde = hoy - timedelta(days=7)
    elif periodo == "ano":
        fecha_desde = hoy - timedelta(days=365)
    else:
        fecha_desde = hoy - timedelta(days=30)
    
    query_ingresos = text("""
        SELECT COALESCE(SUM(v.precio_final), 0) + COALESCE((
            SELECT SUM(t.monto) FROM payment.transaccion t
            WHERE t.tipo = 'canon' AND t.created_at::date BETWEEN :desde AND :hasta
        ), 0)
        FROM trip.viaje_solicitado v
        WHERE v.estado = 'finalizado' AND v.created_at::date BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_ingresos, {"desde": fecha_desde, "hasta": hoy})
    total_ingresos = float(result.scalar() or 0)
    
    query_gastos = text("""
        SELECT COALESCE(SUM(g.monto), 0)
        FROM fleet.gasto_vehiculo g
        WHERE g.fecha_gasto BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_gastos, {"desde": fecha_desde, "hasta": hoy})
    total_gastos = float(result.scalar() or 0)
    
    query_electronico = text("""
        SELECT COALESCE(SUM(v.precio_final), 0)
        FROM trip.viaje_solicitado v
        WHERE v.estado = 'finalizado' AND v.created_at::date BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_electronico, {"desde": fecha_desde, "hasta": hoy})
    electronico = float(result.scalar() or 0)
    
    query_manual = text("""
        SELECT COALESCE(SUM(t.monto), 0)
        FROM payment.transaccion t
        WHERE t.tipo IN ('recaudacion_manual', 'canon')
          AND t.created_at::date BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_manual, {"desde": fecha_desde, "hasta": hoy})
    manual = float(result.scalar() or 0)
    
    query_vehiculos = text("""
        SELECT COUNT(DISTINCT v.id)
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id AND v.activo = true
    """)
    result = await db.execute(query_vehiculos, {"propietario_id": propietario_id})
    total_vehiculos = result.scalar() or 0
    
    return {
        "periodo": periodo,
        "desde": fecha_desde.isoformat(),
        "hasta": hoy.isoformat(),
        "kpis": {
            "total_ingresos": round(total_ingresos, 2),
            "total_gastos": round(total_gastos, 2),
            "ganancia_neta": round(total_ingresos - total_gastos, 2),
            "margen": round(((total_ingresos - total_gastos) / total_ingresos * 100) if total_ingresos > 0 else 0, 2),
            "total_vehiculos": total_vehiculos,
            "ingreso_promedio_por_vehiculo": round(total_ingresos / total_vehiculos, 2) if total_vehiculos > 0 else 0
        },
        "flujo": {
            "electronico": round(electronico, 2),
            "manual": round(manual, 2),
            "porcentaje_electronico": round((electronico / total_ingresos * 100) if total_ingresos > 0 else 0, 2),
            "porcentaje_manual": round((manual / total_ingresos * 100) if total_ingresos > 0 else 0, 2)
        }
    }


@router.get("/flujo-efectivo")
async def flujo_efectivo(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    meses: int = Query(6, ge=1, le=24, description="Número de meses a mostrar"),
):
    """
    Flujo de efectivo mensual usando liquidaciones (D9).
    """
    query = text("""
        SELECT 
            DATE_TRUNC('month', l.calculada_en) as mes,
            COALESCE(SUM(l.total_propietario), 0) as utilidad,
            COALESCE(SUM(l.monto_bruto), 0) as ingresos_brutos,
            COALESCE(SUM(l.total_gastos), 0) as gastos_totales
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en >= NOW() - INTERVAL ':meses months'
        GROUP BY DATE_TRUNC('month', l.calculada_en)
        ORDER BY mes ASC
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "meses": meses
    })
    rows = result.all()
    
    labels = []
    utilidad = []
    ingresos = []
    gastos = []
    
    for row in rows:
        labels.append(row[0].strftime("%b %Y") if row[0] else "")
        utilidad.append(float(row[1] or 0))
        ingresos.append(float(row[2] or 0))
        gastos.append(float(row[3] or 0))
    
    return {
        "labels": labels,
        "utilidad": utilidad,
        "ingresos": ingresos,
        "gastos": gastos,
        "totales": {
            "total_utilidad": sum(utilidad),
            "total_ingresos": sum(ingresos),
            "total_gastos": sum(gastos)
        }
    }


# ============================================================
# CORREGIDO: DEUDA CHOFERES (CANON_FIJO → ALQUILER)
# ============================================================

@router.get("/deuda-choferes")
async def deuda_choferes(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = text("""
        SELECT 
            u.id as chofer_id,
            u.email,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            c.id as contrato_id,
            v.patente,
            c.monto_diario,
            c.fecha_inicio,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) as dias_deuda,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) * c.monto_diario as deuda_estimada
        FROM fleet.contrato_vehiculo c
        JOIN auth.usuario u ON u.id = c.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        WHERE c.propietario_id = :propietario_id
          AND c.tipo_contrato = 'ALQUILER'
          AND c.activo = true
          AND c.fecha_fin IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM payment.transaccion t
              WHERE t.tipo = 'canon'
                AND t.created_at::date >= c.fecha_inicio::date
          )
        ORDER BY deuda_estimada DESC
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    rows = result.all()
    
    return [
        {
            "chofer_id": str(row[0]),
            "email": row[1],
            "chofer_nombre": row[2],
            "contrato_id": str(row[3]),
            "patente": row[4],
            "monto_diario": float(row[5]),
            "fecha_inicio": row[6].isoformat() if row[6] else None,
            "dias_deuda": int(row[7] or 0),
            "deuda_estimada": round(float(row[8] or 0), 2)
        }
        for row in rows
    ]


# ============================================================
# NUEVOS ENDPOINTS
# ============================================================

@router.get("/costo-por-viaje/{vehiculo_id}")
async def costo_por_viaje(
    vehiculo_id: UUID,
    desde: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=200, description="Límite de registros"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Desglose detallado de costo y ganancia por cada viaje.
    """
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    hoy = datetime.now().date()
    if not desde:
        desde = hoy - timedelta(days=30)
    if not hasta:
        hasta = hoy
    
    query_config = text("""
        SELECT 
            costo_combustible_por_km,
            costo_mantenimiento_por_dia,
            costo_seguro_por_dia,
            costo_impuesto_por_dia,
            depreciacion_vehiculo_por_dia
        FROM tenant.configuracion_tenant
        WHERE control_base_id = (
            SELECT control_base_id FROM fleet.vehiculo WHERE id = :vehiculo_id
        )
    """)
    result = await db.execute(query_config, {"vehiculo_id": vehiculo_id})
    config = result.first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuración de costos no encontrada")
    
    costo_combustible_por_km = float(config[0] or 0)
    costo_mantenimiento_por_dia = float(config[1] or 0)
    costo_seguro_por_dia = float(config[2] or 0)
    costo_impuesto_por_dia = float(config[3] or 0)
    depreciacion_por_dia = float(config[4] or 0)
    
    query_viajes = text("""
        SELECT 
            vs.id,
            vs.created_at as fecha,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.distancia_metros / 1000 as distancia_km,
            vs.tiempo_estimado_segundos / 60 as duracion_minutos,
            vs.precio_final as ingreso_bruto,
            COALESCE(vs.comision_plataforma, 0) as comision,
            vs.precio_final - COALESCE(vs.comision_plataforma, 0) as ingreso_neto,
            vs.estado
        FROM trip.viaje_solicitado vs
        WHERE vs.vehiculo_id = :vehiculo_id
          AND vs.estado = 'finalizado'
          AND vs.created_at::date BETWEEN :desde AND :hasta
        ORDER BY vs.created_at DESC
        LIMIT :limit
    """)
    result = await db.execute(query_viajes, {
        "vehiculo_id": vehiculo_id,
        "desde": desde,
        "hasta": hasta,
        "limit": limit
    })
    rows = result.all()
    
    resultados = []
    for row in rows:
        distancia_km = float(row[4] or 0)
        duracion_minutos = float(row[5] or 0)
        ingreso_bruto = float(row[6] or 0)
        comision = float(row[7] or 0)
        ingreso_neto = float(row[8] or 0)
        
        costo_combustible = distancia_km * costo_combustible_por_km
        costo_mantenimiento = (duracion_minutos / 60) * costo_mantenimiento_por_dia
        costo_seguro = (duracion_minutos / 60) * costo_seguro_por_dia
        costo_impuesto = (duracion_minutos / 60) * costo_impuesto_por_dia
        costo_depreciacion = (duracion_minutos / 60) * depreciacion_por_dia
        costo_total = costo_combustible + costo_mantenimiento + costo_seguro + costo_impuesto + costo_depreciacion
        
        ganancia_neta = ingreso_neto - costo_total
        margen = (ganancia_neta / ingreso_neto * 100) if ingreso_neto > 0 else 0
        
        resultados.append({
            "viaje_id": str(row[0]),
            "fecha": row[1].isoformat() if row[1] else None,
            "origen": row[2],
            "destino": row[3],
            "distancia_km": round(distancia_km, 2),
            "duracion_minutos": round(duracion_minutos, 2),
            "ingreso_bruto": round(ingreso_bruto, 2),
            "comision": round(comision, 2),
            "ingreso_neto": round(ingreso_neto, 2),
            "costos": {
                "combustible": round(costo_combustible, 2),
                "mantenimiento": round(costo_mantenimiento, 2),
                "seguro": round(costo_seguro, 2),
                "impuesto": round(costo_impuesto, 2),
                "depreciacion": round(costo_depreciacion, 2),
                "total": round(costo_total, 2)
            },
            "ganancia_neta": round(ganancia_neta, 2),
            "margen": round(margen, 2),
            "estado": row[9]
        })
    
    total_ingresos = sum(r["ingreso_bruto"] for r in resultados)
    total_comisiones = sum(r["comision"] for r in resultados)
    total_costos = sum(r["costos"]["total"] for r in resultados)
    total_ganancia = sum(r["ganancia_neta"] for r in resultados)
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "periodo": {
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat()
        },
        "configuracion_costos": {
            "combustible_por_km": round(costo_combustible_por_km, 2),
            "mantenimiento_por_dia": round(costo_mantenimiento_por_dia, 2),
            "seguro_por_dia": round(costo_seguro_por_dia, 2),
            "impuesto_por_dia": round(costo_impuesto_por_dia, 2),
            "depreciacion_por_dia": round(depreciacion_por_dia, 2)
        },
        "viajes": resultados,
        "resumen": {
            "total_viajes": len(resultados),
            "total_ingresos_brutos": round(total_ingresos, 2),
            "total_comisiones": round(total_comisiones, 2),
            "total_ingresos_netos": round(total_ingresos - total_comisiones, 2),
            "total_costos": round(total_costos, 2),
            "total_ganancia_neta": round(total_ganancia, 2),
            "ganancia_promedio_por_viaje": round(total_ganancia / len(resultados), 2) if resultados else 0,
            "margen_promedio": round(sum(r["margen"] for r in resultados) / len(resultados), 2) if resultados else 0
        }
    }


@router.get("/rentabilidad-por-zona/{vehiculo_id}")
async def rentabilidad_por_zona(
    vehiculo_id: UUID,
    desde: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Análisis de rentabilidad agrupado por zona geográfica.
    """
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    hoy = datetime.now().date()
    if not desde:
        desde = hoy - timedelta(days=30)
    if not hasta:
        hasta = hoy
    
    query = text("""
        WITH viajes_con_zonas AS (
            SELECT 
                vs.id,
                vs.precio_final,
                vs.comision_plataforma,
                vs.distancia_metros / 1000 as distancia_km,
                vs.created_at,
                SPLIT_PART(vs.direccion_origen, ',', 1) as zona_origen,
                SPLIT_PART(vs.direccion_destino, ',', 1) as zona_destino
            FROM trip.viaje_solicitado vs
            WHERE vs.vehiculo_id = :vehiculo_id
              AND vs.estado = 'finalizado'
              AND vs.created_at::date BETWEEN :desde AND :hasta
        ),
        costos_por_viaje AS (
            SELECT 
                v.id,
                v.precio_final,
                v.comision_plataforma,
                v.distancia_km,
                v.zona_origen,
                v.zona_destino,
                COALESCE(c.costo_combustible_por_km, 0) * v.distancia_km as costo_combustible,
                COALESCE(c.costo_mantenimiento_por_dia, 0) * 0.1 as costo_mantenimiento_estimado,
                COALESCE(c.costo_seguro_por_dia, 0) * 0.1 as costo_seguro_estimado
            FROM viajes_con_zonas v
            CROSS JOIN tenant.configuracion_tenant c
            WHERE c.control_base_id = (
                SELECT control_base_id FROM fleet.vehiculo WHERE id = :vehiculo_id
            )
        )
        SELECT 
            zona_origen as zona,
            COUNT(*) as total_viajes,
            SUM(precio_final) as ingresos_brutos,
            SUM(comision_plataforma) as comisiones,
            SUM(precio_final - comision_plataforma) as ingresos_netos,
            SUM(costo_combustible + costo_mantenimiento_estimado + costo_seguro_estimado) as costos_totales,
            SUM(precio_final - comision_plataforma - costo_combustible - costo_mantenimiento_estimado - costo_seguro_estimado) as ganancia_neta,
            AVG(distancia_km) as distancia_promedio
        FROM costos_por_viaje
        WHERE zona_origen IS NOT NULL AND zona_origen != ''
        GROUP BY zona_origen
        ORDER BY ganancia_neta DESC
    """)
    result = await db.execute(query, {
        "vehiculo_id": vehiculo_id,
        "desde": desde,
        "hasta": hasta
    })
    rows = result.all()
    
    resultados = []
    total_ganancia = 0
    for row in rows:
        ganancia = float(row[6] or 0)
        total_ganancia += ganancia
        resultados.append({
            "zona": row[0],
            "total_viajes": int(row[1] or 0),
            "ingresos_brutos": round(float(row[2] or 0), 2),
            "comisiones": round(float(row[3] or 0), 2),
            "ingresos_netos": round(float(row[4] or 0), 2),
            "costos_totales": round(float(row[5] or 0), 2),
            "ganancia_neta": round(ganancia, 2),
            "distancia_promedio": round(float(row[7] or 0), 2),
            "margen": round((ganancia / float(row[4] or 1) * 100) if float(row[4] or 0) > 0 else 0, 2)
        })
    
    for r in resultados:
        r["porcentaje_contribucion"] = round((r["ganancia_neta"] / total_ganancia * 100) if total_ganancia > 0 else 0, 2)
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "periodo": {
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat()
        },
        "zonas": resultados,
        "resumen": {
            "total_zonas": len(resultados),
            "total_viajes": sum(r["total_viajes"] for r in resultados),
            "total_ganancia": round(total_ganancia, 2),
            "zona_mas_rentable": resultados[0]["zona"] if resultados else None,
            "zona_menos_rentable": resultados[-1]["zona"] if resultados else None
        }
    }