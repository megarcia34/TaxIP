"""
Viajes - Rutas principales
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, and_
from uuid import UUID
from datetime import datetime, timedelta
import uuid as uuid_lib
import json
from typing import Optional, List
import logging

from app.database import get_db
from app.dependencies import (
    get_current_user,
    get_current_passenger_user,
    get_current_driver_user,
    get_current_admin_user
)
from app.services.storage import storage_service
from app.services.geocoding_service import reverse_geocode
from app.services.static_maps_service import generar_url_mapa
from app.services.directions import directions_service

# ✅ IMPORTS DEL MOTOR UNIFICADO (Solo estos)
from app.services.precio_estimado import (
    calcular_precio_estimado,
    TarifaNotFoundError,
    TipoVehiculoNotFoundError
)
from app.schemas.reserva_schemas import (
    EstimacionPrecioRequest,
    EstimacionPrecioResponse,
    TipoVehiculoEnum
)

from app.models.payment import ConfiguracionTarifa
from app.models.trip import TipoVehiculo

from .schemas import (
    ViajeEstadoResponse,
    HistorialViajeResponse,    
    SolicitarViajeCalleRequest,
    CancelarViajeRequest,
    CalificarViajeRequest,
    CalificarViajeResponse,
    CalcularCostoRequest,
    ObjetoOlvidadoRequest,
    ObjetoOlvidadoResponse,
    CompartirViajeResponse,
    ReservarViajeRequest,
    ReservarViajeResponse,
    ReservaPendienteResponse,
    ReverseGeocodeResponse,
    MapaEstaticoResponse,
)

from .queries import (
    GET_VIAJE_BY_ID,
    GET_HISTORIAL_VIAJES,
    GET_VIAJES_POR_ESTADO
)

from .services import (
    actualizar_estado_viaje,
    formatear_respuesta_viaje,
    calcular_distancia,
    calcular_tiempo_estimado,
    es_horario_nocturno,
    obtener_tarifas_default
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/viajes", tags=["Viajes"])


# ============================================
# Calcular costos viaje
# ============================================

@router.post("/calcular-costo", response_model=EstimacionPrecioResponse)
async def calcular_costo(
    request: CalcularCostoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcular costo estimado de un viaje usando el MOTOR UNIFICADO TAXIP 2.1.
    """
    _, control_base_id, _, _ = current_user

    try:
        ruta = await directions_service.calcular_ruta_por_coords(
            request.origen_latitud, request.origen_longitud,
            request.destino_latitud, request.destino_longitud,
        )
        if ruta and ruta.get("distancia_km"):
            distancia_km = float(ruta["distancia_km"])
            tiempo_minutos = int(ruta["tiempo_minutos"])
        else:
            raise ValueError("Directions no devolvió distancia válida")
    except Exception as e:
        logger.warning(f"Directions falló en calcular_costo, usando Haversine: {e}")
        distancia_metros = calcular_distancia(
            request.origen_latitud, request.origen_longitud,
            request.destino_latitud, request.destino_longitud,
        )
        distancia_km = distancia_metros / 1000.0
        tiempo_minutos = calcular_tiempo_estimado(distancia_metros) // 60

    tipo_vehiculo_str = (request.tipo_vehiculo or "standard").lower()
    try:
        tipo_vehiculo_enum = TipoVehiculoEnum(tipo_vehiculo_str)
    except ValueError:
        tipo_vehiculo_enum = TipoVehiculoEnum.STANDARD

    estimacion_request = EstimacionPrecioRequest(
        tipo_vehiculo=tipo_vehiculo_enum,
        direccion_origen="",
        direccion_destino="",
        paradas_intermedias=[],
        tiempo_espera_minutos=0,
        latitud_origen=request.origen_latitud,
        longitud_origen=request.origen_longitud,
        latitud_destino=request.destino_latitud,
        longitud_destino=request.destino_longitud,
    )

    try:
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now(),
            es_feriado=False,
        )
        return resultado
        
    except TarifaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TipoVehiculoNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculando costo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al calcular tarifa: {str(e)}"
        )


# ============================================
# NUEVO M3: VIAJE DE CALLE (Etapa 10.1)
# ============================================

