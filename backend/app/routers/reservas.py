"""
Router para gestión de reservas y estimación de precios
Soporta múltiples modos de cálculo (ficha_argentina, por_km, por_minuto, mixto)
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List, Tuple
from datetime import datetime

from app.database import get_db
from app.dependencies import EmpleadoUser, AdminTenantUser
from app.core.validations import validar_tenant_activo, validar_empresa_activa
from app.services.precio_estimado import (
    calcular_precio_estimado,
    TarifaNotFoundError,
    TipoVehiculoNotFoundError
)
from app.services.directions import directions_service
from app.schemas.reserva_schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    EstimacionPrecioRequest,
    EstimacionPrecioResponse,
    EstadoReservaEnum,
    ParadaIntermedia,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


# ============================================
# ESTIMAR PRECIO - ✅ CORREGIDO (ACCESIBLE PARA EMPLEADOS)
# ============================================
@router.post("/estimar-precio", response_model=EstimacionPrecioResponse)
async def estimar_precio(
    data: EstimacionPrecioRequest,
    current_user: EmpleadoUser,  # ✅ CORREGIDO: permite empleados (solo visualización)
    db: AsyncSession = Depends(get_db),
):
    """
    Estima el precio de un viaje.
    Accesible para empleados (solo visualización) y administradores.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    logger.info(f"📊 Estimando precio para empleado {email} (tenant {control_base_id})")
    
    # 1. Validar que el tenant esté activo
    await validar_tenant_activo(control_base_id, db)
    
    # 2. Obtener distancia y tiempo con Directions API
    try:
        ruta = await directions_service.calcular_ruta(
            origen=data.direccion_origen,
            destino=data.direccion_destino,
            paradas=[p.direccion for p in data.paradas_intermedias] if data.paradas_intermedias else []
        )
        
        distancia_km = ruta.get("distancia_km", 0)
        tiempo_minutos = ruta.get("tiempo_minutos", 0)
        lat_origen = ruta.get("lat_origen")
        lon_origen = ruta.get("lon_origen")
        lat_destino = ruta.get("lat_destino")
        lon_destino = ruta.get("lon_destino")
        
        logger.info(f"📍 Ruta calculada: {distancia_km}km, {tiempo_minutos}min")
        
    except Exception as e:
        logger.error(f"❌ Error calculando ruta: {str(e)}")
        distancia_km = 5.0
        tiempo_minutos = 15
        lat_origen = None
        lon_origen = None
        lat_destino = None
        lon_destino = None
    
    # 3. Determinar fecha/hora para recargos
    fecha_hora = data.fecha_programada or datetime.now()
    
    # 4. Calcular precio usando el nuevo servicio
    try:
        resultado = await calcular_precio_estimado(
            request=data,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=fecha_hora,
            es_feriado=False
        )
        
        resultado.latitud_origen = lat_origen
        resultado.longitud_origen = lon_origen
        resultado.latitud_destino = lat_destino
        resultado.longitud_destino = lon_destino
        
        logger.info(f"✅ Precio estimado: {resultado.precio_estimado} {resultado.moneda}")
        return resultado
        
    except TarifaNotFoundError as e:
        logger.error(f"❌ {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TipoVehiculoNotFoundError as e:
        logger.error(f"❌ {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular el precio: {str(e)}"
        )


# ============================================
# CREAR RESERVA (EMPLEADO)
# ============================================
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReservaResponse)
async def create_reserva(
    data: ReservaCreate,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva reserva de viaje.
    Solo accesible para empleados con turno activo.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    logger.info("=" * 60)
    logger.info(f"📥 SOLICITUD DE VIAJE RECIBIDA:")
    logger.info(f"  - Empleado ID: {user_id} ({email})")
    logger.info(f"  - Empresa: {empresa_nombre} (ID: {empresa_id})")
    logger.info(f"  - Turno Activo ID: {turno_id}")
    logger.info(f"  - Pasajero: {data.pasajero_nombre}")
    logger.info(f"  - Destino: {data.direccion_destino}")
    logger.info("=" * 60)
    
    # 1. Validar que la empresa del token esté activa
    await validar_empresa_activa(empresa_id, db)
    
    # 2. Validar que el tenant esté activo
    await validar_tenant_activo(control_base_id, db)
    
    # 3. Validar que el empleado tenga un turno abierto
    if not turno_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes un turno activo. Realiza el check-in antes de despachar un viaje."
        )
    
    id_empresa_final = empresa_id

    # 4. Calcular precio estimado
    try:
        ruta = await directions_service.calcular_ruta(
            origen=data.direccion_origen,
            destino=data.direccion_destino,
            paradas=[p.direccion for p in data.paradas_intermedias] if data.paradas_intermedias else []
        )
        
        distancia_km = ruta.get("distancia_km", 0)
        tiempo_minutos = ruta.get("tiempo_minutos", 0)
        lat_origen = ruta.get("lat_origen")
        lon_origen = ruta.get("lon_origen")
        lat_destino = ruta.get("lat_destino")
        lon_destino = ruta.get("lon_destino")
        
        if data.latitud_origen is None and lat_origen is not None:
            data.latitud_origen = lat_origen
        if data.longitud_origen is None and lon_origen is not None:
            data.longitud_origen = lon_origen
        if data.latitud_destino is None and lat_destino is not None:
            data.latitud_destino = lat_destino
        if data.longitud_destino is None and lon_destino is not None:
            data.longitud_destino = lon_destino
        
        estimacion_request = EstimacionPrecioRequest(
            direccion_origen=data.direccion_origen,
            direccion_destino=data.direccion_destino,
            paradas_intermedias=data.paradas_intermedias or [],
            tipo_vehiculo=data.tipo_vehiculo,
            tiempo_espera_minutos=0,
            es_programado=data.es_programado,
            fecha_programada=data.fecha_programada
        )
        
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=data.fecha_programada or datetime.now(),
            es_feriado=False
        )
        
        precio_estimado = resultado.precio_estimado
        
    except Exception as e:
        logger.error(f"❌ Error calculando precio: {str(e)}")
        distancia_km = 5.0
        tiempo_minutos = 15
        precio_estimado = (distancia_km * 200) + (tiempo_minutos * 50)
    
    # 5. Insertar la reserva
    query = text("""
        INSERT INTO trip.reserva (
            id, empresa_id, empleado_id, turno_id,
            pasajero_nombre, pasajero_telefono,
            direccion_origen, latitud_origen, longitud_origen,
            direccion_destino, latitud_destino, longitud_destino,
            paradas_intermedias,
            tipo_vehiculo, nota_conductor,
            estado, es_programado, fecha_programada,
            distancia_estimada_km, tiempo_estimado_minutos, precio_estimado,
            metodo_pago, centro_costo, created_at, updated_at, creado_por,
            cantidad_pasajeros, cantidad_equipaje
        )
        VALUES (
            gen_random_uuid(), :empresa_id, :empleado_id, :turno_id,
            :pasajero_nombre, :pasajero_telefono,
            :direccion_origen, :latitud_origen, :longitud_origen,
            :direccion_destino, :latitud_destino, :longitud_destino,
            CAST(:paradas_intermedias AS jsonb),
            :tipo_vehiculo, :nota_conductor,
            'reservado', :es_programado, :fecha_programada,
            :distancia_km, :tiempo_minutos, :precio_estimado,
            :metodo_pago, :centro_costo, NOW(), NOW(), :creado_por,
            :cantidad_pasajeros, :cantidad_equipaje
        )
        RETURNING id
    """)
    
    paradas_json = []
    if data.paradas_intermedias:
        paradas_json = [p.model_dump() for p in data.paradas_intermedias]
    
    result = await db.execute(query, {
        "empresa_id": id_empresa_final,
        "empleado_id": user_id,
        "turno_id": turno_id,
        "pasajero_nombre": data.pasajero_nombre,
        "pasajero_telefono": data.pasajero_telefono,
        "direccion_origen": data.direccion_origen,
        "latitud_origen": data.latitud_origen,
        "longitud_origen": data.longitud_origen,
        "direccion_destino": data.direccion_destino,
        "latitud_destino": data.latitud_destino,
        "longitud_destino": data.longitud_destino,
        "paradas_intermedias": json.dumps(paradas_json),
        "tipo_vehiculo": data.tipo_vehiculo.value,
        "nota_conductor": data.nota_conductor,
        "es_programado": data.es_programado,
        "fecha_programada": data.fecha_programada,
        "distancia_km": distancia_km,
        "tiempo_minutos": tiempo_minutos,
        "precio_estimado": precio_estimado,
        "metodo_pago": data.metodo_pago.value,
        "centro_costo": data.centro_costo,
        "creado_por": user_id,
        "cantidad_pasajeros": data.cantidad_pasajeros,
        "cantidad_equipaje": data.cantidad_equipaje,
    })
    await db.commit()
    
    row = result.first()
    reserva_id = row[0]
    
    return await get_reserva_detail(str(reserva_id), current_user, db)


