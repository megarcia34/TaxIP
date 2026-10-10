"""
Router para gestión de reservas y estimación de precios
Usa el MOTOR UNIFICADO TAXIP 2.1 para el cálculo de tarifas.

R13: migrado de trip.reserva a trip.viaje_solicitado.
- La tabla trip.reserva fue deprecada (nunca existio en DB).
- Los estados visibles del frontend se preservan:
    reservado, despachado, vehiculo_llego, pasajero_a_bordo, completado, cancelado
- Se mapean a (viaje_solicitado.estado, viaje_solicitado.subestado_despacho).
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.dependencies import EmpleadoUser, AdminTenantUser
from app.core.validations import validar_tenant_activo, validar_empresa_activa
from app.services.precio_estimado import (
    calcular_precio_estimado,
    TarifaNotFoundError,
    TipoVehiculoNotFoundError,
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


# ============================================================
# MAPEO DE ESTADOS (R13)
# ============================================================
# El frontend usa 6 estados visibles:
#     reservado | despachado | vehiculo_llego | pasajero_a_bordo | completado | cancelado
#
# En trip.viaje_solicitado se representan con dos columnas:
#     estado (varchar 30) + subestado_despacho (varchar 30)
#
# Mapeo canonico:
#     reservado         -> estado='pendiente',  subestado_despacho='reservado'
#     despachado        -> estado='aceptado',   subestado_despacho='despachado'
#     vehiculo_llego    -> estado='aceptado',   subestado_despacho='vehiculo_llego'
#     pasajero_a_bordo  -> estado='en_curso',   subestado_despacho='pasajero_a_bordo'
#     completado        -> estado='finalizado', subestado_despacho='completado'
#     cancelado         -> estado='cancelado',  subestado_despacho=NULL

_MAP_ESTADO_VISIBLE_A_DB = {
    "reservado": ("pendiente", "reservado"),
    "despachado": ("aceptado", "despachado"),
    "vehiculo_llego": ("aceptado", "vehiculo_llego"),
    "pasajero_a_bordo": ("en_curso", "pasajero_a_bordo"),
    "completado": ("finalizado", "completado"),
    "cancelado": ("cancelado", None),
}


def _map_estado_db(estado_visible: str):
    """
    Devuelve (estado_db, subestado_despacho) a partir del estado visible.
    Si el estado no esta mapeado, devuelve (estado_visible, None) como fallback.
    """
    return _MAP_ESTADO_VISIBLE_A_DB.get(estado_visible, (estado_visible, None))


def _map_estado_visible(estado_db: str, subestado_db: Optional[str]) -> str:
    """
    Devuelve el estado visible a partir de (estado_db, subestado_despacho).
    Regla:
      - Si estado_db='cancelado' -> 'cancelado'.
      - Si subestado_despacho coincide con uno de los 6 visibles -> ese.
      - Si no -> 'reservado' como fallback.
    """
    if estado_db == "cancelado":
        return "cancelado"
    if subestado_db in _MAP_ESTADO_VISIBLE_A_DB:
        return subestado_db
    return "reservado"


# ============================================================
# ESTIMAR PRECIO
# ============================================================
@router.post("/estimar-precio", response_model=EstimacionPrecioResponse)
async def estimar_precio(
    data: EstimacionPrecioRequest,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Estima el precio de un viaje usando el MOTOR UNIFICADO TAXIP 2.1.
    Accesible para empleados (solo visualización) y administradores.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    logger.info(f"Estimando precio para empleado {email} (tenant {control_base_id})")

    # 1. Validar que el tenant esté activo
    await validar_tenant_activo(control_base_id, db)

    # 2. Obtener distancia y tiempo con Directions API
    try:
        ruta = await directions_service.calcular_ruta(
            origen=data.direccion_origen,
            destino=data.direccion_destino,
            paradas=[p.direccion for p in data.paradas_intermedias] if data.paradas_intermedias else [],
        )
        distancia_km = ruta.get("distancia_km", 0)
        tiempo_minutos = ruta.get("tiempo_minutos", 0)
        lat_origen = ruta.get("lat_origen")
        lon_origen = ruta.get("lon_origen")
        lat_destino = ruta.get("lat_destino")
        lon_destino = ruta.get("lon_destino")
        logger.info(f"Ruta calculada: {distancia_km}km, {tiempo_minutos}min")
    except Exception as e:
        logger.error(f"Error calculando ruta: {str(e)}")
        distancia_km = 5.0
        tiempo_minutos = 15
        lat_origen = None
        lon_origen = None
        lat_destino = None
        lon_destino = None

    # 3. Determinar fecha/hora para recargos
    fecha_hora = data.fecha_programada or datetime.now()

    # 4. Calcular precio usando el MOTOR UNIFICADO
    try:
        resultado = await calcular_precio_estimado(
            request=data,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=fecha_hora,
            es_feriado=False,
        )
        resultado.latitud_origen = lat_origen
        resultado.longitud_origen = lon_origen
        resultado.latitud_destino = lat_destino
        resultado.longitud_destino = lon_destino
        logger.info(f"Precio estimado: {resultado.precio_estimado} {resultado.moneda}")
        return resultado
    except TarifaNotFoundError as e:
        logger.error(f"{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except TipoVehiculoNotFoundError as e:
        logger.error(f"{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular el precio: {str(e)}",
        )


# ============================================================
# CREAR RESERVA (EMPLEADO)
# ============================================================
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReservaResponse)
async def create_reserva(
    data: ReservaCreate,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva reserva de viaje.
    Solo accesible para empleados con turno activo.

    R13: inserta en trip.viaje_solicitado (antes trip.reserva).
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user
    logger.info("=" * 60)
    logger.info("SOLICITUD DE VIAJE RECIBIDA:")
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
            detail="No tienes un turno activo. Realiza el check-in antes de despachar un viaje.",
        )

    id_empresa_final = empresa_id

    # 4. Calcular precio estimado con MOTOR UNIFICADO
    try:
        ruta = await directions_service.calcular_ruta(
            origen=data.direccion_origen,
            destino=data.direccion_destino,
            paradas=[p.direccion for p in data.paradas_intermedias] if data.paradas_intermedias else [],
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
            fecha_programada=data.fecha_programada,
        )
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=data.fecha_programada or datetime.now(),
            es_feriado=False,
        )
        precio_estimado = resultado.precio_estimado
    except Exception as e:
        logger.error(f"Error calculando precio: {str(e)}")
        # Fallback: estimación básica si falla el motor
        distancia_km = 5.0
        tiempo_minutos = 15
        precio_estimado = (distancia_km * 200) + (tiempo_minutos * 50)

    # 5. Insertar la reserva en trip.viaje_solicitado
    # Mapeo:
    #   empresa_id           -> empresa_id
    #   empleado_id          -> empleado_id
    #   turno_id             -> turno_empleado_id
    #   pasajero_nombre      -> nombre_pasajero
    #   pasajero_telefono    -> pasajero_telefono
    #   lat/lng origen       -> origen (Geography, ST_SetSRID + ST_MakePoint)
    #   lat/lng destino      -> destino (Geography)
    #   tipo_vehiculo        -> tipo_vehiculo_solicitado
    #   nota_conductor       -> notas
    #   estado='reservado'   -> estado='pendiente' + subestado_despacho='reservado'
    #   distancia_km         -> distancia_metros (x1000)
    #   tiempo_minutos       -> tiempo_estimado_segundos (x60)
    #   cantidad_equipaje    -> cantidad_valijas
    #   creado_por           -> empleado_id (mismo valor)
    estado_db, subestado_db = _map_estado_db("reservado")

    query = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id, empresa_id, empleado_id, turno_empleado_id,
            nombre_pasajero, pasajero_telefono,
            direccion_origen, origen,
            direccion_destino, destino,
            paradas_intermedias,
            tipo_vehiculo_solicitado, notas,
            estado, subestado_despacho,
            es_programado, fecha_programada,
            distancia_metros, tiempo_estimado_segundos, precio_estimado,
            metodo_pago, centro_costo,
            solicitado_en, created_at, updated_at,
            cantidad_pasajeros, cantidad_valijas
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :empresa_id, :empleado_id, :turno_empleado_id,
            :nombre_pasajero, :pasajero_telefono,
            :direccion_origen,
            CASE WHEN :latitud_origen IS NOT NULL AND :longitud_origen IS NOT NULL
                 THEN ST_SetSRID(ST_MakePoint(:longitud_origen, :latitud_origen), 4326)::geography
                 ELSE NULL END,
            :direccion_destino,
            CASE WHEN :latitud_destino IS NOT NULL AND :longitud_destino IS NOT NULL
                 THEN ST_SetSRID(ST_MakePoint(:longitud_destino, :latitud_destino), 4326)::geography
                 ELSE NULL END,
            CAST(:paradas_intermedias AS jsonb),
            :tipo_vehiculo, :nota_conductor,
            :estado_db, :subestado_db,
            :es_programado, :fecha_programada,
            :distancia_metros, :tiempo_estimado_segundos, :precio_estimado,
            :metodo_pago, :centro_costo,
            NOW(), NOW(), NOW(),
            :cantidad_pasajeros, :cantidad_valijas
        )
        RETURNING id
    """)

    paradas_json = []
    if data.paradas_intermedias:
        paradas_json = [p.model_dump() for p in data.paradas_intermedias]

    result = await db.execute(query, {
        "control_base_id": control_base_id,
        "empresa_id": id_empresa_final,
        "empleado_id": user_id,
        "turno_empleado_id": turno_id,
        "nombre_pasajero": data.pasajero_nombre,
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
        "estado_db": estado_db,
        "subestado_db": subestado_db,
        "es_programado": data.es_programado,
        "fecha_programada": data.fecha_programada,
        "distancia_metros": int(distancia_km * 1000) if distancia_km else None,
        "tiempo_estimado_segundos": int(tiempo_minutos * 60) if tiempo_minutos else None,
        "precio_estimado": precio_estimado,
        "metodo_pago": data.metodo_pago.value,
        "centro_costo": data.centro_costo,
        "cantidad_pasajeros": data.cantidad_pasajeros,
        "cantidad_valijas": data.cantidad_equipaje,
    })
    await db.commit()
    row = result.first()
    reserva_id = row[0]

    return await get_reserva_detail(str(reserva_id), current_user, db)


