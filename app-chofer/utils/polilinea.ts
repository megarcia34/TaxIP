/**
 * Utilidades de polilínea para mapas (Google Directions).
 *
 * STUB de Fase 9.2: `decodificarPolilinea` está implementado (algoritmo
 * estándar de Google) pero no se usa todavía. Va a hacer falta en Etapa 11
 * para dibujar la ruta en el mapa.
 *
 * Ref: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
 */
import type { Coordenada } from '@/types/ubicacion.types';

/**
 * Decodifica una polilínea codificada de Google a un array de coordenadas.
 */
export function decodificarPolilinea(encoded: string): Coordenada[] {
  if (!encoded) return [];

  const puntos: Coordenada[] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let b: number;
    let shift = 0;
    let result = 0;

    // Decodificar latitud
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);

    const dlat = result & 1 ? ~(result >> 1) : result >> 1;
    lat += dlat;

    // Decodificar longitud
    shift = 0;
    result = 0;
    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);

    const dlng = result & 1 ? ~(result >> 1) : result >> 1;
    lng += dlng;

    puntos.push({
      lat: lat / 1e5,
      lng: lng / 1e5,
    });
  }

  return puntos;
}

/**
 * Calcula el bounding box de un conjunto de coordenadas.
 * Devuelve null si el array está vacío.
 */
export function calcularBoundingBox(
  coords: Coordenada[]
): {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
} | null {
  if (coords.length === 0) return null;

  let minLat = coords[0].lat;
  let maxLat = coords[0].lat;
  let minLng = coords[0].lng;
  let maxLng = coords[0].lng;

  for (const c of coords) {
    if (c.lat < minLat) minLat = c.lat;
    if (c.lat > maxLat) maxLat = c.lat;
    if (c.lng < minLng) minLng = c.lng;
    if (c.lng > maxLng) maxLng = c.lng;
  }

  return { minLat, maxLat, minLng, maxLng };
}