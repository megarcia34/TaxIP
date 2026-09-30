"""
Servicio de Directions API de Google Maps
Calcula distancia, tiempo y coordenadas entre puntos
"""

import logging
import httpx
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class DirectionsService:
    """
    Servicio para interactuar con Google Maps Directions API
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        
        if not self.api_key:
            logger.warning("⚠️ GOOGLE_MAPS_API_KEY no configurada en .env")
    
    async def calcular_ruta(
        self,
        origen: str,
        destino: str,
        paradas: Optional[List[str]] = None,
        modo: str = "driving"
    ) -> Dict[str, Any]:
        """
        Calcula la ruta entre origen y destino, incluyendo paradas intermedias
        
        Args:
            origen: Dirección de origen
            destino: Dirección de destino
            paradas: Lista de direcciones intermedias (waypoints)
            modo: Tipo de transporte (driving, walking, transit)
            
        Returns:
            Dict con distancia_km, tiempo_minutos y coordenadas
        """
        if not self.api_key:
            logger.warning("⚠️ API Key no disponible, usando valores simulados")
            return self._simular_ruta(origen, destino)
        
        try:
            # Construir waypoints si hay paradas
            waypoints = ""
            if paradas and len(paradas) > 0:
                waypoints = "|".join(paradas)
                waypoints = f"&waypoints={waypoints}"
            
            url = f"{self.base_url}?origin={origen}&destination={destino}{waypoints}&mode={modo}&key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"❌ Error en Directions API: {data.get('status')} - {data.get('error_message')}")
                return self._simular_ruta(origen, destino)
            
            # Extraer información de la primera ruta
            ruta = data["routes"][0]
            leg = ruta["legs"][0]
            
            distancia_km = leg["distance"]["value"] / 1000  # metros a km
            tiempo_minutos = leg["duration"]["value"] / 60   # segundos a minutos
            
            # Coordenadas de origen y destino
            lat_origen = leg["start_location"]["lat"]
            lon_origen = leg["start_location"]["lng"]
            lat_destino = leg["end_location"]["lat"]
            lon_destino = leg["end_location"]["lng"]
            
            logger.info(f"✅ Ruta calculada: {distancia_km:.2f}km, {tiempo_minutos:.0f}min")
            
            return {
                "distancia_km": round(distancia_km, 2),
                "tiempo_minutos": int(round(tiempo_minutos, 0)),
                "lat_origen": lat_origen,
                "lon_origen": lon_origen,
                "lat_destino": lat_destino,
                "lon_destino": lon_destino,
                "ruta_completa": data
            }
            
        except httpx.TimeoutException:
            logger.error("❌ Timeout en Directions API")
            return self._simular_ruta(origen, destino)
        except Exception as e:
            logger.error(f"❌ Error en Directions API: {str(e)}")
            return self._simular_ruta(origen, destino)

    async def calcular_ruta_por_coords(
        self,
        origen_lat: float,
        origen_lng: float,
        destino_lat: float,
        destino_lng: float,
        modo: str = "driving",
    ) -> Dict[str, Any]:
        """
        Calcula la ruta entre dos coordenadas (no direcciones).

        Es un wrapper sobre calcular_ruta() que:
        1. Formatea las coordenadas como "lat,lng" (formato que acepta
           Directions API).
        2. Delega en calcular_ruta().
        3. Extrae `overview_polyline` a un campo de primer nivel del
           dict de respuesta, para que los consumidores (Static Maps)
           no tengan que escarbar en ruta_completa.

        Devuelve el mismo dict que calcular_ruta, más:
            - overview_polyline: str | None
              (encoded polyline de la ruta completa, lista para
              pasar a Static Maps como `path=enc:...`)
        """
        origen = f"{origen_lat},{origen_lng}"
        destino = f"{destino_lat},{destino_lng}"

        resultado = await self.calcular_ruta(
            origen=origen,
            destino=destino,
            paradas=None,
            modo=modo,
        )

        # Extraer overview_polyline si está disponible.
        # La estructura es: data["routes"][0]["overview_polyline"]["points"]
        overview_polyline = None
        ruta_completa = resultado.get("ruta_completa")
        if ruta_completa:
            routes = ruta_completa.get("routes") or []
            if routes:
                overview_polyline = (
                    routes[0].get("overview_polyline") or {}
                ).get("points")

        resultado["overview_polyline"] = overview_polyline

        return resultado
    
    async def obtener_coordenadas(
        self,
        direccion: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Obtiene coordenadas (lat, lng) a partir de una dirección
        
        Args:
            direccion: Dirección a geocodificar
            
        Returns:
            Tuple (latitud, longitud) o (None, None) si falla
        """
        if not self.api_key:
            logger.warning("⚠️ API Key no disponible, retornando None")
            return None, None
        
        try:
            url = f"{self.geocode_url}?address={direccion}&key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"❌ Error en Geocode API: {data.get('status')}")
                return None, None
            
            location = data["results"][0]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            
            logger.info(f"✅ Coordenadas obtenidas: ({lat}, {lng}) para '{direccion}'")
            return lat, lng
            
        except Exception as e:
            logger.error(f"❌ Error en Geocode API: {str(e)}")
            return None, None
    
    def _simular_ruta(
       self,
       origen: str,
       destino: str
    ) -> Dict[str, Any]:
        """
        Fallback cuando Directions API no esta disponible.

        NO devuelve valores simulados: devuelve None en todos los campos
        para forzar a los consumidores a usar su propio fallback (Haversine
        o datos persistidos). Antes devolvia 5 km / 15 min hardcodeados,
        lo que causaba que se cobraran distancias ficticias.

        Los 6 consumidores chequean `if ruta and ruta.get("distancia_km")`,
        por lo que con este cambio caen correctamente a Haversine.

        Ref: G59 en DEUDA_TECNICA.md.
        """
        logger.error(
           f"Directions API no disponible. "
           f"Origen: {origen}, Destino: {destino}. "
           f"Devolviendo dict vacio para forzar fallback del consumidor."
        )

        return {
            "distancia_km": None,
            "tiempo_minutos": None,
            "lat_origen": None,
            "lon_origen": None,
            "lat_destino": None,
            "lon_destino": None,
            "ruta_completa": None,
            "overview_polyline": None,
            "es_fallback": True,
        }


# ============================================================
# INSTANCIA SINGLETON
# ============================================================

directions_service = DirectionsService()