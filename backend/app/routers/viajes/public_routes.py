"""
Public endpoints for web booking (no authentication required)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4, UUID
from datetime import datetime
import logging

from app.database import get_db
from app.routers.viajes.schemas import (
    SolicitarViajePublicoRequest,
    SolicitarViajePublicoResponse
)
from app.routers.viajes.services import encontrar_y_asignar_chofer
from app.services.precio_estimado import calcular_precio_estimado
from app.schemas.reserva_schemas import EstimacionPrecioRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/public/viajes", tags=["Public - Viajes"])


@router.post("/calcular-tarifa")
async def calcular_tarifa_publico(
    origen_lat: float,
    origen_lng: float,
    destino_lat: float,
    destino_lng: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate estimated fare (public endpoint)
    USANDO EL MISMO SERVICIO QUE EL DASHBOARD CORPORATIVO
    """
    try:
        # 1. Obtener control_base_id por defecto
        query = text("SELECT id FROM tenant.control_base LIMIT 1")
        result = await db.execute(query)
        row = result.first()
        if not row:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")
        control_base_id = row[0]
        
        # 2. Calcular distancia (Haversine)
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        lat1, lon1 = radians(origen_lat), radians(origen_lng)
        lat2, lon2 = radians(destino_lat), radians(destino_lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distancia_km = R * c
        
        # 3. Calcular tiempo estimado (~2 min por km)
        tiempo_minutos = max(1, int(distancia_km * 2))
        
        # 4. Usar el servicio unificado de cálculo de tarifa
        # Crear request con todos los campos requeridos
        estimacion_request = EstimacionPrecioRequest(
            tipo_vehiculo="standard",
            direccion_origen="",  # Campo requerido, no usado para cálculo
            direccion_destino="",  # Campo requerido, no usado para cálculo
            paradas_intermedias=[],
            tiempo_espera_minutos=0,
            latitud_origen=origen_lat,
            longitud_origen=origen_lng,
            latitud_destino=destino_lat,
            longitud_destino=destino_lng
        )
        
        # Obtener el precio usando el servicio completo
        resultado = await calcular_precio_estimado(
            request=estimacion_request,
            control_base_id=control_base_id,
            db=db,
            distancia_km=distancia_km,
            tiempo_minutos=tiempo_minutos,
            fecha_hora=datetime.now()
        )
        
        return {
            "success": True,
            "tarifa": resultado.precio_estimado,
            "distancia_km": resultado.distancia_km,
            "tiempo_estimado_min": resultado.tiempo_minutos,
            "tarifa_base": resultado.desglose.get("bajada", 0),
            "precio_por_km": resultado.desglose.get("precio_por_km", 0),
            "modo_calculo": resultado.modo_calculo,
            "moneda": resultado.moneda,
            "desglose": resultado.desglose,
            "recargos": resultado.recargos_aplicados
        }
        
    except Exception as e:
        logger.error(f"Error calculando tarifa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular tarifa: {str(e)}"
        )


@router.get("/calcular-tarifa")
async def calcular_tarifa_publico_get(
    origen_lat: float,
    origen_lng: float,
    destino_lat: float,
    destino_lng: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate estimated fare (public endpoint) - GET version
    """
    return await calcular_tarifa_publico(origen_lat, origen_lng, destino_lat, destino_lng, db)


@router.post("/solicitar", response_model=SolicitarViajePublicoResponse)
async def solicitar_viaje_publico(
    request: SolicitarViajePublicoRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a trip (public endpoint) - automatic driver assignment
    """
    try:
        # Obtener control_base_id por defecto
        query = text("SELECT id FROM tenant.control_base LIMIT 1")
        result = await db.execute(query)
        row = result.first()
        if not row:
            raise HTTPException(status_code=400, detail="No hay empresa configurada")
        control_base_id = row[0]
        
        # Obtener o crear pasajero
        pasajero_id = None
        
        if request.telefono_pasajero:
            query = text("""
                SELECT u.id FROM auth.usuario u
                JOIN auth.perfil_general p ON p.usuario_id = u.id
                WHERE p.telefono = :telefono
            """)
            result = await db.execute(query, {"telefono": request.telefono_pasajero})
            row = result.first()
            if row:
                pasajero_id = row[0]
        
        if not pasajero_id:
            tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero'")
            tipo_result = await db.execute(tipo_query)
            tipo_row = tipo_result.first()
            if not tipo_row:
                raise HTTPException(status_code=400, detail="Tipo de usuario 'pasajero' no encontrado")
            tipo_usuario_id = tipo_row[0]
            
            pasajero_id = uuid4()
            insert_user = text("""
                INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
                VALUES (:id, :tipo_id, :control_base_id, :email, :password_hash, true, NOW())
            """)
            await db.execute(insert_user, {
                "id": pasajero_id,
                "tipo_id": tipo_usuario_id,
                "control_base_id": control_base_id,
                "email": request.telefono_pasajero + "@temp.taxip.com" if request.telefono_pasajero else f"{uuid4()}@temp.taxip.com",
                "password_hash": "$2b$12$temp"
            })
            
            insert_perfil = text("""
                INSERT INTO auth.perfil_general (id, usuario_id, nombre, telefono, created_at)
                VALUES (gen_random_uuid(), :user_id, :nombre, :telefono, NOW())
            """)
            await db.execute(insert_perfil, {
                "user_id": pasajero_id,
                "nombre": request.nombre_pasajero or "Usuario Web",
                "telefono": request.telefono_pasajero
            })
            
            await db.commit()
        
        # Crear viaje
        viaje_id = uuid4()
        insert_viaje = text("""
            INSERT INTO trip.viaje_solicitado (
                id, control_base_id, pasajero_id,
                direccion_origen, direccion_destino,
                origen, destino,
                estado, precio_estimado, created_at, nombre_pasajero
            )
            VALUES (
                :id, :control_base_id, :pasajero_id,
                :direccion_origen, :direccion_destino,
                ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326),
                ST_SetSRID(ST_MakePoint(:destino_lng, :destino_lat), 4326),
                'pendiente', :precio_estimado, NOW(), :nombre_pasajero
            )
            RETURNING id
        """)
        
        await db.execute(insert_viaje, {
            "id": viaje_id,
            "control_base_id": control_base_id,
            "pasajero_id": pasajero_id,
            "direccion_origen": request.direccion_origen,
            "direccion_destino": request.direccion_destino,
            "origen_lat": request.origen_lat,
            "origen_lng": request.origen_lng,
            "destino_lat": request.destino_lat,
            "destino_lng": request.destino_lng,
            "precio_estimado": request.precio_estimado or 0,
            "nombre_pasajero": request.nombre_pasajero or "Usuario Web"
        })
        
        await db.commit()
        
        # Buscar y asignar chofer automáticamente
        chofer_asignado = await encontrar_y_asignar_chofer(
            db, viaje_id, control_base_id, request.origen_lat, request.origen_lng
        )
        
        tiempo_espera = 5
        if chofer_asignado and chofer_asignado.get("distancia"):
            tiempo_espera = max(1, int(chofer_asignado["distancia"] * 2))
        
        return SolicitarViajePublicoResponse(
            success=True,
            viaje_id=viaje_id,
            mensaje="Viaje solicitado correctamente" + (" - Conductor asignado" if chofer_asignado else " - Buscando conductor..."),
            chofer_asignado=chofer_asignado,
            tiempo_espera_estimado=tiempo_espera if chofer_asignado else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solicitando viaje público: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al solicitar viaje: {str(e)}"
        )
    
    # ============================================
# OBTENER ESTADO DEL VIAJE (PÚBLICO)
# ============================================
@router.get("/{viaje_id}/estado")
async def obtener_estado_viaje_publico(
    viaje_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado de un viaje (público - sin autenticación)
    """
    query = text("""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_estimado,
            vs.precio_final,
            vs.created_at,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en,
            vs.nombre_pasajero,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            ST_X(vs.origen::geometry) as origen_lat,
            ST_Y(vs.origen::geometry) as origen_lng,
            ST_X(vs.destino::geometry) as destino_lat,
            ST_Y(vs.destino::geometry) as destino_lng
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE vs.id = :viaje_id
    """)
    
    result = await db.execute(query, {"viaje_id": viaje_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": row[2],
        "direccion_destino": row[3],
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "pasajero_nombre": row[10],
        "chofer_nombre": row[11],
        "origen_lat": float(row[12]) if row[12] else None,
        "origen_lng": float(row[13]) if row[13] else None,
        "destino_lat": float(row[14]) if row[14] else None,
        "destino_lng": float(row[15]) if row[15] else None,
    }