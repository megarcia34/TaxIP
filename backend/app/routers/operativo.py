"""
Router para endpoints operativos del empleado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime  # ✅ IMPORTACIÓN AGREGADA

from app.database import get_db
from app.dependencies import EmpleadoUser

router = APIRouter(prefix="/operativo", tags=["Operativo"])


@router.get("/reporte/turno")
async def get_reporte_turno(
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el reporte del turno actual del empleado.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    # ✅ CORRECCIÓN: Verificar si hay turno activo
    if not turno_id:
        return {
            "total_viajes": 0,
            "completados": 0,
            "cancelados": 0,
            "facturado_total": 0,
            "promedio_viaje": 0,
            "tiempo_turno": "Sin turno activo",
            "viajes": [],
            "mensaje": "No hay turno activo"
        }
    
    # Obtener duración del turno
    query_turno = text("""
        SELECT fecha_inicio, fecha_fin, viajes_gestionados, facturado_total
        FROM auth.turno_empleado
        WHERE id = :turno_id
    """)
    result_turno = await db.execute(query_turno, {"turno_id": turno_id})
    turno_row = result_turno.first()
    
    # ✅ CORRECCIÓN: Verificar si existe el turno
    if not turno_row:
        return {
            "total_viajes": 0,
            "completados": 0,
            "cancelados": 0,
            "facturado_total": 0,
            "promedio_viaje": 0,
            "tiempo_turno": "Turno no encontrado",
            "viajes": [],
            "mensaje": "Turno no encontrado"
        }
    
    # ✅ CORRECCIÓN: Manejar fechas correctamente
    fecha_inicio = turno_row[0]
    fecha_fin = turno_row[1]
    
    tiempo_turno = "En curso"
    
    if fecha_inicio and fecha_fin:
        # Turno finalizado
        diff = fecha_fin - fecha_inicio
        horas = diff.seconds // 3600
        minutos = (diff.seconds % 3600) // 60
        dias = diff.days
        if dias > 0:
            tiempo_turno = f"{dias}d {horas}h {minutos}m"
        else:
            tiempo_turno = f"{horas}h {minutos}m"
    elif fecha_inicio:
        # Turno en curso
        diff = datetime.now() - fecha_inicio
        horas = diff.seconds // 3600
        minutos = (diff.seconds % 3600) // 60
        dias = diff.days
        if dias > 0:
            tiempo_turno = f"{dias}d {horas}h {minutos}m (activo)"
        else:
            tiempo_turno = f"{horas}h {minutos}m (activo)"
    else:
        tiempo_turno = "Sin fecha de inicio"
    
    # Obtener viajes del turno
    query = text("""
        SELECT 
            r.id,
            r.pasajero_nombre,
            r.estado,
            r.precio_final,
            r.centro_costo,
            r.created_at
        FROM trip.reserva r
        WHERE r.turno_id = :turno_id
        ORDER BY r.created_at DESC
    """)
    
    result = await db.execute(query, {"turno_id": turno_id})
    rows = result.fetchall()
    
    viajes = []
    total_completados = 0
    total_cancelados = 0
    total_facturado = 0
    
    for row in rows:
        estado = row[2] or "reservado"
        precio = float(row[3]) if row[3] else 0
        
        viajes.append({
            "id": str(row[0]),
            "pasajero_nombre": row[1] or "Sin nombre",
            "estado": estado,
            "precio_final": precio,
            "centro_costo": row[4] or "Sin asignar",
            "created_at": row[5].isoformat() if row[5] else None,
        })
        
        if estado == "completado":
            total_completados += 1
            total_facturado += precio
        elif estado == "cancelado":
            total_cancelados += 1
    
    return {
        "total_viajes": len(viajes),
        "completados": total_completados,
        "cancelados": total_cancelados,
        "facturado_total": total_facturado,
        "promedio_viaje": round(total_facturado / total_completados, 2) if total_completados > 0 else 0,
        "tiempo_turno": tiempo_turno,
        "viajes": viajes
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene estadísticas del dashboard del empleado.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    if not turno_id:
        return {
            "total_viajes_turno": 0,
            "completados_turno": 0,
            "cancelados_turno": 0,
            "facturado_turno": 0,
            "viajes_en_curso": 0,
            "proximas_reservas": 0,
            "choferes_disponibles": 0,
            "mensaje": "No hay turno activo"
        }
    
    # Viajes del turno
    query = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN estado = 'completado' THEN 1 END) as completados,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as cancelados,
            COALESCE(SUM(precio_final), 0) as facturado,
            COUNT(CASE WHEN estado IN ('despachado', 'vehiculo_llego', 'pasajero_a_bordo') THEN 1 END) as en_curso
        FROM trip.reserva
        WHERE turno_id = :turno_id
    """)
    result = await db.execute(query, {"turno_id": turno_id})
    row = result.first()
    
    # Próximas reservas (para hoy)
    query_reservas = text("""
        SELECT COUNT(*)
        FROM trip.reserva
        WHERE empresa_id = :empresa_id
        AND es_programado = true
        AND DATE(fecha_programada) = CURRENT_DATE
        AND estado NOT IN ('completado', 'cancelado')
    """)
    result_reservas = await db.execute(query_reservas, {"empresa_id": empresa_id})
    proximas_reservas = result_reservas.scalar() or 0
    
    # ✅ MEJORA: Obtener choferes disponibles (Fase 6)
    query_choferes = text("""
        SELECT COUNT(*)
        FROM fleet.chofer_vehiculo
        WHERE control_base_id = :control_base_id
        AND estado_laboral = 'libre'
        AND activo = true
    """)
    result_choferes = await db.execute(query_choferes, {"control_base_id": control_base_id})
    choferes_disponibles = result_choferes.scalar() or 0
    
    return {
        "total_viajes_turno": row[0] or 0,
        "completados_turno": row[1] or 0,
        "cancelados_turno": row[2] or 0,
        "facturado_turno": float(row[3] or 0),
        "viajes_en_curso": row[4] or 0,
        "proximas_reservas": proximas_reservas,
        "choferes_disponibles": choferes_disponibles
    }


