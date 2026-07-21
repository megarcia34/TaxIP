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
        Simula una ruta cuando la API no está disponible (fallback)
        """
        # Distancia aproximada en km (simulación)
        distancia_km = 5.0
        
        # Tiempo aproximado en minutos
        tiempo_minutos = 15
        
        logger.info(f"🔄 Simulando ruta: {distancia_km}km, {tiempo_minutos}min")
        
        return {
            "distancia_km": distancia_km,
            "tiempo_minutos": tiempo_minutos,
            "lat_origen": None,
            "lon_origen": None,
            "lat_destino": None,
            "lon_destino": None,
            "ruta_completa": None
        }


# ============================================================
# INSTANCIA SINGLETON
# ============================================================

directions_service = DirectionsService()