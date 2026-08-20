# app/routers/propietario/reportes.py
"""
Reportes y finanzas para propietarios - D9 (Refactorizado con liquidacion)
Todos los reportes consumen la tabla liquidacion
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, date, timedelta
import csv
import io
from openpyxl import Workbook

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.routers.propietario.utils import verificar_vehiculo_propietario

router = APIRouter()


# ============================================================
# ENDPOINTS EXISTENTES (SE MANTIENEN PARA COMPATIBILIDAD)
# ============================================================

@router.get("/reportes/gastos/csv")
async def exportar_gastos_csv(
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    vehiculo_id: Optional[UUID] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Exportar gastos a CSV"""
    query = text("""
        SELECT 
            g.fecha_gasto as fecha,
            v.patente as vehiculo,
            g.tipo_gasto as categoria,
            g.monto as monto,
            g.descripcion as descripcion,
            g.km_registro as km
        FROM fleet.gasto_vehiculo g
        JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
        WHERE g.propietario_id = :propietario_id
    """)
    params = {"propietario_id": propietario_id}
    
    if desde:
        query = text(query.text + " AND g.fecha_gasto >= :desde")
        params["desde"] = desde
    if hasta:
        query = text(query.text + " AND g.fecha_gasto <= :hasta")
        params["hasta"] = hasta
    if vehiculo_id:
        query = text(query.text + " AND g.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    query = text(query.text + " ORDER BY g.fecha_gasto DESC")
    
    result = await db.execute(query, params)
    rows = result.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Vehículo", "Categoría", "Monto", "Descripción", "Kilometraje"])
    
    for row in rows:
        writer.writerow([
            row[0].strftime("%d/%m/%Y") if row[0] else "",
            row[1] or "",
            row[2] or "",
            f"{row[3]:.2f}" if row[3] else "0.00",
            row[4] or "",
            row[5] or ""
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=gastos_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/reportes/gastos/excel")
async def exportar_gastos_excel(
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    vehiculo_id: Optional[UUID] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Exportar gastos a Excel"""
    query = text("""
        SELECT 
            g.fecha_gasto as fecha,
            v.patente as vehiculo,
            g.tipo_gasto as categoria,
            g.monto as monto,
            g.descripcion as descripcion,
            g.km_registro as km
        FROM fleet.gasto_vehiculo g
        JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
        WHERE g.propietario_id = :propietario_id
    """)
    params = {"propietario_id": propietario_id}
    
    if desde:
        query = text(query.text + " AND g.fecha_gasto >= :desde")
        params["desde"] = desde
    if hasta:
        query = text(query.text + " AND g.fecha_gasto <= :hasta")
        params["hasta"] = hasta
    if vehiculo_id:
        query = text(query.text + " AND g.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    query = text(query.text + " ORDER BY g.fecha_gasto DESC")
    
    result = await db.execute(query, params)
    rows = result.all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Gastos"
    
    headers = ["Fecha", "Vehículo", "Categoría", "Monto", "Descripción", "Kilometraje"]
    ws.append(headers)
    
    for row in rows:
        ws.append([
            row[0].strftime("%d/%m/%Y") if row[0] else "",
            row[1] or "",
            row[2] or "",
            float(row[3]) if row[3] else 0,
            row[4] or "",
            row[5] or ""
        ])
    
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws.column_dimensions[column].width = adjusted_width
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=gastos_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )


@router.get("/reportes/mantenimientos/csv")
async def exportar_mantenimientos_csv(
    vehiculo_id: Optional[UUID] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Exportar mantenimientos a CSV"""
    query = text("""
        SELECT 
            m.fecha_servicio as fecha,
            v.patente as vehiculo,
            m.tipo_servicio as servicio,
            m.taller_nombre as taller,
            m.costo as costo,
            m.kilometraje as km,
            m.observaciones as observaciones
        FROM fleet.mantenimiento_vehiculo m
        JOIN fleet.vehiculo v ON v.id = m.vehiculo_id
        WHERE m.propietario_id = :propietario_id
    """)
    params = {"propietario_id": propietario_id}
    
    if vehiculo_id:
        query = text(query.text + " AND m.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    query = text(query.text + " ORDER BY m.fecha_servicio DESC")
    
    result = await db.execute(query, params)
    rows = result.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Vehículo", "Servicio", "Taller", "Costo", "Kilometraje", "Observaciones"])
    
    for row in rows:
        writer.writerow([
            row[0].strftime("%d/%m/%Y") if row[0] else "",
            row[1] or "",
            row[2] or "",
            row[3] or "",
            f"{row[4]:.2f}" if row[4] else "",
            row[5] or "",
            row[6] or ""
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=mantenimientos_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


# ============================================================
# NUEVOS ENDPOINTS - USANDO LIQUIDACION (D9)
# ============================================================

@router.get("/reportes/resumen-ejecutivo/{vehiculo_id}")
async def resumen_ejecutivo(
    vehiculo_id: UUID,
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resumen ejecutivo completo del vehículo usando liquidaciones (D9).
    """
    
    await verificar_vehiculo_propietario(vehiculo_id, propietario_id, db)
    
    hoy = datetime.now().date()
    if periodo == "dia":
        fecha_desde = hoy
    elif periodo == "semana":
        fecha_desde = hoy - timedelta(days=7)
    else:
        fecha_desde = hoy - timedelta(days=30)
    
    query_vehiculo = text("""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            v.numero_licencia,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) AS conductor_nombre,
            COALESCE(cv.calificacion_promedio, 0) AS calificacion_promedio,
            COALESCE(cv.total_viajes, 0) AS total_viajes_historico
        FROM fleet.vehiculo v
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE v.id = :vehiculo_id
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
    row_vehiculo = result.first()
    
    if not row_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    query_liquidaciones = text("""
        SELECT 
            COALESCE(COUNT(l.id), 0) AS total_liquidaciones,
            COALESCE(SUM(l.monto_bruto), 0) AS ingresos_brutos,
            COALESCE(SUM(l.total_gastos), 0) AS gastos_totales,
            COALESCE(SUM(l.total_propietario), 0) AS utilidad_neta,
            COALESCE(AVG(l.total_propietario), 0) AS utilidad_promedio,
            COALESCE(SUM(l.comision_chofer), 0) AS comisiones,
            COALESCE(SUM(l.canon), 0) AS canon_total
        FROM fleet.liquidacion l
        WHERE l.vehiculo_id = :vehiculo_id
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en::date BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_liquidaciones, {
        "vehiculo_id": vehiculo_id,
        "desde": fecha_desde,
        "hasta": hoy
    })
    row_liquidaciones = result.first()
    
    query_gastos = text("""
        SELECT 
            COALESCE(SUM(CASE WHEN LOWER(tipo_gasto) = 'combustible' THEN monto ELSE 0 END), 0) AS combustible,
            COALESCE(SUM(CASE WHEN LOWER(tipo_gasto) = 'mantenimiento' THEN monto ELSE 0 END), 0) AS mantenimiento,
            COALESCE(SUM(CASE WHEN LOWER(tipo_gasto) = 'seguro' THEN monto ELSE 0 END), 0) AS seguro,
            COALESCE(SUM(CASE WHEN LOWER(tipo_gasto) NOT IN ('combustible', 'mantenimiento', 'seguro') THEN monto ELSE 0 END), 0) AS otros,
            COALESCE(SUM(monto), 0) AS total_gastos
        FROM fleet.gasto_vehiculo
        WHERE vehiculo_id = :vehiculo_id
          AND fecha_gasto BETWEEN :desde AND :hasta
    """)
    result = await db.execute(query_gastos, {
        "vehiculo_id": vehiculo_id,
        "desde": fecha_desde,
        "hasta": hoy
    })
    row_gastos = result.first()
    
    query_benchmarking = text("""
        WITH flota_stats AS (
            SELECT 
                v.id AS vehiculo_id,
                COALESCE(SUM(l.monto_bruto), 0) AS ingresos_brutos,
                COALESCE(SUM(l.total_propietario), 0) AS utilidad_neta
            FROM fleet.vehiculo v
            LEFT JOIN fleet.liquidacion l ON v.id = l.vehiculo_id 
                AND l.estado IN ('APROBADA', 'PAGADA')
                AND l.calculada_en::date BETWEEN :desde AND :hasta
            INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE pv.propietario_id = :propietario_id AND v.activo = true
            GROUP BY v.id
        ),
        avg_stats AS (
            SELECT 
                COALESCE(AVG(ingresos_brutos), 0) AS avg_ingresos,
                COALESCE(AVG(utilidad_neta), 0) AS avg_utilidad
            FROM flota_stats
        ),
        ranked AS (
            SELECT 
                *,
                RANK() OVER (ORDER BY ingresos_brutos DESC) AS ranking
            FROM flota_stats
        )
        SELECT 
            fs.ingresos_brutos,
            fs.utilidad_neta,
            avg.avg_ingresos,
            avg.avg_utilidad,
            r.ranking
        FROM flota_stats fs
        CROSS JOIN avg_stats avg
        LEFT JOIN ranked r ON r.vehiculo_id = fs.vehiculo_id
        WHERE fs.vehiculo_id = :vehiculo_id
    """)
    result = await db.execute(query_benchmarking, {
        "vehiculo_id": vehiculo_id,
        "propietario_id": propietario_id,
        "desde": fecha_desde,
        "hasta": hoy
    })
    row_bench = result.first()
    
    query_total = text("""
        SELECT COUNT(DISTINCT v.id)
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id AND v.activo = true
    """)
    result = await db.execute(query_total, {"propietario_id": propietario_id})
    total_vehiculos = result.scalar() or 0
    
    query_alertas = text("""
        SELECT 
            (SELECT fecha_servicio FROM fleet.mantenimiento_vehiculo 
             WHERE vehiculo_id = :vehiculo_id ORDER BY fecha_servicio DESC LIMIT 1) AS ultimo_service,
            (SELECT tipo_servicio FROM fleet.mantenimiento_vehiculo 
             WHERE vehiculo_id = :vehiculo_id ORDER BY fecha_servicio DESC LIMIT 1) AS ultimo_tipo,
            COALESCE(v.desgaste_neumaticos, 0) AS desgaste_neumaticos
        FROM fleet.vehiculo v
        WHERE v.id = :vehiculo_id
    """)
    result = await db.execute(query_alertas, {"vehiculo_id": vehiculo_id})
    row_alertas = result.first()
    
    return {
        "vehiculo": {
            "id": str(row_vehiculo[0]),
            "patente": row_vehiculo[1] or "SIN PATENTE",
            "marca": row_vehiculo[2] or "SIN MARCA",
            "modelo": row_vehiculo[3] or "SIN MODELO",
            "anio": row_vehiculo[4] or 0,
            "numero_licencia": row_vehiculo[5] or "SIN LICENCIA",
            "conductor_actual": row_vehiculo[6] or "Sin conductor",
            "calificacion_promedio": float(row_vehiculo[7] or 0),
            "total_viajes_historico": int(row_vehiculo[8] or 0)
        },
        "periodo": {
            "desde": fecha_desde.isoformat(),
            "hasta": hoy.isoformat(),
            "nombre": periodo
        },
        "liquidaciones": {
            "total": int(row_liquidaciones[0] or 0),
            "ingresos_brutos": float(row_liquidaciones[1] or 0),
            "gastos_totales": float(row_liquidaciones[2] or 0),
            "utilidad_neta": float(row_liquidaciones[3] or 0),
            "utilidad_promedio": float(row_liquidaciones[4] or 0),
            "comisiones": float(row_liquidaciones[5] or 0),
            "canon_total": float(row_liquidaciones[6] or 0)
        },
        "gastos_operativos": {
            "combustible": float(row_gastos[0] or 0),
            "mantenimiento": float(row_gastos[1] or 0),
            "seguro": float(row_gastos[2] or 0),
            "otros": float(row_gastos[3] or 0),
            "total": float(row_gastos[4] or 0)
        },
        "benchmarking": {
            "ingresos": {
                "valor": float(row_bench[0] or 0) if row_bench else 0,
                "promedio_flota": float(row_bench[2] or 0) if row_bench else 0,
                "comparativa": "POR_ENCIMA" if row_bench and float(row_bench[0] or 0) > float(row_bench[2] or 0) else "POR_DEBAJO" if row_bench and float(row_bench[2] or 0) > 0 else "SIN_DATOS"
            },
            "utilidad": {
                "valor": float(row_bench[1] or 0) if row_bench else 0,
                "promedio_flota": float(row_bench[3] or 0) if row_bench else 0,
                "comparativa": "POR_ENCIMA" if row_bench and float(row_bench[1] or 0) > float(row_bench[3] or 0) else "POR_DEBAJO" if row_bench and float(row_bench[3] or 0) > 0 else "SIN_DATOS"
            },
            "puesto": int(row_bench[4] or 0) if row_bench else 0,
            "total_vehiculos": total_vehiculos
        },
        "alertas": {
            "ultimo_service": row_alertas[0].strftime("%d/%m/%Y") if row_alertas and row_alertas[0] else None,
            "ultimo_tipo": row_alertas[1] if row_alertas and row_alertas[1] else "Sin mantenimientos",
            "desgaste_neumaticos": f"{int(row_alertas[2] or 0)}%",
            "estado_neumaticos": "CRITICO" if (row_alertas[2] or 0) > 80 else "ALTO" if (row_alertas[2] or 0) > 60 else "MEDIO" if (row_alertas[2] or 0) > 40 else "BUENO"
        }
    }


@router.get("/reportes/resumen-ejecutivo/{vehiculo_id}/csv")
async def exportar_resumen_ejecutivo_csv(
    vehiculo_id: UUID,
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exportar resumen ejecutivo a CSV.
    """
    resumen = await resumen_ejecutivo(
        vehiculo_id=vehiculo_id,
        periodo=periodo,
        propietario_id=propietario_id,
        current_user=current_user,
        db=db
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["=== DATOS DEL VEHÍCULO ==="])
    writer.writerow(["ID", "Patente", "Marca", "Modelo", "Año", "Conductor", "Calificación"])
    v = resumen["vehiculo"]
    writer.writerow([
        v["id"], v["patente"], v["marca"], v["modelo"], v["anio"],
        v["conductor_actual"], v["calificacion_promedio"]
    ])
    writer.writerow([])
    
    writer.writerow(["=== LIQUIDACIONES ==="])
    writer.writerow(["Total", "Ingresos Brutos", "Gastos", "Utilidad Neta", "Promedio", "Comisiones", "Canon"])
    l = resumen["liquidaciones"]
    writer.writerow([
        l["total"], l["ingresos_brutos"], l["gastos_totales"],
        l["utilidad_neta"], l["utilidad_promedio"],
        l["comisiones"], l["canon_total"]
    ])
    writer.writerow([])
    
    writer.writerow(["=== GASTOS OPERATIVOS ==="])
    writer.writerow(["Combustible", "Mantenimiento", "Seguro", "Otros", "Total"])
    g = resumen["gastos_operativos"]
    writer.writerow([
        g["combustible"], g["mantenimiento"], g["seguro"], g["otros"], g["total"]
    ])
    writer.writerow([])
    
    writer.writerow(["=== BENCHMARKING ==="])
    writer.writerow(["Métrica", "Valor", "Promedio Flota", "Comparativa"])
    b = resumen["benchmarking"]
    writer.writerow([
        "Ingresos", b["ingresos"]["valor"], b["ingresos"]["promedio_flota"],
        b["ingresos"]["comparativa"]
    ])
    writer.writerow([
        "Utilidad", b["utilidad"]["valor"], b["utilidad"]["promedio_flota"],
        b["utilidad"]["comparativa"]
    ])
    writer.writerow(["Puesto", b["puesto"], f"de {b['total_vehiculos']}", ""])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=resumen_ejecutivo_{vehiculo_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/reportes/resumen-financiero")
async def resumen_financiero_reportes(
    periodo: str = Query("mensual", regex="^(mensual|trimestral|anual)$"),
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resumen financiero consolidado del propietario usando liquidaciones (D9).
    """
    if not fecha_hasta:
        fecha_hasta = datetime.now()
    if not fecha_desde:
        if periodo == "mensual":
            fecha_desde = fecha_hasta.replace(day=1)
        elif periodo == "trimestral":
            fecha_desde = fecha_hasta - timedelta(days=90)
        else:
            fecha_desde = fecha_hasta.replace(month=1, day=1)
    
    query_resumen = text("""
        SELECT 
            COALESCE(SUM(l.monto_bruto), 0) as ingresos_brutos,
            COALESCE(SUM(l.total_gastos), 0) as gastos_totales,
            COALESCE(SUM(l.total_propietario), 0) as utilidad_neta,
            COUNT(DISTINCT l.vehiculo_id) as vehiculos_activos,
            COUNT(l.id) as total_liquidaciones,
            COALESCE(AVG(l.total_propietario), 0) as utilidad_promedio,
            COALESCE(SUM(l.comision_chofer), 0) as comisiones,
            COALESCE(SUM(l.canon), 0) as canon_total
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en BETWEEN :fecha_desde AND :fecha_hasta
    """)
    result = await db.execute(query_resumen, {
        "propietario_id": propietario_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta
    })
    row = result.first()
    
    query_ultimas = text("""
        SELECT 
            l.id,
            l.monto_bruto,
            l.total_propietario,
            l.estado,
            l.calculada_en,
            v.patente
        FROM fleet.liquidacion l
        JOIN fleet.vehiculo v ON v.id = l.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
        ORDER BY l.calculada_en DESC
        LIMIT 5
    """)
    result = await db.execute(query_ultimas, {"propietario_id": propietario_id})
    ultimas_rows = result.all()
    
    return {
        "periodo": {
            "desde": fecha_desde,
            "hasta": fecha_hasta,
            "tipo": periodo
        },
        "resumen": {
            "ingresos_brutos": float(row[0] or 0),
            "gastos_totales": float(row[1] or 0),
            "utilidad_neta": float(row[2] or 0),
            "vehiculos_activos": row[3] or 0,
            "total_liquidaciones": row[4] or 0,
            "utilidad_promedio": float(row[5] or 0),
            "comisiones": float(row[6] or 0),
            "canon_total": float(row[7] or 0)
        },
        "ultimas_liquidaciones": [
            {
                "id": str(r[0]),
                "monto_bruto": float(r[1] or 0),
                "utilidad": float(r[2] or 0),
                "estado": r[3],
                "fecha": r[4],
                "patente": r[5]
            }
            for r in ultimas_rows
        ]
    }


@router.get("/reportes/anual")
async def reporte_anual(
    anio: int = Query(datetime.now().year, description="Año a reportar"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reporte anual completo del propietario (D9).
    """
    fecha_inicio = datetime(anio, 1, 1)
    fecha_fin = datetime(anio, 12, 31, 23, 59, 59)
    
    query_resumen = text("""
        SELECT 
            COALESCE(SUM(l.monto_bruto), 0) as ingresos_brutos,
            COALESCE(SUM(l.total_gastos), 0) as gastos_totales,
            COALESCE(SUM(l.total_propietario), 0) as utilidad_neta,
            COUNT(DISTINCT l.vehiculo_id) as vehiculos_activos,
            COUNT(l.id) as total_liquidaciones,
            COALESCE(SUM(l.comision_chofer), 0) as comisiones,
            COALESCE(SUM(l.canon), 0) as canon_total
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en BETWEEN :fecha_inicio AND :fecha_fin
    """)
    result = await db.execute(query_resumen, {
        "propietario_id": propietario_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })
    row = result.first()
    
    query_mensual = text("""
        SELECT 
            DATE_TRUNC('month', l.calculada_en) as mes,
            COALESCE(SUM(l.monto_bruto), 0) as ingresos,
            COALESCE(SUM(l.total_gastos), 0) as gastos,
            COALESCE(SUM(l.total_propietario), 0) as utilidad,
            COUNT(l.id) as liquidaciones
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en BETWEEN :fecha_inicio AND :fecha_fin
        GROUP BY DATE_TRUNC('month', l.calculada_en)
        ORDER BY mes ASC
    """)
    result = await db.execute(query_mensual, {
        "propietario_id": propietario_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })
    mensual_rows = result.all()
    
    mensual = [
        {
            "mes": r[0].strftime("%B") if r[0] else "",
            "ingresos": float(r[1] or 0),
            "gastos": float(r[2] or 0),
            "utilidad": float(r[3] or 0),
            "liquidaciones": int(r[4] or 0)
        }
        for r in mensual_rows
    ]
    
    query_top = text("""
        SELECT 
            v.patente,
            COALESCE(SUM(l.total_propietario), 0) as utilidad,
            COALESCE(SUM(l.monto_bruto), 0) as ingresos,
            COUNT(l.id) as liquidaciones
        FROM fleet.liquidacion l
        JOIN fleet.vehiculo v ON v.id = l.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en BETWEEN :fecha_inicio AND :fecha_fin
        GROUP BY v.patente
        ORDER BY utilidad DESC
        LIMIT 5
    """)
    result = await db.execute(query_top, {
        "propietario_id": propietario_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })
    top_rows = result.all()
    
    top_vehiculos = [
        {
            "patente": r[0],
            "utilidad": float(r[1] or 0),
            "ingresos": float(r[2] or 0),
            "liquidaciones": int(r[3] or 0)
        }
        for r in top_rows
    ]
    
    return {
        "anio": anio,
        "periodo": {
            "desde": fecha_inicio.isoformat(),
            "hasta": fecha_fin.isoformat()
        },
        "resumen": {
            "ingresos_brutos": float(row[0] or 0),
            "gastos_totales": float(row[1] or 0),
            "utilidad_neta": float(row[2] or 0),
            "vehiculos_activos": row[3] or 0,
            "total_liquidaciones": row[4] or 0,
            "comisiones": float(row[5] or 0),
            "canon_total": float(row[6] or 0)
        },
        "mensual": mensual,
        "top_vehiculos": top_vehiculos,
        "total_meses_con_datos": len(mensual)
    }


@router.get("/reportes/comparativo")
async def comparativo_vehiculos(
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Comparativo de rendimiento entre vehículos usando liquidaciones (D9).
    """
    if not fecha_hasta:
        fecha_hasta = datetime.now()
    if not fecha_desde:
        fecha_desde = fecha_hasta - timedelta(days=30)
    
    query = text("""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            COALESCE(SUM(l.monto_bruto), 0) as ingresos,
            COALESCE(SUM(l.total_gastos), 0) as gastos,
            COALESCE(SUM(l.total_propietario), 0) as utilidad,
            COUNT(l.id) as liquidaciones,
            COALESCE(AVG(l.total_propietario), 0) as utilidad_promedio,
            (COALESCE(SUM(l.total_propietario), 0) / NULLIF(COALESCE(SUM(l.monto_bruto), 0), 0)) * 100 as margen
        FROM fleet.vehiculo v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN fleet.liquidacion l ON l.vehiculo_id = v.id 
            AND l.estado IN ('APROBADA', 'PAGADA')
            AND l.calculada_en BETWEEN :fecha_desde AND :fecha_hasta
        WHERE pv.propietario_id = :propietario_id AND pv.activo = true
        GROUP BY v.id, v.patente, v.marca, v.modelo
        ORDER BY utilidad DESC
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta
    })
    rows = result.all()
    
    return {
        "periodo": {
            "desde": fecha_desde,
            "hasta": fecha_hasta
        },
        "vehiculos": [
            {
                "id": str(r[0]),
                "patente": r[1],
                "marca": r[2],
                "modelo": r[3],
                "ingresos": float(r[4] or 0),
                "gastos": float(r[5] or 0),
                "utilidad": float(r[6] or 0),
                "liquidaciones": r[7] or 0,
                "utilidad_promedio": float(r[8] or 0),
                "margen_porcentaje": float(r[9] or 0) if r[9] else 0
            }
            for r in rows
        ],
        "totales": {
            "total_ingresos": sum(float(r[4] or 0) for r in rows),
            "total_gastos": sum(float(r[5] or 0) for r in rows),
            "total_utilidad": sum(float(r[6] or 0) for r in rows),
            "total_liquidaciones": sum(r[7] or 0 for r in rows)
        }
    }