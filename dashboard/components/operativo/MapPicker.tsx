// components/operativo/MapPicker.tsx

'use client';

import { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { GoogleMap, Marker, DirectionsRenderer } from '@react-google-maps/api';
import { Loader2, Navigation, AlertCircle } from 'lucide-react';

// Centro por defecto: San Miguel de Tucumán
const DEFAULT_CENTER = {
  lat: -26.8083,
  lng: -65.2176,
};

const mapContainerStyle = {
  width: '100%',
  height: '100%',
  minHeight: '400px',
};

const mapOptions: google.maps.MapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: false,
  mapTypeControl: false,
  fullscreenControl: true,
};

interface MapPickerProps {
  origin?: { lat: number; lng: number; address?: string } | null;
  destination?: { lat: number; lng: number; address?: string } | null;
  waypoints?: Array<{ lat: number; lng: number; address?: string }>;
  onOriginDragEnd?: (lat: number, lng: number) => void;
  onDestinationDragEnd?: (lat: number, lng: number) => void;
  onWaypointDragEnd?: (index: number, lat: number, lng: number) => void;
  onRouteChange?: (distanceKm: number, durationMin: number) => void;
  height?: string;
  zoom?: number;
  center?: { lat: number; lng: number };
  disabled?: boolean;
  draggable?: boolean;
}

