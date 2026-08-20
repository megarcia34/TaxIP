"""
Dashboard del propietario - Fase 9
Endpoints agregados para widgets del dashboard principal
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select, and_
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.models.fleet import Vehiculo, PropietarioVehiculo, ChoferVehiculo
from app.models.turno import TurnoChofer

router = APIRouter(tags=["Dashboard Propietario"])


# ============================================================
# 1. TARJETAS DE ESTADO DE FLOTA
# ============================================================

@router.get("/resumen-flota")
async def resumen_flota(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resumen general de la flota del propietario.
    """
    query = text("""
        SELECT 
            COUNT(DISTINCT v.id) as total_vehiculos,
            COUNT(DISTINCT cv.usuario_id) as total_choferes_activos,
            COUNT(DISTINCT CASE WHEN cv.estado_laboral IN ('libre', 'ocupado') THEN cv.usuario_id END) as choferes_conectados,
            COUNT(DISTINCT CASE WHEN cv.estado_laboral = 'libre' THEN cv.usuario_id END) as choferes_disponibles,
            COUNT(DISTINCT CASE WHEN cv.estado_laboral = 'ocupado' THEN cv.usuario_id END) as choferes_ocupados,
            COUNT(DISTINCT CASE WHEN cv.estado_laboral = 'fuera_servicio' THEN cv.usuario_id END) as choferes_fuera_servicio,
            COUNT(DISTINCT CASE WHEN t.estado = 'ACTIVO' THEN t.vehiculo_id END) as vehiculos_en_turno,
            COUNT(DISTINCT CASE WHEN v.activo = true AND t.estado IS NULL THEN v.id END) as vehiculos_disponibles
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN fleet.turno_chofer t ON t.vehiculo_id = v.id AND t.estado = 'ACTIVO'
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND v.activo = true
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    row = result.first()
    
    return {
        "total_vehiculos": row[0] or 0,
        "total_choferes_activos": row[1] or 0,
        "choferes_conectados": row[2] or 0,
        "choferes_disponibles": row[3] or 0,
        "choferes_ocupados": row[4] or 0,
        "choferes_fuera_servicio": row[5] or 0,
        "vehiculos_en_turno": row[6] or 0,
        "vehiculos_disponibles": row[7] or 0
    }


# ============================================================
# 2. MINI MAPA - VEHÍCULOS CON GPS ACTIVO
# ============================================================

@router.get("/vehiculos-ubicacion")
async def vehiculos_ubicacion(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener ubicación de todos los vehículos con GPS activo.
    """
    query = text("""
        SELECT 
            v.id as vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            cv.latitud,
            cv.longitud,
            cv.estado_laboral,
            cv.ultima_conexion,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as conductor_nombre,
            COALESCE(t.id, NULL) as turno_activo_id
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        INNER JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.turno_chofer t ON t.vehiculo_id = v.id AND t.estado = 'ACTIVO'
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND v.activo = true
          AND cv.latitud IS NOT NULL
          AND cv.longitud IS NOT NULL
          AND cv.ultima_conexion >= NOW() - INTERVAL '5 minutes'
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    rows = result.all()
    
    return [
        {
            "vehiculo_id": str(row[0]),
            "patente": row[1],
            "marca": row[2],
            "modelo": row[3],
            "latitud": float(row[4]),
            "longitud": float(row[5]),
            "estado": row[6] or "desconocido",
            "ultima_conexion": row[7].isoformat() if row[7] else None,
            "conductor": row[8] or "Sin conductor",
            "turno_activo": str(row[9]) if row[9] else None
        }
        for row in rows
    ]


# ============================================================
# 3. WIDGET DE RENTABILIDAD
# ============================================================

@router.get("/rentabilidad-widget")
async def rentabilidad_widget(
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Widget de rentabilidad con KPIs principales.
    """
    hoy = datetime.now().date()
    
    if periodo == "dia":
        fecha_desde = hoy
        label = "Hoy"
    elif periodo == "semana":
        fecha_desde = hoy - timedelta(days=7)
        label = "Última semana"
    else:
        fecha_desde = hoy - timedelta(days=30)
        label = "Último mes"
    
    # Período anterior para comparación
    if periodo == "dia":
        fecha_anterior_desde = hoy - timedelta(days=1)
        fecha_anterior_hasta = hoy - timedelta(days=1)
    elif periodo == "semana":
        fecha_anterior_desde = hoy - timedelta(days=14)
        fecha_anterior_hasta = hoy - timedelta(days=7)
    else:
        fecha_anterior_desde = hoy - timedelta(days=60)
        fecha_anterior_hasta = hoy - timedelta(days=30)
    
    query_actual = text("""
        SELECT 
            COALESCE(SUM(l.monto_bruto), 0) as ingresos,
            COALESCE(SUM(l.total_gastos), 0) as gastos,
            COALESCE(SUM(l.total_propietario), 0) as utilidad,
            COALESCE(AVG(l.total_propietario), 0) as utilidad_promedio,
            COUNT(l.id) as total_viajes,
            COALESCE(AVG(l.monto_bruto), 0) as ticket_promedio
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en::date BETWEEN :desde AND :hasta
    """)
    result_actual = await db.execute(query_actual, {
        "propietario_id": propietario_id,
        "desde": fecha_desde,
        "hasta": hoy
    })
    row_actual = result_actual.first()
    
    query_anterior = text("""
        SELECT 
            COALESCE(SUM(l.total_propietario), 0) as utilidad
        FROM fleet.liquidacion l
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = l.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND l.estado IN ('APROBADA', 'PAGADA')
          AND l.calculada_en::date BETWEEN :desde AND :hasta
    """)
    result_anterior = await db.execute(query_anterior, {
        "propietario_id": propietario_id,
        "desde": fecha_anterior_desde,
        "hasta": fecha_anterior_hasta
    })
    utilidad_anterior = float(result_anterior.scalar() or 0)
    utilidad_actual = float(row_actual[2] or 0)
    
    variacion = 0
    if utilidad_anterior > 0:
        variacion = ((utilidad_actual - utilidad_anterior) / utilidad_anterior) * 100
    
    return {
        "periodo": {
            "nombre": label,
            "desde": fecha_desde.isoformat(),
            "hasta": hoy.isoformat()
        },
        "ingresos": float(row_actual[0] or 0),
        "gastos": float(row_actual[1] or 0),
        "utilidad": utilidad_actual,
        "utilidad_promedio": float(row_actual[3] or 0),
        "total_viajes": row_actual[4] or 0,
        "ticket_promedio": float(row_actual[5] or 0),
        "variacion": round(variacion, 2),
        "tendencia": "positiva" if variacion >= 0 else "negativa"
    }


# ============================================================
# 4. WIDGET DE GASTOS DEL MES
# ============================================================

@router.get("/gastos-widget")
async def gastos_widget(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Widget de gastos del mes actual con desglose por categoría.
    """
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    mes_anterior_inicio = (inicio_mes - timedelta(days=1)).replace(day=1)
    mes_anterior_fin = inicio_mes - timedelta(days=1)
    
    query_actual = text("""
        SELECT 
            COALESCE(SUM(g.monto), 0) as total_gastos,
            COALESCE(SUM(CASE WHEN LOWER(g.tipo_gasto) = 'combustible' THEN g.monto ELSE 0 END), 0) as combustible,
            COALESCE(SUM(CASE WHEN LOWER(g.tipo_gasto) = 'mantenimiento' THEN g.monto ELSE 0 END), 0) as mantenimiento,
            COALESCE(SUM(CASE WHEN LOWER(g.tipo_gasto) = 'seguro' THEN g.monto ELSE 0 END), 0) as seguro,
            COALESCE(SUM(CASE WHEN LOWER(g.tipo_gasto) NOT IN ('combustible', 'mantenimiento', 'seguro') THEN g.monto ELSE 0 END), 0) as otros
        FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND g.fecha_gasto BETWEEN :desde AND :hasta
    """)
    result_actual = await db.execute(query_actual, {
        "propietario_id": propietario_id,
        "desde": inicio_mes,
        "hasta": hoy
    })
    row_actual = result_actual.first()
    
    query_anterior = text("""
        SELECT COALESCE(SUM(g.monto), 0) as total_gastos
        FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND g.fecha_gasto BETWEEN :desde AND :hasta
    """)
    result_anterior = await db.execute(query_anterior, {
        "propietario_id": propietario_id,
        "desde": mes_anterior_inicio,
        "hasta": mes_anterior_fin
    })
    gastos_anterior = float(result_anterior.scalar() or 0)
    gastos_actual = float(row_actual[0] or 0)
    
    variacion = 0
    if gastos_anterior > 0:
        variacion = ((gastos_actual - gastos_anterior) / gastos_anterior) * 100
    
    return {
        "periodo": {
            "mes": hoy.strftime("%B %Y"),
            "desde": inicio_mes.isoformat(),
            "hasta": hoy.isoformat()
        },
        "total_gastos": gastos_actual,
        "desglose": {
            "combustible": float(row_actual[1] or 0),
            "mantenimiento": float(row_actual[2] or 0),
            "seguro": float(row_actual[3] or 0),
            "otros": float(row_actual[4] or 0)
        },
        "variacion": round(variacion, 2),
        "tendencia": "positiva" if variacion <= 0 else "negativa"  # Si los gastos bajan es positivo
    }


# ============================================================
# 5. WIDGET DE ALERTAS UNIFICADAS
# ============================================================

@router.get("/alertas-widget")
async def alertas_widget(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Widget de alertas unificadas (mantenimiento, documentos, deuda choferes).
    """
    hoy = datetime.now().date()
    alertas = []
    
    # 1. Alertas de mantenimiento
    query_mantenimiento = text("""
        SELECT 
            v.patente,
            m.tipo_servicio,
            m.fecha_servicio,
            m.kilometraje,
            m.kilometraje + 5000 - COALESCE((
                SELECT km_inicial FROM fleet.turno_chofer 
                WHERE vehiculo_id = v.id AND estado = 'ACTIVO' 
                ORDER BY inicio_turno DESC LIMIT 1
            ), 0) as km_restante
        FROM fleet.mantenimiento_vehiculo m
        JOIN fleet.vehiculo v ON v.id = m.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND m.fecha_servicio <= NOW() - INTERVAL '90 days'
        ORDER BY m.fecha_servicio ASC
        LIMIT 5
    """)
    result = await db.execute(query_mantenimiento, {"propietario_id": propietario_id})
    rows = result.all()
    
    for row in rows:
        alertas.append({
            "tipo": "mantenimiento",
            "vehiculo": row[0],
            "servicio": row[1],
            "fecha_ultimo": row[2].isoformat() if row[2] else None,
            "km_restante": int(row[4] or 0),
            "urgencia": "alta" if (row[4] or 0) < 1000 else "media",
            "mensaje": f"Vencimiento de {row[1]} para {row[0]}"
        })
    
    # 2. Alertas de documentos
    query_documentos = text("""
        SELECT 
            d.tipo_documento,
            d.numero,
            d.fecha_vencimiento,
            v.patente,
            d.fecha_vencimiento - NOW()::date as dias_restantes
        FROM fleet.documento_vehiculo d
        JOIN fleet.vehiculo v ON v.id = d.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND d.activo = true
          AND d.fecha_vencimiento IS NOT NULL
          AND d.fecha_vencimiento BETWEEN NOW()::date AND NOW()::date + INTERVAL '15 days'
        ORDER BY d.fecha_vencimiento ASC
        LIMIT 5
    """)
    result = await db.execute(query_documentos, {"propietario_id": propietario_id})
    rows = result.all()
    
    for row in rows:
        alertas.append({
            "tipo": "documento",
            "documento": row[0],
            "numero": row[1],
            "fecha_vencimiento": row[2].isoformat() if row[2] else None,
            "vehiculo": row[3],
            "dias_restantes": int(row[4] or 0),
            "urgencia": "alta" if (row[4] or 0) < 7 else "media",
            "mensaje": f"{row[0]} {row[1]} vence en {int(row[4] or 0)} días para {row[3]}"
        })
    
    # 3. Alertas de deuda de choferes
    query_deuda = text("""
        SELECT 
            v.patente,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            c.monto_diario,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) as dias_deuda,
            EXTRACT(DAY FROM NOW() - c.fecha_inicio) * c.monto_diario as deuda_estimada
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        JOIN auth.usuario u ON u.id = c.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND c.tipo_contrato = 'ALQUILER'
          AND c.activo = true
          AND c.fecha_fin IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM payment.transaccion t
              WHERE t.tipo = 'canon'
                AND t.created_at::date >= c.fecha_inicio::date
          )
        ORDER BY deuda_estimada DESC
        LIMIT 3
    """)
    result = await db.execute(query_deuda, {"propietario_id": propietario_id})
    rows = result.all()
    
    for row in rows:
        alertas.append({
            "tipo": "deuda",
            "vehiculo": row[0],
            "chofer": row[1],
            "monto_diario": float(row[2] or 0),
            "dias_deuda": int(row[3] or 0),
            "deuda_estimada": float(row[4] or 0),
            "urgencia": "alta" if (row[3] or 0) > 30 else "media" if (row[3] or 0) > 15 else "baja",
            "mensaje": f"Deuda de {row[1]} por ${float(row[4] or 0):.2f} ({int(row[3] or 0)} días)"
        })
    
    # Ordenar por urgencia
    orden_urgencia = {"alta": 0, "media": 1, "baja": 2}
    alertas.sort(key=lambda x: orden_urgencia.get(x.get("urgencia", "baja"), 2))
    
    return {
        "total_alertas": len(alertas),
        "alertas": alertas[:10]  # Máximo 10 alertas
    }


# ============================================================
# 6. GRÁFICO DE INGRESOS Y GASTOS (ÚLTIMOS 6 MESES)
# ============================================================
@router.get("/grafico-ingresos-gastos")
async def grafico_ingresos_gastos(
    meses: int = Query(6, ge=1, le=24),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Datos para gráfico de ingresos vs gastos (últimos N meses).
    """
    # CORREGIDO: Usar CAST para que PostgreSQL entienda el tipo
    query = text("""
        WITH meses_series AS (
            SELECT generate_series(
                DATE_TRUNC('month', NOW() - (CAST(:meses AS INTEGER) || ' months')::INTERVAL),
                DATE_TRUNC('month', NOW()),
                '1 month'::interval
            ) as mes
        )
        SELECT 
            ms.mes,
            COALESCE(SUM(l.monto_bruto), 0) as ingresos,
            COALESCE(SUM(l.total_gastos), 0) as gastos,
            COALESCE(SUM(l.total_propietario), 0) as utilidad
        FROM meses_series ms
        LEFT JOIN fleet.liquidacion l ON DATE_TRUNC('month', l.calculada_en) = ms.mes
            AND l.estado IN ('APROBADA', 'PAGADA')
            AND l.vehiculo_id IN (
                SELECT vehiculo_id FROM fleet.propietario_vehiculo 
                WHERE propietario_id = :propietario_id AND activo = true
            )
        GROUP BY ms.mes
        ORDER BY ms.mes ASC
    """)
    result = await db.execute(query, {
        "meses": meses,
        "propietario_id": propietario_id
    })
    rows = result.all()
    
    labels = []
    ingresos = []
    gastos = []
    utilidad = []
    
    for row in rows:
        labels.append(row[0].strftime("%b %Y") if row[0] else "")
        ingresos.append(float(row[1] or 0))
        gastos.append(float(row[2] or 0))
        utilidad.append(float(row[3] or 0))
    
    return {
        "labels": labels,
        "ingresos": ingresos,
        "gastos": gastos,
        "utilidad": utilidad
    }
# ============================================================
# 7. GRÁFICO DE GASTOS POR CATEGORÍA
# ============================================================

@router.get("/grafico-gastos-categoria")
async def grafico_gastos_categoria(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Datos para gráfico de torta de gastos por categoría (último mes).
    """
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    
    query = text("""
        SELECT 
            COALESCE(CASE 
                WHEN LOWER(g.tipo_gasto) = 'combustible' THEN 'Combustible'
                WHEN LOWER(g.tipo_gasto) = 'mantenimiento' THEN 'Mantenimiento'
                WHEN LOWER(g.tipo_gasto) = 'seguro' THEN 'Seguro'
                WHEN LOWER(g.tipo_gasto) IN ('patente', 'impuesto') THEN 'Impuestos'
                ELSE 'Otros'
            END, 'Otros') as categoria,
            COALESCE(SUM(g.monto), 0) as total
        FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND g.fecha_gasto BETWEEN :desde AND :hasta
        GROUP BY categoria
        ORDER BY total DESC
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "desde": inicio_mes,
        "hasta": hoy
    })
    rows = result.all()
    
    colores = {
        "Combustible": "#F59E0B",
        "Mantenimiento": "#3B82F6",
        "Seguro": "#10B981",
        "Impuestos": "#EF4444",
        "Otros": "#6B7280"
    }
    
    return {
        "labels": [row[0] for row in rows],
        "values": [float(row[1] or 0) for row in rows],
        "colors": [colores.get(row[0], "#6B7280") for row in rows]
    }


# ============================================================
# 8. ÚLTIMOS VIAJES
# ============================================================

@router.get("/ultimos-viajes")
async def ultimos_viajes(
    limit: int = Query(10, ge=1, le=50),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista de los últimos viajes realizados por vehículos del propietario.
    """
    query = text("""
        SELECT 
            vs.id,
            vs.created_at as fecha,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_final,
            vs.estado,
            v.patente,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre
        FROM trip.viaje_solicitado vs
        JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND vs.estado = 'finalizado'
        ORDER BY vs.created_at DESC
        LIMIT :limit
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "limit": limit
    })
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "fecha": row[1].isoformat() if row[1] else None,
            "origen": row[2],
            "destino": row[3],
            "monto": float(row[4] or 0),
            "estado": row[5],
            "patente": row[6],
            "chofer": row[7] or "Sin conductor"
        }
        for row in rows
    ]


# ============================================================
# 9. PRÓXIMOS MANTENIMIENTOS
# ============================================================

@router.get("/proximos-mantenimientos")
async def proximos_mantenimientos(
    limit: int = Query(5, ge=1, le=20),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista de próximos mantenimientos programados.
    """
    query = text("""
        SELECT DISTINCT ON (v.id)
            v.id as vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            m.tipo_servicio as ultimo_servicio,
            m.fecha_servicio as ultima_fecha,
            m.kilometraje as ultimo_km,
            COALESCE((
                SELECT km_inicial FROM fleet.turno_chofer 
                WHERE vehiculo_id = v.id AND estado = 'ACTIVO' 
                ORDER BY inicio_turno DESC LIMIT 1
            ), m.kilometraje) as km_actual
        FROM fleet.vehiculo v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN fleet.mantenimiento_vehiculo m ON m.vehiculo_id = v.id
            AND m.fecha_servicio = (
                SELECT MAX(fecha_servicio) 
                FROM fleet.mantenimiento_vehiculo 
                WHERE vehiculo_id = v.id
            )
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND v.activo = true
        ORDER BY v.id, m.fecha_servicio DESC NULLS LAST
        LIMIT :limit
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "limit": limit * 2
    })
    rows = result.all()
    
    mantenimientos = []
    for row in rows:
        # CORREGIDO: row[6] es el kilometraje, row[5] es la fecha
        km_actual = int(row[7] or 0)      # columna 7 = km_actual
        ultimo_km = int(row[6] or 0)      # columna 6 = ultimo_km (kilometraje)
        proximo_km = ultimo_km + 5000
        km_restante = max(0, proximo_km - km_actual)
        
        if km_restante <= 2000:
            mantenimientos.append({
                "vehiculo_id": str(row[0]),
                "patente": row[1],
                "marca": row[2] or "",
                "modelo": row[3] or "",
                "ultimo_servicio": row[4] or "Sin mantenimientos",
                "ultima_fecha": row[5].isoformat() if row[5] else None,
                "km_actual": km_actual,
                "proximo_km": proximo_km,
                "km_restante": km_restante,
                "urgencia": "alta" if km_restante <= 500 else "media" if km_restante <= 1000 else "baja"
            })
    
    # Ordenar por urgencia
    orden_urgencia = {"alta": 0, "media": 1, "baja": 2}
    mantenimientos.sort(key=lambda x: orden_urgencia.get(x["urgencia"], 2))
    
    return mantenimientos[:limit]


# ============================================================
# 10. VEHÍCULOS CON TURNOS ACTIVOS
# ============================================================

@router.get("/vehiculos-turnos-activos")
async def vehiculos_turnos_activos(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista de vehículos con turnos activos y sus conductores.
    """
    query = text("""
        SELECT 
            v.id as vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            t.id as turno_id,
            t.inicio_turno,
            t.km_inicial,
            t.estado as turno_estado,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as conductor_nombre,
            COALESCE(cv.calificacion_promedio, 0) as calificacion
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        JOIN auth.usuario u ON u.id = t.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id AND cv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND t.estado = 'ACTIVO'
        ORDER BY t.inicio_turno ASC
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    rows = result.all()
    
    return [
        {
            "vehiculo_id": str(row[0]),
            "patente": row[1],
            "marca": row[2] or "",
            "modelo": row[3] or "",
            "turno_id": str(row[4]),
            "inicio_turno": row[5].isoformat() if row[5] else None,
            "km_inicial": float(row[6] or 0),
            "turno_estado": row[7],
            "conductor": row[8] or "Sin conductor",
            "calificacion": float(row[9] or 0)
        }
        for row in rows
    ]