@router.post("/calle", response_model=ViajeEstadoResponse)
async def solicitar_viaje_calle(
    request: SolicitarViajeCalleRequest,
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Registrar un viaje de calle (pasajero anónimo que subió al auto).
    """
    chofer_id, control_base_id, _, _ = current_user

    METODOS_VALIDOS = {"efectivo", "tarjeta_debito", "qr", "transferencia"}
    if request.metodo_pago not in METODOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Método de pago inválido. Permitidos: {sorted(METODOS_VALIDOS)}",
        )

    ctx_query = text("""
        SELECT
            cv.id            AS chofer_vehiculo_id,
            cv.vehiculo_id   AS vehiculo_id,
            tc.id            AS turno_id
        FROM fleet.chofer_vehiculo cv
        LEFT JOIN fleet.turno_chofer tc
            ON tc.chofer_id = cv.usuario_id
           AND tc.estado = 'ACTIVO'
        WHERE cv.usuario_id = :chofer_id
          AND cv.control_base_id = :control_base_id
          AND cv.activo = true
        ORDER BY tc.inicio_turno DESC NULLS LAST
        LIMIT 1
    """)
    ctx_result = await db.execute(ctx_query, {
        "chofer_id": chofer_id,
        "control_base_id": control_base_id,
    })
    ctx = ctx_result.first()

    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chofer sin vehículo asignado en este tenant",
        )

    chofer_vehiculo_id = ctx[0]
    vehiculo_id = ctx[1]
    turno_id = ctx[2]

    if not turno_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chofer sin turno activo. Inicie turno antes de registrar un viaje de calle.",
        )

    try:
        ruta = await directions_service.calcular_ruta_por_coords(
            request.origen_lat, request.origen_lng,
            request.destino_lat, request.destino_lng,
        )
        if ruta and ruta.get("distancia_km"):
            distancia_metros = int(ruta["distancia_km"] * 1000)
            tiempo_estimado_segundos = int(ruta["tiempo_minutos"] * 60)
        else:
            raise ValueError("Directions no devolvió distancia válida")
    except Exception as e:
        logger.warning(
            f"Directions falló en solicitar_viaje_calle, usando Haversine: {e}"
        )
        distancia_metros = calcular_distancia(
            request.origen_lat, request.origen_lng,
            request.destino_lat, request.destino_lng,
        )
        tiempo_estimado_segundos = calcular_tiempo_estimado(distancia_metros)

    distancia_km = distancia_metros / 1000.0
    tiempo_minutos = tiempo_estimado_segundos // 60

    tipo_vehiculo_str = getattr(request, 'tipo_vehiculo', 'standard') or 'standard'
    try:
        tipo_vehiculo_enum = TipoVehiculoEnum(tipo_vehiculo_str.lower())
    except ValueError:
        tipo_vehiculo_enum = TipoVehiculoEnum.STANDARD

    estimacion_request = EstimacionPrecioRequest(
        tipo_vehiculo=tipo_vehiculo_enum,
        direccion_origen="",
        direccion_destino="",
        paradas_intermedias=getattr(request, 'paradas_intermedias', []) or [],
        tiempo_espera_minutos=0,
        latitud_origen=request.origen_lat,
        longitud_origen=request.origen_lng,
        latitud_destino=request.destino_lat,
        longitud_destino=request.destino_lng,
    )

    try:
        resultado_precio = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now(),
            es_feriado=False,
        )
        precio_estimado = resultado_precio.precio_estimado
    except TarifaNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tenant no tiene tarifa configurada. Contactar al administrador.",
        )
    except TipoVehiculoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error calculando precio en viaje de calle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular tarifa: {str(e)}",
        )

    geo = await reverse_geocode(request.origen_lat, request.origen_lng)
    direccion_origen_final = geo["direccion"]

    viaje_id = uuid_lib.uuid4()
    paradas_json = json.dumps(getattr(request, 'paradas_intermedias', []) or [])

    insert_query = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id,
            pasajero_id,
            chofer_id, vehiculo_id, chofer_vehiculo_id, turno_id,
            origen, destino,
            direccion_origen, direccion_destino,
            estado, origen_tipo, es_anonimo,
            metodo_pago, notas, paradas_intermedias,
            precio_estimado, distancia_metros, tiempo_estimado_segundos,
            solicitado_en, iniciado_en, created_at, updated_at
        )
        VALUES (
            :id, :control_base_id,
            NULL,
            :chofer_id, :vehiculo_id, :chofer_vehiculo_id, :turno_id,
            ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326)::geography,
            ST_SetSRID(ST_MakePoint(:destino_lng, :destino_lat), 4326)::geography,
            :direccion_origen, :direccion_destino,
            'en_curso', 'via_publica', true,
            :metodo_pago, :notas, CAST(:paradas AS jsonb),
            :precio_estimado, :distancia_metros, :tiempo_estimado_segundos,
            NOW(), NOW(), NOW(), NOW()
        )
    """)

    await db.execute(insert_query, {
        "id": viaje_id,
        "control_base_id": control_base_id,
        "chofer_id": chofer_id,
        "vehiculo_id": vehiculo_id,
        "chofer_vehiculo_id": chofer_vehiculo_id,
        "turno_id": turno_id,
        "origen_lat": request.origen_lat,
        "origen_lng": request.origen_lng,
        "destino_lat": request.destino_lat,
        "destino_lng": request.destino_lng,
        "direccion_origen": direccion_origen_final,
        "direccion_destino": request.direccion_destino,
        "metodo_pago": request.metodo_pago,
        "notas": request.notas,
        "paradas": paradas_json,
        "precio_estimado": precio_estimado,
        "distancia_metros": distancia_metros,
        "tiempo_estimado_segundos": tiempo_estimado_segundos,
    })

    historial_query = text("""
        INSERT INTO trip.historial_estado_viaje (
            id, viaje_id, estado, latitud, longitud, observacion, created_at
        )
        VALUES (
            gen_random_uuid(), :viaje_id, 'en_curso',
            :origen_lat, :origen_lng,
            'Viaje de calle iniciado', NOW()
        )
    """)
    await db.execute(historial_query, {
        "viaje_id": viaje_id,
        "origen_lat": request.origen_lat,
        "origen_lng": request.origen_lng,
    })

    update_chofer = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = 'ocupado',
            updated_at = NOW()
        WHERE id = :chofer_vehiculo_id
    """)
    await db.execute(update_chofer, {"chofer_vehiculo_id": chofer_vehiculo_id})

    await db.commit()

    result = await db.execute(GET_VIAJE_BY_ID, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })
    row = result.first()
    return await formatear_respuesta_viaje(row)


# ============================================
# VIAJE ACTIVO DEL CHOFER (NUEVO - J15)
# ============================================

@router.get("/activo")
async def obtener_viaje_activo(
    current_user: tuple = Depends(get_current_driver_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el viaje activo del chofer autenticado (estado 'aceptado' o 'en_curso').
    Devuelve null si no hay ninguno.
    """
    chofer_id, control_base_id, _, _ = current_user

    query = text("""
        SELECT
            vs.id, vs.estado, vs.direccion_origen, vs.direccion_destino,
            ST_Y(vs.origen::geometry) as origen_lat,
            ST_X(vs.origen::geometry) as origen_lng,
            ST_Y(vs.destino::geometry) as destino_lat,
            ST_X(vs.destino::geometry) as destino_lng,
            vs.precio_estimado, vs.precio_final, vs.moneda,
            vs.tiempo_estimado_segundos, vs.distancia_metros,
            vs.solicitado_en, vs.aceptado_en, vs.iniciado_en,
            vs.metodo_pago, vs.pasajero_id
        FROM trip.viaje_solicitado vs
        WHERE vs.chofer_id = :chofer_id
            AND vs.control_base_id = :control_base_id
            AND vs.estado IN ('aceptado', 'en_curso')
        ORDER BY vs.created_at DESC
        LIMIT 1
    """)

    result = await db.execute(query, {
        "chofer_id": chofer_id,
        "control_base_id": control_base_id,
    })
    row = result.first()

    if not row:
        return {"viaje_activo": None}

    return {
        "viaje_activo": {
            "id": str(row[0]),
            "estado": row[1],
            "direccion_origen": row[2],
            "direccion_destino": row[3],
            "origen_lat": float(row[4]) if row[4] else None,
            "origen_lng": float(row[5]) if row[5] else None,
            "destino_lat": float(row[6]) if row[6] else None,
            "destino_lng": float(row[7]) if row[7] else None,
            "precio_estimado": float(row[8]) if row[8] else None,
            "precio_final": float(row[9]) if row[9] else None,
            "moneda": row[10] or "ARS",
            "tiempo_estimado_segundos": row[11],
            "distancia_metros": row[12],
            "solicitado_en": row[13],
            "aceptado_en": row[14],
            "iniciado_en": row[15],
            "metodo_pago": row[16],
            "pasajero_id": str(row[17]) if row[17] else None,
        }
    }


# ============================================
# INCLUIR SUB-ROUTERS
# ============================================
from app.routers.viajes import routes_objetos
from app.routers.viajes import routes_dashboard
from app.routers.viajes import routes_geocode
from app.routers.viajes import routes_historial
from app.routers.viajes import routes_lifecycle

router.include_router(routes_objetos.router)
router.include_router(routes_dashboard.router)
router.include_router(routes_geocode.router)
router.include_router(routes_historial.router)
router.include_router(routes_lifecycle.router)