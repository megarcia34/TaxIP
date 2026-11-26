"""
Viajes - Endpoints de historial, estado y calificación.
Extraído de routes.py (refactor 2026-09-24).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import get_current_user

from .queries import GET_VIAJE_BY_ID
from .services import formatear_respuesta_viaje
from .schemas import (
    ViajeEstadoResponse,
    CalificarViajeRequest,
    CalificarViajeResponse,
)

router = APIRouter()


# ============================================
# CALIFICAR VIAJE
# ============================================

@router.post("/{viaje_id}/calificar", response_model=CalificarViajeResponse)
async def calificar_viaje(
    viaje_id: UUID,
    request: CalificarViajeRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calificar un viaje completado"""
    user_id, _, _, user_tipo = current_user

    if user_tipo.lower() == "pasajero":
        calificado_tipo = "chofer"
        get_query = text("""
            SELECT id, chofer_id, estado FROM trip.viaje_solicitado
            WHERE id = :viaje_id AND pasajero_id = :user_id AND estado = 'finalizado'
        """)
    else:
        calificado_tipo = "pasajero"
        get_query = text("""
            SELECT id, pasajero_id, estado FROM trip.viaje_solicitado
            WHERE id = :viaje_id AND chofer_id = :user_id AND estado = 'finalizado'
        """)

    result = await db.execute(get_query, {"viaje_id": viaje_id, "user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Viaje no encontrado o no finalizado"
        )

    calificado_id = row[1]

    check_rate = text("""
        SELECT id FROM trip.calificacion
        WHERE viaje_id = :viaje_id AND calificador_id = :user_id
    """)

    rate_result = await db.execute(check_rate, {"viaje_id": viaje_id, "user_id": user_id})
    if rate_result.first():
        raise HTTPException(status_code=400, detail="Ya calificaste este viaje")

    insert_query = text("""
        INSERT INTO trip.calificacion (
            id, viaje_id, calificador_id, calificado_id, puntaje, comentario, created_at
        )
        VALUES (gen_random_uuid(), :viaje_id, :calificador_id, :calificado_id, :puntaje, :comentario, NOW())
    """)

    await db.execute(insert_query, {
        "viaje_id": viaje_id,
        "calificador_id": user_id,
        "calificado_id": calificado_id,
        "puntaje": request.puntaje,
        "comentario": request.comentario
    })

    if calificado_tipo == "chofer":
        update_rating = text("""
            UPDATE fleet.chofer_vehiculo
            SET calificacion_promedio = (
                SELECT AVG(puntaje)::DECIMAL(3,2)
                FROM trip.calificacion
                WHERE calificado_id = :chofer_id
            ),
            total_calificaciones = total_calificaciones + 1
            WHERE usuario_id = :chofer_id
        """)
        await db.execute(update_rating, {"chofer_id": calificado_id})

    await db.commit()

    return CalificarViajeResponse(
        success=True,
        message="Calificación registrada"
    )

# ============================================
# Historial de viajes y ESTADO DEL VIAJE 
# ============================================


@router.get("/historial", response_model=dict)
async def obtener_historial_viajes(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    estado: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener historial de viajes con más detalles.
    Endpoint polimórfico: filtra por rol (Propietario, Chofer o Admin).
    """
    user_id, control_base_id, _, user_tipo = current_user

    filters = ["1=1"]
    params = {"limit": limit, "offset": offset}

    # 1. LÓGICA DE ROLES
    if user_tipo.lower() in ("propietario", "admin_propietario"):
        # Si es admin_propietario, buscar su ID real de propietario
        propietario_id = user_id
        if user_tipo.lower() == "admin_propietario":
            q_prop = text("SELECT propietario_id FROM fleet.propietario_vehiculo WHERE usuario_id = :user_id LIMIT 1")
            res_prop = await db.execute(q_prop, {"user_id": user_id})
            row_prop = res_prop.first()
            if row_prop:
                propietario_id = row_prop[0]
        
        filters.append("pv.propietario_id = :propietario_id")
        params["propietario_id"] = propietario_id

    elif user_tipo.lower() in ("chofer", "conductor"):
        filters.append("vs.chofer_id = :user_id")
        params["user_id"] = user_id

    else:
        # Admin Tenant (o super_admin con control_base_id)
        filters.append("vs.control_base_id = :control_base_id")
        params["control_base_id"] = control_base_id

    if estado:
        filters.append("vs.estado = :estado")
        params["estado"] = estado

    # FILTRO DE FECHAS
    if desde:
        filters.append("vs.created_at >= :desde")
        params["desde"] = datetime.strptime(desde, "%Y-%m-%d")

    if hasta:
        # Le sumamos un día para incluir todo el día "hasta"
        fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d") + timedelta(days=1)
        filters.append("vs.created_at < :hasta")
        params["hasta"] = fecha_hasta

    where_clause = " AND ".join(filters)

    # 2. CONSULTA SQL CON CÁLCULOS EN BACKEND
    query = text(f"""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_estimado,
            vs.precio_final,
            vs.created_at,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            vs.metodo_pago,
            vs.motivo_cancelacion,
            vs.origen_tipo,
            
            -- Pasajero
            COALESCE(p.nombre || ' ' || p.apellido, up.email, 'Pasajero anónimo') as pasajero_nombre,
            
            -- Chofer
            COALESCE(p2.nombre || ' ' || p2.apellido, uc.email, 'Sin asignar') as chofer_nombre,
            
            -- Fecha formateada
            TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
            TO_CHAR(vs.created_at, 'HH24:MI') as hora,
            
            -- Precio según estado
            CASE 
                WHEN vs.estado = 'finalizado' THEN vs.precio_final
                ELSE vs.precio_estimado
            END as precio_mostrado,
            
            -- Empresa
            cb.nombre as empresa,
            
            -- Propietario
            COALESCE(p_prop.nombre || ' ' || p_prop.apellido, u_prop.email, 'No asignado') as propietario_nombre,
            
            -- Vehículo
            v.patente,
            v.marca,
            v.modelo,
            
            -- Calificación
            c.puntaje as calificacion,
            
            -- Coordenadas
            ST_Y(vs.origen::geometry) as origen_lat,
            ST_X(vs.origen::geometry) as origen_lng,
            ST_Y(vs.destino::geometry) as destino_lat,
            ST_X(vs.destino::geometry) as destino_lng,

            -- ✅ CALCULOS EN BACKEND (Regla de Oro)
            
            -- Duracion real en minutos
            CASE 
                WHEN vs.iniciado_en IS NOT NULL AND vs.finalizado_en IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (vs.finalizado_en - vs.iniciado_en)) / 60
                ELSE NULL 
            END as duracion_minutos,

            -- Estado legible
            CASE vs.estado
                WHEN 'pendiente' THEN 'Pendiente'
                WHEN 'publicado' THEN 'Publicado'
                WHEN 'aceptado' THEN 'Aceptado'
                WHEN 'en_curso' THEN 'En Curso'
                WHEN 'finalizado' THEN 'Finalizado'
                WHEN 'cancelado' THEN 'Cancelado'
                WHEN 'pagado' THEN 'Pagado'
                WHEN 'expirado' THEN 'Expirado'
                WHEN 'programada' THEN 'Programada'
                ELSE vs.estado
            END as estado_label,

            -- Fuente legible
            CASE vs.origen_tipo
                WHEN 'via_publica' THEN 'Calle'
                WHEN 'plataforma' THEN 'App/Landing'
                WHEN 'qr_comercio' THEN 'Código QR'
                WHEN 'corporativo' THEN 'Corporativo'
                WHEN 'despacho_manual' THEN 'Operativo'
                ELSE 'Desconocido'
            END as fuente_label,

            -- Metodo de pago legible
            CASE vs.metodo_pago
                WHEN 'efectivo' THEN 'Efectivo'
                WHEN 'tarjeta_debito' THEN 'Tarjeta Débito'
                WHEN 'qr' THEN 'QR'
                WHEN 'transferencia' THEN 'Transferencia'
                ELSE COALESCE(vs.metodo_pago, '—')
            END as metodo_pago_label,

            -- Correlativo
            vs.codigo AS codigo_correlativo

        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario up ON up.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = up.id
        LEFT JOIN auth.usuario uc ON uc.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = uc.id
        LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id
        LEFT JOIN trip.calificacion c ON c.viaje_id = vs.id AND c.calificador_id = vs.pasajero_id
        WHERE {where_clause}
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(query, params)
    rows = result.all()

    return {
        "total": len(rows),
        "limit": limit,
        "offset": offset,
        "viajes": [
            {
                "id": row[0],
                "estado": row[1],
                "direccion_origen": row[2] or '',
                "direccion_destino": row[3] or '',
                "precio_estimado": float(row[4]) if row[4] else None,
                "precio_final": float(row[5]) if row[5] else None,
                "created_at": row[6],
                "aceptado_en": row[7],
                "iniciado_en": row[8],
                "finalizado_en": row[9],
                "distancia_metros": row[10],
                "tiempo_estimado_segundos": row[11],
                "metodo_pago": row[12],
                "motivo_cancelacion": row[13],
                "origen_tipo": row[14],
                "pasajero_nombre": row[15],
                "chofer_nombre": row[16] or "Sin asignar",
                "fecha": row[17],
                "hora": row[18],
                "precio_mostrado": float(row[19]) if row[19] else None,
                "empresa": row[20] or "N/A",
                "propietario_nombre": row[21] or "No asignado",
                "patente": row[22] or "N/A",
                "marca": row[23] or "N/A",
                "modelo": row[24] or "N/A",
                "calificacion": row[25],
                "origen_lat": float(row[26]) if row[26] else None,
                "origen_lng": float(row[27]) if row[27] else None,
                "destino_lat": float(row[28]) if row[28] else None,
                "destino_lng": float(row[29]) if row[29] else None,
                "duracion_minutos": int(row[30]) if row[30] is not None else None,
                "estado_label": row[31],
                "fuente_label": row[32],
                "metodo_pago_label": row[33],
                "codigo_correlativo": row[34],
            }
            for row in rows
        ]
    }

# ============================================
# ESTADO DEL VIAJE
# ============================================

@router.get("/{viaje_id}/estado", response_model=ViajeEstadoResponse)
async def obtener_estado_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estado de un viaje especifico"""
    _, control_base_id, _, _ = current_user

    result = await db.execute(GET_VIAJE_BY_ID, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    return await formatear_respuesta_viaje(row)

# ============================================
# RECORRIDO REAL DEL GPS
# ============================================

@router.get("/{viaje_id}/gps")
async def obtener_recorrido_gps(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los puntos GPS reales del viaje desde audit.log_gps.
    Devuelve una lista de {lat, lng, timestamp}.
    """
    _, control_base_id, _, _ = current_user

    # Verificar que el viaje pertenece al tenant
    check_query = text("""
        SELECT id FROM trip.viaje_solicitado
        WHERE id = :viaje_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # Obtener puntos GPS
    query = text("""
        SELECT 
            latitud, 
            longitud, 
            created_at
        FROM audit.log_gps
        WHERE viaje_id = :viaje_id
        ORDER BY created_at ASC
    """)
    result = await db.execute(query, {"viaje_id": viaje_id})
    rows = result.all()

    return {
        "viaje_id": str(viaje_id),
        "total_puntos": len(rows),
        "puntos": [
            {
                "lat": float(row[0]),
                "lng": float(row[1]),
                "timestamp": row[2].isoformat() if row[2] else None
            }
            for row in rows
        ]
    }

@router.get("/resumen")
async def obtener_resumen_viajes(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve el conteo de viajes agrupado por estado.
    Polimórfico: filtra según el rol del usuario.
    """
    user_id, control_base_id, _, user_tipo = current_user

    filters = ["1=1"]
    params = {}

    if user_tipo.lower() in ("propietario", "admin_propietario"):
        propietario_id = user_id
        if user_tipo.lower() == "admin_propietario":
            q_prop = text("SELECT propietario_id FROM fleet.propietario_vehiculo WHERE usuario_id = :user_id LIMIT 1")
            res_prop = await db.execute(q_prop, {"user_id": user_id})
            row_prop = res_prop.first()
            if row_prop:
                propietario_id = row_prop[0]
        
        filters.append("pv.propietario_id = :propietario_id")
        params["propietario_id"] = propietario_id

    elif user_tipo.lower() in ("chofer", "conductor"):
        filters.append("vs.chofer_id = :user_id")
        params["user_id"] = user_id

    else:
        filters.append("vs.control_base_id = :control_base_id")
        params["control_base_id"] = control_base_id

    where_clause = " AND ".join(filters)

    query = text(f"""
        SELECT vs.estado, COUNT(*) as cantidad
        FROM trip.viaje_solicitado vs
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        WHERE {where_clause}
        GROUP BY vs.estado
    """)

    result = await db.execute(query, params)
    rows = result.all()

    conteos = {row[0]: row[1] for row in rows}

    return {
        "pendiente": conteos.get("pendiente", 0) + conteos.get("publicado", 0),
        "en_curso": conteos.get("en_curso", 0) + conteos.get("aceptado", 0),
        "finalizado": conteos.get("finalizado", 0) + conteos.get("pagado", 0),
        "cancelado": conteos.get("cancelado", 0) + conteos.get("expirado", 0),
    }