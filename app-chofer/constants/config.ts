/**
 * Configuración general de la app.
 */

export const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const APP_VERSION = process.env.EXPO_PUBLIC_APP_VERSION || 'v1.0.0';

export const CLOUDINARY_CLOUD_NAME = process.env.EXPO_PUBLIC_CLOUDINARY_CLOUD_NAME || '';
export const CLOUDINARY_UPLOAD_PRESET = process.env.EXPO_PUBLIC_CLOUDINARY_UPLOAD_PRESET || '';

export const GOOGLE_MAPS_API_KEY = process.env.EXPO_PUBLIC_GOOGLE_MAPS_API_KEY || '';

export const API_TIMEOUT = 30000;

export const STORAGE_KEYS = {
  // Legacy — los escribía el authService viejo. Se limpian en logout.
  AUTH_TOKEN: '@taxip:auth_token',
  REFRESH_TOKEN: '@taxip:refresh_token',
  USER: '@taxip:user',
  // Persist del useAuthStore (fuente de verdad de la sesión).
  AUTH_STORE: '@taxip:auth_store',
} as const;

export const WS_URL = process.env.EXPO_PUBLIC_WS_URL || 'ws://localhost:8000';