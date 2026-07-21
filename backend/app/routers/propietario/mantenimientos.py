from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta, date

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.schemas.propietario_schemas import (
    MantenimientoVehiculoRequest,
    MantenimientoVehiculoResponse
)

router = APIRouter()

PERIODICIDAD_MANTENIMIENTO = {
    "SERVICE_MENOR": {"km": 5000, "dias": 90, "alerta_a": "chofer"},
    "SERVICE_MAYOR": {"km": 20000, "dias": 365, "alerta_a": "dueno"},
    "NEUMATICOS": {"km": 10000, "dias": None, "alerta_a": "chofer"},
    "FRENOS": {"km": 15000, "dias": None, "alerta_a": "chofer"},
    "DISTRIBUCION": {"km": 60000, "dias": None, "alerta_a": "dueno"},
    "ALINEACION": {"km": 10000, "dias": 180, "alerta_a": "chofer"},
    "CAMBIO_ACEITE": {"km": 5000, "dias": 180, "alerta_a": "chofer"},
    "LUBRICACION": {"km": 5000, "dias": 180, "alerta_a": "chofer"},
    "ELECTRICO": {"km": None, "dias": 365, "alerta_a": "dueno"},
    "GENERAL": {"km": 10000, "dias": 180, "alerta_a": "chofer"},
}