@router.get("/viajes/facturacion")
async def get_viajes_facturacion(
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene viajes completados para asignación de centro de costo.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    if not turno_id:
        return {
            "viajes": [],
            "total": 0,
            "mensaje": "No hay turno activo"
        }
    
    query = text("""
        SELECT 
            r.id,
            r.pasajero_nombre,
            r.direccion_origen,
            r.direccion_destino,
            r.precio_final,
            r.centro_costo,
            r.updated_at as completado_at
        FROM trip.reserva r
        WHERE r.turno_id = :turno_id
        AND r.estado = 'completado'
        ORDER BY r.updated_at DESC
    """)
    
    result = await db.execute(query, {"turno_id": turno_id})
    rows = result.fetchall()
    
    return {
        "viajes": [
            {
                "id": str(row[0]),
                "pasajero_nombre": row[1] or "Sin nombre",
                "direccion_origen": row[2],
                "direccion_destino": row[3],
                "precio_final": float(row[4]) if row[4] else 0,
                "centro_costo": row[5],
                "completado_at": row[6].isoformat() if row[6] else None,
            }
            for row in rows
        ],
        "total": len(rows)
    }


@router.get("/viajes/cancelables")
async def get_viajes_cancelables(
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene viajes que se pueden cancelar.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    if not turno_id:
        return {
            "viajes": [],
            "total": 0,
            "mensaje": "No hay turno activo"
        }
    
    query = text("""
        SELECT 
            r.id,
            r.pasajero_nombre,
            r.direccion_origen,
            r.direccion_destino,
            r.estado,
            r.created_at
        FROM trip.reserva r
        WHERE r.turno_id = :turno_id
        AND r.estado IN ('reservado', 'despachado')
        ORDER BY r.created_at DESC
    """)
    
    result = await db.execute(query, {"turno_id": turno_id})
    rows = result.fetchall()
    
    return {
        "viajes": [
            {
                "id": str(row[0]),
                "pasajero_nombre": row[1] or "Sin nombre",
                "direccion_origen": row[2],
                "direccion_destino": row[3],
                "estado": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
            }
            for row in rows
        ],
        "total": len(rows)
    }


@router.get("/viajes/completados")
async def get_viajes_completados(
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene viajes completados para reporte de objetos olvidados.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    if not turno_id:
        return {
            "viajes": [],
            "total": 0,
            "mensaje": "No hay turno activo"
        }
    
    query = text("""
        SELECT 
            r.id,
            r.pasajero_nombre,
            r.direccion_origen,
            r.direccion_destino,
            r.updated_at as completado_at
        FROM trip.reserva r
        WHERE r.turno_id = :turno_id
        AND r.estado = 'completado'
        ORDER BY r.updated_at DESC
        LIMIT 50
    """)
    
    result = await db.execute(query, {"turno_id": turno_id})
    rows = result.fetchall()
    
    return {
        "viajes": [
            {
                "id": str(row[0]),
                "pasajero_nombre": row[1] or "Sin nombre",
                "direccion_origen": row[2],
                "direccion_destino": row[3],
                "completado_at": row[4].isoformat() if row[4] else None,
            }
            for row in rows
        ],
        "total": len(rows)
    }