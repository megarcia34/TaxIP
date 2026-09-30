/**
 * Servicio del Splash Screen.
 */
import api from './api';
import type { SplashEstado } from '@/types/splash.types';

export const splashService = {
  /**
   * Obtiene el estado consolidado del chofer.
   */
  async obtenerEstado(): Promise<SplashEstado> {
    const response = await api.get<SplashEstado>('/api/chofer/splash-estado');
    return response.data;
  },

  /**
   * Obtiene el estado del expediente (usado en el polling del Paso 6).
   * GET /api/chofer/splash-estado
   */
  async obtenerEstadoExpediente(): Promise<SplashEstado> {
    const response = await api.get<SplashEstado>('/api/chofer/splash-estado');
    return response.data;
  },
};