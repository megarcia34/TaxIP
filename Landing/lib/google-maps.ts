// ============================================
// GOOGLE MAPS UTILITIES
// ============================================

declare global {
  interface Window {
    google: any;
    initGoogleMaps: () => void;
  }
}

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

// ============================================
// CARGAR GOOGLE MAPS SCRIPT
// ============================================
export async function loadGoogleMapsScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    // Si ya está cargado, resolver
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
      if (window.google && window.google.maps) {
        resolve();
        return;
      }
    }

    // Si ya existe la función de callback, no la volvemos a definir
    if (typeof window.initGoogleMaps === 'function') {
      // Esperar a que se cargue
      const checkLoaded = setInterval(() => {
        if (window.google && window.google.maps) {
          clearInterval(checkLoaded);
          resolve();
        }
      }, 100);
      return;
    }

    // Definir callback global
    window.initGoogleMaps = () => {
      resolve();
    };

    // Crear script - LIBRERÍAS CORRECTAS
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&libraries=places,geometry&callback=initGoogleMaps`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      reject(new Error('Error al cargar Google Maps'));
    };
    document.head.appendChild(script);
  });
}

// ============================================
// GEOCODIFICAR DIRECCIÓN
// ============================================
export async function geocodeAddress(address: string): Promise<{
  lat: number;
  lng: number;
  formatted_address: string;
} | null> {
  if (!window.google) {
    throw new Error('Google Maps no está cargado');
  }

  const geocoder = new window.google.maps.Geocoder();
  
  return new Promise((resolve, reject) => {
    geocoder.geocode(
      { address, componentRestrictions: { country: 'ar' } },
      (results: any[], status: any) => {
        if (status === 'OK' && results && results.length > 0) {
          const { lat, lng } = results[0].geometry.location;
          resolve({
            lat: lat(),
            lng: lng(),
            formatted_address: results[0].formatted_address,
          });
        } else {
          reject(new Error(`No se pudo geocodificar: ${status}`));
        }
      }
    );
  });
}

// ============================================
// CALCULAR RUTA
// ============================================
export async function calcularRuta(
  origin: { lat: number; lng: number },
  destination: { lat: number; lng: number },
  waypoints?: { lat: number; lng: number }[]
): Promise<{
  distance: number; // metros
  duration: number; // segundos
  polyline: string;
  steps: any[];
}> {
  if (!window.google) {
    throw new Error('Google Maps no está cargado');
  }

  const directionsService = new window.google.maps.DirectionsService();

  return new Promise((resolve, reject) => {
    const request: any = {
      origin: new window.google.maps.LatLng(origin.lat, origin.lng),
      destination: new window.google.maps.LatLng(destination.lat, destination.lng),
      travelMode: window.google.maps.TravelMode.DRIVING,
    };

    if (waypoints && waypoints.length > 0) {
      request.waypoints = waypoints.map((wp) => ({
        location: new window.google.maps.LatLng(wp.lat, wp.lng),
        stopover: true,
      }));
    }

    directionsService.route(request, (result: any, status: any) => {
      if (status === 'OK' && result) {
        const route = result.routes[0];
        const leg = route.legs[0];
        resolve({
          distance: leg.distance.value,
          duration: leg.duration.value,
          polyline: route.overview_polyline,
          steps: leg.steps.map((step: any) => ({
            instruction: step.instructions,
            distance: step.distance.value,
            duration: step.duration.value,
            start_location: {
              lat: step.start_location.lat(),
              lng: step.start_location.lng(),
            },
            end_location: {
              lat: step.end_location.lat(),
              lng: step.end_location.lng(),
            },
          })),
        });
      } else {
        reject(new Error(`No se pudo calcular la ruta: ${status}`));
      }
    });
  });
}

// ============================================
// DECODIFICAR POLILÍNEA
// ============================================
export function decodePolyline(encoded: string): Array<{ lat: number; lng: number }> {
  if (!window.google) {
    throw new Error('Google Maps no está cargado');
  }
  
  const path = window.google.maps.geometry.encoding.decodePath(encoded);
  return path.map((point: any) => ({
    lat: point.lat(),
    lng: point.lng(),
  }));
}

// ============================================
// AUTOCOMPLETADO DE DIRECCIONES
// ============================================
export function createAutocomplete(
  inputElement: HTMLInputElement,
  onSelect: (result: { address: string; lat: number; lng: number }) => void
): any {
  if (!window.google) {
    throw new Error('Google Maps no está cargado');
  }

  const autocomplete = new window.google.maps.places.Autocomplete(inputElement, {
    types: ['address'],
    componentRestrictions: { country: 'ar' },
    fields: ['formatted_address', 'geometry', 'place_id', 'name'],
  });

  autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace();
    if (place.geometry && place.geometry.location) {
      onSelect({
        address: place.formatted_address || place.name || inputElement.value,
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
      });
    }
  });

  return autocomplete;
}