# ============================================
# LISTAR RESERVAS
# ============================================
@router.get("", response_model=List[ReservaResponse])
async def list_reservas(
    current_user: EmpleadoUser,
    estado: Optional[EstadoReservaEnum] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista las reservas creadas por la empresa del empleado autenticado.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    query_str = """
        SELECT r.id FROM trip.reserva r
        WHERE r.empresa_id = :empresa_id
    """
    params = {"empresa_id": empresa_id, "limit": limit, "offset": offset}
    
    if estado:
        query_str += " AND r.estado = :estado"
        params["estado"] = estado.value
        
    query_str += " ORDER BY r.created_at DESC LIMIT :limit OFFSET :offset"
    
    result = await db.execute(text(query_str), params)
    rows = result.fetchall()
    
    reservas = []
    for row in rows:
        detail = await get_reserva_detail(str(row[0]), current_user, db)
        if detail:
            reservas.append(detail)
            
    return reservas


# ============================================
# OBTENER DETALLE DE UNA RESERVA
# ============================================
@router.get("/{id}", response_model=ReservaResponse)
async def get_reserva(
    id: str,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el detalle completo de una reserva.
    """
    return await get_reserva_detail(id, current_user, db)


# ============================================
# ACTUALIZAR ESTADO DE LA RESERVA
# ============================================
@router.patch("/{id}/estado", response_model=ReservaResponse)
async def update_reserva_estado(
    id: str,
    estado: EstadoReservaEnum,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Permite transicionar de estado un viaje de forma controlada.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    check_query = text("""
        SELECT id, estado FROM trip.reserva
        WHERE id = :id AND empresa_id = :empresa_id
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "empresa_id": empresa_id,
    })
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    estado_actual = row[1]
    
    transiciones_permitidas = {
        "reservado": ["despachado", "cancelado"],
        "despachado": ["vehiculo_llego", "cancelado"],
        "vehiculo_llego": ["pasajero_a_bordo", "cancelado"],
        "pasajero_a_bordo": ["completado", "cancelado"],
        "completado": [],
        "cancelado": [],
    }
    
    if estado.value not in transiciones_permitidas.get(estado_actual, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cambiar de '{estado_actual}' a '{estado.value}'"
        )
    
    update_query = text("""
        UPDATE trip.reserva 
        SET estado = :estado, updated_at = NOW()
        WHERE id = :id
    """)
    
    await db.execute(update_query, {
        "id": UUID(id),
        "estado": estado.value
    })
    await db.commit()
    
    return await get_reserva_detail(id, current_user, db)


