from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import date

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.schemas.propietario_schemas import (
    GastoVehiculoRequest,
    GastoVehiculoResponse,
    ResumenGastosResponse
)

router = APIRouter()


@router.post("/gasto", response_model=GastoVehiculoResponse)
async def registrar_gasto(
    request_data: GastoVehiculoRequest,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    verify_query = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(verify_query, {"vehiculo_id": request_data.vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="Vehículo no pertenece al propietario")
    
    insert_query = text("""
        INSERT INTO fleet.gasto_vehiculo (
            id, vehiculo_id, propietario_id, tipo_gasto, monto, 
            descripcion, kilometraje, comprobante_url, fecha_gasto, created_at
        )
        VALUES (
            gen_random_uuid(), :vehiculo_id, :propietario_id, :tipo_gasto, :monto,
            :descripcion, :kilometraje, :comprobante_url, :fecha_gasto, NOW()
        )
        RETURNING id, created_at
    """)
    result = await db.execute(insert_query, {
        "vehiculo_id": request_data.vehiculo_id,
        "propietario_id": propietario_id,
        "tipo_gasto": request_data.tipo_gasto,
        "monto": request_data.monto,
        "descripcion": request_data.descripcion,
        "kilometraje": request_data.kilometraje,
        "comprobante_url": request_data.comprobante_url,
        "fecha_gasto": request_data.fecha_gasto
    })
    await db.commit()
    row = result.first()
    return GastoVehiculoResponse(
        id=row[0],
        vehiculo_id=request_data.vehiculo_id,
        vehiculo_patente="",
        tipo_gasto=request_data.tipo_gasto,
        monto=request_data.monto,
        descripcion=request_data.descripcion,
        kilometraje=request_data.kilometraje,
        comprobante_url=request_data.comprobante_url,
        fecha_gasto=request_data.fecha_gasto,
        created_at=row[1]
    )


@router.get("/gastos", response_model=list[GastoVehiculoResponse])
# ✅ CORRECTO - request: Request va ANTES de los parámetros con default
async def listar_gastos(
    request: Request,  # <--- PRIMERO (sin default)
    vehiculo_id: UUID = None,
    tipo_gasto: str = None,
    desde: date = None,
    hasta: date = None,
    limit: int = 100,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    filters = ["g.propietario_id = :propietario_id"]
    params = {"propietario_id": propietario_id, "limit": limit, "offset": offset}
    if vehiculo_id:
        filters.append("g.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    if tipo_gasto:
        filters.append("g.tipo_gasto = :tipo_gasto")
        params["tipo_gasto"] = tipo_gasto
    if desde:
        filters.append("g.fecha_gasto >= :desde")
        params["desde"] = desde
    if hasta:
        filters.append("g.fecha_gasto <= :hasta")
        params["hasta"] = hasta
    where_clause = " AND ".join(filters)
    query = text(f"""
        SELECT g.id, g.vehiculo_id, v.patente as vehiculo_patente, g.tipo_gasto, g.monto,
               g.descripcion, g.kilometraje, g.comprobante_url, g.fecha_gasto, g.created_at
        FROM fleet.gasto_vehiculo g
        JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
        WHERE {where_clause}
        ORDER BY g.fecha_gasto DESC, g.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, params)
    rows = result.all()
    return [
        GastoVehiculoResponse(
            id=row[0], vehiculo_id=row[1], vehiculo_patente=row[2], tipo_gasto=row[3],
            monto=float(row[4]), descripcion=row[5], kilometraje=row[6],
            comprobante_url=row[7], fecha_gasto=row[8], created_at=row[9]
        ) for row in rows
    ]


@router.get("/gastos/resumen", response_model=ResumenGastosResponse)
async def resumen_gastos(
    desde: date,
    hasta: date,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    total_query = text("""
        SELECT COALESCE(SUM(monto), 0) FROM fleet.gasto_vehiculo
        WHERE propietario_id = :propietario_id AND fecha_gasto BETWEEN :desde AND :hasta
    """)
    total_result = await db.execute(total_query, {"propietario_id": propietario_id, "desde": desde, "hasta": hasta})
    total = float(total_result.scalar() or 0)
    by_type_query = text("""
        SELECT tipo_gasto, COALESCE(SUM(monto), 0) as total
        FROM fleet.gasto_vehiculo
        WHERE propietario_id = :propietario_id AND fecha_gasto BETWEEN :desde AND :hasta
        GROUP BY tipo_gasto ORDER BY total DESC
    """)
    by_type_result = await db.execute(by_type_query, {"propietario_id": propietario_id, "desde": desde, "hasta": hasta})
    by_type = {row[0]: float(row[1]) for row in by_type_result.all()}
    by_vehicle_query = text("""
        SELECT v.patente, COALESCE(SUM(g.monto), 0) as total
        FROM fleet.gasto_vehiculo g
        JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
        WHERE g.propietario_id = :propietario_id AND g.fecha_gasto BETWEEN :desde AND :hasta
        GROUP BY v.patente ORDER BY total DESC
    """)
    by_vehicle_result = await db.execute(by_vehicle_query, {"propietario_id": propietario_id, "desde": desde, "hasta": hasta})
    by_vehicle = [{"patente": row[0], "total": float(row[1])} for row in by_vehicle_result.all()]
    return ResumenGastosResponse(
        total_gastos=total, por_tipo=by_type, por_vehiculo=by_vehicle,
        periodo_desde=desde, periodo_hasta=hasta
    )


@router.put("/gasto/{gasto_id}")
async def actualizar_gasto(
    gasto_id: UUID,
    request_data: dict,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar un gasto existente"""
    query_check = text("""
        SELECT g.id FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE g.id = :gasto_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_check, {"gasto_id": gasto_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    updates = []
    params = {"gasto_id": gasto_id}
    
    if "tipo_gasto" in request_data:
        updates.append("tipo_gasto = :tipo_gasto")
        params["tipo_gasto"] = request_data["tipo_gasto"]
    if "monto" in request_data:
        updates.append("monto = :monto")
        params["monto"] = request_data["monto"]
    if "descripcion" in request_data:
        updates.append("descripcion = :descripcion")
        params["descripcion"] = request_data["descripcion"]
    if "kilometraje" in request_data:
        updates.append("kilometraje = :kilometraje")
        params["kilometraje"] = request_data["kilometraje"]
    if "fecha_gasto" in request_data:
        updates.append("fecha_gasto = :fecha_gasto")
        params["fecha_gasto"] = request_data["fecha_gasto"]
    
    if updates:
        update_query = text(f"UPDATE fleet.gasto_vehiculo SET {', '.join(updates)} WHERE id = :gasto_id")
        await db.execute(update_query, params)
        await db.commit()
    
    return {"success": True, "message": "Gasto actualizado correctamente"}


@router.delete("/gasto/{gasto_id}")
async def eliminar_gasto(
    gasto_id: UUID,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un gasto"""
    query_check = text("""
        SELECT g.id FROM fleet.gasto_vehiculo g
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = g.vehiculo_id
        WHERE g.id = :gasto_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_check, {"gasto_id": gasto_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    await db.execute(text("DELETE FROM fleet.gasto_vehiculo WHERE id = :gasto_id"), {"gasto_id": gasto_id})
    await db.commit()
    
    return {"success": True, "message": "Gasto eliminado correctamente"}