@router.post("/mantenimiento", response_model=MantenimientoVehiculoResponse)
async def registrar_mantenimiento(
    request_data: MantenimientoVehiculoRequest,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    verify_query = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(verify_query, {
        "vehiculo_id": request_data.vehiculo_id,
        "propietario_id": propietario_id  # ✅ Ya es UUID
    })
    if not result.first():
        raise HTTPException(status_code=403, detail="Vehículo no pertenece al propietario")
    
    insert_query = text("""
        INSERT INTO fleet.mantenimiento_vehiculo (
            id, vehiculo_id, propietario_id, tipo_servicio, taller_nombre,
            taller_direccion, costo, kilometraje, observaciones, fecha_servicio, created_at
        )
        VALUES (
            gen_random_uuid(), :vehiculo_id, :propietario_id, :tipo_servicio, :taller_nombre,
            :taller_direccion, :costo, :kilometraje, :observaciones, :fecha_servicio, NOW()
        )
        RETURNING id, created_at
    """)
    result = await db.execute(insert_query, {
        "vehiculo_id": request_data.vehiculo_id,
        "propietario_id": propietario_id,  # ✅ Ya es UUID
        "tipo_servicio": request_data.tipo_servicio,
        "taller_nombre": request_data.taller_nombre,
        "taller_direccion": request_data.taller_direccion,
        "costo": request_data.costo,
        "kilometraje": request_data.kilometraje,
        "observaciones": request_data.observaciones,
        "fecha_servicio": request_data.fecha_servicio
    })
    await db.commit()
    row = result.first()
    return MantenimientoVehiculoResponse(
        id=row[0], vehiculo_id=request_data.vehiculo_id, vehiculo_patente="",
        tipo_servicio=request_data.tipo_servicio, taller_nombre=request_data.taller_nombre,
        taller_direccion=request_data.taller_direccion, costo=request_data.costo,
        kilometraje=request_data.kilometraje, observaciones=request_data.observaciones,
        fecha_servicio=request_data.fecha_servicio, created_at=row[1]
    )


@router.get("/mantenimientos", response_model=list[MantenimientoVehiculoResponse])
async def listar_mantenimientos(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    vehiculo_id: Optional[UUID] = None,
    limit: int = 100,
    offset: int = 0,
):
    filters = ["m.propietario_id = :propietario_id"]
    params = {"propietario_id": propietario_id, "limit": limit, "offset": offset}  # ✅ Ya es UUID
    if vehiculo_id:
        filters.append("m.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    where_clause = " AND ".join(filters)
    query = text(f"""
        SELECT m.id, m.vehiculo_id, v.patente as vehiculo_patente, m.tipo_servicio,
               m.taller_nombre, m.taller_direccion, m.costo, m.kilometraje,
               m.observaciones, m.fecha_servicio, m.created_at
        FROM fleet.mantenimiento_vehiculo m
        JOIN fleet.vehiculo v ON v.id = m.vehiculo_id
        WHERE {where_clause}
        ORDER BY m.fecha_servicio DESC, m.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, params)
    rows = result.all()
    return [
        MantenimientoVehiculoResponse(
            id=row[0], vehiculo_id=row[1], vehiculo_patente=row[2], tipo_servicio=row[3],
            taller_nombre=row[4], taller_direccion=row[5], costo=float(row[6]) if row[6] else None,
            kilometraje=row[7], observaciones=row[8], fecha_servicio=row[9], created_at=row[10]
        ) for row in rows
    ]


@router.get("/mantenimientos/proximo")
async def calcular_proximo_mantenimiento(
    vehiculo_id: UUID,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query_vehiculo = text("""
        SELECT v.id, v.patente, COALESCE(cv.kilometraje, 0) as km_actual
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_vehiculo, {
        "vehiculo_id": vehiculo_id,
        "propietario_id": propietario_id  # ✅ Ya es UUID
    })
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    vehiculo_id_str, patente, km_actual = row
    km_actual = km_actual or 0
    
    query_ultimo = text("""
        SELECT tipo_servicio, kilometraje, fecha_servicio
        FROM fleet.mantenimiento_vehiculo
        WHERE vehiculo_id = :vehiculo_id
        ORDER BY fecha_servicio DESC, created_at DESC
        LIMIT 1
    """)
    result = await db.execute(query_ultimo, {"vehiculo_id": vehiculo_id})
    ultimo = result.first()
    
    proximos = []
    for tipo, config in PERIODICIDAD_MANTENIMIENTO.items():
        if config.get("km"):
            km_proximo = (ultimo.kilometraje if ultimo else 0) + config["km"]
            km_restante = max(0, km_proximo - km_actual)
        else:
            km_restante = None
        
        if config.get("dias"):
            fecha_base = ultimo.fecha_servicio if ultimo else datetime.now().date()
            fecha_proximo = fecha_base + timedelta(days=config["dias"])
            dias_restantes = max(0, (fecha_proximo - datetime.now().date()).days)
        else:
            dias_restantes = None
        
        if (km_restante is not None and km_restante <= 1000) or (dias_restantes is not None and dias_restantes <= 15):
            proximos.append({
                "tipo_servicio": tipo,
                "tipo_nombre": tipo.replace("_", " ").title(),
                "km_restante": km_restante,
                "dias_restantes": dias_restantes,
                "alerta_a": config["alerta_a"],
                "urgencia": "alta" if (km_restante is not None and km_restante <= 500) or (dias_restantes is not None and dias_restantes <= 7) else "media"
            })
    
    proximos.sort(key=lambda x: 0 if x["urgencia"] == "alta" else 1)
    
    return {
        "vehiculo_id": str(vehiculo_id_str),
        "patente": patente,
        "km_actual": km_actual,
        "mantenimientos_proximos": proximos[:5]
    }


@router.get("/mantenimientos/alertas")
async def obtener_alertas_mantenimiento(
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query_vehiculos = text("""
        SELECT DISTINCT v.id, v.patente
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id AND v.activo = true
    """)
    result = await db.execute(query_vehiculos, {
        "propietario_id": propietario_id  # ✅ Ya es UUID
    })
    vehiculos = result.all()
    
    todas_alertas = []
    for vehiculo in vehiculos:
        try:
            proximo = await calcular_proximo_mantenimiento(
                vehiculo[0], request, propietario_id, current_user, db
            )
            if proximo.get("mantenimientos_proximos"):
                todas_alertas.append(proximo)
        except Exception:
            pass
    
    return {
        "total_alertas": sum(len(v["mantenimientos_proximos"]) for v in todas_alertas),
        "vehiculos_con_alertas": todas_alertas
    }


@router.post("/mantenimientos/{mantenimiento_id}/comprobante")
async def subir_comprobante_mantenimiento(
    mantenimiento_id: UUID,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),  # ✅ Ya es UUID
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query_check = text("""
        SELECT m.id FROM fleet.mantenimiento_vehiculo m
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = m.vehiculo_id
        WHERE m.id = :mantenimiento_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_check, {
        "mantenimiento_id": mantenimiento_id,
        "propietario_id": propietario_id  # ✅ Ya es UUID
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    
    return {"message": "Funcionalidad de subida de archivos pendiente de implementar"}