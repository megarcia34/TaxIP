
/**
 * Store del Splash Screen.
 */
import { create } from 'zustand';
import type { SplashEstado, EtapaActual } from '@/types/splash.types';
import { splashService } from '@/services/splash.service';

interface SplashState {
  estado: SplashEstado | null;
  etapaActual: EtapaActual | null;
  isLoading: boolean;
  error: string | null;

  cargarEstado: () => Promise<SplashEstado | null>;
  reset: () => void;
}

export const useSplashStore = create<SplashState>((set) => ({
  estado: null,
  etapaActual: null,
  isLoading: false,
  error: null,

  cargarEstado: async () => {
    set({ isLoading: true, error: null });
    try {
      const estado = await splashService.obtenerEstado();
      set({
        estado,
        etapaActual: estado.etapa_actual,
        isLoading: false,
      });
      return estado;
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al cargar el estado';
      set({ error: mensaje, isLoading: false });
      throw error;
    }
  },

  reset: () =>
    set({
      estado: null,
      etapaActual: null,
      isLoading: false,
      error: null,
    }),
}));
