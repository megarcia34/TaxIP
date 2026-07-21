from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id

router = APIRouter()


class DocumentoCreate(BaseModel):
    tipo_documento: str
    numero: str
    fecha_emision: date
    fecha_vencimiento: date
    observaciones: Optional[str] = None


@router.post("/vehiculos/{vehiculo_id}/documentos")
async def subir_documento(
    vehiculo_id: UUID,
    data: DocumentoCreate,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query_check = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    insert_query = text("""
        INSERT INTO fleet.documento_vehiculo (
            id, vehiculo_id, tipo_documento, numero, fecha_emision, fecha_vencimiento,
            observaciones, url_archivo, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :vehiculo_id, :tipo_documento, :numero, :fecha_emision, :fecha_vencimiento,
            :observaciones, :url_archivo, NOW(), NOW()
        )
        RETURNING id
    """)
    result = await db.execute(insert_query, {
        "vehiculo_id": vehiculo_id,
        "tipo_documento": data.tipo_documento,
        "numero": data.numero,
        "fecha_emision": data.fecha_emision,
        "fecha_vencimiento": data.fecha_vencimiento,
        "observaciones": data.observaciones,
        "url_archivo": None
    })
    doc_id = result.scalar()
    await db.commit()
    
    return {"success": True, "message": "Documento subido correctamente", "documento_id": str(doc_id)}


@router.get("/vehiculos/{vehiculo_id}/documentos")
async def listar_documentos(
    vehiculo_id: UUID,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query = text("""
        SELECT id, tipo_documento, numero, fecha_emision, fecha_vencimiento,
               observaciones, url_archivo, created_at
        FROM fleet.documento_vehiculo
        WHERE vehiculo_id = :vehiculo_id
        ORDER BY fecha_vencimiento ASC, created_at DESC
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id})
    rows = result.all()
    
    hoy = datetime.now().date()
    documentos = []
    for row in rows:
        dias = (row[4] - hoy).days if row[4] else None
        documentos.append({
            "id": str(row[0]),
            "tipo_documento": row[1],
            "numero": row[2],
            "fecha_emision": row[3].isoformat() if row[3] else None,
            "fecha_vencimiento": row[4].isoformat() if row[4] else None,
            "observaciones": row[5],
            "url_archivo": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "dias_para_vencer": dias if dias is not None else None,
            "estado": "vigente" if dias and dias > 30 else "proximo" if dias and dias > 0 else "vencido"
        })
    
    return documentos


@router.delete("/vehiculos/documentos/{documento_id}")
async def eliminar_documento(
    documento_id: UUID,
    request: Request,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query_check = text("""
        SELECT d.id FROM fleet.documento_vehiculo d
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = d.vehiculo_id
        WHERE d.id = :documento_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_check, {"documento_id": documento_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    await db.execute(text("DELETE FROM fleet.documento_vehiculo WHERE id = :documento_id"), {"documento_id": documento_id})
    await db.commit()
    
    return {"success": True, "message": "Documento eliminado correctamente"}


@router.get("/documentos/vencimientos")
async def alertas_vencimiento(
    request: Request,
    dias_previos: int = Query(30, description="Días antes del vencimiento para alertar"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id, control_base_id, email, tipo = current_user
    
    query = text("""
        SELECT 
            d.id, d.tipo_documento, d.numero, d.fecha_vencimiento,
            v.patente,
            d.fecha_vencimiento - NOW()::date as dias_restantes
        FROM fleet.documento_vehiculo d
        INNER JOIN fleet.vehiculo v ON v.id = d.vehiculo_id
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND d.fecha_vencimiento IS NOT NULL
          AND d.fecha_vencimiento - NOW()::date <= :dias_previos
          AND d.fecha_vencimiento >= NOW()::date
        ORDER BY d.fecha_vencimiento ASC
    """)
    result = await db.execute(query, {"propietario_id": propietario_id, "dias_previos": dias_previos})
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "tipo_documento": row[1],
            "numero": row[2],
            "fecha_vencimiento": row[3].isoformat() if row[3] else None,
            "patente": row[4],
            "dias_restantes": row[5]
        }
        for row in rows
    ]