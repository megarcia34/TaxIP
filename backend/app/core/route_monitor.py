"""
Route monitoring with Google Maps API
Detects when driver deviates from expected route
"""

import json
import logging
from typing import Optional, Dict
from uuid import UUID
from sqlalchemy import text

from app.core.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize Google Maps client if API key is available
try:
    import googlemaps
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) if settings.GOOGLE_MAPS_API_KEY else None
except ImportError:
    gmaps = None
    logger.warning("googlemaps package not installed. Route deviation feature disabled.")


class RouteMonitor:
    """Monitor driver routes and detect deviations"""
    
    _route_cache: Dict[str, dict] = {}
    
    @classmethod
    async def get_or_create_route(
        cls,
        viaje_id: UUID,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Optional[dict]:
        """Get or calculate expected route for a trip"""
        route_key = str(viaje_id)
        
        if route_key in cls._route_cache:
            return cls._route_cache[route_key]
        
        if not gmaps:
            return None
        
        try:
            directions = gmaps.directions(
                origin=(origin_lat, origin_lng),
                destination=(dest_lat, dest_lng),
                mode="driving",
                alternatives=False
            )
            
            if directions:
                route = directions[0]
                route_data = {
                    "polyline": route["overview_polyline"]["points"],
                    "distance_meters": route["legs"][0]["distance"]["value"],
                    "duration_seconds": route["legs"][0]["duration"]["value"],
                    "steps": [
                        {
                            "lat": step["start_location"]["lat"],
                            "lng": step["start_location"]["lng"],
                            "distance": step["distance"]["value"]
                        }
                        for step in route["legs"][0]["steps"]
                    ]
                }
                cls._route_cache[route_key] = route_data
                
                # Save to database
                async with AsyncSessionLocal() as db:
                    update_query = text("""
                        UPDATE trip.viaje_solicitado
                        SET distancia_metros = :distance, tiempo_estimado_segundos = :duration
                        WHERE id = :viaje_id
                    """)
                    await db.execute(update_query, {
                        "distance": route_data["distance_meters"],
                        "duration": route_data["duration_seconds"],
                        "viaje_id": viaje_id
                    })
                    await db.commit()
                
                return route_data
        
        except Exception as e:
            logger.error(f"Error getting route from Google Maps: {e}")
        
        return None
    
    @classmethod
    async def check_deviation(
        cls,
        viaje_id: UUID,
        current_lat: float,
        current_lng: float
    ) -> Optional[float]:
        """Check if current location deviates from expected route"""
        route_key = str(viaje_id)
        
        if route_key not in cls._route_cache:
            async with AsyncSessionLocal() as db:
                query = text("""
                    SELECT ruta_esperada_json FROM audit.alerta_desvio
                    WHERE viaje_id = :viaje_id
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                result = await db.execute(query, {"viaje_id": viaje_id})
                row = result.first()
                if row and row[0]:
                    cls._route_cache[route_key] = json.loads(row[0])
                else:
                    return None
        
        route = cls._route_cache.get(route_key)
        if not route or not gmaps:
            return None
        
        try:
            # Calculate distance to nearest point on route
            min_distance = float('inf')
            for step in route.get("steps", []):
                from math import radians, sin, cos, sqrt, atan2
                
                lat1, lon1 = radians(current_lat), radians(current_lng)
                lat2, lon2 = radians(step["lat"]), radians(step["lng"])
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                distance = 6371000 * c
                
                min_distance = min(min_distance, distance)
            
            return min_distance if min_distance != float('inf') else None
        
        except Exception as e:
            logger.error(f"Error calculating deviation: {e}")
        
        return None
    
    @classmethod
    async def alert_deviation(
        cls,
        viaje_id: UUID,
        lat: float,
        lng: float,
        deviation_meters: float
    ):
        """Create alert for route deviation"""
        threshold = settings.DEVIATION_THRESHOLD_METERS
        
        if deviation_meters > threshold:
            async with AsyncSessionLocal() as db:
                check_query = text("""
                    SELECT id FROM audit.alerta_desvio
                    WHERE viaje_id = :viaje_id
                    AND created_at > NOW() - INTERVAL '5 minutes'
                    LIMIT 1
                """)
                result = await db.execute(check_query, {"viaje_id": viaje_id})
                
                if not result.first():
                    insert_query = text("""
                        INSERT INTO audit.alerta_desvio (
                            id, viaje_id, latitud, longitud, distancia_desvio_metros,
                            notificado, created_at
                        )
                        VALUES (
                            gen_random_uuid(), :viaje_id, :lat, :lng, :deviation,
                            false, NOW()
                        )
                    """)
                    await db.execute(insert_query, {
                        "viaje_id": viaje_id,
                        "lat": lat,
                        "lng": lng,
                        "deviation": deviation_meters
                    })
                    await db.commit()
                    
                    logger.warning(f"🚨 Route deviation: Trip {viaje_id} deviated {deviation_meters}m")