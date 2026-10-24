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



# ============================================
# FORWARD GEOCODING (Para la app del chofer)
# ============================================

from pydantic import BaseModel

class GeocodeForwardRequest(BaseModel):
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class GeocodeForwardResponse(BaseModel):
    lat: float
    lng: float
    direccion_formateada: str

@router.post("/geocode/forward", response_model=GeocodeForwardResponse)
async def forward_geocode_endpoint(
    request: GeocodeForwardRequest,
    current_user: tuple = Depends(get_current_driver_user),
):
    """
    Forward geocoding: convierte una direccion de texto en coordenadas (lat, lng).
    Usa lat/lng opcionales para sesgar la busqueda a la zona del chofer.
    """
    lat, lng = await directions_service.obtener_coordenadas(
        request.address,
        lat_sesgo=request.lat,
        lng_sesgo=request.lng
    )
    
    if lat is None or lng is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro la direccion. Verifica que sea correcta."
        )
    
    return GeocodeForwardResponse(
        lat=lat,
        lng=lng,
        direccion_formateada=request.address
    )

# ============================================
# AUTOCOMPLETE Y PLACE DETAILS (Para la app del chofer)
# ============================================

class AutocompleteRequest(BaseModel):
    input: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class AutocompletePrediction(BaseModel):
    description: str
    place_id: str

class AutocompleteResponse(BaseModel):
    predictions: list[AutocompletePrediction]

class PlaceDetailsResponse(BaseModel):
    lat: float
    lng: float
    direccion_formateada: str

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_endpoint(
    request: AutocompleteRequest,
    current_user: tuple = Depends(get_current_driver_user),
):
    """
    Devuelve sugerencias de direcciones usando Google Places Autocomplete.
    Usa locationBias para priorizar resultados cercanos sin excluir otros.
    """
    from app.core.config import settings
    import httpx

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": request.input,
        "key": settings.GOOGLE_MAPS_API_KEY,
        "language": "es",
        "components": "country:ar",
    }

    if request.lat is not None and request.lng is not None:
        params["location"] = f"{request.lat},{request.lng}"
        params["radius"] = 50000  # 50 km (locationBias, no restrictivo)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            logger.error(f"❌ Error en Autocomplete API: {data.get('status')}")
            return AutocompleteResponse(predictions=[])

        predictions = [
            AutocompletePrediction(
                description=p["description"],
                place_id=p["place_id"],
            )
            for p in data.get("predictions", [])
        ]
        return AutocompleteResponse(predictions=predictions)
    except Exception as e:
        logger.error(f"❌ Error en Autocomplete API: {str(e)}")
        return AutocompleteResponse(predictions=[])


class PlaceDetailsRequest(BaseModel):
    place_id: str

@router.post("/geocode/place-details", response_model=PlaceDetailsResponse)
async def place_details_endpoint(
    request: PlaceDetailsRequest,
    current_user: tuple = Depends(get_current_driver_user),
):
    """
    Obtiene coordenadas y direccion formateada a partir de un place_id.
    """
    from app.core.config import settings
    import httpx

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": request.place_id,
        "key": settings.GOOGLE_MAPS_API_KEY,
        "fields": "geometry,formatted_address",
        "language": "es",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("status") != "OK":
            raise HTTPException(status_code=404, detail="Place no encontrado")

        result = data["result"]
        location = result["geometry"]["location"]

        return PlaceDetailsResponse(
            lat=location["lat"],
            lng=location["lng"],
            direccion_formateada=result.get("formatted_address", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en Place Details API: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener detalles del lugar")