"""
Geo Service - Busqueda geoespacial de choferes.

Usa PostGIS (ST_DWithin, ST_Distance) para encontrar choferes elegibles
dentro de un radio, aplicando filtros opt-in del viaje.
"""
import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography

from app.models.fleet import ChoferVehiculo, Vehiculo

logger = logging.getLogger(__name__)


# ============================================================
# HELPERS DE FILTROS OPT-IN
# ============================================================

def _calidad_suficiente(calidad_vehiculo: str, calidad_minima: str) -> bool:
    """
    Verifica que el vehiculo cumpla la calidad minima.
    Orden: regular < bueno < excelente
    """
    orden = {"regular": 1, "bueno": 2, "excelente": 3}
    return orden.get(calidad_vehiculo, 0) >= orden.get(calidad_minima, 0)


def _baul_suficiente(capacidad_baul: str, requiere_baul_grande: bool) -> bool:
    """
    Verifica que el baul sea suficiente si el viaje requiere baul grande.
    """
    if not requiere_baul_grande:
        return True
    return capacidad_baul in ("baul_grande", "van_carga")


# ============================================================
# BUSQUEDA PRINCIPAL
# ============================================================

async def buscar_choferes_cercanos(
    db: AsyncSession,
    control_base_id: UUID,
    lat: float,
    lng: float,
    radio_metros: int = 2000,
    requiere_baul_grande: bool = False,
    calidad_minima_vehiculo: Optional[str] = None,
    tipo_vehiculo_solicitado: Optional[str] = None,
    excluir_chofer_ids: Optional[List[UUID]] = None,
    limit: int = 50,
) -> List[dict]:
    """
    Busca choferes elegibles cerca de (lat, lng) usando PostGIS.

    Filtros aplicados:
    - control_base_id (multi-tenant)
    - estado_laboral = 'libre'
    - activo = True
    - estado_aprobacion = 'aprobado'
    - ubicacion IS NOT NULL
    - ST_DWithin(ubicacion, punto, radio_metros)
    - Filtros opt-in (baul, calidad)
    - Excluir lista de choferes (rechazaron antes)

    Returns:
        Lista de dicts con:
        - chofer_id (UUID)
        - vehiculo_id (UUID)
        - chofer_vehiculo_id (UUID)
        - distancia_metros (float)
        - capacidad_baul (str)
        - estado_vehiculo (str)
        - patente (str)
        - calificacion_promedio (float)
    """
    # Punto de referencia (PostGIS Geography)
    punto = func.ST_SetSRID(
        func.ST_MakePoint(lng, lat),
        4326
    ).cast(Geography)

    # Query base
    query = (
        select(
            ChoferVehiculo.id.label("chofer_vehiculo_id"),
            ChoferVehiculo.usuario_id.label("chofer_id"),
            ChoferVehiculo.vehiculo_id.label("vehiculo_id"),
            ChoferVehiculo.calificacion_promedio,
            Vehiculo.capacidad_baul,
            Vehiculo.estado_vehiculo,
            Vehiculo.patente,
            func.ST_Distance(ChoferVehiculo.ubicacion, punto).label("distancia_metros"),
        )
        .join(Vehiculo, Vehiculo.id == ChoferVehiculo.vehiculo_id)
        .where(
            ChoferVehiculo.control_base_id == control_base_id,
            ChoferVehiculo.estado_laboral == "libre",
            ChoferVehiculo.activo.is_(True),
            ChoferVehiculo.estado_aprobacion == "aprobado",
            ChoferVehiculo.ubicacion.isnot(None),
            func.ST_DWithin(ChoferVehiculo.ubicacion, punto, radio_metros),
        )
        .order_by(func.ST_Distance(ChoferVehiculo.ubicacion, punto).asc())
        .limit(limit)
    )

    # Filtro: excluir choferes que ya rechazaron
    if excluir_chofer_ids:
        query = query.where(ChoferVehiculo.usuario_id.notin_(excluir_chofer_ids))

    result = await db.execute(query)
    candidatos = result.all()

    # Filtros opt-in (aplicados en Python para simplicidad)
    elegibles = []
    excluidos = []

    for row in candidatos:
        c = dict(row._mapping)

        # Filtro: baul grande
        if not _baul_suficiente(c["capacidad_baul"], requiere_baul_grande):
            excluidos.append({**c, "motivo_exclusion": "baul_insuficiente"})
            continue

        # Filtro: calidad minima
        if calidad_minima_vehiculo:
            if not _calidad_suficiente(c["estado_vehiculo"], calidad_minima_vehiculo):
                excluidos.append({**c, "motivo_exclusion": "calidad_insuficiente"})
                continue

        # Filtro: tipo de vehiculo (TODO Etapa 6)
        # El modelo Vehiculo aun no tiene tipo_vehiculo. Se implementa
        # cuando se agregue la relacion.

        elegibles.append(c)

    logger.info(
        f"GeoService: {len(elegibles)} elegibles, {len(excluidos)} excluidos "
        f"(tenant={control_base_id}, radio={radio_metros}m)"
    )

    # Guardamos la lista de excluidos en un atributo interno temporal
    # para que broadcast_service pueda notificarlos
    for c in elegibles:
        c["_excluidos"] = excluidos

    return elegibles


async def contar_choferes_disponibles(
    db: AsyncSession,
    control_base_id: UUID,
) -> int:
    """
    Cuenta choferes con turno activo y disponibles (sin filtros de radio).
    Util para el dashboard operativo (validacion previa al despacho).
    """
    query = (
        select(func.count(ChoferVehiculo.id))
        .where(
            ChoferVehiculo.control_base_id == control_base_id,
            ChoferVehiculo.estado_laboral == "libre",
            ChoferVehiculo.activo.is_(True),
            ChoferVehiculo.estado_aprobacion == "aprobado",
        )
    )
    result = await db.execute(query)
    return result.scalar() or 0


async def obtener_ubicacion_chofer(
    db: AsyncSession,
    chofer_id: UUID,
) -> Optional[dict]:
    """
    Devuelve la ultima ubicacion conocida de un chofer.
    """
    query = (
        select(
            ChoferVehiculo.latitud,
            ChoferVehiculo.longitud,
            ChoferVehiculo.ultima_conexion,
            ChoferVehiculo.estado_laboral,
        )
        .where(ChoferVehiculo.usuario_id == chofer_id)
        .limit(1)
    )
    result = await db.execute(query)
    row = result.first()
    return dict(row._mapping) if row else None