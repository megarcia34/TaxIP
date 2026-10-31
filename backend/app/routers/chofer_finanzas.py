"""
Router de Finanzas del Chofer.
Expone GET /api/chofer/finanzas/resumen con el resumen financiero del
turno activo (o del ultimo turno cerrado si no hay activo).
FASE 1: Integra estimacion en vivo, fix de KM activo y split de caja.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import logging
from app.database import get_db
from app.dependencies import get_current_driver_user
from app.services.liquidacion_engine import LiquidacionEngine

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
    Incluye estimacion en vivo del motor de liquidacion.
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
                t.contrato_id,
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
                "desglosePorOrigen": {},
                "recaudacion_efectivo": 0.0,
                "recaudacion_electronico": 0.0,
                "contrato": None
            },
            "viajes": [],
            "gastos": [],
            "ingresos": [],
            "liquidacion": None,
            "estimacion_liquidacion": None
        }

    (turno_id, estado, inicio_turno, fin_turno, km_inicial, km_final, 
     contrato_id, patente, marca, modelo) = turno_row

    # ------------------------------------------
    # 2. Duracion y KM (con FIX para turno activo)
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
        # FIX FASE 1: Sumar distancia_metros de viajes finalizados si km_final es nulo
        res_km = await db.execute(
            text("""
                SELECT COALESCE(SUM(distancia_metros), 0)
                FROM trip.viaje_solicitado
                WHERE turno_id = :turno_id AND estado = 'finalizado'
            """),
            {"turno_id": turno_id}
        )
        km_recorridos = float(res_km.scalar() or 0) / 1000.0

    # ------------------------------------------
    # 3. Contexto del Contrato
    # ------------------------------------------
    contrato_info = None
    if contrato_id:
        res_contrato = await db.execute(
            text("""
                SELECT tipo_contrato, porcentaje_chofer, canon_diario, tratamiento_gastos
                FROM fleet.contrato_vehiculo
                WHERE id = :contrato_id
            """),
            {"contrato_id": contrato_id}
        )
        c_row = res_contrato.first()
        if c_row:
            contrato_info = {
                "tipo_contrato": c_row[0],
                "porcentaje_chofer": float(c_row[1]) if c_row[1] else None,
                "monto_diario": float(c_row[2]) if c_row[2] else None,
                "tratamiento_gastos": c_row[3]
            }

    # ------------------------------------------
    # 4. Split de Caja (FIX: usar trip.viaje_solicitado.metodo_pago)
    # ------------------------------------------
    res_caja = await db.execute(
        text("""
            SELECT
                COALESCE(SUM(CASE WHEN COALESCE(metodo_pago, 'efectivo') = 'efectivo' 
                    THEN COALESCE(precio_final, precio_estimado, 0) ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN COALESCE(metodo_pago, 'efectivo') != 'efectivo' 
                    THEN COALESCE(precio_final, precio_estimado, 0) ELSE 0 END), 0)
            FROM trip.viaje_solicitado
            WHERE turno_id = :turno_id AND estado = 'finalizado'
        """),
        {"turno_id": turno_id}
    )
    caja_row = res_caja.first()
    recaudacion_efectivo = float(caja_row[0] or 0)
    recaudacion_electronico = float(caja_row[1] or 0)
    recaudacion_total = recaudacion_efectivo + recaudacion_electronico

    # ------------------------------------------
    # 5. Viajes finalizados del turno
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT
                vs.id,
                COALESCE(vs.finalizado_en, vs.aceptado_en, vs.solicitado_en, vs.created_at) AS hora_ref,
                vs.direccion_origen,
                vs.direccion_destino,
                COALESCE(vs.precio_final, vs.precio_estimado, 0) AS monto,
                COALESCE(vs.metodo_pago, 'efectivo') AS metodo_pago,
                COALESCE(vs.origen_tipo, 'desconocido') AS origen_tipo
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
    
    recaudacion_por_metodo = {}
    desglose_por_origen = {}
    viajes_list = []
    
    for v in viajes_rows:
        monto = _to_float(v[4])
        metodo = (v[5] or "efectivo").strip().lower()
        origen = v[6]
        
        recaudacion_por_metodo[metodo] = recaudacion_por_metodo.get(metodo, 0.0) + monto
        
        if origen not in desglose_por_origen:
            desglose_por_origen[origen] = {"viajes": 0, "recaudado": 0.0}
        desglose_por_origen[origen]["viajes"] += 1
        desglose_por_origen[origen]["recaudado"] += monto
        
        viajes_list.append({
            "id": str(v[0]),
            "hora": v[1].strftime("%H:%M") if v[1] else None,
            "origen": v[2] or "",
            "destino": v[3] or "",
            "monto": round(monto, 2),
            "metodoPago": metodo,
        })

    # Redondear desglose por origen
    for orig in desglose_por_origen:
        desglose_por_origen[orig]["recaudado"] = round(desglose_por_origen[orig]["recaudado"], 2)

    # ------------------------------------------
    # 6. Gastos del turno (con estado de aprobacion)
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT id, tipo_gasto, monto, url_comprobante, created_at
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
        monto = _to_float(g[2])
        gastos_total += monto
        gastos_list.append({
            "id": str(g[0]),
            "hora": g[4].strftime("%H:%M") if g[4] else None,
            "tipo": g[1] or "",
            "monto": round(monto, 2),
            "urlComprobante": g[3] or None,
            "descripcion": "",
            "estado_aprobacion": "pendiente"
        })

    # ------------------------------------------
    # 7. Ingresos manuales
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT COALESCE(medio_pago, tipo_ingreso, '') AS tipo, monto, COALESCE(observaciones, '') AS descripcion, created_at
            FROM fleet.ingreso_turno
            WHERE turno_id = :turno_id
              AND (LOWER(COALESCE(origen, '')) = 'manual' OR LOWER(COALESCE(tipo_ingreso, '')) = 'manual')
              AND estado = 'aprobado'
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
    # 8. Liquidacion Real (si existe)
    # ------------------------------------------
    result = await db.execute(
        text("""
            SELECT monto_bruto, total_chofer, total_propietario, total_gastos, estado
            FROM fleet.liquidacion
            WHERE turno_id = :turno_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"turno_id": turno_id},
    )
    liq_row = result.first()
    
    liquidacion_real = None
    comision_propietario_real = 0.0
    
    if liq_row:
        liquidacion_real = {
            "montoBruto": round(_to_float(liq_row[0]), 2),
            "comisionChofer": round(_to_float(liq_row[1]), 2),
            "utilidadPropietario": round(_to_float(liq_row[2]), 2),
            "totalGastos": round(_to_float(liq_row[3]), 2),
            "estado": liq_row[4],
        }
        comision_propietario_real = _to_float(liq_row[2])

    # ------------------------------------------
    # 9. ESTIMACION EN VIVO (Motor de Liquidacion)
    # ------------------------------------------
    estimacion_liquidacion = None
    if not liquidacion_real:
        try:
            logger.info(f"Iniciando estimacion para turno {turno_id}")
            engine = LiquidacionEngine(db)
            resultado_estimado = await engine.estimar(turno_id)
            
            estimacion_liquidacion = {
                "monto_bruto": float(resultado_estimado.monto_bruto),
                "total_gastos": float(resultado_estimado.total_gastos),
                "comision_chofer": float(resultado_estimado.comision_chofer),
                "utilidad_propietario": float(resultado_estimado.total_propietario),
                "es_estimacion": True,
                "desglose": resultado_estimado.detalles if hasattr(resultado_estimado, 'detalles') else []
            }
            logger.info(f"Estimacion exitosa para turno {turno_id}: {estimacion_liquidacion}")
        except Exception as e:
            logger.error(f"Error al estimar liquidacion para turno {turno_id}: {e}", exc_info=True)
            estimacion_liquidacion = None

    # ------------------------------------------
    # 10. Utilidad neta (Calculo de respaldo)
    # ------------------------------------------
    if liquidacion_real:
        utilidad_neta = liquidacion_real["comisionChofer"]
        comision_estimada = False
    elif estimacion_liquidacion:
        utilidad_neta = estimacion_liquidacion["comision_chofer"]
        comision_estimada = True
    else:
        utilidad_neta = recaudacion_total + ingresos_total - gastos_total
        comision_estimada = True

    return {
        "turno": {
            "id": str(turno_id),
            "estado": estado,
            "inicioTurno": inicio_turno.isoformat() if inicio_turno else None,
            "finTurno": fin_turno.isoformat() if fin_turno else None,
            "kmRecorridos": round(km_recorridos, 2),
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
            "comisionPropietario": round(comision_propietario_real, 2),
            "comisionEstimada": comision_estimada,
            "utilidadNeta": round(utilidad_neta, 2),
            "desglosePorOrigen": desglose_por_origen,
            "recaudacion_efectivo": round(recaudacion_efectivo, 2),
            "recaudacion_electronico": round(recaudacion_electronico, 2),
            "contrato": contrato_info
        },
        "viajes": viajes_list,
        "gastos": gastos_list,
        "ingresos": ingresos_list,
        "liquidacion": liquidacion_real,
        "estimacion_liquidacion": estimacion_liquidacion
    }