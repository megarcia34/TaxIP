from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


@router.get("/rentabilidad")
async def obtener_rentabilidad(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
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
    # ✅ CORREGIDO: propietario_id ya es UUID
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
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
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
    # ✅ CORREGIDO: propietario_id ya es UUID
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
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = text("""
        SELECT 
            DATE_TRUNC('month', t.created_at) as mes,
            t.tipo,
            COALESCE(SUM(t.monto), 0) as total
        FROM payment.transaccion t
        WHERE t.tipo IN ('viaje', 'recaudacion_manual', 'canon')
          AND t.created_at >= NOW() - INTERVAL '6 months'
        GROUP BY mes, t.tipo
        ORDER BY mes DESC, t.tipo
    """)
    result = await db.execute(query)
    rows = result.all()
    
    meses = {}
    for row in rows:
        mes = row[0].strftime("%Y-%m") if row[0] else None
        if mes not in meses:
            meses[mes] = {"electronico": 0, "manual": 0}
        if row[1] == "viaje":
            meses[mes]["electronico"] = float(row[2])
        else:
            meses[mes]["manual"] = float(row[2])
    
    labels = sorted(meses.keys())
    electronico = [meses[m]["electronico"] for m in labels]
    manual = [meses[m]["manual"] for m in labels]
    
    return {
        "labels": labels,
        "electronico": electronico,
        "manual": manual,
        "totales": {
            "electronico": sum(electronico),
            "manual": sum(manual)
        }
    }


@router.get("/deuda-choferes")
async def deuda_choferes(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = text("""
        SELECT 
            u.id as chofer_id,
            u.email,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            c.id as contrato_id,
            c.patente,
            c.monto_diario,
            c.fecha_inicio,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) as dias_deuda,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) * c.monto_diario as deuda_estimada
        FROM fleet.contrato_vehiculo c
        JOIN auth.usuario u ON u.id = c.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE c.propietario_id = :propietario_id
          AND c.tipo_contrato = 'CANON_FIJO'
          AND c.activo = true
          AND c.fecha_fin IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM payment.transaccion t
              WHERE t.tipo = 'canon'
                AND t.created_at::date >= c.fecha_inicio::date
          )
        ORDER BY deuda_estimada DESC
    """)
    # ✅ CORREGIDO: propietario_id ya es UUID
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