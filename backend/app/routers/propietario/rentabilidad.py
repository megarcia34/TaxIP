"""
Router de Rentabilidad del Propietario.

Cruza liquidaciones (ingresos post-conciliacion) + gastos del vehiculo
para dar la utilidad neta real por vehiculo y periodo.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import date, timedelta
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


def _rango_por_periodo(periodo: str) -> tuple[date, date]:
    """Devuelve (desde, hasta) segun el periodo."""
    hoy = date.today()
    if periodo == "dia":
        return hoy, hoy
    elif periodo == "ano":
        return date(hoy.year, 1, 1), date(hoy.year, 12, 31)
    else:  # mes
        desde = hoy.replace(day=1)
        if hoy.month == 12:
            hasta = date(hoy.year, 12, 31)
        else:
            hasta = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
        return desde, hasta


@router.get("/rentabilidad")
async def get_rentabilidad(
    periodo: str = "mes",
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve la rentabilidad real por vehiculo del propietario.

    Reglas (R24):
    - Ingreso del propietario = total_propietario de las liquidaciones.
    - Gastos turno = total_gastos de las liquidaciones (cargados por el chofer).
    - Gastos vehiculo = fleet.gasto_vehiculo (cargados por el propietario).
    - Utilidad neta = Ingreso propietario - Gastos turno - Gastos vehiculo.
    """
    if desde and hasta:
        fecha_desde, fecha_hasta = desde, hasta
    else:
        if periodo not in ("dia", "mes", "ano"):
            raise HTTPException(status_code=400, detail="Periodo invalido.")
        fecha_desde, fecha_hasta = _rango_por_periodo(periodo)

    hasta_plus_one = fecha_hasta + timedelta(days=1)

    # 1. Traer vehiculos del propietario
    query_vehiculos = text("""
        SELECT v.id, v.patente
        FROM fleet.vehiculo v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND v.activo = true
        ORDER BY v.patente
    """)
    result = await db.execute(query_vehiculos, {"propietario_id": propietario_id})
    vehiculos = result.fetchall()

    vehiculos_data = []
    totales = {
        "ingresos": 0.0,
        "gastos_turno": 0.0,
        "gastos_vehiculo": 0.0,
        "comision_chofer": 0.0,
        "utilidad_neta": 0.0,
        "turnos": 0,
    }

    for v_id, patente in vehiculos:
        # 2. Liquidaciones del periodo
        query_liq = text("""
            SELECT
                COUNT(*) AS turnos,
                COALESCE(SUM(total_propietario), 0) AS ingresos,
                COALESCE(SUM(total_gastos), 0) AS gastos_turno,
                COALESCE(SUM(total_chofer), 0) AS comision_chofer
            FROM fleet.liquidacion
            WHERE vehiculo_id = :vehiculo_id
              AND estado != 'OBSOLETA'
              AND calculada_en >= :desde
              AND calculada_en < :hasta_plus_one
        """)
        result = await db.execute(query_liq, {
            "vehiculo_id": v_id,
            "desde": fecha_desde,
            "hasta_plus_one": hasta_plus_one,
        })
        liq = result.first()
        turnos = int(liq[0] or 0)
        ingresos = float(liq[1] or 0)
        gastos_turno = float(liq[2] or 0)
        comision_chofer = float(liq[3] or 0)

        # 3. Gastos del vehiculo (propietario)
        query_gastos = text("""
            SELECT COALESCE(SUM(monto), 0) AS total
            FROM fleet.gasto_vehiculo
            WHERE vehiculo_id = :vehiculo_id
              AND fecha_gasto >= :desde
              AND fecha_gasto < :hasta_plus_one
        """)
        result = await db.execute(query_gastos, {
            "vehiculo_id": v_id,
            "desde": fecha_desde,
            "hasta_plus_one": hasta_plus_one,
        })
        gastos_vehiculo = float(result.scalar() or 0)

        # 4. Calculos finales
        utilidad_neta = ingresos - gastos_turno - gastos_vehiculo
        margen = (utilidad_neta / ingresos * 100) if ingresos > 0 else 0
        gastos_totales = gastos_turno + gastos_vehiculo
        roi = (utilidad_neta / gastos_totales * 100) if gastos_totales > 0 else 0

        vehiculos_data.append({
            "vehiculo_id": str(v_id),
            "patente": patente,
            "turnos_conciliados": turnos,
            "ingresos": round(ingresos, 2),
            "gastos_turno": round(gastos_turno, 2),
            "gastos_vehiculo": round(gastos_vehiculo, 2),
            "comision_chofer": round(comision_chofer, 2),
            "utilidad_neta": round(utilidad_neta, 2),
            "margen": round(margen, 2),
            "roi": round(roi, 2),
        })

        totales["ingresos"] += ingresos
        totales["gastos_turno"] += gastos_turno
        totales["gastos_vehiculo"] += gastos_vehiculo
        totales["comision_chofer"] += comision_chofer
        totales["utilidad_neta"] += utilidad_neta
        totales["turnos"] += turnos

    vehiculos_con_ingresos = [v for v in vehiculos_data if v["ingresos"] > 0]
    promedio_margen = (
        sum(v["margen"] for v in vehiculos_con_ingresos) / len(vehiculos_con_ingresos)
        if vehiculos_con_ingresos else 0
    )

    return {
        "periodo": periodo,
        "desde": fecha_desde.isoformat(),
        "hasta": fecha_hasta.isoformat(),
        "vehiculos": vehiculos_data,
        "resumen_total": {
            "total_turnos": totales["turnos"],
            "total_ingresos": round(totales["ingresos"], 2),
            "total_gastos_turno": round(totales["gastos_turno"], 2),
            "total_gastos_vehiculo": round(totales["gastos_vehiculo"], 2),
            "total_gastos": round(totales["gastos_turno"] + totales["gastos_vehiculo"], 2),
            "total_comision_chofer": round(totales["comision_chofer"], 2),
            "total_utilidad_neta": round(totales["utilidad_neta"], 2),
            "promedio_margen": round(promedio_margen, 2),
        },
    }