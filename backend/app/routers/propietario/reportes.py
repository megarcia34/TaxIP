from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, date
import csv
import io
import json
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


@router.get("/reportes/gastos/csv")
async def exportar_gastos_csv(
    request: Request,
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
            g.kilometraje as km
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
    request: Request,
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
            g.kilometraje as km
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
    request: Request,
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


@router.get("/reportes/rentabilidad")
async def reporte_rentabilidad(
    request: Request,
    formato: str = Query("json", pattern="^(json|csv|pdf)$"),
    periodo: str = Query("mes", pattern="^(dia|semana|mes|ano)$"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reporte de rentabilidad en diferentes formatos"""
    from datetime import timedelta
    
    user_id, control_base_id, email, tipo = current_user
    
    hoy = datetime.now().date()
    
    if periodo == "dia":
        fecha_desde = hoy
    elif periodo == "semana":
        fecha_desde = hoy - timedelta(days=7)
    elif periodo == "ano":
        fecha_desde = hoy - timedelta(days=365)
    else:
        fecha_desde = hoy - timedelta(days=30)
    
    query = text("""
        SELECT 
            v.patente,
            COALESCE(SUM(vj.precio_final), 0) as ingresos,
            COALESCE(SUM(g.monto), 0) as gastos,
            COALESCE(SUM(vj.precio_final), 0) - COALESCE(SUM(g.monto), 0) as ganancia
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN trip.viaje_solicitado vj ON vj.vehiculo_id = v.id 
            AND vj.estado = 'finalizado'
            AND vj.created_at::date BETWEEN :desde AND :hasta
        LEFT JOIN fleet.gasto_vehiculo g ON g.vehiculo_id = v.id 
            AND g.fecha_gasto BETWEEN :desde AND :hasta
        WHERE pv.propietario_id = :propietario_id AND v.activo = true
        GROUP BY v.id, v.patente
        ORDER BY ganancia DESC
    """)
    result = await db.execute(query, {"propietario_id": propietario_id, "desde": fecha_desde, "hasta": hoy})
    rows = result.all()
    
    if formato == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Vehículo", "Ingresos", "Gastos", "Ganancia Neta"])
        for row in rows:
            writer.writerow([row[0], f"{row[1]:.2f}", f"{row[2]:.2f}", f"{row[3]:.2f}"])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=rentabilidad_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {
        "periodo": periodo,
        "desde": fecha_desde.isoformat(),
        "hasta": hoy.isoformat(),
        "datos": [
            {
                "vehiculo": row[0],
                "ingresos": float(row[1]),
                "gastos": float(row[2]),
                "ganancia": float(row[3])
            }
            for row in rows
        ]
    }


@router.get("/reportes/anual")
async def reporte_anual(
    request: Request,
    anio: int = Query(datetime.now().year, description="Año del reporte"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reporte anual consolidado"""
    user_id, control_base_id, email, tipo = current_user
    
    query_ingresos = text("""
        SELECT 
            EXTRACT(MONTH FROM v.created_at) as mes,
            COALESCE(SUM(v.precio_final), 0) as total
        FROM trip.viaje_solicitado v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND v.estado = 'finalizado'
          AND EXTRACT(YEAR FROM v.created_at) = :anio
        GROUP BY mes
        ORDER BY mes
    """)
    result = await db.execute(query_ingresos, {"propietario_id": propietario_id, "anio": anio})
    ingresos = {int(row[0]): float(row[1]) for row in result.all()}
    
    query_gastos = text("""
        SELECT 
            EXTRACT(MONTH FROM g.fecha_gasto) as mes,
            COALESCE(SUM(g.monto), 0) as total
        FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND EXTRACT(YEAR FROM g.fecha_gasto) = :anio
        GROUP BY mes
        ORDER BY mes
    """)
    result = await db.execute(query_gastos, {"propietario_id": propietario_id, "anio": anio})
    gastos = {int(row[0]): float(row[1]) for row in result.all()}
    
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    datos_mensuales = []
    total_ingresos = 0
    total_gastos = 0
    
    for i, mes in enumerate(meses, 1):
        ing = ingresos.get(i, 0)
        gast = gastos.get(i, 0)
        total_ingresos += ing
        total_gastos += gast
        datos_mensuales.append({
            "mes": mes,
            "ingresos": round(ing, 2),
            "gastos": round(gast, 2),
            "ganancia": round(ing - gast, 2)
        })
    
    return {
        "anio": anio,
        "resumen": {
            "total_ingresos": round(total_ingresos, 2),
            "total_gastos": round(total_gastos, 2),
            "ganancia_neta": round(total_ingresos - total_gastos, 2),
            "margen": round(((total_ingresos - total_gastos) / total_ingresos * 100) if total_ingresos > 0 else 0, 2)
        },
        "datos_mensuales": datos_mensuales
    }