/**
 * Store del Módulo 3 - Conexión WebSocket.
 *
 * Solo memoria: la conexión se restablece al abrir la app. No se persiste.
 * Sin lógica de negocio: el ciclo de conexión/reconexión vive en
 * services/websocket.service.ts (Fase 9.3). Este store es solo el espejo
 * de estado para la UI.
 */
import { create } from 'zustand';
import type { EstadoWS } from '@/types/websocket.types';

interface ConexionState {
  // Estado
  estadoWS: EstadoWS;
  ultimaConexion: number | null;
  intentosReconexion: number;

  // Acciones
  setEstadoWS: (estado: EstadoWS) => void;
  setUltimaConexion: (timestamp: number) => void;
  incrementarIntentos: () => void;
  resetear: () => void;
}

export const useConexionStore = create<ConexionState>()((set) => ({
  // Estado inicial
  estadoWS: 'desconectado',
  ultimaConexion: null,
  intentosReconexion: 0,

  // ============================================
  // ESTADO WS
  // ============================================
  setEstadoWS: (estado) => {
    set({ estadoWS: estado });
  },

  // ============================================
  // ÚLTIMA CONEXIÓN
  // ============================================
  setUltimaConexion: (timestamp) => {
    set({ ultimaConexion: timestamp });
  },

  // ============================================
  // INTENTOS DE RECONEXIÓN
  // ============================================
  incrementarIntentos: () => {
    set((state) => ({ intentosReconexion: state.intentosReconexion + 1 }));
  },

  // ============================================
  // RESET
  // ============================================
  resetear: () => {
    set({
      estadoWS: 'desconectado',
      ultimaConexion: null,
      intentosReconexion: 0,
    });
  },
}));