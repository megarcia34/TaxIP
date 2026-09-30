/**
 * Store del Módulo 2 - Turno.
 * Persiste el estado en AsyncStorage para recuperarse si la app se cierra.
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { turnoService } from '@/services/turno.service';
import type {
  EstadoChofer,
  TurnoActivo,
  EstadoLaboral,
  Combustible,
  ValidarCodigoResponse,
  CheckInResponse,
  CheckOutResponse,
  TurnoHistorial,
} from '@/types/turno.types';

interface TurnoState {
  // Estado
  estadoChofer: EstadoChofer | null;
  turnoActivo: TurnoActivo | null;
  estadoLaboral: EstadoLaboral;
  historial: TurnoHistorial[];
  isLoading: boolean;
  error: string | null;

  // Acciones
  cargarEstado: () => Promise<EstadoChofer | null>;
  cargarTurnoActivo: () => Promise<void>;
  cargarHistorial: (limit?: number, offset?: number) => Promise<void>;
  validarCodigo: (codigo: string) => Promise<ValidarCodigoResponse>;
  checkIn: (
    authToken: string,
    kmInicial: number,
    combustibleInicial: Combustible
  ) => Promise<CheckInResponse>;
  checkOut: (
    kmFinal: number,
    combustibleFinal: Combustible,
    recaudacionTicketera: number
  ) => Promise<CheckOutResponse>;
  setEstadoLaboral: (estado: EstadoLaboral) => void;
  setTurnoActivo: (turno: TurnoActivo | null) => void;
  reset: () => void;
}

export const useTurnoStore = create<TurnoState>()(
  persist(
    (set, get) => ({
      // Estado inicial
      estadoChofer: null,
      turnoActivo: null,
      estadoLaboral: 'fuera_servicio',
      historial: [],
      isLoading: false,
      error: null,

      // ============================================
      // CARGAR ESTADO DEL CHOFER
      // ============================================
      cargarEstado: async () => {
        set({ isLoading: true, error: null });
        try {
          const estado = await turnoService.obtenerEstado();
          set({
            estadoChofer: estado,
            estadoLaboral: estado.estadoLaboral,
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

      // ============================================
      // CARGAR TURNO ACTIVO
      // ============================================
      cargarTurnoActivo: async () => {
        try {
          const data = await turnoService.obtenerTurnoActivo();

          if (data.tieneTurnoActivo && data.turnoId) {
            set({
              turnoActivo: {
                id: data.turnoId,
                estado: 'ACTIVO',
                inicioTurno: data.inicioTurno || new Date().toISOString(),
                vehiculoId: data.vehiculoId || '',
                patente: data.patente || '',
                marca: data.marca,
                modelo: data.modelo,
                anio: data.anio,
                estadoLaboral: (data.estadoLaboral as EstadoLaboral) || 'libre',
                kmInicial: data.kmInicial || 0,
                combustibleInicial:
                  (data.combustibleInicial as Combustible) || 'LLENO',
                duracionMinutos: data.duracionMinutos || 0,
                duracionFormateada: data.duracionFormateada || '00:00:00',
              },
              estadoLaboral: (data.estadoLaboral as EstadoLaboral) || 'libre',
            });
          } else {
            set({ turnoActivo: null, estadoLaboral: 'fuera_servicio' });
          }
        } catch (error: any) {
          // Si no hay turno activo, no es un error crítico
          console.warn('Error al cargar turno activo:', error?.message);
        }
      },

      // ============================================
      // CARGAR HISTORIAL
      // ============================================
      cargarHistorial: async (limit = 20, offset = 0) => {
        set({ isLoading: true, error: null });
        try {
          const historial = await turnoService.obtenerHistorial(limit, offset);
          set({ historial, isLoading: false });
        } catch (error: any) {
          const mensaje =
            error?.response?.data?.detail ||
            error?.message ||
            'Error al cargar el historial';
          set({ error: mensaje, isLoading: false });
          throw error;
        }
      },

      // ============================================
      // VALIDAR CÓDIGO
      // ============================================
      validarCodigo: async (codigo: string) => {
        try {
          const response = await turnoService.validarCodigo(codigo);
          return response;
        } catch (error: any) {
          const mensaje =
            error?.response?.data?.detail ||
            error?.message ||
            'Código inválido';
          throw new Error(mensaje);
        }
      },

      // ============================================
      // CHECK-IN
      // ============================================
      checkIn: async (
        authToken: string,
        kmInicial: number,
        combustibleInicial: Combustible
      ) => {
        try {
          const response = await turnoService.checkIn(
            authToken,
            kmInicial,
            combustibleInicial
          );

          // Actualizar el store con el turno activo
          set({
            turnoActivo: {
              id: response.turnoId,
              estado: 'ACTIVO',
              inicioTurno: response.inicioTurno,
              vehiculoId: response.vehiculoId,
              patente: response.patente,
              marca: response.marca,
              modelo: response.modelo,
              anio: response.anio,
              estadoLaboral: response.estadoLaboral,
              kmInicial,
              combustibleInicial,
              duracionMinutos: response.duracionMinutos,
              duracionFormateada: response.duracionFormateada,
            },
            estadoLaboral: response.estadoLaboral,
          });

          return response;
        } catch (error: any) {
          const mensaje =
            error?.response?.data?.detail ||
            error?.message ||
            'Error al iniciar turno';
          throw new Error(mensaje);
        }
      },

      // ============================================
      // CHECK-OUT
      // ============================================
      checkOut: async (
        kmFinal: number,
        combustibleFinal: Combustible,
        recaudacionTicketera: number
      ) => {
        try {
          const response = await turnoService.checkOut(
            kmFinal,
            combustibleFinal,
            recaudacionTicketera
          );

          // Limpiar el turno activo
          set({
            turnoActivo: null,
            estadoLaboral: 'fuera_servicio',
          });

          return response;
        } catch (error: any) {
          const mensaje =
            error?.response?.data?.detail ||
            error?.message ||
            'Error al finalizar turno';
          throw new Error(mensaje);
        }
      },

      // ============================================
      // SET ESTADO LABORAL
      // ============================================
      setEstadoLaboral: (estado: EstadoLaboral) => {
        set({ estadoLaboral: estado });
      },

      // ============================================
      // SET TURNO ACTIVO (actualización inmediata)
      // ============================================
      setTurnoActivo: (turno: TurnoActivo | null) => {
        set({
          turnoActivo: turno,
          estadoLaboral: turno?.estadoLaboral || 'fuera_servicio',
        });
      },

      // ============================================
      // RESET
      // ============================================
      reset: () => {
        set({
          estadoChofer: null,
          turnoActivo: null,
          estadoLaboral: 'fuera_servicio',
          historial: [],
          isLoading: false,
          error: null,
        });
      },
    }),
    {
      name: 'taxip-turno',
      storage: createJSONStorage(() => AsyncStorage),
      // Persistir solo lo necesario
      partialize: (state) => ({
        turnoActivo: state.turnoActivo,
        estadoLaboral: state.estadoLaboral,
      }),
    }
  )
);