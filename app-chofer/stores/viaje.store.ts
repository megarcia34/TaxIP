/**
 * Store del Módulo 3 - Viajes.
 *
 * Solo memoria: el viaje activo, los disponibles del broadcast y el
 * historial se recargan al abrir la app. No se persiste a AsyncStorage.
 *
 * Sin lógica de negocio: solo setters. La lógica vive en los services y
 * en los hooks (useWebSocket, useViajeActivo).
 */
import { create } from 'zustand';
import type { ViajeActivo, ViajeSolicitado } from '@/types/viaje.types';

interface ViajeState {
  // Estado
  viajeActivo: ViajeActivo | null;
  viajesDisponibles: ViajeSolicitado[];
  historial: ViajeSolicitado[];

  // Acciones
  setViajeActivo: (viaje: ViajeActivo | null) => void;
  agregarViajeDisponible: (viaje: ViajeSolicitado) => void;
  quitarViajeDisponible: (viajeId: string) => void;
  setHistorial: (viajes: ViajeSolicitado[]) => void;
  reset: () => void;
}

export const useViajeStore = create<ViajeState>()((set) => ({
  // Estado inicial
  viajeActivo: null,
  viajesDisponibles: [],
  historial: [],

  // ============================================
  // VIAJE ACTIVO
  // ============================================
  setViajeActivo: (viaje) => {
    set({ viajeActivo: viaje });
  },

  // ============================================
  // VIAJES DISPONIBLES (BROADCAST)
  // ============================================
  agregarViajeDisponible: (viaje) => {
    set((state) => {
      // Dedup por id: el WS puede reemitir NUEVO_VIAJE del mismo viaje.
      if (state.viajesDisponibles.some((v) => v.id === viaje.id)) {
        return state;
      }
      return { viajesDisponibles: [...state.viajesDisponibles, viaje] };
    });
  },

  quitarViajeDisponible: (viajeId) => {
    set((state) => ({
      viajesDisponibles: state.viajesDisponibles.filter(
        (v) => v.id !== viajeId
      ),
    }));
  },

  // ============================================
  // HISTORIAL
  // ============================================
  setHistorial: (viajes) => {
    set({ historial: viajes });
  },

  // ============================================
  // RESET
  // ============================================
  reset: () => {
    set({
      viajeActivo: null,
      viajesDisponibles: [],
      historial: [],
    });
  },
}));