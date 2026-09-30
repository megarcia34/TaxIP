/**
 * Tipos de ubicación geográfica.
 *
 * Convención: coordenadas siempre en WGS84 (SRID 4326), que es lo que usa PostGIS
 * y lo que devuelven Google Maps y expo-location.
 */

export interface Coordenada {
  lat: number;
  lng: number;
}

export interface Ubicacion {
  lat: number;
  lng: number;
  /** Precisión en metros. Menor es mejor. `null` si no está disponible. */
  accuracy: number | null;
  /** Timestamp Unix en milisegundos. */
  timestamp: number;
}

/**
 * Estado del GPS/permisos de ubicación.
 * - `desconocido`: todavía no se consultó.
 * - `obteniendo`: se está pidiendo permiso o la primera ubicación.
 * - `activo`: permiso concedido y ubicación obteniéndose.
 * - `denegado`: el usuario rechazó el permiso.
 * - `error`: fallo técnico (GPS apagado, timeout, etc.).
 */
export type EstadoGPS =
  | 'desconocido'
  | 'obteniendo'
  | 'activo'
  | 'denegado'
  | 'error';