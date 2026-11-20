'use client'

import { useEffect, useRef, useState } from 'react'
import api from '@/lib/api/client'

interface MapaRutaViajeProps {
  viajeId: string;
}

let isGoogleMapsLoaded = false;
let googleMapsPromise: Promise<void> | null = null;

const loadGoogleMaps = (apiKey: string): Promise<void> => {
  if (isGoogleMapsLoaded) return Promise.resolve();
  if (googleMapsPromise) return googleMapsPromise;

  googleMapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      isGoogleMapsLoaded = true;
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });

  return googleMapsPromise;
}

export function MapaRutaViaje({ viajeId }: MapaRutaViajeProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  
  const [viajeData, setViajeData] = useState<any>(null);
  const [puntosGps, setPuntosGps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Cargar datos
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        const { data: viaje } = await api.get(`/viajes/${viajeId}/estado`);
        const { data: gpsData } = await api.get(`/viajes/${viajeId}/gps`).catch(() => ({ data: { puntos: [] } }));
        
        if (!isMounted) return;
        setViajeData(viaje);
        setPuntosGps(gpsData.puntos || []);
        setLoading(false);
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || err.message || 'Error cargando datos');
          setLoading(false);
        }
      }
    };
    fetchData();
    return () => { isMounted = false; };
  }, [viajeId]);

  // 2. Inicializar Mapa y dibujar rutas
  useEffect(() => {
    if (!viajeData || loading || !mapRef.current) return;
    let isMounted = true;

    const initMap = async () => {
      try {
        const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
        if (!apiKey) throw new Error('Falta la API Key');
        await loadGoogleMaps(apiKey);
        if (!isMounted || !mapRef.current) return;

        const map = new google.maps.Map(mapRef.current, {
          center: { 
            lat: viajeData.origen_lat || -26.8304, 
            lng: viajeData.origen_lng || -65.2038 
          },
          zoom: 14,
          mapTypeControl: false,
          fullscreenControl: true,
          streetViewControl: false,
        });
        mapInstanceRef.current = map;

        // --- Marcadores ---
        if (viajeData.origen_lat && viajeData.origen_lng) {
          new google.maps.Marker({
            position: { lat: viajeData.origen_lat, lng: viajeData.origen_lng },
            map,
            title: 'Origen',
            icon: { path: google.maps.SymbolPath.CIRCLE, fillColor: '#22c55e', fillOpacity: 1, strokeWeight: 2, strokeColor: '#ffffff', scale: 10 }
          });
        }

        if (viajeData.destino_lat && viajeData.destino_lng) {
          new google.maps.Marker({
            position: { lat: viajeData.destino_lat, lng: viajeData.destino_lng },
            map,
            title: 'Destino',
            icon: { path: google.maps.SymbolPath.CIRCLE, fillColor: '#ef4444', fillOpacity: 1, strokeWeight: 2, strokeColor: '#ffffff', scale: 10 }
          });
        }

        // --- Ruta Tentativa (DirectionsService) ---
        if (viajeData.origen_lat && viajeData.destino_lat) {
          const directionsService = new google.maps.DirectionsService();
          const directionsRenderer = new google.maps.DirectionsRenderer({
            map: map,
            suppressMarkers: true, // Para usar nuestros propios pines
            polylineOptions: {
              strokeColor: '#3b82f6', // Azul
              strokeWeight: 4,
              strokeOpacity: 0.8,
            }
          });

          directionsService.route({
            origin: { lat: viajeData.origen_lat, lng: viajeData.origen_lng },
            destination: { lat: viajeData.destino_lat, lng: viajeData.destino_lng },
            travelMode: google.maps.TravelMode.DRIVING,
          }, (result, status) => {
            if (status === google.maps.DirectionsStatus.OK && result) {
              directionsRenderer.setDirections(result);
            } else {
              console.warn('No se pudo calcular la ruta tentativa:', status);
            }
          });
        }

        // --- Ruta GPS Real (Violeta) ---
        if (puntosGps.length > 0) {
          const gpsPath = puntosGps.map((p: any) => ({ lat: p.lat, lng: p.lng }));
          new google.maps.Polyline({
            path: gpsPath,
            geodesic: true,
            strokeColor: '#8b5cf6',
            strokeOpacity: 1.0,
            strokeWeight: 4,
            map: map,
          });
        }

        // --- Ajustar Zoom ---
        const bounds = new google.maps.LatLngBounds();
        if (viajeData.origen_lat && viajeData.origen_lng) bounds.extend({ lat: viajeData.origen_lat, lng: viajeData.origen_lng });
        if (viajeData.destino_lat && viajeData.destino_lng) bounds.extend({ lat: viajeData.destino_lat, lng: viajeData.destino_lng });
        puntosGps.forEach((p: any) => bounds.extend({ lat: p.lat, lng: p.lng }));
        
        // Si la ruta GPS está vacía, el bounds solo tiene Origen y Destino (perfecto para la ruta tentativa)
        if (bounds.getNorthEast().equals(bounds.getSouthWest())) {
           map.setCenter(bounds.getCenter());
           map.setZoom(16);
        } else {
           map.fitBounds(bounds);
        }

      } catch (err: any) {
        console.error('❌ Error en initMap:', err);
        if (isMounted) setError('Error al inicializar el mapa de Google');
      }
    };

    initMap();
    return () => { isMounted = false; };
  }, [viajeData, loading, puntosGps]);

  if (error) return <div className="h-full w-full flex items-center justify-center p-6 text-center text-red-500 bg-muted/20">{error}</div>;
  if (loading) return <div className="h-full w-full flex items-center justify-center bg-muted/20"><p className="text-muted-foreground animate-pulse">Cargando datos del viaje...</p></div>;

  return <div ref={mapRef} className="w-full h-full min-h-[400px]" />;
}