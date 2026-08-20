"""
Funciones auxiliares para el módulo de neumáticos
"""
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# ============================================================
# MAPEO DE POSICIONES (Frontend → Base de datos)
# ============================================================
POSICION_MAP = {
    'DI': 'D1',
    'DD': 'D2',
    'TI': 'T1',
    'TD': 'T2',
    'REPUESTO': 'REPUESTO'
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def determinar_color_neumatico(profundidad_mm: Optional[float], km_recorridos: int, vida_util_km: int) -> str:
    """
    Determina el color del neumático según profundidad y km recorridos.
    """
    if profundidad_mm is not None:
        if profundidad_mm >= 4.0:
            return "VERDE"
        elif profundidad_mm >= 2.0:
            return "AMARILLO"
        else:
            return "ROJO"
    
    # Si no hay medición, usar km como referencia
    porcentaje_km = (km_recorridos / vida_util_km) * 100 if vida_util_km > 0 else 0
    if porcentaje_km < 60:
        return "VERDE"
    elif porcentaje_km < 85:
        return "AMARILLO"
    else:
        return "ROJO"


def calcular_estado_neumatico(profundidad_mm: Optional[float], vida_util_km: int, km_recorridos: int) -> Dict[str, Any]:
    """
    Calcula el estado completo del neumático.
    """
    color = determinar_color_neumatico(profundidad_mm, km_recorridos, vida_util_km)
    
    if profundidad_mm is not None:
        if profundidad_mm >= 4.0:
            estado_texto = "BUENO"
            recomendacion = "Mantener"
        elif profundidad_mm >= 2.0:
            estado_texto = "ATENCION"
            recomendacion = "Planificar cambio en los próximos 5,000 km"
        else:
            estado_texto = "CRITICO"
            recomendacion = "¡Cambiar inmediatamente!"
    else:
        porcentaje_km = (km_recorridos / vida_util_km) * 100 if vida_util_km > 0 else 0
        if porcentaje_km < 60:
            estado_texto = "BUENO"
            recomendacion = "Mantener"
        elif porcentaje_km < 85:
            estado_texto = "ATENCION"
            recomendacion = "Planificar cambio"
        else:
            estado_texto = "CRITICO"
            recomendacion = "¡Cambiar inmediatamente!"
    
    return {
        "color": color,
        "estado_texto": estado_texto,
        "recomendacion": recomendacion
    }


def generar_codigo_interno(patente: str, posicion: str, secuencia: int) -> str:
    """
    Genera un código interno para el neumático.
    Formato: {patente}-{posicion}-{secuencia}
    """
    return f"{patente}-{posicion}-{secuencia:03d}"


async def get_patente_vehiculo(vehiculo_id: UUID, db: AsyncSession) -> str:
    """Obtiene la patente de un vehículo."""
    query = text("SELECT patente FROM fleet.vehiculo WHERE id = :vehiculo_id")
    result = await db.execute(query, {"vehiculo_id": vehiculo_id})
    row = result.first()
    return row[0] if row else "UNKNOWN"


async def generar_sugerencia_neumatico(
    neumatico_id: UUID,
    vehiculo_id: UUID,
    control_base_id: UUID,
    tipo_sugerencia: str,
    prioridad: str,
    mensaje: str,
    km_actual: int,
    db: AsyncSession
) -> Optional[str]:
    """
    Genera una sugerencia automática para un neumático.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        insert_sugerencia = text("""
            INSERT INTO fleet.neumatico_sugerencia (
                id, vehiculo_id, control_base_id, tipo_sugerencia,
                neumatico_vehiculo_id, mensaje, prioridad,
                km_actual, estado, fecha_generacion
            ) VALUES (
                gen_random_uuid(), :vehiculo_id, :control_base_id, :tipo_sugerencia,
                :neumatico_id, :mensaje, :prioridad,
                :km_actual, 'PENDIENTE', NOW()
            ) RETURNING id
        """)
        result = await db.execute(insert_sugerencia, {
            "vehiculo_id": vehiculo_id,
            "control_base_id": control_base_id,
            "tipo_sugerencia": tipo_sugerencia,
            "neumatico_id": neumatico_id,
            "mensaje": mensaje,
            "prioridad": prioridad,
            "km_actual": km_actual
        })
        sugerencia_id = result.scalar()
        await db.commit()
        return str(sugerencia_id)
    except Exception as e:
        logger.error(f"Error generando sugerencia: {e}")
        return None


# ============================================================
# MAPEO INVERSO
# ============================================================
def get_posicion_inversa():
    """Retorna el mapeo inverso de posiciones."""
    return {v: k for k, v in POSICION_MAP.items()}