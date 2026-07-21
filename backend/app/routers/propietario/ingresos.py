from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import date
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


class RecaudacionManualRequest(BaseModel):
    vehiculo_id: UUID
    monto: float
    fecha: date
    descripcion: Optional[str] = None


class RegistrarCanonRequest(BaseModel):
    contrato_id: UUID
    fecha_pago: date
    monto: float


@router.post("/ingresos/recaudacion-manual")
async def registrar_recaudacion_manual(
    request_data: RecaudacionManualRequest,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query_vehiculo = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": request_data.vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no pertenece al propietario")
    
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
    result = await db.execute(insert_query, {
        "monto": request_data.monto,
        "descripcion": f"Recaudación manual - {request_data.descripcion or ''}"
    })
    await db.commit()
    
    return {"success": True, "message": "Recaudación manual registrada", "id": result.scalar()}


@router.post("/ingresos/canon/pagar")
async def registrar_pago_canon(
    request_data: RegistrarCanonRequest,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query_contrato = text("""
        SELECT id, monto_diario FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id AND propietario_id = :propietario_id AND tipo_contrato = 'CANON_FIJO' AND activo = true
    """)
    result = await db.execute(query_contrato, {"contrato_id": request_data.contrato_id, "propietario_id": propietario_id})
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Contrato no encontrado o no es de tipo canon fijo")
    
    insert_query = text("""
        INSERT INTO payment.transaccion (
            id, viaje_id, metodo_pago_id, monto, estado, tipo, descripcion, created_at, billetera_id
        )
        VALUES (
            gen_random_uuid(), NULL, NULL, :monto, 'completado', 'canon',
            :descripcion, NOW(), NULL
        )
        RETURNING id
    """)
    result = await db.execute(insert_query, {
        "monto": request_data.monto,
        "descripcion": f"Pago de canon - Contrato {request_data.contrato_id}"
    })
    await db.commit()
    
    return {"success": True, "message": "Pago de canon registrado", "id": result.scalar()}


@router.get("/ingresos")
async def listar_ingresos(
    request: Request,  # <--- MOVIDO AL PRINCIPIO
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    vehiculo_id: Optional[UUID] = None,
    limit: int = 100,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    params = {
        "propietario_id": propietario_id,
        "vehiculo_id": vehiculo_id if vehiculo_id else None,
        "desde": desde,
        "hasta": hasta,
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
                COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre
            FROM trip.viaje_solicitado v
            JOIN fleet.vehiculo ve ON ve.id = v.vehiculo_id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = ve.id
            LEFT JOIN auth.usuario u ON u.id = v.chofer_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            WHERE v.estado = 'finalizado'
              AND pv.propietario_id = :propietario_id
            
            UNION ALL
            
            -- Recaudaciones manuales
            SELECT 
                t.id::text,
                'recaudacion_manual' as tipo,
                t.monto as monto,
                t.created_at as fecha,
                t.descripcion as descripcion,
                v.patente as vehiculo_patente,
                NULL as chofer_nombre
            FROM payment.transaccion t
            LEFT JOIN fleet.vehiculo v ON v.id = :vehiculo_id
            WHERE t.tipo = 'recaudacion_manual'
            
            UNION ALL
            
            -- Cánones
            SELECT 
                t.id::text,
                'canon' as tipo,
                t.monto as monto,
                t.created_at as fecha,
                t.descripcion as descripcion,
                ve.patente as vehiculo_patente,
                NULL as chofer_nombre
            FROM payment.transaccion t
            LEFT JOIN fleet.contrato_vehiculo c ON c.id = t.id
            LEFT JOIN fleet.vehiculo ve ON ve.id = c.vehiculo_id
            WHERE t.tipo = 'canon'
              AND c.propietario_id = :propietario_id
        ) ingresos
        WHERE 1=1
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
            "chofer_nombre": row[6] or "-"
        }
        for row in rows
    ]