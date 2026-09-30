"""""
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
    SolicitarViajeRequest,
    SolicitarViajeResponse,
    SolicitarViajeCalleRequest,
    CancelarViajeRequest,
    CalificarViajeRequest,
    CalificarViajeResponse,
    CalcularCostoRequest,
    # CalcularCostoResponse,  # ⚠️ Opcional: si ya no lo usas, puedes comentarlo o borrarlo
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
    # calcular_precio,  # ⚠️ Opcional: si ya no se usa porque ahora usamos el motor unificado
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

    # 1. Obtener distancia y tiempo con Directions API (fallback a Haversine)
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

    # 2. Preparar el request para el motor unificado
    tipo_vehiculo_str = (request.tipo_vehiculo or "standard").lower()
    try:
        tipo_vehiculo_enum = TipoVehiculoEnum(tipo_vehiculo_str)
    except ValueError:
        tipo_vehiculo_enum = TipoVehiculoEnum.STANDARD

    estimacion_request = EstimacionPrecioRequest(
        tipo_vehiculo=tipo_vehiculo_enum,
        direccion_origen="",  # El motor unificado usa las coords, pero el schema lo pide
        direccion_destino="",
        paradas_intermedias=[],
        tiempo_espera_minutos=0,
        latitud_origen=request.origen_latitud,
        longitud_origen=request.origen_longitud,
        latitud_destino=request.destino_latitud,
        longitud_destino=request.destino_longitud,
    )

    # 3. Calcular precio usando el MOTOR UNIFICADO
    try:
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now(),
            es_feriado=False,  # O determinar externamente si tu app lo requiere
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

    El viaje se crea directo en estado 'en_curso' porque el pasajero
    ya está a bordo. No hay broadcast ni asignación: el chofer lo toma
    espontáneamente.

    Requiere:
    - Chofer autenticado (get_current_driver_user).
    - Chofer con vehículo activo en el tenant.
    - Chofer con turno activo (fleet.turno_chofer.estado = 'ACTIVO').
    - Destino obligatorio (para calcular precio).

    El precio se calcula con el MOTOR UNIFICADO TAXIP 2.1.
    """
    chofer_id, control_base_id, _, _ = current_user

    # 1. Validar método de pago
    METODOS_VALIDOS = {"efectivo", "tarjeta_debito", "qr", "transferencia"}
    if request.metodo_pago not in METODOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Método de pago inválido. Permitidos: {sorted(METODOS_VALIDOS)}",
        )

    # 2. Resolver chofer_vehiculo activo + turno activo en una sola query
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

    # 3. Calcular distancia, tiempo y precio con MOTOR UNIFICADO

    # 3.1. Distancia con Directions API (fallback Haversine)
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

    # 3.2. Preparar cálculo con Motor Unificado
    distancia_km = distancia_metros / 1000.0
    tiempo_minutos = tiempo_estimado_segundos // 60

    # Determinar tipo de vehículo (default 'standard' si no viene en el request)
    tipo_vehiculo_str = getattr(request, 'tipo_vehiculo', 'standard') or 'standard'
    try:
        tipo_vehiculo_enum = TipoVehiculoEnum(tipo_vehiculo_str.lower())
    except ValueError:
        tipo_vehiculo_enum = TipoVehiculoEnum.STANDARD

    estimacion_request = EstimacionPrecioRequest(
        tipo_vehiculo=tipo_vehiculo_enum,
        direccion_origen="",  # No usado para cálculo, pero requerido por schema
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

    # 3.3. Reverse geocoding del origen (G25)
    # Reemplaza el placeholder "Ubicación GPS del chofer" por la dirección real.
    geo = await reverse_geocode(request.origen_lat, request.origen_lng)
    direccion_origen_final = geo["direccion"]

    # 4. Insertar viaje
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

    # 5. Registrar historial de estado
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

    # 6. Marcar chofer ocupado
    update_chofer = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = 'ocupado',
            updated_at = NOW()
        WHERE id = :chofer_vehiculo_id
    """)
    await db.execute(update_chofer, {"chofer_vehiculo_id": chofer_vehiculo_id})

    # 7. Commit único
    await db.commit()

    # 8. Leer el viaje recién creado y devolverlo completo
    result = await db.execute(GET_VIAJE_BY_ID, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
    })
    row = result.first()
    return await formatear_respuesta_viaje(row)

# ============================================
# SOLICITAR VIAJE (LEGACY - DEPRECADO)
# ============================================
# A3: Endpoint sin clientes reales.
# Auditoria 2026-09-25: los 2 usos detectados (proxy dashboard huerfano +
# helper viajeApi.solicitar) nunca llegan con auth valido. El proxy va sin
# token (401) y el helper usa auth de dashboard (403, no es pasajero).
# No hay reemplazo directo identificado en el codigo. Candidato a eliminar
# en Fase 2 tras auditar el flujo completo de pedidos multi-canal.

@router.post("/solicitar", response_model=SolicitarViajeResponse, deprecated=True)
async def solicitar_viaje(
    request: SolicitarViajeRequest,
    current_user: tuple = Depends(get_current_passenger_user),
    db: AsyncSession = Depends(get_db)
):
    """
    [DEPRECADO 2026-09-25] Solicitar un viaje legacy.

    Asigna directo un chofer libre sin broadcast. Sin clientes reales.
    Candidato a eliminar.
    """

    user_id, control_base_id, _, _ = current_user

    if not control_base_id:
        default_cb = await db.execute(text("SELECT id FROM tenant.control_base LIMIT 1"))
        control_base_id = default_cb.scalar()
        if not control_base_id:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")

    driver_query = text("""
        SELECT cv.id, cv.usuario_id, cv.vehiculo_id
        FROM fleet.chofer_vehiculo cv
        WHERE cv.control_base_id = :control_base_id
          AND cv.estado_laboral = 'libre'
          AND cv.activo = true
        LIMIT 1
    """)

    driver_result = await db.execute(driver_query, {"control_base_id": control_base_id})
    driver_row = driver_result.first()

    if not driver_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay conductores disponibles"
        )

    chofer_vehiculo_id = driver_row[0]
    chofer_id = driver_row[1]
    vehiculo_id = driver_row[2]

    viaje_id = uuid_lib.uuid4()

    insert_query = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id, pasajero_id, chofer_id, vehiculo_id,
            direccion_origen, direccion_destino,
            estado, created_at
        )
        VALUES (
            :id, :control_base_id, :pasajero_id, :chofer_id, :vehiculo_id,
            :direccion_origen, :direccion_destino,
            'pendiente', NOW()
        )
        RETURNING id
    """)

    await db.execute(insert_query, {
        "id": viaje_id,
        "control_base_id": control_base_id,
        "pasajero_id": user_id,
        "chofer_id": chofer_id,
        "vehiculo_id": vehiculo_id,
        "direccion_origen": request.direccion_origen,
        "direccion_destino": request.direccion_destino
    })

    update_driver = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = 'ocupado'
        WHERE id = :chofer_vehiculo_id
    """)
    await db.execute(update_driver, {"chofer_vehiculo_id": chofer_vehiculo_id})

    await db.commit()

    return SolicitarViajeResponse(
        success=True,
        viaje_id=viaje_id,
        estado="pendiente",
        mensaje="Viaje solicitado. Esperando confirmación del conductor.",
        tiempo_estimado_segundos=None,
        precio_estimado=None
    )






# ============================================
# INCLUIR SUB-ROUTERS (refactor 2026-09-24)
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