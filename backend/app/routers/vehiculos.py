"""
Vehicle management routes (Admin read-only + suspension)
Los endpoints de creación/edición/eliminación están en el módulo Propietario
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_admin_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/vehiculos", tags=["Vehículos"])


# ============================================
# Schemas
# ============================================

class VehiculoResponse(BaseModel):
    id: UUID
    patente: str
    marca: str
    modelo: str
    anio: Optional[int] = None
    activo: bool
    numero_licencia: Optional[str] = None
    chofer_nombre: Optional[str] = None
    chofer_id: Optional[UUID] = None
    chofer_estado: Optional[str] = None
    propietario_nombre: Optional[str] = None
    propietario_id: Optional[UUID] = None
    tenant_nombre: Optional[str] = None
    contrato_tipo: Optional[str] = None
    contrato_turno: Optional[str] = None
    contrato_estado: Optional[str] = None
    qr_uuid: Optional[str] = None  # Cambiado a str
    qr_activo: Optional[bool] = None


class SuspenderVehiculoRequest(BaseModel):
    motivo: str
    tipo_suspension: str  # PAGO, MANTENIMIENTO, INFRACCION, OTRO
    fecha_fin: Optional[datetime] = None


class SuspensionVehiculoResponse(BaseModel):
    id: UUID
    vehiculo_id: UUID
    patente: str
    suspendido_por: UUID
    suspendido_por_nombre: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    motivo: str
    tipo_suspension: str
    activo: bool
    creado_en: datetime


# ============================================
# READ-ONLY ENDPOINTS
# ============================================

@router.get("/lista", response_model=List[VehiculoResponse])
async def listar_vehiculos(
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    activo: Optional[bool] = None
):
    """
    Listar todos los vehículos con propietario, chofer y tenant
    (SOLO LECTURA - Admin)
    """
    control_base_id = current_user[1]
    
    params = {
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }
    
    filters = ["v.control_base_id = :control_base_id"]
    
    if activo is not None:
        filters.append("v.activo = :activo")
        params["activo"] = activo
    
    where_clause = " AND ".join(filters)
    
    query = text(f"""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            v.activo,
            v.numero_licencia,
            v.qr_uuid,
            v.qr_activo,
            -- Chofer actual
            COALESCE(pchofer.nombre || ' ' || pchofer.apellido, uchofer.email) as chofer_nombre,
            uchofer.id as chofer_id,
            cv.estado_laboral as chofer_estado,
            -- Propietario actual
            COALESCE(pprop.nombre || ' ' || pprop.apellido, uprop.email) as propietario_nombre,
            uprop.id as propietario_id,
            -- Tenant
            cb.nombre as tenant_nombre,
            -- Contrato
            c.tipo_contrato as contrato_tipo,
            c.turno_asignado as contrato_turno,
            c.estado_contrato as contrato_estado,
            -- Fechas
            v.created_at
        FROM fleet.vehiculo v
        LEFT JOIN tenant.control_base cb ON cb.id = v.control_base_id
        -- Chofer actual
        LEFT JOIN fleet.contrato_vehiculo c ON c.vehiculo_id = v.id AND c.estado_contrato = 'ACTIVO'
        LEFT JOIN auth.usuario uchofer ON uchofer.id = c.chofer_id
        LEFT JOIN auth.perfil_general pchofer ON pchofer.usuario_id = uchofer.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = uchofer.id
        -- Propietario actual
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario uprop ON uprop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general pprop ON pprop.usuario_id = uprop.id
        WHERE {where_clause}
        ORDER BY v.patente ASC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        VehiculoResponse(
            id=row[0],
            patente=row[1],
            marca=row[2],
            modelo=row[3],
            anio=row[4],
            activo=row[5],
            numero_licencia=row[6],
            qr_uuid=str(row[7]) if row[7] else None,  # Convertir UUID a str
            qr_activo=row[8],
            chofer_nombre=row[9],
            chofer_id=row[10],
            chofer_estado=row[11],
            propietario_nombre=row[12],
            propietario_id=row[13],
            tenant_nombre=row[14],
            contrato_tipo=row[15],
            contrato_turno=row[16],
            contrato_estado=row[17]
        )
        for row in rows
    ]


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(
    vehiculo_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle de un vehículo específico (SOLO LECTURA)
    """
    control_base_id = current_user[1]
    
    query = text("""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            v.activo,
            v.numero_licencia,
            v.qr_uuid,
            v.qr_activo,
            -- Chofer actual
            COALESCE(pchofer.nombre || ' ' || pchofer.apellido, uchofer.email) as chofer_nombre,
            uchofer.id as chofer_id,
            cv.estado_laboral as chofer_estado,
            -- Propietario actual
            COALESCE(pprop.nombre || ' ' || pprop.apellido, uprop.email) as propietario_nombre,
            uprop.id as propietario_id,
            -- Tenant
            cb.nombre as tenant_nombre,
            -- Contrato
            c.tipo_contrato as contrato_tipo,
            c.turno_asignado as contrato_turno,
            c.estado_contrato as contrato_estado,
            c.fecha_inicio as contrato_inicio,
            c.fecha_fin as contrato_fin,
            -- Fechas
            v.created_at
        FROM fleet.vehiculo v
        LEFT JOIN tenant.control_base cb ON cb.id = v.control_base_id
        -- Chofer actual
        LEFT JOIN fleet.contrato_vehiculo c ON c.vehiculo_id = v.id AND c.estado_contrato = 'ACTIVO'
        LEFT JOIN auth.usuario uchofer ON uchofer.id = c.chofer_id
        LEFT JOIN auth.perfil_general pchofer ON pchofer.usuario_id = uchofer.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = uchofer.id
        -- Propietario actual
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario uprop ON uprop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general pprop ON pprop.usuario_id = uprop.id
        WHERE v.id = :vehiculo_id AND v.control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return VehiculoResponse(
        id=row[0],
        patente=row[1],
        marca=row[2],
        modelo=row[3],
        anio=row[4],
        activo=row[5],
        numero_licencia=row[6],
        qr_uuid=str(row[7]) if row[7] else None,  # Convertir UUID a str
        qr_activo=row[8],
        chofer_nombre=row[9],
        chofer_id=row[10],
        chofer_estado=row[11],
        propietario_nombre=row[12],
        propietario_id=row[13],
        tenant_nombre=row[14],
        contrato_tipo=row[15],
        contrato_turno=row[16],
        contrato_estado=row[17]
    )


# ============================================
# VER QR (Público)
# ============================================

@router.get("/{vehiculo_id}/qr")
async def obtener_qr_vehiculo(
    vehiculo_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener URL del QR del vehículo
    """
    control_base_id = current_user[1]
    
    query = text("""
        SELECT qr_uuid, qr_activo
        FROM fleet.vehiculo
        WHERE id = :vehiculo_id AND control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    qr_uuid = str(row[0]) if row[0] else None
    
    return {
        "vehiculo_id": str(vehiculo_id),
        "qr_uuid": qr_uuid,
        "qr_activo": row[1],
        "qr_url": f"/public/qr/{qr_uuid}" if qr_uuid and row[1] else None,
        "mensaje": "QR activo" if row[1] else "QR inactivo"
    }


# ============================================
# SUSPENSIÓN DE VEHÍCULOS
# ============================================

@router.post("/{vehiculo_id}/suspender", response_model=SuspensionVehiculoResponse)
async def suspender_vehiculo(
    vehiculo_id: UUID,
    request: SuspenderVehiculoRequest,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Suspender un vehículo por falta de pago, mantenimiento, etc.
    El vehículo no podrá ser asignado a choferes mientras esté suspendido.
    """
    admin_id, control_base_id, _, _ = current_user
    
    # 1. Verificar que el vehículo existe y pertenece al tenant
    check_query = text("""
        SELECT id, patente, activo FROM fleet.vehiculo
        WHERE id = :vehiculo_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    vehiculo = result.first()
    
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    vehiculo_id_str, patente, activo = vehiculo
    
    if not activo:
        raise HTTPException(status_code=400, detail="El vehículo ya está inactivo")
    
    # 2. Verificar que no tenga una suspensión activa
    check_suspension = text("""
        SELECT id FROM fleet.suspension_vehiculo
        WHERE vehiculo_id = :vehiculo_id AND activo = true
    """)
    result = await db.execute(check_suspension, {"vehiculo_id": vehiculo_id})
    if result.first():
        raise HTTPException(status_code=400, detail="El vehículo ya tiene una suspensión activa")
    
    # 3. Validar tipo de suspensión
    tipos_validos = ["PAGO", "MANTENIMIENTO", "INFRACCION", "OTRO"]
    if request.tipo_suspension.upper() not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de suspensión inválido. Permitidos: {', '.join(tipos_validos)}"
        )
    
    # 4. Crear la suspensión
    insert_query = text("""
        INSERT INTO fleet.suspension_vehiculo (
            id, vehiculo_id, suspendido_por, motivo, tipo_suspension, 
            fecha_inicio, fecha_fin, activo, created_at
        )
        VALUES (
            gen_random_uuid(), :vehiculo_id, :suspendido_por, :motivo, :tipo_suspension,
            NOW(), :fecha_fin, true, NOW()
        )
        RETURNING id, created_at
    """)
    
    result = await db.execute(insert_query, {
        "vehiculo_id": vehiculo_id,
        "suspendido_por": admin_id,
        "motivo": request.motivo,
        "tipo_suspension": request.tipo_suspension.upper(),
        "fecha_fin": request.fecha_fin
    })
    row = result.first()
    suspension_id = row[0]
    created_at = row[1]
    
    # 5. Desactivar el vehículo
    update_vehiculo = text("""
        UPDATE fleet.vehiculo
        SET activo = false, updated_at = NOW()
        WHERE id = :vehiculo_id
    """)
    await db.execute(update_vehiculo, {"vehiculo_id": vehiculo_id})
    
    # 6. Si tiene contrato activo, notificar
    contrato_query = text("""
        SELECT c.id, c.chofer_id, COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre
        FROM fleet.contrato_vehiculo c
        LEFT JOIN auth.usuario u ON u.id = c.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE c.vehiculo_id = :vehiculo_id AND c.estado_contrato = 'ACTIVO'
    """)
    contrato_result = await db.execute(contrato_query, {"vehiculo_id": vehiculo_id})
    contrato = contrato_result.first()
    
    if contrato:
        # Crear notificación para el chofer
        insert_notificacion = text("""
            INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
            VALUES (
                gen_random_uuid(), :chofer_id, 
                'Vehículo suspendido', 
                'El vehículo ' || :patente || ' ha sido suspendido por: ' || :motivo,
                'suspension_vehiculo', false, NOW()
            )
        """)
        await db.execute(insert_notificacion, {
            "chofer_id": contrato[1],
            "patente": patente,
            "motivo": request.motivo
        })
    
    await db.commit()
    
    # 7. Retornar respuesta
    return SuspensionVehiculoResponse(
        id=suspension_id,
        vehiculo_id=vehiculo_id,
        patente=patente,
        suspendido_por=admin_id,
        suspendido_por_nombre=current_user[2] if len(current_user) > 2 else "Admin",
        fecha_inicio=datetime.now(),
        fecha_fin=request.fecha_fin,
        motivo=request.motivo,
        tipo_suspension=request.tipo_suspension.upper(),
        activo=True,
        creado_en=created_at
    )


@router.post("/{vehiculo_id}/reactivar")
async def reactivar_vehiculo(
    vehiculo_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivar un vehículo suspendido (fin de la suspensión)
    """
    admin_id, control_base_id, _, _ = current_user
    
    # 1. Verificar que el vehículo existe
    check_query = text("""
        SELECT id, patente, activo FROM fleet.vehiculo
        WHERE id = :vehiculo_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    vehiculo = result.first()
    
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    if vehiculo[2]:
        raise HTTPException(status_code=400, detail="El vehículo ya está activo")
    
    # 2. Buscar suspensión activa
    suspension_query = text("""
        SELECT id FROM fleet.suspension_vehiculo
        WHERE vehiculo_id = :vehiculo_id AND activo = true
    """)
    result = await db.execute(suspension_query, {"vehiculo_id": vehiculo_id})
    suspension = result.first()
    
    if not suspension:
        raise HTTPException(status_code=400, detail="El vehículo no tiene una suspensión activa")
    
    suspension_id = suspension[0]
    
    # 3. Finalizar la suspensión
    update_suspension = text("""
        UPDATE fleet.suspension_vehiculo
        SET fecha_fin = NOW(), activo = false, updated_at = NOW()
        WHERE id = :suspension_id
    """)
    await db.execute(update_suspension, {"suspension_id": suspension_id})
    
    # 4. Reactivar el vehículo
    update_vehiculo = text("""
        UPDATE fleet.vehiculo
        SET activo = true, updated_at = NOW()
        WHERE id = :vehiculo_id
    """)
    await db.execute(update_vehiculo, {"vehiculo_id": vehiculo_id})
    
    # 5. Notificar al chofer si tiene contrato activo
    contrato_query = text("""
        SELECT c.chofer_id, COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre
        FROM fleet.contrato_vehiculo c
        LEFT JOIN auth.usuario u ON u.id = c.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE c.vehiculo_id = :vehiculo_id AND c.estado_contrato = 'ACTIVO'
    """)
    contrato_result = await db.execute(contrato_query, {"vehiculo_id": vehiculo_id})
    contrato = contrato_result.first()
    
    if contrato:
        insert_notificacion = text("""
            INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
            VALUES (
                gen_random_uuid(), :chofer_id, 
                'Vehículo reactivado', 
                'El vehículo ' || :patente || ' ha sido reactivado',
                'reactivacion_vehiculo', false, NOW()
            )
        """)
        await db.execute(insert_notificacion, {
            "chofer_id": contrato[0],
            "patente": vehiculo[1]
        })
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"Vehículo {vehiculo[1]} reactivado correctamente",
        "vehiculo_id": str(vehiculo_id),
        "suspension_id": str(suspension_id)
    }


@router.get("/{vehiculo_id}/suspensiones")
async def listar_suspensiones_vehiculo(
    vehiculo_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    activas: Optional[bool] = None
):
    """
    Listar el historial de suspensiones de un vehículo
    """
    control_base_id = current_user[1]
    
    # Verificar que el vehículo existe
    check_query = text("""
        SELECT id FROM fleet.vehiculo
        WHERE id = :vehiculo_id AND control_base_id = :control_base_id
    """)
    result = await db.execute(check_query, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    params = {"vehiculo_id": vehiculo_id}
    filtro_activo = ""
    
    if activas is not None:
        filtro_activo = "AND s.activo = :activo"
        params["activo"] = activas
    
    query = text(f"""
        SELECT 
            s.id,
            s.vehiculo_id,
            s.suspendido_por,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as suspendido_por_nombre,
            s.fecha_inicio,
            s.fecha_fin,
            s.motivo,
            s.tipo_suspension,
            s.activo,
            s.created_at
        FROM fleet.suspension_vehiculo s
        JOIN auth.usuario u ON u.id = s.suspendido_por
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE s.vehiculo_id = :vehiculo_id
        {filtro_activo}
        ORDER BY s.created_at DESC
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "vehiculo_id": str(row[1]),
            "suspendido_por": str(row[2]),
            "suspendido_por_nombre": row[3],
            "fecha_inicio": row[4],
            "fecha_fin": row[5],
            "motivo": row[6],
            "tipo_suspension": row[7],
            "activo": row[8],
            "created_at": row[9]
        }
        for row in rows
    ]


@router.get("/suspensiones/activas")
async def listar_suspensiones_activas(
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """
    Listar todas las suspensiones activas del tenant
    """
    control_base_id = current_user[1]
    
    query = text("""
        SELECT 
            s.id,
            s.vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            s.suspendido_por,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as suspendido_por_nombre,
            s.fecha_inicio,
            s.motivo,
            s.tipo_suspension,
            s.created_at,
            -- Chofer asignado
            COALESCE(pc.nombre || ' ' || pc.apellido, uc.email) as chofer_nombre
        FROM fleet.suspension_vehiculo s
        JOIN fleet.vehiculo v ON v.id = s.vehiculo_id
        JOIN auth.usuario u ON u.id = s.suspendido_por
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.contrato_vehiculo c ON c.vehiculo_id = v.id AND c.estado_contrato = 'ACTIVO'
        LEFT JOIN auth.usuario uc ON uc.id = c.chofer_id
        LEFT JOIN auth.perfil_general pc ON pc.usuario_id = uc.id
        WHERE s.activo = true AND v.control_base_id = :control_base_id
        ORDER BY s.created_at DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {
        "control_base_id": control_base_id,
        "limit": limit
    })
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "vehiculo_id": str(row[1]),
            "patente": row[2],
            "vehiculo": f"{row[3]} {row[4]}",
            "suspendido_por": str(row[5]),
            "suspendido_por_nombre": row[6],
            "fecha_inicio": row[7],
            "motivo": row[8],
            "tipo_suspension": row[9],
            "created_at": row[10],
            "chofer_asignado": row[11]
        }
        for row in rows
    ]