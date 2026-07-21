"""
Driver management routes (Admin CRUD + driver actions)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import uuid as uuid_lib

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user, get_current_driver_user
from app.core.security import get_password_hash
from app.schemas.chofer_schemas import (
    ChoferCreateRequest,
    ChoferUpdateRequest,
    ChoferResponse,
    ActualizarUbicacionRequest,
    CambiarEstadoLaboralRequest
)
from datetime import datetime
from app.services.turno_service import TurnoService
from app.schemas.turno_schemas import (
    CheckInRequest,
    CheckOutRequest,
    GastoRequest,
    TurnoActivoResponse,
    TurnoResponse
)

router = APIRouter(prefix="/api/choferes", tags=["Choferes"])


# ============================================
# ADMIN CRUD
# ============================================

@router.get("/lista", response_model=list[ChoferResponse])
async def listar_choferes(
    estado_laboral: str = None,
    activo: bool = None,
    limit: int = 100,
    offset: int = 0,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all drivers with total trips, rating, vehicle and tenant info
    """
    control_base_id = current_user[1]
    
    filters = ["cv.control_base_id = :control_base_id"]
    params = {"control_base_id": control_base_id, "limit": limit, "offset": offset}
    
    if estado_laboral:
        filters.append("cv.estado_laboral = :estado_laboral")
        params["estado_laboral"] = estado_laboral
    
    if activo is not None:
        filters.append("cv.activo = :activo")
        params["activo"] = activo
    
    where_clause = " AND ".join(filters)
    
    query = text(f"""
        SELECT 
            u.id,
            u.email,
            p.nombre,
            p.apellido,
            p.telefono,
            cv.estado_laboral,
            cv.calificacion_promedio,
            cv.total_calificaciones,
            cv.total_viajes,
            cv.ultima_conexion,
            cv.activo,
            v.id as vehiculo_id,
            v.patente as vehiculo_patente,
            v.marca as vehiculo_marca,
            v.modelo as vehiculo_modelo,
            v.anio as vehiculo_anio,
            cv.latitud,
            cv.longitud,
            cb.nombre as tenant_nombre,
            COALESCE(pprop.nombre || ' ' || pprop.apellido, uprop.email) as propietario_nombre
        FROM fleet.chofer_vehiculo cv
        JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario uprop ON uprop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general pprop ON pprop.usuario_id = uprop.id
        LEFT JOIN tenant.control_base cb ON cb.id = cv.control_base_id
        WHERE {where_clause}
        ORDER BY cv.total_viajes DESC, cv.calificacion_promedio DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        ChoferResponse(
            id=row[0],
            email=row[1],
            nombre=row[2],
            apellido=row[3],
            telefono=row[4],
            estado_laboral=row[5],
            calificacion_promedio=float(row[6]) if row[6] else 5.0,
            total_calificaciones=row[7] or 0,
            total_viajes=row[8] or 0,
            ultima_conexion=row[9],
            activo=row[10],
            vehiculo_id=row[11],
            vehiculo_patente=row[12],
            vehiculo_marca=row[13],
            vehiculo_modelo=row[14],
            vehiculo_anio=row[15],
            ubicacion_lat=float(row[16]) if row[16] else None,
            ubicacion_lng=float(row[17]) if row[17] else None,
            tenant_nombre=row[18],
            propietario_nombre=row[19]
        )
        for row in rows
    ]


@router.get("/{chofer_id}", response_model=ChoferResponse)
async def obtener_chofer(
    chofer_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get driver details with all information
    """
    query = text("""
        SELECT 
            u.id,
            u.email,
            p.nombre,
            p.apellido,
            p.telefono,
            cv.estado_laboral,
            cv.calificacion_promedio,
            cv.total_calificaciones,
            cv.total_viajes,
            cv.ultima_conexion,
            cv.activo,
            v.id as vehiculo_id,
            v.patente as vehiculo_patente,
            v.marca as vehiculo_marca,
            v.modelo as vehiculo_modelo,
            v.anio as vehiculo_anio,
            cv.latitud,
            cv.longitud,
            cb.nombre as tenant_nombre,
            COALESCE(pprop.nombre || ' ' || pprop.apellido, uprop.email) as propietario_nombre
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario uprop ON uprop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general pprop ON pprop.usuario_id = uprop.id
        LEFT JOIN tenant.control_base cb ON cb.id = cv.control_base_id
        WHERE u.id = :chofer_id AND tu.nombre = 'chofer'
        GROUP BY 
            u.id, u.email, p.nombre, p.apellido, p.telefono, 
            cv.estado_laboral, cv.calificacion_promedio, cv.total_calificaciones,
            cv.total_viajes, cv.ultima_conexion, cv.activo,
            v.id, v.patente, v.marca, v.modelo, v.anio,
            cv.latitud, cv.longitud, cb.nombre,
            pprop.nombre, pprop.apellido, uprop.email
    """)
    
    result = await db.execute(query, {"chofer_id": chofer_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    return ChoferResponse(
        id=row[0],
        email=row[1],
        nombre=row[2],
        apellido=row[3],
        telefono=row[4],
        estado_laboral=row[5],
        calificacion_promedio=float(row[6]) if row[6] else 5.0,
        total_calificaciones=row[7] or 0,
        total_viajes=row[8] or 0,
        ultima_conexion=row[9],
        activo=row[10],
        vehiculo_id=row[11],
        vehiculo_patente=row[12],
        vehiculo_marca=row[13],
        vehiculo_modelo=row[14],
        vehiculo_anio=row[15],
        ubicacion_lat=float(row[16]) if row[16] else None,
        ubicacion_lng=float(row[17]) if row[17] else None,
        tenant_nombre=row[18],
        propietario_nombre=row[19]
    )


@router.post("/crear")
async def crear_chofer(
    request: ChoferCreateRequest,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new driver with vehicle (Admin only)
    """
    control_base_id = current_user[1]
    
    # Check if email exists
    check_query = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_query, {"email": request.email})
    if result.first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Get tipo_usuario ID for 'chofer'
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer'")
    tipo_result = await db.execute(tipo_query)
    tipo_id = tipo_result.scalar()
    
    # Create user
    user_id = uuid_lib.uuid4()
    hashed_password = get_password_hash(request.password)
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, control_base_id, tipo_usuario_id, email, password_hash, activo, created_at, updated_at)
        VALUES (:id, :control_base_id, :tipo_id, :email, :password_hash, true, NOW(), NOW())
    """)
    
    await db.execute(insert_user, {
        "id": user_id,
        "control_base_id": control_base_id,
        "tipo_id": tipo_id,
        "email": request.email,
        "password_hash": hashed_password
    })
    
    # Create profile
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, documento, created_at)
        VALUES (gen_random_uuid(), :user_id, :nombre, :apellido, :telefono, :documento, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "user_id": user_id,
        "nombre": request.nombre,
        "apellido": request.apellido,
        "telefono": request.telefono,
        "documento": request.documento
    })
    
    # Create vehicle (only with columns that exist)
    insert_vehiculo = text("""
        INSERT INTO fleet.vehiculo (id, control_base_id, patente, marca, modelo, anio, activo, created_at)
        VALUES (gen_random_uuid(), :control_base_id, :patente, :marca, :modelo, :anio, true, NOW())
        RETURNING id
    """)
    
    vehiculo_result = await db.execute(insert_vehiculo, {
        "control_base_id": control_base_id,
        "patente": request.vehiculo_patente,
        "marca": request.vehiculo_marca,
        "modelo": request.vehiculo_modelo,
        "anio": request.vehiculo_anio
    })
    vehiculo_id = vehiculo_result.scalar()
    
    # Link driver to vehicle
    insert_link = text("""
        INSERT INTO fleet.chofer_vehiculo (id, usuario_id, vehiculo_id, control_base_id, estado_laboral, activo, created_at)
        VALUES (gen_random_uuid(), :usuario_id, :vehiculo_id, :control_base_id, 'libre', true, NOW())
    """)
    
    await db.execute(insert_link, {
        "usuario_id": user_id,
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    
    await db.commit()
    
    return {"success": True, "message": "Chofer creado exitosamente", "user_id": user_id}


@router.put("/modificar/{chofer_id}")
async def modificar_chofer(
    chofer_id: UUID,
    request: ChoferUpdateRequest,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update driver information (Admin only)
    """
    # Update profile
    updates = []
    params = {"chofer_id": chofer_id}
    
    if request.nombre is not None:
        updates.append("nombre = :nombre")
        params["nombre"] = request.nombre
    if request.apellido is not None:
        updates.append("apellido = :apellido")
        params["apellido"] = request.apellido
    if request.telefono is not None:
        updates.append("telefono = :telefono")
        params["telefono"] = request.telefono
    if request.documento is not None:
        updates.append("documento = :documento")
        params["documento"] = request.documento
    
    if updates:
        update_query = text(f"""
            UPDATE auth.perfil_general
            SET {', '.join(updates)}
            WHERE usuario_id = :chofer_id
        """)
        await db.execute(update_query, params)
    
    # Update driver status and active flag
    if request.estado_laboral is not None or request.activo is not None:
        driver_updates = []
        if request.estado_laboral is not None:
            driver_updates.append("estado_laboral = :estado_laboral")
            params["estado_laboral"] = request.estado_laboral
        if request.activo is not None:
            driver_updates.append("activo = :activo")
            params["activo"] = request.activo
        
        if driver_updates:
            update_driver = text(f"""
                UPDATE fleet.chofer_vehiculo
                SET {', '.join(driver_updates)}
                WHERE usuario_id = :chofer_id
            """)
            await db.execute(update_driver, params)
    
    await db.commit()
    
    return {"success": True, "message": "Chofer actualizado"}


@router.delete("/eliminar/{chofer_id}")
async def eliminar_chofer(
    chofer_id: UUID,
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete driver (set active=false) (Admin only)
    """
    query = text("""
        UPDATE auth.usuario
        SET activo = false, updated_at = NOW()
        WHERE id = :chofer_id
    """)
    
    result = await db.execute(query, {"chofer_id": chofer_id})
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    return {"success": True, "message": "Chofer eliminado"}


# ============================================
# DRIVER ACTIONS (Authenticated driver)
# ============================================
@router.post("/actualizar-ubicacion")
async def actualizar_ubicacion(
    request: ActualizarUbicacionRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update driver's GPS location in real-time
    Also logs GPS history and checks for route deviation
    """
    driver_id = current_user[0]  # user_id from tuple
    
    lat = str(request.latitud)
    lng = str(request.longitud)
    
    # Update current location
    query = text("""
        UPDATE fleet.chofer_vehiculo
        SET latitud = CAST(:latitud AS DECIMAL),
            longitud = CAST(:longitud AS DECIMAL),
            ubicacion = ST_SetSRID(ST_MakePoint(CAST(:longitud AS DECIMAL), CAST(:latitud AS DECIMAL)), 4326)::geography,
            ultima_conexion = NOW()
        WHERE usuario_id = :driver_id
        RETURNING id
    """)
    
    result = await db.execute(query, {
        "latitud": lat,
        "longitud": lng,
        "driver_id": driver_id
    })
    
    if not result.first():
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    # Check if driver has an active trip
    trip_query = text("""
        SELECT id FROM trip.viaje_solicitado
        WHERE chofer_id = :driver_id AND estado IN ('aceptado', 'en_curso')
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    trip_result = await db.execute(trip_query, {"driver_id": driver_id})
    trip_row = trip_result.first()
    
    if trip_row:
        viaje_id = trip_row[0]
        
        # Log GPS position to audit table
        log_query = text("""
            INSERT INTO audit.log_gps (id, viaje_id, usuario_id, latitud, longitud, ubicacion, created_at)
            VALUES (gen_random_uuid(), :viaje_id, :driver_id, CAST(:latitud AS DECIMAL), CAST(:longitud AS DECIMAL),
                    ST_SetSRID(ST_MakePoint(CAST(:longitud AS DECIMAL), CAST(:latitud AS DECIMAL)), 4326)::geography, NOW())
        """)
        await db.execute(log_query, {
            "viaje_id": viaje_id,
            "driver_id": driver_id,
            "latitud": lat,
            "longitud": lng
        })
        
        # Check route deviation (import RouteMonitor at top of file)
        from app.core.route_monitor import RouteMonitor
        
        deviation = await RouteMonitor.check_deviation(viaje_id, request.latitud, request.longitud)
        if deviation and deviation > 100:
            await RouteMonitor.alert_deviation(viaje_id, request.latitud, request.longitud, deviation)
    
    await db.commit()
    
    return {"success": True, "message": "Ubicación actualizada"}


@router.put("/cambiar-estado")
async def cambiar_estado_laboral(
    request: CambiarEstadoLaboralRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change driver work status (libre, ocupado, fuera_servicio)
    """
    valid_states = ["libre", "ocupado", "fuera_servicio", "en_viaje"]
    if request.estado not in valid_states:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Permitidos: {valid_states}"
        )
    
    driver_id = current_user[0]
    
    query = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = :estado
        WHERE usuario_id = :driver_id
        RETURNING id
    """)
    
    result = await db.execute(query, {
        "estado": request.estado,
        "driver_id": driver_id
    })
    
    await db.commit()
    
    if not result.first():
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    return {"success": True, "message": f"Estado cambiado a {request.estado}"}


@router.post("/panico/activar")
async def activar_panico(
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate panic button (security alert)
    """
    driver_id = current_user[0]
    
    # Get current location
    location_query = text("""
        SELECT latitud, longitud, id as chofer_vehiculo_id
        FROM fleet.chofer_vehiculo
        WHERE usuario_id = :driver_id
    """)
    
    result = await db.execute(location_query, {"driver_id": driver_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    latitud, longitud, chofer_vehiculo_id = row
    
    # Update panic status
    update_query = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_panico = true
        WHERE usuario_id = :driver_id
    """)
    await db.execute(update_query, {"driver_id": driver_id})
    
    # Record panic event (if there's an active trip)
    trip_query = text("""
        SELECT id FROM trip.viaje_solicitado
        WHERE chofer_id = :driver_id AND estado IN ('aceptado', 'en_curso')
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    trip_result = await db.execute(trip_query, {"driver_id": driver_id})
    trip_row = trip_result.first()
    
    if trip_row:
        insert_panic = text("""
            INSERT INTO trip.panico (id, viaje_id, usuario_id, ubicacion, activo, created_at)
            VALUES (
                gen_random_uuid(), :viaje_id, :usuario_id,
                ST_SetSRID(ST_MakePoint(:longitud, :latitud), 4326)::geography,
                true, NOW()
            )
        """)
        await db.execute(insert_panic, {
            "viaje_id": trip_row[0],
            "usuario_id": driver_id,
            "latitud": latitud or 0,
            "longitud": longitud or 0
        })
    
    await db.commit()
    
    return {"success": True, "message": "Alerta de pánico activada. Ayuda en camino."}


@router.post("/panico/desactivar")
async def desactivar_panico(
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate panic button
    """
    driver_id = current_user[0]
    
    query = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_panico = false
        WHERE usuario_id = :driver_id
        RETURNING id
    """)
    
    result = await db.execute(query, {"driver_id": driver_id})
    await db.commit()
    
    if not result.first():
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update panic record
    update_panic = text("""
        UPDATE trip.panico
        SET activo = false, resuelto_en = NOW()
        WHERE usuario_id = :driver_id AND activo = true
    """)
    await db.execute(update_panic, {"driver_id": driver_id})
    await db.commit()
    
    return {"success": True, "message": "Alerta de pánico desactivada"}

# ============================================
# VINCULACIÓN CHOFER (Escaneo QR)
# ============================================

@router.post("/vincular")
async def vincular_chofer(
    vehiculo_id: UUID,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chofer escanea QR y solicita vinculación con un vehículo
    """
    chofer_id = current_user[0]
    
    # Verificar que el vehículo existe y QR activo
    query = text("""
        SELECT v.id, v.patente, v.qr_activo, v.activo
        FROM fleet.vehiculo v
        WHERE v.id = :vehiculo_id
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    if not row[2] or not row[3]:
        raise HTTPException(status_code=400, detail="QR del vehículo inactivo o vehículo deshabilitado")
    
    # Verificar que el chofer no tenga contrato activo
    contrato_activo = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE chofer_id = :chofer_id AND estado_contrato = 'ACTIVO'
    """)
    result = await db.execute(contrato_activo, {"chofer_id": chofer_id})
    if result.first():
        raise HTTPException(status_code=400, detail="Ya tienes un contrato activo con otro vehículo")
    
    # Verificar que el vehículo no tenga contrato activo
    contrato_vehiculo = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE vehiculo_id = :vehiculo_id AND estado_contrato = 'ACTIVO'
    """)
    result = await db.execute(contrato_vehiculo, {"vehiculo_id": vehiculo_id})
    if result.first():
        raise HTTPException(status_code=400, detail="El vehículo ya tiene un contrato activo con otro chofer")
    
    # Obtener propietario del vehículo
    propietario = text("""
        SELECT pv.propietario_id
        FROM fleet.propietario_vehiculo pv
        WHERE pv.vehiculo_id = :vehiculo_id AND pv.activo = true
        LIMIT 1
    """)
    result = await db.execute(propietario, {"vehiculo_id": vehiculo_id})
    propietario_row = result.first()
    
    if not propietario_row:
        raise HTTPException(status_code=400, detail="El vehículo no tiene un propietario asignado")
    
    propietario_id = propietario_row[0]
    
    # Obtener control_base_id
    control_base = text("""
        SELECT control_base_id FROM fleet.vehiculo WHERE id = :vehiculo_id
    """)
    result = await db.execute(control_base, {"vehiculo_id": vehiculo_id})
    control_base_id = result.scalar()
    
    # Crear contrato en estado PENDIENTE_CONFIGURACION
    insert_contrato = text("""
        INSERT INTO fleet.contrato_vehiculo (
            id, control_base_id, propietario_id, vehiculo_id, chofer_id,
            tipo_contrato, turno_asignado, estado_contrato, fecha_inicio, activo
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :propietario_id, :vehiculo_id, :chofer_id,
            'PORCENTAJE', 'mañana', 'PENDIENTE_CONFIGURACION', NOW(), true
        )
        RETURNING id
    """)
    result = await db.execute(insert_contrato, {
        "control_base_id": control_base_id,
        "propietario_id": propietario_id,
        "vehiculo_id": vehiculo_id,
        "chofer_id": chofer_id
    })
    contrato_id = result.scalar()
    await db.commit()
    
    # Crear notificación para el propietario
    insert_notificacion = text("""
        INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
        VALUES (gen_random_uuid(), :propietario_id, 'Nueva solicitud de vinculación', 
                'El chofer ha solicitado vincularse al vehículo', 'contrato_pendiente', false, NOW())
    """)
    await db.execute(insert_notificacion, {"propietario_id": propietario_id})
    await db.commit()
    
    return {
        "success": True,
        "contrato_id": str(contrato_id),
        "mensaje": "Solicitud enviada. Esperando configuración del propietario."
    }


# ============================================
# GESTIÓN DE TURNOS (Check-in / Check-out)
# ============================================

@router.post("/turnos/check-in")
async def check_in(
    request: CheckInRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Iniciar jornada laboral (Check-in)
    """
    chofer_id = current_user[0]
    
    result = await TurnoService.check_in(
        db=db,
        chofer_id=chofer_id,
        vehiculo_id=request.vehiculo_id,
        km_inicial=request.km_inicial,
        combustible_inicial=request.combustible_inicial
    )
    
    return result


@router.post("/turnos/gasto")
async def registrar_gasto_turno(
    request: GastoRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar gasto durante el turno
    """
    chofer_id = current_user[0]
    
    result = await TurnoService.registrar_gasto(
        db=db,
        turno_id=request.turno_id,
        chofer_id=chofer_id,
        tipo_gasto=request.tipo_gasto,
        monto=request.monto,
        km_registro=request.km_registro,
        url_comprobante=request.url_comprobante
    )
    
    return result


@router.post("/turnos/check-out")
async def check_out(
    request: CheckOutRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar turno y liquidar (Check-out)
    """
    chofer_id = current_user[0]
    
    result = await TurnoService.check_out(
        db=db,
        turno_id=request.turno_id,
        chofer_id=chofer_id,
        km_final=request.km_final,
        combustible_final=request.combustible_final,
        recaudacion_ticketera=request.recaudacion_ticketera_calle
    )
    
    return result


@router.get("/turnos/activo", response_model=TurnoActivoResponse)
async def turno_activo(
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener turno activo del chofer
    """
    chofer_id = current_user[0]
    
    query = text("""
        SELECT t.id, t.vehiculo_id, v.patente, t.inicio_turno, t.km_inicial, t.combustible_inicial,
               t.estado, c.id as contrato_id
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        WHERE t.chofer_id = :chofer_id AND t.estado = 'ACTIVO'
        ORDER BY t.inicio_turno DESC
        LIMIT 1
    """)
    
    result = await db.execute(query, {"chofer_id": chofer_id})
    row = result.first()
    
    if not row:
        return TurnoActivoResponse(
            tiene_turno_activo=False,
            mensaje="No hay turno activo"
        )
    
    return TurnoActivoResponse(
        tiene_turno_activo=True,
        turno_id=str(row[0]),
        vehiculo_id=str(row[1]),
        patente=row[2],
        inicio_turno=row[3],
        km_inicial=float(row[4]),
        combustible_inicial=row[5],
        estado=row[6],
        contrato_id=str(row[7])
    )