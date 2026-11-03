from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
import logging

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================
# SCHEMAS
# ============================================================

class RecaudacionManualRequest(BaseModel):
    vehiculo_id: Optional[UUID] = None
    monto: float
    fecha: date
    descripcion: Optional[str] = None

# ============================================================
# ENDPOINTS DE ESCRITURA
# ============================================================

@router.post("/ingresos/recaudacion-manual")
async def registrar_recaudacion_manual(
    request_data: RecaudacionManualRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registra una recaudacion manual (ticketera o efectivo que no entro al sistema)."""
    if request_data.vehiculo_id:
        query_vehiculo = text("""
            SELECT v.id FROM fleet.vehiculo v
            INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
        """)
        result = await db.execute(query_vehiculo, {
            "vehiculo_id": request_data.vehiculo_id, 
            "propietario_id": propietario_id
        })
        if not result.first():
            raise HTTPException(status_code=404, detail="Vehiculo no pertenece al propietario")

    insert_query = text("""
        INSERT INTO payment.transaccion (
            id, viaje_id, metodo_pago_id, monto, estado, tipo, descripcion, created_at, billetera_id
        )
        VALUES (
            gen_random_uuid(), NULL, NULL, :monto, 'completado', 'recaudacion_manual', 
            :descripcion, NOW(), NULL
        )
        RETURNING id
    """)
    
    descripcion_completa = f"Recaudacion manual - {request_data.descripcion or ''}"
    result = await db.execute(insert_query, {
        "monto": request_data.monto,
        "descripcion": descripcion_completa
    })
    await db.commit()
    
    return {"success": True, "message": "Recaudacion manual registrada", "id": result.scalar()}

# ============================================================
# ENDPOINTS DE LECTURA
# ============================================================

@router.get("/ingresos")
async def listar_ingresos(
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    vehiculo_id: Optional[UUID] = None,
    tipo: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista los ingresos del propietario con filtros dinamicos."""
    
    if not desde and not hasta:
        hoy = date.today()
        desde = hoy.replace(day=1)
        hasta = hoy

    # Calcular "hasta + 1 dia" en Python para evitar problemas con ::date en SQLAlchemy
    hasta_plus_one = hasta + timedelta(days=1)
    
    params = {
        "propietario_id": propietario_id,
        "vehiculo_id": vehiculo_id if vehiculo_id else None,
        "desde": desde,
        "hasta_plus_one": hasta_plus_one,
        "tipo": tipo,
        "limit": limit,
        "offset": offset
    }
    
    query = text("""
        SELECT * FROM (
            -- Viajes finalizados
            SELECT 
                v.id::text,
                'viaje' as tipo,
                COALESCE(v.precio_final, 0) as monto,
                v.created_at as fecha,
                COALESCE(v.direccion_origen, '') as descripcion,
                ve.patente as vehiculo_patente,
                COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
                COALESCE(v.metodo_pago, 'efectivo') as metodo_pago,
                COALESCE(v.origen_tipo, 'desconocido') as origen_tipo
            FROM trip.viaje_solicitado v
            JOIN fleet.vehiculo ve ON ve.id = v.vehiculo_id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = ve.id
            LEFT JOIN auth.usuario u ON u.id = v.chofer_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            WHERE v.estado = 'finalizado'
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
              AND COALESCE(v.finalizado_en, v.created_at) >= :desde
              AND COALESCE(v.finalizado_en, v.created_at) < :hasta_plus_one
              AND (CAST(:vehiculo_id AS UUID) IS NULL OR v.vehiculo_id = :vehiculo_id)
            
            UNION ALL
            
            -- Recaudaciones manuales
            SELECT 
                t.id::text,
                'recaudacion_manual' as tipo,
                t.monto as monto,
                t.created_at as fecha,
                COALESCE(t.descripcion, 'Recaudacion manual') as descripcion,
                'Sin vehiculo' as vehiculo_patente,
                NULL as chofer_nombre,
                'efectivo' as metodo_pago,
                'manual' as origen_tipo
            FROM payment.transaccion t
            WHERE t.tipo = 'recaudacion_manual'
              AND t.created_at >= :desde
              AND t.created_at < :hasta_plus_one
        ) ingresos
        WHERE 1=1
          AND (CAST(:tipo AS VARCHAR) IS NULL OR tipo = :tipo)
        ORDER BY fecha DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": row[0],
            "tipo": row[1],
            "monto": float(row[2]) if row[2] else 0,
            "fecha": row[3].isoformat() if row[3] else None,
            "descripcion": row[4] or "-",
            "vehiculo_patente": row[5] or "-",
            "chofer_nombre": row[6] or "-",
            "metodo_pago": row[7] or "efectivo",
            "origen_tipo": row[8] or "desconocido"
        }
        for row in rows
    ]


@router.get("/ingresos/resumen")
async def resumen_ingresos(
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Devuelve los totales y splits de ingresos para los KPIs del frontend."""
    
    if not desde and not hasta:
        hoy = date.today()
        desde = hoy.replace(day=1)
        hasta = hoy

    hasta_plus_one = hasta + timedelta(days=1)
    params = {
        "propietario_id": propietario_id,
        "desde": desde,
        "hasta_plus_one": hasta_plus_one,
    }

    # 1. Totales por tipo
    query_totales = text("""
        SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'viaje' THEN monto ELSE 0 END), 0) as total_viajes,
            COALESCE(SUM(CASE WHEN tipo = 'recaudacion_manual' THEN monto ELSE 0 END), 0) as total_manual,
            COALESCE(SUM(monto), 0) as total_general
        FROM (
            SELECT COALESCE(precio_final, 0) as monto, 'viaje' as tipo
            FROM trip.viaje_solicitado v
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.vehiculo_id
            WHERE v.estado = 'finalizado' AND pv.propietario_id = :propietario_id AND pv.activo = true
              AND COALESCE(v.finalizado_en, v.created_at) >= :desde
              AND COALESCE(v.finalizado_en, v.created_at) < :hasta_plus_one
            UNION ALL
            SELECT monto, 'recaudacion_manual' as tipo
            FROM payment.transaccion
            WHERE tipo = 'recaudacion_manual'
              AND created_at >= :desde
              AND created_at < :hasta_plus_one
        ) sub
    """)
    result = await db.execute(query_totales, params)
    row = result.first()
    total_viajes = float(row[0] or 0)
    total_manual = float(row[1] or 0)
    total_general = float(row[2] or 0)

    # 2. Split por metodo de pago
    query_metodos = text("""
        SELECT COALESCE(metodo_pago, 'efectivo') as metodo, SUM(COALESCE(precio_final, 0)) as total
        FROM trip.viaje_solicitado v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.vehiculo_id
        WHERE v.estado = 'finalizado' AND pv.propietario_id = :propietario_id AND pv.activo = true
          AND COALESCE(v.finalizado_en, v.created_at) >= :desde
          AND COALESCE(v.finalizado_en, v.created_at) < :hasta_plus_one
        GROUP BY COALESCE(metodo_pago, 'efectivo')
    """)
    result = await db.execute(query_metodos, params)
    metodos = {row[0]: float(row[1] or 0) for row in result.all()}

    # 3. Split por canal de origen
    query_canales = text("""
        SELECT COALESCE(origen_tipo, 'desconocido') as canal, SUM(COALESCE(precio_final, 0)) as total
        FROM trip.viaje_solicitado v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.vehiculo_id
        WHERE v.estado = 'finalizado' AND pv.propietario_id = :propietario_id AND pv.activo = true
          AND COALESCE(v.finalizado_en, v.created_at) >= :desde
          AND COALESCE(v.finalizado_en, v.created_at) < :hasta_plus_one
        GROUP BY COALESCE(origen_tipo, 'desconocido')
    """)
    result = await db.execute(query_canales, params)
    canales = {row[0]: float(row[1] or 0) for row in result.all()}

    return {
        "periodo": {
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat()
        },
        "totales": {
            "viajes": total_viajes,
            "manuales": total_manual,
            "general": total_general
        },
        "por_metodo_pago": metodos,
        "por_canal": canales
    }