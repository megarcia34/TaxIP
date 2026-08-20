# app/routers/propietario/vehiculos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
import uuid as uuid_lib
import qrcode
from io import BytesIO
import base64

from app.database import get_db
from app.dependencies import get_propietario_context, get_propietario_id
from app.core.config import settings
from pydantic import BaseModel, Field

router = APIRouter()


class VehiculoCreate(BaseModel):
    patente: str = Field(..., min_length=5, max_length=10)
    marca: str = Field(..., min_length=2, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=50)
    anio: Optional[int] = None
    numero_licencia: Optional[str] = None


class VehiculoUpdate(BaseModel):
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    numero_licencia: Optional[str] = None


class KilometrajeUpdate(BaseModel):
    kilometraje: int = Field(..., ge=0)


@router.get("/vehiculos")
async def listar_vehiculos(
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query = text("""
        SELECT DISTINCT
            v.id, v.patente, v.marca, v.modelo, v.anio, v.numero_licencia,
            v.qr_uuid, v.qr_activo,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_asignado,
            cv.estado_laboral
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true AND pv.propietario_id = :propietario_id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE v.activo = true
        ORDER BY v.patente
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    rows = result.all()
    
    return [
        {
            "id": str(row[0]), "patente": row[1], "marca": row[2],
            "modelo": row[3], "anio": row[4], "numero_licencia": row[5],
            "qr_uuid": str(row[6]), "qr_activo": row[7],
            "chofer_asignado": row[8], "estado_laboral": row[9]
        }
        for row in rows
    ]


@router.post("/vehiculos", status_code=201)
async def crear_vehiculo(
    data: VehiculoCreate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    control_base_id_str = ctx.get("control_base_id")
    if not control_base_id_str:
        raise HTTPException(status_code=400, detail="control_base_id no encontrado en el contexto")
    
    try:
        control_base_id = UUID(control_base_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"control_base_id inválido: {control_base_id_str}")
    
    query_check = text("SELECT id FROM fleet.vehiculo WHERE patente = :patente AND activo = true")
    result = await db.execute(query_check, {"patente": data.patente.upper()})
    if result.first():
        raise HTTPException(status_code=400, detail="Ya existe un vehículo con esa patente")
    
    qr_uuid = uuid_lib.uuid4()
    
    insert_vehiculo = text("""
        INSERT INTO fleet.vehiculo (id, control_base_id, patente, marca, modelo, anio, numero_licencia, qr_uuid, qr_activo, activo, created_at)
        VALUES (gen_random_uuid(), :control_base_id, :patente, :marca, :modelo, :anio, :numero_licencia, :qr_uuid, true, true, NOW())
        RETURNING id
    """)
    result = await db.execute(insert_vehiculo, {
        "control_base_id": control_base_id,
        "patente": data.patente.upper(),
        "marca": data.marca,
        "modelo": data.modelo,
        "anio": data.anio,
        "numero_licencia": data.numero_licencia,
        "qr_uuid": qr_uuid
    })
    vehiculo_id = result.scalar()
    
    insert_relacion = text("""
        INSERT INTO fleet.propietario_vehiculo (id, propietario_id, vehiculo_id, porcentaje_participacion, fecha_inicio, activo, created_at)
        VALUES (gen_random_uuid(), :propietario_id, :vehiculo_id, 100, NOW(), true, NOW())
    """)
    await db.execute(insert_relacion, {"propietario_id": propietario_id, "vehiculo_id": vehiculo_id})
    await db.commit()
    
    qr_url = f"{settings.API_BASE_URL}/public/qr/{qr_uuid}"
    qr_img = qrcode.make(qr_url)
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "success": True,
        "message": "Vehículo creado correctamente",
        "vehiculo_id": str(vehiculo_id),
        "qr_uuid": str(qr_uuid),
        "qr_url": qr_url,
        "qr_base64": qr_base64
    }


@router.get("/vehiculos/{vehiculo_id}")
async def obtener_vehiculo(
    vehiculo_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query = text("""
        SELECT v.id, v.patente, v.marca, v.modelo, v.anio, v.numero_licencia, 
               v.qr_uuid, v.qr_activo, v.activo,
               COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_actual
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return {
        "id": str(row[0]), "patente": row[1], "marca": row[2], "modelo": row[3],
        "anio": row[4], "numero_licencia": row[5],
        "qr_uuid": str(row[6]), "qr_activo": row[7], "activo": row[8],
        "chofer_actual": row[9]
    }


@router.get("/vehiculos/{vehiculo_id}/qr")
async def obtener_qr_vehiculo(
    vehiculo_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query = text("""
        SELECT v.qr_uuid, v.patente
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true AND v.activo = true
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    qr_uuid = row[0]
    patente = row[1]
    
    qr_url = f"{settings.API_BASE_URL}/public/qr/{qr_uuid}"
    qr_img = qrcode.make(qr_url)
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "patente": patente,
        "qr_uuid": str(qr_uuid),
        "qr_url": qr_url,
        "qr_base64": qr_base64
    }


@router.put("/vehiculos/{vehiculo_id}")
async def actualizar_vehiculo(
    vehiculo_id: UUID,
    data: VehiculoUpdate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query_check = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    updates = []
    params = {"vehiculo_id": vehiculo_id}
    
    if data.patente is not None:
        updates.append("patente = :patente")
        params["patente"] = data.patente.upper()
    if data.marca is not None:
        updates.append("marca = :marca")
        params["marca"] = data.marca
    if data.modelo is not None:
        updates.append("modelo = :modelo")
        params["modelo"] = data.modelo
    if data.anio is not None:
        updates.append("anio = :anio")
        params["anio"] = data.anio
    if data.numero_licencia is not None:
        updates.append("numero_licencia = :numero_licencia")
        params["numero_licencia"] = data.numero_licencia
    
    if updates:
        update_query = text(f"UPDATE fleet.vehiculo SET {', '.join(updates)} WHERE id = :vehiculo_id")
        await db.execute(update_query, params)
        await db.commit()
    
    return {"success": True, "message": "Vehículo actualizado correctamente"}


@router.put("/vehiculos/{vehiculo_id}/toggle-qr")
async def toggle_qr_vehiculo(
    vehiculo_id: UUID,
    activo: bool,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query_check = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    await db.execute(
        text("UPDATE fleet.vehiculo SET qr_activo = :activo WHERE id = :vehiculo_id"),
        {"activo": activo, "vehiculo_id": vehiculo_id}
    )
    await db.commit()
    
    return {"success": True, "message": f"QR {'activado' if activo else 'desactivado'} correctamente"}


@router.delete("/vehiculos/{vehiculo_id}")
async def eliminar_vehiculo(
    vehiculo_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    
    query_check = text("""
        SELECT pv.id FROM fleet.propietario_vehiculo pv
        WHERE pv.vehiculo_id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_check, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    query_contrato = text("SELECT id FROM fleet.contrato_vehiculo WHERE vehiculo_id = :vehiculo_id AND activo = true AND fecha_fin IS NULL")
    result = await db.execute(query_contrato, {"vehiculo_id": vehiculo_id})
    if result.first():
        raise HTTPException(status_code=400, detail="No se puede eliminar un vehículo con contratos activos")
    
    await db.execute(text("UPDATE fleet.vehiculo SET activo = false WHERE id = :vehiculo_id"), {"vehiculo_id": vehiculo_id})
    await db.execute(text("UPDATE fleet.propietario_vehiculo SET activo = false, fecha_fin = NOW() WHERE vehiculo_id = :vehiculo_id AND propietario_id = :propietario_id"), {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    await db.commit()
    
    return {"success": True, "message": "Vehículo eliminado correctamente"}


@router.put("/vehiculos/{vehiculo_id}/kilometraje")
async def actualizar_kilometraje(
    vehiculo_id: UUID,
    data: KilometrajeUpdate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = ctx["propietario_id"]
    control_base_id = UUID(ctx["control_base_id"])
    
    query_check = text("SELECT id FROM fleet.chofer_vehiculo WHERE vehiculo_id = :vehiculo_id AND activo = true")
    result = await db.execute(query_check, {"vehiculo_id": vehiculo_id})
    
    if result.first():
        await db.execute(text("UPDATE fleet.chofer_vehiculo SET kilometraje = :kilometraje WHERE vehiculo_id = :vehiculo_id AND activo = true"), {"vehiculo_id": vehiculo_id, "kilometraje": data.kilometraje})
    else:
        await db.execute(text("""
            INSERT INTO fleet.chofer_vehiculo (id, usuario_id, vehiculo_id, control_base_id, kilometraje, activo, created_at)
            VALUES (gen_random_uuid(), :propietario_id, :vehiculo_id, :control_base_id, :kilometraje, true, NOW())
        """), {"propietario_id": propietario_id, "vehiculo_id": vehiculo_id, "control_base_id": control_base_id, "kilometraje": data.kilometraje})
    
    await db.commit()
    return {"success": True, "message": "Kilometraje actualizado correctamente"}


# ============================================================
# ✅ NUEVO ENDPOINT: Estado completo del vehículo
# ============================================================

@router.get("/vehiculos/{vehiculo_id}/estado")
async def obtener_estado_vehiculo(
    vehiculo_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado completo de configuración del vehículo.
    Verifica: neumáticos, documentos (seguro, VTV, cédula) y mantenimientos.
    """
    
    # 1. Verificar que el vehículo pertenece al propietario
    query_vehiculo = text("""
        SELECT v.id, v.patente, v.marca, v.modelo, v.anio
        FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :propietario_id AND pv.activo = true
    """)
    result = await db.execute(query_vehiculo, {
        "vehiculo_id": vehiculo_id,
        "propietario_id": propietario_id
    })
    vehiculo = result.first()
    
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # 2. Verificar neumáticos (4 activos)
    query_neumaticos = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN estado = 'ACTIVO' THEN 1 END) as activos
        FROM fleet.neumatico_vehiculo
        WHERE vehiculo_id = :vehiculo_id
    """)
    result = await db.execute(query_neumaticos, {"vehiculo_id": vehiculo_id})
    neumaticos = result.first()
    
    total_neumaticos = neumaticos[0] if neumaticos else 0
    activos_neumaticos = neumaticos[1] if neumaticos else 0
    tiene_neumaticos = activos_neumaticos >= 4
    
    # 3. Verificar documentos mínimos requeridos (seguro, VTV, cédula)
    query_documentos = text("""
        SELECT 
            tipo_documento,
            fecha_vencimiento,
            CASE 
                WHEN fecha_vencimiento >= CURRENT_DATE THEN true
                ELSE false
            END as vigente
        FROM fleet.documento_vehiculo
        WHERE vehiculo_id = :vehiculo_id AND activo = true
    """)
    result = await db.execute(query_documentos, {"vehiculo_id": vehiculo_id})
    documentos = result.all()
    
    docs_requeridos = ['SEGURO', 'VTV', 'CEDULA']
    docs_presentes = {}
    docs_faltantes = []
    
    for doc in docs_requeridos:
        encontrado = next((d for d in documentos if d[0] == doc), None)
        if encontrado:
            docs_presentes[doc] = {
                "presente": True,
                "vencimiento": encontrado[1].isoformat() if encontrado[1] else None,
                "vigente": encontrado[2]
            }
        else:
            docs_presentes[doc] = {
                "presente": False,
                "vencimiento": None,
                "vigente": False
            }
            docs_faltantes.append(doc)
    
    tiene_documentos = len(docs_faltantes) == 0
    
    # 4. Verificar mantenimientos (al menos uno registrado)
    query_mantenimientos = text("""
        SELECT 
            COUNT(*) as total,
            MAX(fecha_servicio) as ultimo
        FROM fleet.mantenimiento_vehiculo
        WHERE vehiculo_id = :vehiculo_id
    """)
    result = await db.execute(query_mantenimientos, {"vehiculo_id": vehiculo_id})
    mantenimientos = result.first()
    
    total_mantenimientos = mantenimientos[0] if mantenimientos else 0
    ultimo_mantenimiento = mantenimientos[1] if mantenimientos else None
    tiene_mantenimiento = total_mantenimientos > 0
    
    # 5. Estado completo
    configuracion_completa = tiene_neumaticos and tiene_documentos and tiene_mantenimiento
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "patente": vehiculo[1],
        "marca": vehiculo[2],
        "modelo": vehiculo[3],
        "anio": vehiculo[4],
        "estado": "COMPLETO" if configuracion_completa else "PENDIENTE",
        "configuracion_completa": configuracion_completa,
        "neumaticos": {
            "total": total_neumaticos,
            "activos": activos_neumaticos,
            "requeridos": 4,
            "completo": tiene_neumaticos
        },
        "documentos": {
            "total": len(documentos),
            "requeridos": docs_requeridos,
            "faltantes": docs_faltantes,
            "completo": tiene_documentos,
            "lista": docs_presentes
        },
        "mantenimientos": {
            "total": total_mantenimientos,
            "ultimo": ultimo_mantenimiento.isoformat() if ultimo_mantenimiento else None,
            "completo": tiene_mantenimiento
        }
    }