export function MapPicker({
  origin,
  destination,
  waypoints = [],
  onOriginDragEnd,
  onDestinationDragEnd,
  onWaypointDragEnd,
  onRouteChange,
  height = '400px',
  zoom = 14,
  center,
  disabled = false,
  draggable = true,
}: MapPickerProps) {
  const [directions, setDirections] = useState<google.maps.DirectionsResult | null>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);
  const directionsServiceRef = useRef<google.maps.DirectionsService | null>(null);
  const mapRef = useRef<google.maps.Map | null>(null);

  // Calcular el centro del mapa
  const mapCenter = useMemo(() => {
    if (center) return center;
    if (origin && destination) {
      return {
        lat: (origin.lat + destination.lat) / 2,
        lng: (origin.lng + destination.lng) / 2,
      };
    }
    if (origin) return { lat: origin.lat, lng: origin.lng };
    if (destination) return { lat: destination.lat, lng: destination.lng };
    return DEFAULT_CENTER;
  }, [center, origin, destination]);

  // Calcular el zoom automático
  const mapZoom = useMemo(() => {
    if (origin && destination) {
      const latDiff = Math.abs(origin.lat - destination.lat);
      const lngDiff = Math.abs(origin.lng - destination.lng);
      const maxDiff = Math.max(latDiff, lngDiff);

      if (maxDiff > 0.5) return 11;
      if (maxDiff > 0.2) return 12;
      if (maxDiff > 0.1) return 13;
      if (maxDiff > 0.05) return 14;
      return 15;
    }
    return zoom;
  }, [origin, destination, zoom]);

  // Inicializar DirectionsService
  useEffect(() => {
    if (typeof window !== 'undefined' && window.google?.maps) {
      directionsServiceRef.current = new window.google.maps.DirectionsService();
    }
  }, []);

  // ✅ Calcular ruta cuando cambian origen, destino o waypoints
  useEffect(() => {
    // Resetear estados
    setRouteError(null);

    // Si no hay origen o destino, limpiar ruta
    if (!origin || !destination) {
      setDirections(null);
      return;
    }

    // Validar que las coordenadas sean válidas
    if (!origin.lat || !origin.lng || !destination.lat || !destination.lng) {
      setRouteError('Coordenadas inválidas');
      setDirections(null);
      return;
    }

    // Si no hay DirectionsService, esperar
    if (!directionsServiceRef.current) return;

    const fetchRoute = async () => {
      setIsLoadingRoute(true);
      setRouteError(null);

      // Filtrar waypoints válidos
      const validWaypoints = waypoints.filter(
        (wp) => wp && wp.lat && wp.lng && wp.lat !== 0 && wp.lng !== 0
      );

      const waypointList = validWaypoints.map((wp) => ({
        location: new window.google.maps.LatLng(wp.lat, wp.lng),
        stopover: true,
      }));

      const request: google.maps.DirectionsRequest = {
        origin: new window.google.maps.LatLng(origin.lat, origin.lng),
        destination: new window.google.maps.LatLng(destination.lat, destination.lng),
        waypoints: waypointList,
        travelMode: google.maps.TravelMode.DRIVING,
        optimizeWaypoints: false,
        avoidTolls: false,
        avoidHighways: false,
      };

            try {
        if (!directionsServiceRef.current) {
          console.error("⚠️ El servicio de direcciones no está inicializado");
          return;
        }
        const result = await directionsServiceRef.current.route(request);

        if (result.routes && result.routes.length > 0) {
          setDirections(result);
          setRouteError(null);

          // Calcular distancia y tiempo total
          const route = result.routes[0];
          let totalDistance = 0;
          let totalDuration = 0;

          if (route.legs) {
            for (const leg of route.legs) {
              if (leg.distance?.value) totalDistance += leg.distance.value;
              if (leg.duration?.value) totalDuration += leg.duration.value;
            }
          }

          if (onRouteChange) {
            onRouteChange(totalDistance / 1000, Math.ceil(totalDuration / 60));
          }

          // ✅ Ajustar el mapa para mostrar toda la ruta
          if (mapRef.current && result.routes[0]?.bounds) {
            mapRef.current.fitBounds(result.routes[0].bounds);
          }
        } else {
          setRouteError('No se encontró una ruta válida');
          setDirections(null);
        }
      } catch (error: any) {
        console.warn('⚠️ Error calculando ruta:', error);
        setRouteError(error?.message || 'Error al calcular la ruta');
        setDirections(null);
      } finally {
        setIsLoadingRoute(false);
      }
    };

    fetchRoute();
  }, [origin, destination, waypoints, onRouteChange]);

  // Manejar fin de arrastre de marcador
  const handleMarkerDragEnd = useCallback(
    (tipo: 'origin' | 'destination' | 'waypoint', index: number = 0) =>
      (e: google.maps.MapMouseEvent) => {
        if (disabled || !draggable || !e.latLng) return;
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();

        if (tipo === 'origin' && onOriginDragEnd) {
          onOriginDragEnd(lat, lng);
        } else if (tipo === 'destination' && onDestinationDragEnd) {
          onDestinationDragEnd(lat, lng);
        } else if (tipo === 'waypoint' && onWaypointDragEnd) {
          onWaypointDragEnd(index, lat, lng);
        }
      },
    [disabled, draggable, onOriginDragEnd, onDestinationDragEnd, onWaypointDragEnd]
  );

  // Indicador de carga de Google Maps
  if (typeof window === 'undefined') {
    return (
      <div className="flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-lg" style={{ height }}>
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="relative rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700" style={{ height }}>
      <GoogleMap
        mapContainerStyle={{ ...mapContainerStyle, height }}
        center={mapCenter}
        zoom={mapZoom}
        options={{
          ...mapOptions,
          draggable: !disabled,
          zoomControl: !disabled,
          scrollwheel: !disabled,
        }}
        onLoad={(map) => {
          mapRef.current = map;
        }}
      >
        {/* Marcador de Origen */}
        {origin && origin.lat && origin.lng && (
          <Marker
            position={{ lat: origin.lat, lng: origin.lng }}
            draggable={draggable && !disabled}
            onDragEnd={handleMarkerDragEnd('origin')}
            icon={{
              url: 'data:image/svg+xml,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3" fill="#22c55e" stroke="white" stroke-width="2"/>
                </svg>
              `),
              scaledSize: new window.google.maps.Size(32, 32),
              anchor: new window.google.maps.Point(16, 32),
            }}
            label={{
              text: 'A',
              color: 'white',
              fontSize: '12px',
              fontWeight: 'bold',
            }}
          />
        )}

        {/* Marcador de Destino */}
        {destination && destination.lat && destination.lng && (
          <Marker
            position={{ lat: destination.lat, lng: destination.lng }}
            draggable={draggable && !disabled}
            onDragEnd={handleMarkerDragEnd('destination')}
            icon={{
              url: 'data:image/svg+xml,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3" fill="#ef4444" stroke="white" stroke-width="2"/>
                </svg>
              `),
              scaledSize: new window.google.maps.Size(32, 32),
              anchor: new window.google.maps.Point(16, 32),
            }}
            label={{
              text: 'B',
              color: 'white',
              fontSize: '12px',
              fontWeight: 'bold',
            }}
          />
        )}

        {/* Marcadores de Paradas */}
        {waypoints.map((wp, index) => {
          if (!wp || !wp.lat || !wp.lng || wp.lat === 0 || wp.lng === 0) return null;
          return (
            <Marker
              key={`waypoint-${index}`}
              position={{ lat: wp.lat, lng: wp.lng }}
              draggable={draggable && !disabled}
              onDragEnd={handleMarkerDragEnd('waypoint', index)}
              icon={{
                url: 'data:image/svg+xml,' + encodeURIComponent(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                    <circle cx="12" cy="10" r="3" fill="#f59e0b" stroke="white" stroke-width="2"/>
                  </svg>
                `),
                scaledSize: new window.google.maps.Size(28, 28),
                anchor: new window.google.maps.Point(14, 28),
              }}
              label={{
                text: String(index + 1),
                color: 'white',
                fontSize: '12px',
                fontWeight: 'bold',
              }}
            />
          );
        })}

        {/* ✅ RUTA - Línea azul con puntos */}
        {directions && (
          <DirectionsRenderer
            directions={directions}
            options={{
              polylineOptions: {
                strokeColor: '#3b82f6', // Azul
                strokeWeight: 5,
                strokeOpacity: 0.9,
              },
              suppressMarkers: true, // Ocultar marcadores de DirectionsRenderer
              preserveViewport: false,
            }}
          />
        )}
      </GoogleMap>

      {/* ✅ Indicador de carga de ruta */}
      {isLoadingRoute && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-md flex items-center gap-2 z-10">
          <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
          <span className="text-sm">Calculando ruta...</span>
        </div>
      )}

      {/* ✅ Mensaje de error de ruta */}
      {routeError && !isLoadingRoute && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-red-50 dark:bg-red-950/80 border border-red-200 dark:border-red-800 px-4 py-2 rounded-lg shadow-md flex items-center gap-2 z-10">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-600 dark:text-red-400">{routeError}</span>
        </div>
      )}

      {/* Leyenda */}
      <div className="absolute bottom-4 right-4 bg-white dark:bg-gray-800 p-2 rounded-lg shadow-md text-xs z-10">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span>Origen</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Destino</span>
          </div>
          {waypoints.filter((wp) => wp.lat && wp.lng).length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span>{waypoints.filter((wp) => wp.lat && wp.lng).length} parada(s)</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">
            <div className="w-6 h-1 bg-blue-500 rounded" />
            <span>Ruta</span>
          </div>
        </div>
      </div>

      {/* Botón de centrar */}
      <button
        onClick={() => {
          if (mapRef.current && origin) {
            mapRef.current.panTo({ lat: origin.lat, lng: origin.lng });
            mapRef.current.setZoom(15);
          }
        }}
        className="absolute top-4 right-4 bg-white dark:bg-gray-800 p-2 rounded-lg shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors z-10"
        disabled={disabled}
      >
        <Navigation className="h-4 w-4" />
      </button>
    </div>
  );
}

export default MapPicker;