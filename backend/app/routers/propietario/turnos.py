# app/routers/propietario/turnos.py
"""
Propietario - Gestión de turnos de sus vehículos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_propietario_context
from pydantic import BaseModel

router = APIRouter()


class ConfirmarLiquidacionRequest(BaseModel):
    observacion: Optional[str] = None


@router.get("/turnos")
async def listar_turnos(
    vehiculo_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar turnos de los vehículos del propietario
    """
    propietario_id = ctx["propietario_id"]
    
    filters = ["pv.propietario_id = :propietario_id"]
    params = {"propietario_id": propietario_id, "limit": limit, "offset": offset}
    
    if vehiculo_id:
        filters.append("t.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    if estado:
        filters.append("t.estado = :estado")
        params["estado"] = estado
    
    if desde:
        filters.append("t.inicio_turno >= :desde")
        params["desde"] = desde
    
    if hasta:
        filters.append("t.inicio_turno <= :hasta")
        params["hasta"] = hasta
    
    where_clause = " AND ".join(filters)
    
    query = text(f"""
        SELECT 
            t.id,
            t.vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            t.chofer_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            t.estado,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            t.recaudacion_app_efectivo,
            t.recaudacion_app_debito,
            t.recaudacion_ticketera_calle,
            t.monto_bruto_calculado,
            t.comision_chofer_calculada,
            t.utilidad_propietario_calculada,
            t.inicio_turno,
            t.fin_turno,
            c.tipo_contrato,
            c.porcentaje_chofer,
            c.monto_diario
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        JOIN auth.usuario u ON u.id = t.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE {where_clause}
        ORDER BY t.inicio_turno DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "vehiculo_id": str(row[1]),
            "patente": row[2],
            "marca": row[3],
            "modelo": row[4],
            "chofer_id": str(row[5]),
            "chofer_nombre": row[6],
            "estado": row[7],
            "km_inicial": float(row[8]) if row[8] else None,
            "km_final": float(row[9]) if row[9] else None,
            "combustible_inicial": row[10],
            "combustible_final": row[11],
            "recaudacion_app_efectivo": float(row[12]) if row[12] else 0,
            "recaudacion_app_debito": float(row[13]) if row[13] else 0,
            "recaudacion_ticketera": float(row[14]) if row[14] else 0,
            "monto_bruto": float(row[15]) if row[15] else 0,
            "comision_chofer": float(row[16]) if row[16] else 0,
            "utilidad_propietario": float(row[17]) if row[17] else 0,
            "inicio_turno": row[18],
            "fin_turno": row[19],
            "tipo_contrato": row[20],
            "porcentaje_chofer": float(row[21]) if row[21] else None,
            "monto_diario": float(row[22]) if row[22] else None
        }
        for row in rows
    ]


@router.get("/turnos/{turno_id}")
async def obtener_turno(
    turno_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle de un turno específico
    """
    propietario_id = ctx["propietario_id"]
    
    query = text("""
        SELECT 
            t.id,
            t.vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            t.chofer_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            t.estado,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            t.recaudacion_app_efectivo,
            t.recaudacion_app_debito,
            t.recaudacion_ticketera_calle,
            t.monto_bruto_calculado,
            t.comision_chofer_calculada,
            t.utilidad_propietario_calculada,
            t.inicio_turno,
            t.fin_turno,
            c.tipo_contrato,
            c.porcentaje_chofer,
            c.monto_diario
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        JOIN auth.usuario u ON u.id = t.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE t.id = :turno_id AND pv.propietario_id = :propietario_id
    """)
    
    result = await db.execute(query, {"turno_id": turno_id, "propietario_id": propietario_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Obtener gastos del turno
    gastos_query = text("""
        SELECT id, tipo_gasto, monto, km_registro, url_comprobante, created_at
        FROM fleet.gasto_turno
        WHERE turno_id = :turno_id
        ORDER BY created_at DESC
    """)
    gastos_result = await db.execute(gastos_query, {"turno_id": turno_id})
    gastos_rows = gastos_result.all()
    
    gastos = [
        {
            "id": str(g[0]),
            "tipo_gasto": g[1],
            "monto": float(g[2]),
            "km_registro": float(g[3]) if g[3] else None,
            "url_comprobante": g[4],
            "created_at": g[5]
        }
        for g in gastos_rows
    ]
    
    return {
        "id": str(row[0]),
        "vehiculo_id": str(row[1]),
        "patente": row[2],
        "marca": row[3],
        "modelo": row[4],
        "chofer_id": str(row[5]),
        "chofer_nombre": row[6],
        "estado": row[7],
        "km_inicial": float(row[8]) if row[8] else None,
        "km_final": float(row[9]) if row[9] else None,
        "combustible_inicial": row[10],
        "combustible_final": row[11],
        "recaudacion_app_efectivo": float(row[12]) if row[12] else 0,
        "recaudacion_app_debito": float(row[13]) if row[13] else 0,
        "recaudacion_ticketera": float(row[14]) if row[14] else 0,
        "monto_bruto": float(row[15]) if row[15] else 0,
        "comision_chofer": float(row[16]) if row[16] else 0,
        "utilidad_propietario": float(row[17]) if row[17] else 0,
        "inicio_turno": row[18],
        "fin_turno": row[19],
        "tipo_contrato": row[20],
        "porcentaje_chofer": float(row[21]) if row[21] else None,
        "monto_diario": float(row[22]) if row[22] else None,
        "gastos": gastos
    }


@router.post("/turnos/{turno_id}/confirmar")
async def confirmar_liquidacion(
    turno_id: UUID,
    request: ConfirmarLiquidacionRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Propietario confirma liquidación final del turno
    """
    propietario_id = ctx["propietario_id"]
    
    # Verificar que el turno existe y pertenece al propietario
    query = text("""
        SELECT t.id, t.estado, t.chofer_id, v.patente
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE t.id = :turno_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query, {"turno_id": turno_id, "propietario_id": propietario_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    if row[1] != 'PENDIENTE_CONFIRMACION':
        raise HTTPException(
            status_code=400,
            detail=f"El turno no está pendiente de confirmación. Estado actual: {row[1]}"
        )
    
    chofer_id = row[2]
    patente = row[3]
    
    # Actualizar turno a LIQUIDADO
    update_query = text("""
        UPDATE fleet.turno_chofer
        SET estado = 'LIQUIDADO', updated_at = NOW()
        WHERE id = :turno_id
    """)
    await db.execute(update_query, {"turno_id": turno_id})
    
    # Notificar al chofer
    insert_notificacion = text("""
        INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
        VALUES (gen_random_uuid(), :chofer_id, 'Turno liquidado', 
                'El propietario ha confirmado la liquidación del turno del vehículo ' || :patente, 
                'turno_liquidado', false, NOW())
    """)
    await db.execute(insert_notificacion, {"chofer_id": chofer_id, "patente": patente})
    await db.commit()
    
    return {
        "success": True,
        "mensaje": "Liquidación confirmada correctamente"
    }