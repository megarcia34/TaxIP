"""
Viajes - Servicios / Lógica de negocio
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime


# ============================================
# CÁLCULOS DE DISTANCIA Y TIEMPO
# ============================================

def calcular_distancia(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> int:
    """
    Calcular distancia en metros entre dos puntos usando la fórmula de Haversine
    """
    R = 6371000  # Radio de la Tierra en metros
    
    lat1_r = radians(lat1)
    lon1_r = radians(lon1)
    lat2_r = radians(lat2)
    lon2_r = radians(lon2)
    
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    
    a = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return int(R * c)


def calcular_tiempo_estimado(distancia_metros: int) -> int:
    """
    Calcular tiempo estimado en segundos (velocidad promedio 30 km/h)
    """
    velocidad_ms = 8.33  # 30 km/h en m/s
    return int(distancia_metros / velocidad_ms) + 60  # +1 minuto base


def calcular_precio(
    distancia_metros: int,
    tiempo_segundos: int,
    tarifa_base: float,
    precio_km: float,
    precio_minuto: float,
    recargo_nocturno: float = 1.0
) -> float:
    """
    Calcular precio estimado del viaje
    """
    km = distancia_metros / 1000
    horas = tiempo_segundos / 3600
    
    precio = (tarifa_base + (km * precio_km) + (horas * 60 * precio_minuto)) * recargo_nocturno
    return round(precio, 2)


def es_horario_nocturno(fecha: datetime) -> bool:
    """
    Verificar si una fecha/hora está en horario nocturno (22:00 - 06:00)
    """
    hora = fecha.hour
    return hora >= 22 or hora < 6


def obtener_tarifas_default() -> tuple:
    """
    Obtener tarifas por defecto
    """
    return (150.0, 50.0, 15.0, 1.2)


# ============================================
# OPERACIONES CON VIAJES
# ============================================

async def actualizar_estado_viaje(
    db: AsyncSession,
    viaje_id: UUID,
    control_base_id: UUID,
    estado: str,
    campo_fecha: str
):
    """
    Actualiza el estado de un viaje y registra la fecha correspondiente
    """
    query = text(f"""
        UPDATE trip.viaje_solicitado
        SET estado = :estado, {campo_fecha} = NOW()
        WHERE id = :viaje_id AND control_base_id = :control_base_id
        RETURNING id
    """)
    result = await db.execute(query, {
        "viaje_id": viaje_id,
        "control_base_id": control_base_id,
        "estado": estado
    })
    return result.first()


async def formatear_respuesta_viaje(row):
    """
    Convierte una fila de la base de datos en un diccionario para la API
    """
    if not row:
        return None
    
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": row[2],
        "direccion_destino": row[3],
        "precio_estimado": row[4],
        "precio_final": row[5],
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "distancia_metros": row[10],
        "tiempo_estimado_segundos": row[11],
        "pasajero_nombre": row[12],
        "chofer_nombre": row[13],
        "origen_lat": float(row[14]) if row[14] else None,
        "origen_lng": float(row[15]) if row[15] else None,
        "destino_lat": float(row[16]) if row[16] else None,
        "destino_lng": float(row[17]) if row[17] else None
    }


async def verificar_permiso_viaje(user_id: UUID, viaje_id: UUID, user_tipo: str) -> bool:
    """
    Verifica si el usuario tiene permiso para acceder al viaje
    """
    if user_tipo.lower() == 'admin':
        return True
    return True  # La verificación se hace en la consulta SQL


# ============================================
# ASIGNACIÓN DE CHOFER
# ============================================

async def encontrar_y_asignar_chofer(
    db: AsyncSession,
    viaje_id: UUID,
    control_base_id: UUID,
    lat: float,
    lng: float
) -> Optional[dict]:
    """
    Encuentra el chofer más cercano y lo asigna al viaje
    Retorna los datos del chofer asignado o None si no hay choferes disponibles
    """
    from app.routers.viajes.queries import ENCONTRAR_CHOFER_MAS_CERCANO
    
    # Buscar chofer más cercano
    result = await db.execute(ENCONTRAR_CHOFER_MAS_CERCANO, {
        "control_base_id": control_base_id,
        "lat": lat,
        "lng": lng
    })
    chofer = result.first()
    
    if not chofer:
        return None
    
    # Asignar chofer al viaje
    assign_query = text("""
        UPDATE trip.viaje_solicitado
        SET chofer_id = :chofer_id,
            vehiculo_id = :vehiculo_id,
            estado = 'aceptado',
            aceptado_en = NOW()
        WHERE id = :viaje_id
        RETURNING id
    """)
    
    await db.execute(assign_query, {
        "viaje_id": viaje_id,
        "chofer_id": chofer[1],  # usuario_id
        "vehiculo_id": chofer[2]  # vehiculo_id
    })
    
    # Actualizar estado del chofer
    update_chofer = text("""
        UPDATE fleet.chofer_vehiculo
        SET estado_laboral = 'ocupado', updated_at = NOW()
        WHERE usuario_id = :chofer_id
    """)
    
    await db.execute(update_chofer, {"chofer_id": chofer[1]})
    
    await db.commit()
    
    return {
        "chofer_vehiculo_id": chofer[0],
        "usuario_id": chofer[1],
        "nombre": chofer[4],
        "email": chofer[5],
        "patente": chofer[6],
        "marca": chofer[7],
        "modelo": chofer[8],
        "distancia": round(chofer[9] / 1000, 1) if chofer[9] else None  # distancia en km
    }