"use client";

import { useState, useRef, useEffect } from 'react';
import { calcularRuta } from '@/lib/google-maps';

interface MapPickerProps {
  origin?: { lat: number; lng: number; address?: string } | null;
  destination?: { lat: number; lng: number; address?: string } | null;
  waypoints?: { lat: number; lng: number }[];
  onMapClick?: (lat: number, lng: number) => void;
  height?: string;
  showRoute?: boolean;
  className?: string;
  onRouteCalculated?: (data: { distance: number; duration: number }) => void;
}

export function MapPicker({
  origin,
  destination,
  waypoints = [],
  onMapClick,
  height = '500px',
  showRoute = true,
  className = '',
  onRouteCalculated,
}: MapPickerProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const polylineRef = useRef<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [routeInfo, setRouteInfo] = useState<{ distance: string; duration: string } | null>(null);
  const [routeError, setRouteError] = useState<string | null>(null);
  const [routeDistanceKm, setRouteDistanceKm] = useState<number | null>(null);
  const [routeDurationMin, setRouteDurationMin] = useState<number | null>(null);
  const [isGoogleMapsReady, setIsGoogleMapsReady] = useState(false);

  // Verificar que Google Maps esté cargado
  useEffect(() => {
    const checkGoogleMaps = () => {
      if (window.google && window.google.maps) {
        setIsGoogleMapsReady(true);
        return true;
      }
      return false;
    };

    // Si ya está cargado
    if (checkGoogleMaps()) return;

    // Esperar a que se cargue
    const interval = setInterval(() => {
      if (checkGoogleMaps()) {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  // Cargar mapa
  useEffect(() => {
    if (!mapRef.current || !isGoogleMapsReady) return;

    const defaultCenter = { lat: -26.8083, lng: -65.2176 };

    const map = new window.google.maps.Map(mapRef.current, {
      center: defaultCenter,
      zoom: 13,
      styles: [
        {
          featureType: 'poi',
          elementType: 'labels',
          stylers: [{ visibility: 'off' }],
        },
      ],
      mapTypeControl: true,
      mapTypeControlOptions: {
        position: window.google.maps.ControlPosition.TOP_RIGHT,
      },
      zoomControl: true,
      zoomControlOptions: {
        position: window.google.maps.ControlPosition.RIGHT_CENTER,
      },
    });

    mapInstanceRef.current = map;
    setIsLoaded(true);

    if (onMapClick) {
      map.addListener('click', (e: any) => {
        onMapClick(e.latLng.lat(), e.latLng.lng());
      });
    }

    return () => {
      // Limpiar
    };
  }, [isGoogleMapsReady]);

  // ============================================
  // ACTUALIZAR MARCADORES Y RUTA
  // ============================================
  useEffect(() => {
    if (!mapInstanceRef.current || !isLoaded) return;

    const map = mapInstanceRef.current;

    // Limpiar marcadores anteriores
    markersRef.current.forEach((marker) => marker.setMap(null));
    markersRef.current = [];

    // Limpiar polilínea anterior
    if (polylineRef.current) {
      polylineRef.current.setMap(null);
      polylineRef.current = null;
    }

    const bounds = new window.google.maps.LatLngBounds();
    let hasMarkers = false;

    // ============================================
    // MARCADOR DE ORIGEN (A - AMARILLO)
    // ============================================
    if (origin) {
      const marker = new window.google.maps.Marker({
        position: { lat: origin.lat, lng: origin.lng },
        map,
        label: {
          text: 'A',
          color: '#FFFFFF',
          fontWeight: 'bold',
          fontSize: '12px',
        },
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: '#FBBF24',
          fillOpacity: 1,
          strokeColor: '#FFFFFF',
          strokeWeight: 2,
          scale: 14,
        },
        title: origin.address || 'Origen',
        animation: window.google.maps.Animation.DROP,
      });
      markersRef.current.push(marker);
      bounds.extend({ lat: origin.lat, lng: origin.lng });
      hasMarkers = true;
    }

    // ============================================
    // MARCADOR DE DESTINO (B - ROJO)
    // ============================================
    if (destination) {
      const marker = new window.google.maps.Marker({
        position: { lat: destination.lat, lng: destination.lng },
        map,
        label: {
          text: 'B',
          color: '#FFFFFF',
          fontWeight: 'bold',
          fontSize: '12px',
        },
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: '#EF4444',
          fillOpacity: 1,
          strokeColor: '#FFFFFF',
          strokeWeight: 2,
          scale: 14,
        },
        title: destination.address || 'Destino',
        animation: window.google.maps.Animation.DROP,
      });
      markersRef.current.push(marker);
      bounds.extend({ lat: destination.lat, lng: destination.lng });
      hasMarkers = true;
    }

    // ============================================
    // CENTRAR MAPA EN EL RECORRIDO
    // ============================================
    if (hasMarkers) {
      if (origin && destination) {
        map.fitBounds(bounds);
        const zoom = map.getZoom();
        if (zoom > 15) map.setZoom(15);
        else if (zoom < 10) map.setZoom(12);
      } else if (origin) {
        map.setCenter({ lat: origin.lat, lng: origin.lng });
        map.setZoom(15);
      } else if (destination) {
        map.setCenter({ lat: destination.lat, lng: destination.lng });
        map.setZoom(15);
      }
    }

    // ============================================
    // CALCULAR Y MOSTRAR RUTA
    // ============================================
    // Solo calcular si hay origen y destino, y showRoute es true
    if (origin && destination && showRoute && isGoogleMapsReady) {
      const isSamePoint = Math.abs(origin.lat - destination.lat) < 0.00001 && 
                          Math.abs(origin.lng - destination.lng) < 0.00001;
      if (!isSamePoint) {
        calcularRutaYMostrar();
      } else {
        setRouteError('Origen y destino son el mismo punto');
        setRouteInfo(null);
        setRouteDistanceKm(null);
        setRouteDurationMin(null);
        if (onRouteCalculated) {
          onRouteCalculated({ distance: 0, duration: 0 });
        }
      }
    } else {
      setRouteInfo(null);
      setRouteError(null);
      setRouteDistanceKm(null);
      setRouteDurationMin(null);
    }
  }, [origin, destination, isLoaded, isGoogleMapsReady]);

  // ============================================
  // CALCULAR RUTA
  // ============================================
  const calcularRutaYMostrar = async () => {
    if (!origin || !destination || !mapInstanceRef.current || !isGoogleMapsReady) return;

    // Verificar que los puntos sean diferentes
    if (Math.abs(origin.lat - destination.lat) < 0.00001 && 
        Math.abs(origin.lng - destination.lng) < 0.00001) {
      setRouteError('Origen y destino son el mismo punto');
      setRouteInfo(null);
      setRouteDistanceKm(null);
      setRouteDurationMin(null);
      return;
    }

    try {
      setIsCalculating(true);
      setRouteError(null);
      setRouteInfo(null);

      const result = await calcularRuta(
        { lat: origin.lat, lng: origin.lng },
        { lat: destination.lat, lng: destination.lng },
        waypoints
      );

      // Dibujar polilínea de la ruta
      const routePath = window.google.maps.geometry.encoding.decodePath(result.polyline);
      if (polylineRef.current) {
        polylineRef.current.setMap(null);
      }
      polylineRef.current = new window.google.maps.Polyline({
        path: routePath,
        geodesic: true,
        strokeColor: '#3B82F6',
        strokeOpacity: 0.9,
        strokeWeight: 5,
        icons: [{
          icon: {
            path: window.google.maps.SymbolPath.FORWARD_OPEN_ARROW,
            scale: 3,
            strokeColor: '#3B82F6',
            strokeWeight: 2,
          },
          offset: '100%',
        }],
      });
      polylineRef.current.setMap(mapInstanceRef.current);

      // Datos de la ruta
      const distanceKm = result.distance / 1000;
      const durationMin = Math.round(result.duration / 60);

      // Guardar datos de ruta real
      setRouteDistanceKm(distanceKm);
      setRouteDurationMin(durationMin);

      // Información de ruta para mostrar
      setRouteInfo({
        distance: distanceKm.toFixed(1) + ' km',
        duration: durationMin + ' min',
      });

      // Notificar al padre
      if (onRouteCalculated) {
        onRouteCalculated({
          distance: distanceKm,
          duration: durationMin,
        });
      }

    } catch (error: any) {
      console.error('Error calculando ruta:', error);
      
      // Manejar errores específicos
      if (error.message?.includes('ZERO_RESULTS')) {
        setRouteError('No se encontró una ruta. Verifica que las direcciones sean accesibles.');
      } else if (error.message?.includes('NOT_FOUND')) {
        setRouteError('Una de las direcciones no fue encontrada. Verifica que estén bien escritas.');
      } else {
        setRouteError('No se pudo calcular la ruta. Intenta con direcciones más precisas.');
      }
      
      if (polylineRef.current) {
        polylineRef.current.setMap(null);
        polylineRef.current = null;
      }
      setRouteDistanceKm(null);
      setRouteDurationMin(null);
      
      // Notificar error al padre
      if (onRouteCalculated) {
        onRouteCalculated({ distance: 0, duration: 0 });
      }
    } finally {
      setIsCalculating(false);
    }
  };

  // ============================================
  // RENDER
  // ============================================
  return (
    <div className={className} style={{ position: 'relative', width: '100%', height }}>
      <div
        ref={mapRef}
        style={{
          width: '100%',
          height: '100%',
          borderRadius: '1rem',
          overflow: 'hidden',
          backgroundColor: '#E5E7EB',
        }}
      />

      {/* Loading overlay */}
      {!isLoaded && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255,255,255,0.8)',
            borderRadius: '1rem',
            zIndex: 10,
          }}
        >
          <span>Cargando mapa...</span>
        </div>
      )}

      {/* Información de ruta */}
      {routeInfo && (
        <div
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(255,255,255,0.95)',
            padding: '0.5rem 1.5rem',
            borderRadius: '9999px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'flex',
            gap: '1.5rem',
            zIndex: 5,
            fontSize: '0.875rem',
            fontWeight: 500,
          }}
        >
          <span>📍 <strong>{routeInfo.distance}</strong></span>
          <span>⏱️ <strong>{routeInfo.duration}</strong></span>
        </div>
      )}

      {/* Error de ruta */}
      {routeError && (
        <div
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(254,242,242,0.95)',
            padding: '0.5rem 1.5rem',
            borderRadius: '0.75rem',
            border: '1px solid #EF4444',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 5,
            fontSize: '0.75rem',
            color: '#991B1B',
            maxWidth: '90%',
            textAlign: 'center',
          }}
        >
          ⚠️ {routeError}
        </div>
      )}

      {/* Calculando overlay */}
      {isCalculating && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'rgba(255,255,255,0.9)',
            padding: '1rem 2rem',
            borderRadius: '0.75rem',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 5,
            fontSize: '0.875rem',
          }}
        >
          ⏳ Calculando ruta...
        </div>
      )}
    </div>
  );
}