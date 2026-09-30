"""
Servicio de Geocoding (reverse) usando Google Maps Geocoding API.

Dado un (lat, lng), devuelve una dirección legible en formato:
    "route + street_number + locality"
Ej: "José Ignacio Thames 146, San Miguel de Tucumán"

- Cache en memoria con TTL 1 hora (dict simple, sin Redis).
- Timeout 3 segundos.
- Fallback: coordenadas formateadas si la API falla.
- Multi-tenant safe: no depende de control_base_id.

Uso:
    from app.services.geocoding_service import reverse_geocode
    resultado = await reverse_geocode(-26.82368, -65.22860)
    # {"direccion": "...", "lat": ..., "lng": ..., "fuente": "google"|"cache"|"fallback"}
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================
# CACHE EN MEMORIA (TTL 1 HORA)
# ============================================================

_CACHE_TTL_SEGUNDOS = 3600  # 1 hora
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _cache_key(lat: float, lng: float) -> str:
    """
    Redondea a 5 decimales (~1 metro de precisión) para agrupar
    llamadas cercanas. Evita que pequeñas variaciones generen
    misses innecesarios.
    """
    return f"{round(lat, 5)},{round(lng, 5)}"


def _cache_get(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    key = _cache_key(lat, lng)
    entry = _cache.get(key)
    if not entry:
        return None
    ts, valor = entry
    if time.time() - ts > _CACHE_TTL_SEGUNDOS:
        del _cache[key]
        return None
    return valor


def _cache_set(lat: float, lng: float, valor: Dict[str, Any]) -> None:
    key = _cache_key(lat, lng)
    _cache[key] = (time.time(), valor)


def limpiar_cache() -> int:
    """
    Limpia toda la cache. Útil para tests. Devuelve cuántas entradas borró.
    """
    n = len(_cache)
    _cache.clear()
    return n


# ============================================================
# SERVICIO
# ============================================================

class GeocodingService:
    """
    Servicio para reverse geocoding con Google Maps Geocoding API.
    """

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.timeout = 3.0

        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY no configurada en .env")

    async def reverse_geocode(
        self,
        lat: float,
        lng: float,
    ) -> Dict[str, Any]:
        """
        Reverse geocoding de un punto. Devuelve dict con:
            - direccion: str
            - lat, lng: float (los mismos que vinieron)
            - fuente: "cache" | "google" | "fallback"
        """
        # 1. Cache hit
        cached = _cache_get(lat, lng)
        if cached:
            return {**cached, "fuente": "cache"}

        # 2. Sin API key: fallback directo
        if not self.api_key:
            logger.warning("Sin GOOGLE_MAPS_API_KEY, usando fallback")
            return self._fallback(lat, lng)

        # 3. Llamada a Google
        try:
            url = (
                f"{self.base_url}"
                f"?latlng={lat},{lng}"
                f"&language=es"
                f"&region=ar"
                f"&key={self.api_key}"
            )

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "OK":
                logger.warning(
                    "Geocoding API status=%s (lat=%s, lng=%s)",
                    data.get("status"), lat, lng
                )
                return self._fallback(lat, lng)

            resultados = data.get("results") or []
            if not resultados:
                logger.warning("Geocoding API sin resultados para %s,%s", lat, lng)
                return self._fallback(lat, lng)

            direccion = self._construir_direccion(resultados[0])
            if not direccion:
                return self._fallback(lat, lng)

            valor = {
                "direccion": direccion,
                "lat": lat,
                "lng": lng,
                "fuente": "google",
            }
            _cache_set(lat, lng, valor)
            logger.info("Reverse geocode OK: %s -> %s", (lat, lng), direccion)
            return valor

        except httpx.TimeoutException:
            logger.warning("Timeout en Geocoding API (lat=%s, lng=%s)", lat, lng)
            return self._fallback(lat, lng)
        except Exception as e:
            logger.error("Error en Geocoding API: %s", e)
            return self._fallback(lat, lng)

    def _construir_direccion(self, resultado: Dict[str, Any]) -> Optional[str]:
        """
        Extrae route + street_number + locality del primer resultado.

        Si no hay locality, cae a sublocality o admin area.
        Si no hay route ni street_number, usa formatted_address.
        """
        componentes = resultado.get("address_components") or []

        route: Optional[str] = None
        street_number: Optional[str] = None
        locality: Optional[str] = None
        sublocality: Optional[str] = None

        for c in componentes:
            types = c.get("types") or []
            if "route" in types and not route:
                route = c.get("long_name")
            elif "street_number" in types and not street_number:
                street_number = c.get("long_name")
            elif "locality" in types and not locality:
                locality = c.get("long_name")
            elif "sublocality" in types and not sublocality:
                sublocality = c.get("long_name")

        # Preferir locality, sino sublocality
        zona = locality or sublocality

        # Armar: "Calle 146, Localidad"
        if route and street_number:
            calle = f"{route} {street_number}"
        elif route:
            calle = route
        else:
            # Último recurso: formatted_address recortado
            fa = resultado.get("formatted_address")
            if fa:
                return fa
            return None

        if zona:
            return f"{calle}, {zona}"
        return calle

    def _fallback(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Fallback: coordenadas formateadas.
        """
        direccion = f"({lat:.5f}, {lng:.5f})"
        valor = {
            "direccion": direccion,
            "lat": lat,
            "lng": lng,
            "fuente": "fallback",
        }
        _cache_set(lat, lng, valor)
        return valor


# ============================================================
# INSTANCIA SINGLETON
# ============================================================

geocoding_service = GeocodingService()


# ============================================================
# HELPER DE MÓDULO (para uso directo)
# ============================================================

async def reverse_geocode(lat: float, lng: float) -> Dict[str, Any]:
    """
    Atajo para llamar al servicio. Útil para imports directos en routes.
    """
    return await geocoding_service.reverse_geocode(lat, lng)