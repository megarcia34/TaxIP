"""
Super Admin Maestro - Dashboard Global
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import date, timedelta

from app.database import get_db
from app.dependencies import get_current_super_admin_user

router = APIRouter(prefix="/api/super-admin/dashboard", tags=["Super Admin"])


@router.get("/global")
async def get_dashboard_global(
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$", description="dia, semana, mes"),
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_current_super_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dashboard global para Super Admin Maestro
    """
    
    # Definir fechas
    hoy = date.today()
    
    if not fecha_desde and not fecha_hasta:
        if periodo == "dia":
            fecha_desde = hoy.isoformat()
            fecha_hasta = hoy.isoformat()
        elif periodo == "semana":
            fecha_desde = (hoy - timedelta(days=7)).isoformat()
            fecha_hasta = hoy.isoformat()
        else:  # mes
            fecha_desde = (hoy - timedelta(days=30)).isoformat()
            fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    # ============================================
    # 1. RESUMEN GLOBAL
    # ============================================
    query_global = text("""
        SELECT 
            (SELECT COUNT(*) FROM tenant.control_base WHERE activo = true) as total_tenants,
            (SELECT COUNT(*) FROM fleet.vehiculo WHERE activo = true) as total_vehiculos,
            COALESCE((
                SELECT COUNT(*) 
                FROM trip.viaje_solicitado 
                WHERE estado = 'finalizado'
                  AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            ), 0) as total_viajes,
            COALESCE((
                SELECT COALESCE(SUM(precio_final), 0) 
                FROM trip.viaje_solicitado 
                WHERE estado = 'finalizado'
                  AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            ), 0) as total_recaudacion
    """)
    
    result_global = await db.execute(query_global, {
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    row_global = result_global.first()
    
    # ============================================
    # 2. DESGLOSE POR TENANT (CORREGIDO)
    # ============================================
    query_tenants = text("""
        SELECT 
            cb.id as tenant_id,
            cb.nombre as tenant_nombre,
            COUNT(DISTINCT v.id) as total_vehiculos,
            COALESCE(COUNT(vs.id), 0) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_recaudacion,
            COALESCE(AVG(vs.precio_final), 0) as promedio_por_viaje,
            COALESCE(SUM(g.monto), 0) as total_gastos
        FROM tenant.control_base cb
        LEFT JOIN fleet.vehiculo v ON v.control_base_id = cb.id AND v.activo = true
        LEFT JOIN trip.viaje_solicitado vs ON vs.vehiculo_id = v.id 
            AND vs.estado = 'finalizado'
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
        LEFT JOIN fleet.gasto_vehiculo g ON g.vehiculo_id = v.id 
            AND g.fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
        WHERE cb.activo = true
        GROUP BY cb.id, cb.nombre
        ORDER BY total_recaudacion DESC
    """)
    
    result_tenants = await db.execute(query_tenants, {
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    tenants = result_tenants.all()
    
    # ============================================
    # 3. MEDIOS DE PAGO (TODOS, INCLUSO CON CERO VIAJES)
    # ============================================
    query_medios = text("""
        WITH medios_base AS (
            SELECT unnest(ARRAY['efectivo', 'transferencia', 'qr', 'debito', 'credito']) as medio_pago
        )
        SELECT 
            mb.medio_pago,
            COALESCE(COUNT(vs.id), 0) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_ingresos
        FROM medios_base mb
        LEFT JOIN trip.viaje_solicitado vs ON 
            COALESCE(
                (SELECT mp.nombre 
                 FROM payment.transaccion t 
                 JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id 
                 WHERE t.viaje_id = vs.id 
                 LIMIT 1), 
                'efectivo'
            ) = mb.medio_pago
            AND vs.estado = 'finalizado'
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
        GROUP BY mb.medio_pago
        ORDER BY total_ingresos DESC
    """)
    
    result_medios = await db.execute(query_medios, {
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    medios = result_medios.all()
    
    total_ingresos_medios = sum(float(m[2] or 0) for m in medios)
    
    # ============================================
    # 4. GASTOS OPERATIVOS
    # ============================================
    query_gastos = text("""
        SELECT 
            tipo_gasto,
            COALESCE(SUM(monto), 0) as total
        FROM fleet.gasto_vehiculo
        WHERE fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
        GROUP BY tipo_gasto
        ORDER BY total DESC
    """)
    
    result_gastos = await db.execute(query_gastos, {
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    gastos = result_gastos.all()
    
    # ============================================
    # 5. EVOLUCIÓN MENSUAL (últimos 6 meses)
    # ============================================
    query_evolucion = text("""
        SELECT 
            TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') as mes,
            COUNT(*) as total_viajes,
            COALESCE(SUM(precio_final), 0) as total_recaudacion
        FROM trip.viaje_solicitado
        WHERE estado = 'finalizado'
          AND created_at >= NOW() - INTERVAL '6 months'
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY mes ASC
    """)
    
    result_evolucion = await db.execute(query_evolucion)
    evolucion = result_evolucion.all()
    
    # ============================================
    # 6. CALCULAR CRECIMIENTO
    # ============================================
    crecimiento = 0
    if len(evolucion) >= 2:
        mes_actual = float(evolucion[-1][2] or 0)
        mes_anterior = float(evolucion[-2][2] or 0)
        if mes_anterior > 0:
            crecimiento = ((mes_actual - mes_anterior) / mes_anterior) * 100
    
    # ============================================
    # 7. RESPONDER
    # ============================================
    
    return {
        "success": True,
        "periodo": {
            "tipo": periodo,
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "resumen_global": {
            "total_tenants": row_global[0] or 0,
            "total_vehiculos": row_global[1] or 0,
            "total_viajes": row_global[2] or 0,
            "total_recaudacion": round(float(row_global[3] or 0), 2),
            "crecimiento": round(crecimiento, 2)
        },
        "tenants": [
            {
                "tenant_id": str(t[0]),
                "tenant_nombre": t[1],
                "total_vehiculos": t[2] or 0,
                "total_viajes": t[3] or 0,
                "total_recaudacion": round(float(t[4] or 0), 2),
                "promedio_por_viaje": round(float(t[5] or 0), 2),
                "total_gastos": round(float(t[6] or 0), 2),
                "utilidad_neta": round(float(t[4] or 0) - float(t[6] or 0), 2),
                "margen": round(
                    ((float(t[4] or 0) - float(t[6] or 0)) / float(t[4] or 0) * 100) 
                    if float(t[4] or 0) > 0 else 0, 
                    2
                )
            }
            for t in tenants
        ],
        "medios_pago": [
            {
                "medio_pago": m[0],
                "total_viajes": m[1] or 0,
                "total_ingresos": round(float(m[2] or 0), 2),
                "porcentaje": round(
                    (float(m[2] or 0) / total_ingresos_medios * 100) 
                    if total_ingresos_medios > 0 else 0, 
                    2
                )
            }
            for m in medios
        ],
        "gastos_operativos": [
            {
                "tipo_gasto": g[0] or "otros",
                "total": round(float(g[1] or 0), 2)
            }
            for g in gastos
        ],
        "evolucion_mensual": [
            {
                "mes": e[0],
                "total_viajes": e[1] or 0,
                "total_recaudacion": round(float(e[2] or 0), 2)
            }
            for e in evolucion
        ]
    }