# ============================================
# CANCELAR RESERVA
# ============================================
@router.patch("/{id}/cancelar", response_model=ReservaResponse)
async def cancelar_reserva(
    id: str,
    current_user: EmpleadoUser,
    motivo: Optional[str] = Query(None, description="Motivo de la cancelación"),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancela una reserva existente.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    check_query = text("""
        SELECT id, estado FROM trip.reserva
        WHERE id = :id AND empresa_id = :empresa_id
    """)
    result = await db.execute(check_query, {
        "id": UUID(id),
        "empresa_id": empresa_id,
    })
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    estado_actual = row[1]
    
    if estado_actual in ["completado", "cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una reserva en estado '{estado_actual}'"
        )
    
    update_query = text("""
        UPDATE trip.reserva 
        SET estado = 'cancelado', updated_at = NOW()
        WHERE id = :id
    """)
    
    await db.execute(update_query, {"id": UUID(id)})
    await db.commit()
    
    if motivo:
        historial_query = text("""
            INSERT INTO trip.historial_estado_viaje (viaje_id, estado, observacion, created_at)
            VALUES (:viaje_id, 'cancelado', :motivo, NOW())
        """)
        await db.execute(historial_query, {
            "viaje_id": UUID(id),
            "motivo": motivo
        })
        await db.commit()
    
    return await get_reserva_detail(id, current_user, db)


# ============================================
# FUNCIÓN AUXILIAR
# ============================================
async def get_reserva_detail(id: str, current_user: EmpleadoUser, db: AsyncSession) -> ReservaResponse:
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    
    query = text("""
        SELECT 
            id, empresa_id, empleado_id, turno_id,
            pasajero_nombre, pasajero_telefono,
            direccion_origen, latitud_origen, longitud_origen,
            direccion_destino, latitud_destino, longitud_destino,
            paradas_intermedias, tipo_vehiculo, nota_conductor,
            estado, es_programado, fecha_programada,
            distancia_estimada_km, tiempo_estimado_minutos, precio_estimado,
            precio_final, metodo_pago, centro_costo, created_at, updated_at,
            cantidad_pasajeros, cantidad_equipaje
        FROM trip.reserva
        WHERE id = :id AND empresa_id = :empresa_id
    """)
    
    result = await db.execute(query, {
        "id": UUID(id),
        "empresa_id": empresa_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva solicitada no existe"
        )
        
    return {
        "id": str(row[0]),
        "empresa_id": str(row[1]),
        "empleado_id": str(row[2]),
        "turno_id": str(row[3]) if row[3] else None,
        "pasajero_nombre": row[4],
        "pasajero_telefono": row[5],
        "direccion_origen": row[6],
        "latitud_origen": row[7],
        "longitud_origen": row[8],
        "direccion_destino": row[9],
        "latitud_destino": row[10],
        "longitud_destino": row[11],
        "paradas_intermedias": row[12] if row[12] else [],
        "tipo_vehiculo": row[13],
        "nota_conductor": row[14],
        "estado": row[15],
        "es_programado": row[16],
        "fecha_programada": row[17].isoformat() if row[17] else None,
        "distancia_estimada_km": float(row[18]) if row[18] else 0.0,
        "tiempo_estimado_minutos": row[19] if row[19] else 0,
        "precio_estimado": float(row[20]) if row[20] else 0.0,
        "precio_final": float(row[21]) if row[21] else None,
        "metodo_pago": row[22],
        "centro_costo": row[23],
        "created_at": row[24].isoformat(),
        "updated_at": row[25].isoformat(),
        "cantidad_pasajeros": row[26] if row[26] is not None else 1,
        "cantidad_equipaje": row[27] if row[27] is not None else 0,
    }