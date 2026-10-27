"""
Router de Finanzas del Chofer.

Expone GET /api/chofer/finanzas/resumen con el resumen financiero del
turno activo (o del ultimo turno cerrado si no hay activo).

Reglas de negocio confirmadas:
- Viajes: solo estado = 'finalizado' del turno (todos los origen_tipo).
- Recaudacion por metodo: se resuelve via payment.transaccion + metodo_pago,
  con fallback a 'efectivo' (mismo patron que app/services/rentabilidad.py).
- Gastos: suma fleet.gasto_turno.monto.
- Ingresos manuales: suma fleet.ingreso_turno (origen o tipo = 'manual').
- utilidad_neta = recaudacion + ingresos_manuales - gastos - comision_propietario.
- Liquidacion: se LEE de fleet.liquidacion. Si no existe (turno activo),
  se devuelve null y comisionEstimada = true. NO se calcula en vivo aca:
  el calculo lo hace POST /api/liquidacion/calcular/{turno_id} (propietario).

NOTA: comentarios en ASCII puro (regla G72/N10).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import logging

from app.database import get_db
from app.dependencies import get_current_driver_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chofer/finanzas", tags=["Chofer - Finanzas"])


# ==========================================
# HELPERS
# ==========================================

def _to_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int_minutes(seconds):
    if seconds is None:
        return 0
    try:
        return int(float(seconds) // 60)
    except (TypeError, ValueError):
        return 0


# ==========================================
# ENDPOINT
# ==========================================

@router.get("/resumen")
async def obtener_resumen_finanzas(
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve el resumen financiero del turno activo o del ultimo cerrado.
    """
    user_id, control_base_id, email, tipo = current_user

    # ------------------------------------------
    # 1. Resolver turno: activo o ultimo cerrado
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                t.id,
                t.estado,
                t.inicio_turno,
                t.fin_turno,
                t.km_inicial,
                t.km_final,
                v.patente,
                v.marca,
                v.modelo
            FROM fleet.turno_chofer t
            JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
            WHERE t.chofer_id = :user_id
              AND t.estado IN ('ACTIVO', 'CERRADO', 'PENDIENTE_CONFIRMACION')
            ORDER BY
                CASE WHEN t.estado = 'ACTIVO' THEN 0 ELSE 1 END,
                t.inicio_turno DESC
            LIMIT 1
        """),
        {"user_id": user_id},
    )
    turno_row = result.first()

    if not turno_row:
        return {
            "turno": None,
            "resumen": {
                "totalViajes": 0,
                "recaudacionTotal": 0.0,
                "recaudacionPorMetodo": {},
                "gastosTotal": 0.0,
                "ingresosManuales": 0.0,
                "comisionPropietario": 0.0,
                "comisionEstimada": False,
                "utilidadNeta": 0.0,
            },
            "viajes": [],
            "gastos": [],
            "ingresos": [],
            "liquidacion": None,
        }

    (turno_id, estado, inicio_turno, fin_turno,
     km_inicial, km_final, patente, marca, modelo) = turno_row

    # ------------------------------------------
    # 2. Duracion y km
    # ------------------------------------------
    if fin_turno is not None and inicio_turno is not None:
        duracion_min = _to_int_minutes((fin_turno - inicio_turno).total_seconds())
    elif inicio_turno is not None:
        duracion_min = _to_int_minutes((datetime.now() - inicio_turno).total_seconds())
    else:
        duracion_min = 0

    if km_final is not None and km_inicial is not None:
        km_recorridos = _to_float(km_final) - _to_float(km_inicial)
    else:
        km_recorridos = None

    # ------------------------------------------
    # 3. Viajes finalizados del turno
    #    Metodo de pago via payment.transaccion (mismo patron que rentabilidad.py)
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                vs.id,
                COALESCE(vs.finalizado_en, vs.aceptado_en, vs.solicitado_en, vs.created_at) AS hora_ref,
                vs.direccion_origen,
                vs.direccion_destino,
                COALESCE(vs.precio_final, vs.precio_estimado, 0) AS monto,
                COALESCE(
                    (SELECT mp.nombre
                     FROM payment.transaccion t
                     JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id
                     WHERE t.viaje_id = vs.id
                     LIMIT 1),
                    'efectivo'
                ) AS metodo_pago
            FROM trip.viaje_solicitado vs
            WHERE vs.chofer_id = :user_id
              AND vs.estado = 'finalizado'
              AND vs.turno_id = :turno_id
            ORDER BY COALESCE(vs.finalizado_en, vs.created_at) ASC
        """),
        {"user_id": user_id, "turno_id": turno_id},
    )
    viajes_rows = result.fetchall()

    total_viajes = len(viajes_rows)
    recaudacion_total = 0.0
    recaudacion_por_metodo = {}
    viajes_list = []

    for v in viajes_rows:
        monto = _to_float(v[4])
        metodo = (v[5] or "efectivo").strip().lower()
        recaudacion_total += monto
        recaudacion_por_metodo[metodo] = recaudacion_por_metodo.get(metodo, 0.0) + monto
        hora_ref = v[1]
        viajes_list.append({
            "hora": hora_ref.strftime("%H:%M") if hora_ref else None,
            "origen": v[2] or "",
            "destino": v[3] or "",
            "monto": round(monto, 2),
            "metodoPago": metodo,
        })

    # ------------------------------------------
    # 4. Gastos del turno
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                COALESCE(tipo_gasto, '') AS tipo,
                monto,
                COALESCE(url_comprobante, '') AS url_comprobante,
                created_at
            FROM fleet.gasto_turno
            WHERE turno_id = :turno_id
            ORDER BY created_at ASC
        """),
        {"turno_id": turno_id},
    )
    gastos_rows = result.fetchall()

    gastos_total = 0.0
    gastos_list = []
    for g in gastos_rows:
        monto = _to_float(g[1])
        gastos_total += monto
        gastos_list.append({
            "hora": g[3].strftime("%H:%M") if g[3] else None,
            "tipo": g[0] or "",
            "monto": round(monto, 2),
            "urlComprobante": g[2] or None, # <-- AGREGADO
            "descripcion": "", 
        })

    # ------------------------------------------
    # 5. Ingresos manuales
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                COALESCE(medio_pago, tipo_ingreso, '') AS tipo,
                monto,
                COALESCE(observaciones, '') AS descripcion,
                created_at
            FROM fleet.ingreso_turno
            WHERE turno_id = :turno_id
              AND (
                    LOWER(COALESCE(origen, '')) = 'manual'
                 OR LOWER(COALESCE(tipo_ingreso, '')) = 'manual'
              )
            ORDER BY created_at ASC
        """),
        {"turno_id": turno_id},
    )
    ingresos_rows = result.fetchall()

    ingresos_total = 0.0
    ingresos_list = []
    for i in ingresos_rows:
        monto = _to_float(i[1])
        ingresos_total += monto
        ingresos_list.append({
            "hora": i[3].strftime("%H:%M") if i[3] else None,
            "tipo": i[0] or "",
            "monto": round(monto, 2),
            "descripcion": i[2] or "",
        })

        # ------------------------------------------
    # 6. Liquidacion (si existe)
    #    El calculo lo hace POST /api/liquidacion/calcular/{turno_id}.
    #    Aca solo LEEMOS. Si no existe (turno activo), null.
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                monto_bruto,
                total_chofer,
                total_propietario,
                total_gastos,
                estado
            FROM fleet.liquidacion
            WHERE turno_id = :turno_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"turno_id": turno_id},
    )
    liq_row = result.first()

    if liq_row:
        liquidacion = {
            "montoBruto": round(_to_float(liq_row[0]), 2),
            "comisionChofer": round(_to_float(liq_row[1]), 2),
            "utilidadPropietario": round(_to_float(liq_row[2]), 2),
            "totalGastos": round(_to_float(liq_row[3]), 2),
            "estado": liq_row[4],
        }
        comision_propietario = _to_float(liq_row[2])
        comision_estimada = False
    else:
        liquidacion = None
        comision_propietario = 0.0
        comision_estimada = True

    # ------------------------------------------
    # 7. Utilidad neta
    # ------------------------------------------
    utilidad_neta = (
        recaudacion_total
        + ingresos_total
        - gastos_total
        - comision_propietario
    )

    return {
        "turno": {
            "id": str(turno_id),
            "estado": estado,
            "inicioTurno": inicio_turno.isoformat() if inicio_turno else None,
            "finTurno": fin_turno.isoformat() if fin_turno else None,
            "kmRecorridos": round(km_recorridos, 2) if km_recorridos is not None else None,
            "duracionMinutos": duracion_min,
            "vehiculo": {
                "patente": patente,
                "marca": marca,
                "modelo": modelo,
            },
        },
        "resumen": {
            "totalViajes": total_viajes,
            "recaudacionTotal": round(recaudacion_total, 2),
            "recaudacionPorMetodo": {k: round(v, 2) for k, v in recaudacion_por_metodo.items()},
            "gastosTotal": round(gastos_total, 2),
            "ingresosManuales": round(ingresos_total, 2),
            "comisionPropietario": round(comision_propietario, 2),
            "comisionEstimada": comision_estimada,
            "utilidadNeta": round(utilidad_neta, 2),
        },
        "viajes": viajes_list,
        "gastos": gastos_list,
        "ingresos": ingresos_list,
        "liquidacion": liquidacion,
    }