# ============================================================
# LISTAR RESERVAS
# ============================================================
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

    R13: lee de trip.viaje_solicitado (antes trip.reserva).
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user

    query_str = """
        SELECT vs.id FROM trip.viaje_solicitado vs
        WHERE vs.empresa_id = :empresa_id
    """
    params = {"empresa_id": empresa_id, "limit": limit, "offset": offset}

    if estado:
        # Filtrar por subestado_despacho que es el que preserva el estado visible.
        query_str += " AND vs.subestado_despacho = :subestado"
        params["subestado"] = estado.value

    query_str += " ORDER BY vs.created_at DESC LIMIT :limit OFFSET :offset"

    result = await db.execute(text(query_str), params)
    rows = result.fetchall()

    reservas = []
    for row in rows:
        detail = await get_reserva_detail(str(row[0]), current_user, db)
        if detail:
            reservas.append(detail)
    return reservas


# ============================================================
# OBTENER DETALLE DE UNA RESERVA
# ============================================================
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


# ============================================================
# ACTUALIZAR ESTADO DE LA RESERVA
# ============================================================
@router.patch("/{id}/estado", response_model=ReservaResponse)
async def update_reserva_estado(
    id: str,
    estado: EstadoReservaEnum,
    current_user: EmpleadoUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Permite transicionar de estado un viaje de forma controlada.

    R13: lee y escribe en trip.viaje_solicitado.
    Los 6 estados visibles se mapean a (estado, subestado_despacho).
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user

    check_query = text("""
        SELECT id, estado, subestado_despacho FROM trip.viaje_solicitado
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
            detail="Reserva no encontrada",
        )

    # Reconstruir el estado visible actual
    estado_actual = _map_estado_visible(row[1], row[2])

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
            detail=f"No se puede cambiar de '{estado_actual}' a '{estado.value}'",
        )

    # Mapear el nuevo estado visible a (estado_db, subestado_db)
    nuevo_estado_db, nuevo_subestado_db = _map_estado_db(estado.value)

    update_query = text("""
        UPDATE trip.viaje_solicitado
        SET estado = :estado,
            subestado_despacho = :subestado,
            updated_at = NOW()
        WHERE id = :id
    """)
    await db.execute(update_query, {
        "id": UUID(id),
        "estado": nuevo_estado_db,
        "subestado": nuevo_subestado_db,
    })
    await db.commit()

    return await get_reserva_detail(id, current_user, db)


# ============================================================
# CANCELAR RESERVA
# ============================================================
@router.patch("/{id}/cancelar", response_model=ReservaResponse)
async def cancelar_reserva(
    id: str,
    current_user: EmpleadoUser,
    motivo: Optional[str] = Query(None, description="Motivo de la cancelación"),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancela una reserva existente.

    R13: lee y escribe en trip.viaje_solicitado.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user

    check_query = text("""
        SELECT id, estado, subestado_despacho FROM trip.viaje_solicitado
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
            detail="Reserva no encontrada",
        )

    estado_actual = _map_estado_visible(row[1], row[2])
    if estado_actual in ["completado", "cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una reserva en estado '{estado_actual}'",
        )

    update_query = text("""
        UPDATE trip.viaje_solicitado
        SET estado = 'cancelado',
            subestado_despacho = NULL,
            updated_at = NOW()
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
            "motivo": motivo,
        })
        await db.commit()

    return await get_reserva_detail(id, current_user, db)


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================
async def get_reserva_detail(
    id: str, current_user: EmpleadoUser, db: AsyncSession
) -> ReservaResponse:
    """
    Obtiene el detalle completo de una reserva.

    R13: lee de trip.viaje_solicitado y desmapea el estado visible.
    """
    user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id = current_user

    query = text("""
        SELECT
            vs.id,
            vs.empresa_id,
            vs.empleado_id,
            vs.turno_empleado_id,
            vs.nombre_pasajero,
            vs.pasajero_telefono,
            vs.direccion_origen,
            ST_Y(vs.origen::geometry) AS latitud_origen,
            ST_X(vs.origen::geometry) AS longitud_origen,
            vs.direccion_destino,
            ST_Y(vs.destino::geometry) AS latitud_destino,
            ST_X(vs.destino::geometry) AS longitud_destino,
            vs.paradas_intermedias,
            vs.tipo_vehiculo_solicitado,
            vs.notas,
            vs.estado,
            vs.subestado_despacho,
            vs.es_programado,
            vs.fecha_programada,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            vs.precio_estimado,
            vs.precio_final,
            vs.metodo_pago,
            vs.centro_costo,
            vs.created_at,
            vs.updated_at,
            vs.cantidad_pasajeros,
            vs.cantidad_valijas
        FROM trip.viaje_solicitado
        WHERE id = :id AND empresa_id = :empresa_id
    """)
    result = await db.execute(query, {
        "id": UUID(id),
        "empresa_id": empresa_id,
    })
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva solicitada no existe",
        )

    # Desmapear estado visible
    estado_visible = _map_estado_visible(row[15], row[16])

    # Convertir distancia (metros -> km) y tiempo (segundos -> minutos)
    distancia_metros = row[19] if row[19] is not None else 0
    tiempo_segundos = row[20] if row[20] is not None else 0

    return {
        "id": str(row[0]),
        "empresa_id": str(row[1]) if row[1] else None,
        "empleado_id": str(row[2]) if row[2] else None,
        "turno_id": str(row[3]) if row[3] else None,
        "pasajero_nombre": row[4],
        "pasajero_telefono": row[5],
        "direccion_origen": row[6],
        "latitud_origen": float(row[7]) if row[7] is not None else None,
        "longitud_origen": float(row[8]) if row[8] is not None else None,
        "direccion_destino": row[9],
        "latitud_destino": float(row[10]) if row[10] is not None else None,
        "longitud_destino": float(row[11]) if row[11] is not None else None,
        "paradas_intermedias": row[12] if row[12] else [],
        "tipo_vehiculo": row[13],
        "nota_conductor": row[14],
        "estado": estado_visible,
        "es_programado": row[17],
        "fecha_programada": row[18].isoformat() if row[18] else None,
        "distancia_estimada_km": float(distancia_metros) / 1000.0,
        "tiempo_estimado_minutos": int(tiempo_segundos) // 60,
        "precio_estimado": float(row[21]) if row[21] is not None else 0.0,
        "precio_final": float(row[22]) if row[22] is not None else None,
        "metodo_pago": row[23],
        "centro_costo": row[24],
        "created_at": row[25].isoformat(),
        "updated_at": row[26].isoformat(),
        "cantidad_pasajeros": row[27] if row[27] is not None else 1,
        "cantidad_equipaje": row[28] if row[28] is not None else 0,
    }