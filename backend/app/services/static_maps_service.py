"""
Servicio de Static Maps API de Google.

Genera URLs firmadas de Google Static Maps a partir de coordenadas
de origen y destino. La URL se sirve al frontend, que la usa en un
componente <Image />.

- Sin cache: cada URL es única por viaje (o por par origen-destino).
- Sin timeout: es solo generación de string, no hay llamada HTTP.
- El frontend es el que hace la request real a Google.

Uso:
    from app.services.static_maps_service import generar_url_mapa
    url = generar_url_mapa(-26.8241, -65.2226, -26.8320, -65.2050)
"""
from typing import Optional
from urllib.parse import urlencode

from app.core.config import settings


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "https://maps.googleapis.com/maps/api/staticmap"

# Defaults
DEFAULT_ANCHO = 640
DEFAULT_ALTO = 320
DEFAULT_SCALE = 2         # retina
DEFAULT_MAPTYPE = "roadmap"
DEFAULT_ZOOM = 14         # fallback si no se puede calcular por distancia

# Colores de marcadores (formato Google Static Maps)
COLOR_ORIGEN = "0x1E88E5"   # azul
COLOR_DESTINO = "0xE53935"  # rojo
COLOR_PATH = "0x1E88E5FF"   # azul con alpha FF


# ============================================================
# HELPERS
# ============================================================

def _zoom_para_distancia(distancia_metros: Optional[float]) -> int:
    """
    Devuelve un zoom sugerido según la distancia entre origen y destino.
    Si no hay distancia, usa DEFAULT_ZOOM.
    """
    if distancia_metros is None:
        return DEFAULT_ZOOM
    if distancia_metros < 500:
        return 16
    if distancia_metros < 1500:
        return 15
    if distancia_metros < 3000:
        return 14
    if distancia_metros < 7000:
        return 13
    if distancia_metros < 15000:
        return 12
    if distancia_metros < 40000:
        return 11
    return 10


# ============================================================
# GENERACIÓN DE URL
# ============================================================

def generar_url_mapa(
    origen_lat: float,
    origen_lng: float,
    destino_lat: float,
    destino_lng: float,
    ancho: int = DEFAULT_ANCHO,
    alto: int = DEFAULT_ALTO,
    zoom: Optional[int] = None,
    overview_polyline: Optional[str] = None,
) -> str:
    """
    Genera una URL de Google Static Maps con:
    - Marcador azul "A" en origen.
    - Marcador rojo "B" en destino.
    - Recorrido por calles si se pasa `overview_polyline` (encoded polyline
      de Directions API). Si no, línea recta entre origen y destino.

    El frontend la usa directo en <Image source={{ uri: url }} />.

    Args:
        origen_lat, origen_lng: coordenadas del origen.
        destino_lat, destino_lng: coordenadas del destino.
        ancho, alto: tamaño de la imagen en px.
        zoom: si no se pasa, se calcula automáticamente según la
              distancia Haversine entre los dos puntos.
        overview_polyline: encoded polyline de Directions API. Si viene,
              se usa para dibujar el recorrido real por calles. Si no,
              se dibuja una recta entre origen y destino.

    Lanza ValueError si la API key no está configurada.
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY no configurada en .env")

    # Calcular zoom si no vino
    if zoom is None:
        # Import local para evitar dependencia circular
        from app.routers.viajes.services import calcular_distancia
        distancia = calcular_distancia(
            origen_lat, origen_lng, destino_lat, destino_lng
        )
        zoom = _zoom_para_distancia(distancia)

    # Armar la polilínea: recorrido real si viene, recta si no
    if overview_polyline:
        path_value = f"color:{COLOR_PATH}|weight:4|enc:{overview_polyline}"
    else:
        path_value = (
            f"color:{COLOR_PATH}|weight:4|"
            f"{origen_lat},{origen_lng}|{destino_lat},{destino_lng}"
        )

    # Armamos la URL con múltiples parámetros del mismo nombre.
    # urlencode() solo no alcanza: necesitamos preservar el orden
    # y la repetición de `markers`.
    params = [
        ("size", f"{ancho}x{alto}"),
        ("scale", str(DEFAULT_SCALE)),
        ("maptype", DEFAULT_MAPTYPE),
        # Marcador A (origen) — azul
        ("markers", f"color:{COLOR_ORIGEN}|label:A|{origen_lat},{origen_lng}"),
        # Marcador B (destino) — rojo
        ("markers", f"color:{COLOR_DESTINO}|label:B|{destino_lat},{destino_lng}"),
        # Recorrido (real o recto)
        ("path", path_value),
        ("zoom", str(zoom)),
        ("key", settings.GOOGLE_MAPS_API_KEY),
    ]

    # urlencode con doseq=False porque ya construimos los strings
    query = "&".join(f"{k}={v}" for k, v in params)
    return f"{BASE_URL}?{query}"