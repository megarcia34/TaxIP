"""
Viajes - Endpoints de geocoding y mapa estático.
Extraído de routes.py (refactor 2026-09-24).

⚠️ IMPORTANTE: estos endpoints DEBEN registrarse ANTES de /{viaje_id}/estado.
Si van después, FastAPI matchea "geocode" y "mapa-estatico" como UUIDs
inválidos y devuelve 422.

El orden de include_router en routes.py respeta esta restricción.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.dependencies import get_current_driver_user
from app.services.geocoding_service import reverse_geocode
from app.services.static_maps_service import generar_url_mapa
from app.services.directions import directions_service

from .schemas import (
    ReverseGeocodeResponse,
    MapaEstaticoResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# REVERSE GEOCODING (M3 - Etapa 10.5.b)
# ============================================
# ⚠️ IMPORTANTE: esta ruta DEBE ir antes de /{viaje_id}/estado.
# Si va después, FastAPI matchea "geocode" como un UUID inválido
# y devuelve 422.

@router.get("/geocode/reverse", response_model=ReverseGeocodeResponse)
async def reverse_geocode_endpoint(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud"),
    current_user: tuple = Depends(get_current_driver_user),
):
    """
    Reverse geocoding: convierte (lat, lng) en una dirección legible.

    Ej: (-26.82368, -65.22860) -> "José Ignacio Thames 146, San Miguel de Tucumán"

    - Auth: chofer autenticado.
    - Cache: TTL 1 hora en memoria.
    - Timeout: 3 segundos.
    - Fallback: coordenadas formateadas si Google falla.
    """
    resultado = await reverse_geocode(lat, lng)
    return resultado


# ============================================
# MAPA ESTÁTICO (M3 - Etapa 10.5.b)
# ============================================
# ⚠️ IMPORTANTE: esta ruta DEBE ir antes de /{viaje_id}/estado.

@router.get("/mapa-estatico", response_model=MapaEstaticoResponse)
async def mapa_estatico_endpoint(
    origen_lat: float = Query(..., ge=-90, le=90),
    origen_lng: float = Query(..., ge=-180, le=180),
    destino_lat: float = Query(..., ge=-90, le=90),
    destino_lng: float = Query(..., ge=-180, le=180),
    ancho: int = Query(640, ge=100, le=1280),
    alto: int = Query(320, ge=100, le=1280),
    current_user: tuple = Depends(get_current_driver_user),
):
    """
    Genera una URL de Google Static Maps para visualizar el viaje.

    - Marcador azul "A" en origen.
    - Marcador rojo "B" en destino.
    - Recorrido real por calles (polilínea de Directions API).
      Si Directions falla, cae a línea recta entre origen y destino.
    - Zoom auto-calculado según la distancia Haversine.
    """
    # Intentar obtener la polilínea real de Directions API
    overview_polyline: Optional[str] = None
    try:
        ruta = await directions_service.calcular_ruta_por_coords(
            origen_lat, origen_lng,
            destino_lat, destino_lng,
        )
        if ruta:
            overview_polyline = ruta.get("overview_polyline")
    except Exception as e:
        logger.warning(
            f"Directions falló en mapa_estatico, usando línea recta: {e}"
        )

    try:
        url = generar_url_mapa(
            origen_lat=origen_lat,
            origen_lng=origen_lng,
            destino_lat=destino_lat,
            destino_lng=destino_lng,
            ancho=ancho,
            alto=alto,
            overview_polyline=overview_polyline,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return MapaEstaticoResponse(url=url)