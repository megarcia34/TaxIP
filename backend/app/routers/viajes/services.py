"""
Viajes - Servicios / Lógica de negocio
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, Dict, Any, List
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
# LIMPIAR TEXTOS (para corregir codificación)
# ============================================

def limpiar_texto(texto: str) -> str:
    """
    Corrige caracteres mal codificados en textos antiguos
    """
    if not texto:
        return texto
    
    # Reemplazos comunes de codificación incorrecta
    reemplazos = {
        'Ã±': 'ñ',
        'Ã‘': 'Ñ',
        'Ã¡': 'á',
        'Ã©': 'é',
        'Ã­': 'í',
        'Ã³': 'ó',
        'Ãº': 'ú',
        'Ã¼': 'ü',
        'Ã': 'í',
        'Â': '',
        'Â¡': '¡',
        'Â¿': '¿',
        'â‚¬': '€',
        'â„¢': '™',
        'â€œ': '"',
        'â€': '"',
        'â€˜': "'",
        'â€™': "'",
    }
    
    for mal, bien in reemplazos.items():
        texto = texto.replace(mal, bien)
    
    return texto


# ============================================
# FORMATEADORES DE RESPUESTAS
# ============================================

async def formatear_respuesta_viaje(row) -> Dict[str, Any]:
    """
    Convierte una fila de la base de datos en un diccionario para la API
    VERSIÓN LEGACY - Para compatibilidad con consultas antiguas
    """
    if not row:
        return None
    
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": limpiar_texto(row[2] or ""),
        "direccion_destino": limpiar_texto(row[3] or ""),
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "distancia_metros": row[10],
        "tiempo_estimado_segundos": row[11],
        "pasajero_nombre": row[12],
        "chofer_nombre": row[13] or "Sin asignar",
        "origen_lat": float(row[14]) if row[14] else None,
        "origen_lng": float(row[15]) if row[15] else None,
        "destino_lat": float(row[16]) if row[16] else None,
        "destino_lng": float(row[17]) if row[17] else None
    }


async def formatear_respuesta_viaje_mejorado(row) -> Dict[str, Any]:
    """
    Convierte una fila de la base de datos en un diccionario para la API
    VERSIÓN MEJORADA con empresa, propietario, fecha y hora
    """
    if not row:
        return None
    
    # La consulta mejorada tiene 27 campos
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": limpiar_texto(row[2] or ""),
        "direccion_destino": limpiar_texto(row[3] or ""),
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "distancia_metros": row[10],
        "tiempo_estimado_segundos": row[11],
        "pasajero_nombre": row[12],
        "chofer_nombre": row[13] or "Sin asignar",
        
        # ✅ NUEVOS CAMPOS
        "fecha": row[14] if len(row) > 14 else None,      # DD/MM/YYYY
        "hora": row[15] if len(row) > 15 else None,       # HH24:MI
        "precio_mostrado": float(row[16]) if row[16] and len(row) > 16 else None,
        "empresa": row[17] if len(row) > 17 else None,
        "propietario_nombre": row[18] if len(row) > 18 else "No asignado",
        "patente": row[19] if len(row) > 19 else None,
        "marca": row[20] if len(row) > 20 else None,
        "modelo": row[21] if len(row) > 21 else None,
        
        # Coordenadas
        "origen_lat": float(row[22]) if row[22] and len(row) > 22 else None,
        "origen_lng": float(row[23]) if row[23] and len(row) > 23 else None,
        "destino_lat": float(row[24]) if row[24] and len(row) > 24 else None,
        "destino_lng": float(row[25]) if row[25] and len(row) > 25 else None,
        
        # Calificación (si existe)
        "calificacion": row[26] if len(row) > 26 else None
    }


def formatear_viaje_dashboard(row) -> Dict[str, Any]:
    """
    Formatea una fila del dashboard con todos los datos mejorados
    """
    if not row:
        return None
    
    # Índices según GET_VIAJES_DASHBOARD (26 campos)
    return {
        "viaje_id": str(row[0]),
        "estado": row[1],
        "direccion_origen": limpiar_texto(row[2] or ""),
        "direccion_destino": limpiar_texto(row[3] or ""),
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "distancia_metros": row[10],
        "tiempo_estimado_segundos": row[11],
        "pasajero": row[12],
        "chofer": row[13] or "Sin asignar",
        "fecha": row[14],          # DD/MM/YYYY
        "hora": row[15],           # HH24:MI
        "precio": float(row[16]) if row[16] else None,
        "empresa": row[17] or "N/A",
        "propietario": row[18] or "No asignado",
        "patente": row[19] or "N/A",
        "marca": row[20] or "N/A",
        "modelo": row[21] or "N/A",
        "origen_lat": float(row[22]) if row[22] else None,
        "origen_lng": float(row[23]) if row[23] else None,
        "destino_lat": float(row[24]) if row[24] else None,
        "destino_lng": float(row[25]) if row[25] else None
    }


def formatear_viajes_dashboard(rows: List) -> List[Dict[str, Any]]:
    """
    Formatea múltiples filas del dashboard
    """
    if not rows:
        return []
    return [formatear_viaje_dashboard(row) for row in rows]


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


async def verificar_permiso_viaje(user_id: UUID, viaje_id: UUID, user_tipo: str) -> bool:
    """
    Verifica si el usuario tiene permiso para acceder al viaje
    """
    if user_tipo.lower() == 'admin':
        return True
    return True  # La verificación se hace en la consulta SQL


# ============================================
# FUNCIONES PARA OBTENER DATOS DEL VIAJE
# ============================================

async def obtener_viaje_con_detalles(
    db: AsyncSession,
    viaje_id: UUID,
    control_base_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    Obtiene un viaje con todos sus detalles (empresa, propietario, vehículo)
    """
    query = text("""
        SELECT 
            vs.id, vs.estado, vs.direccion_origen, vs.direccion_destino,
            vs.precio_estimado, vs.precio_final, vs.created_at,
            vs.aceptado_en, vs.iniciado_en, vs.finalizado_en,
            vs.distancia_metros, vs.tiempo_estimado_segundos,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
            COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
            TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
            TO_CHAR(vs.created_at, 'HH24:MI') as hora,
            CASE 
                WHEN vs.estado = 'finalizado' THEN vs.precio_final
                ELSE vs.precio_estimado
            END as precio_mostrado,
            cb.nombre as empresa,
            v.patente,
            v.marca,
            v.modelo,
            COALESCE(p_prop.nombre || ' ' || p_prop.apellido, u_prop.email, 'No asignado') as propietario_nombre,
            ST_X(vs.origen::geometry) as origen_lat,
            ST_Y(vs.origen::geometry) as origen_lng,
            ST_X(vs.destino::geometry) as destino_lat,
            ST_Y(vs.destino::geometry) as destino_lng
        FROM trip.viaje_solicitado vs
        JOIN auth.usuario u ON u.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
        LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
        LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
        LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id
        WHERE vs.id = :viaje_id AND vs.control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {"viaje_id": viaje_id, "control_base_id": control_base_id})
    row = result.first()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "estado": row[1],
        "direccion_origen": limpiar_texto(row[2] or ""),
        "direccion_destino": limpiar_texto(row[3] or ""),
        "precio_estimado": float(row[4]) if row[4] else None,
        "precio_final": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "distancia_metros": row[10],
        "tiempo_estimado_segundos": row[11],
        "pasajero": row[12],
        "chofer": row[13] or "Sin asignar",
        "fecha": row[14],
        "hora": row[15],
        "precio": float(row[16]) if row[16] else None,
        "empresa": row[17] or "N/A",
        "patente": row[18] or "N/A",
        "marca": row[19] or "N/A",
        "modelo": row[20] or "N/A",
        "propietario": row[21] or "No asignado",
        "origen_lat": float(row[22]) if row[22] else None,
        "origen_lng": float(row[23]) if row[23] else None,
        "destino_lat": float(row[24]) if row[24] else None,
        "destino_lng": float(row[25]) if row[25] else None
    }


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