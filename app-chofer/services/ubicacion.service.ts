/**
 * Servicio del Módulo 3 - Ubicación.
 *
 * Wrapper de expo-location.
 * STUB de Fase 9.2: solo la estructura. El tracking adaptativo (10s en
 * movimiento, 30s detenido) se implementa en Fase 9.3.
 */
import * as Location from 'expo-location';
import type { Coordenada } from '@/types/ubicacion.types';

type TrackingCallback = (coordenada: Coordenada) => void;

const PENDIENTE = '[Ubicación] pendiente Fase 9.3';

export const ubicacionService = {
  /**
   * Solicita permisos de ubicación en primer plano.
   * Devuelve true si el permiso fue concedido.
   */
  async pedirPermisos(): Promise<boolean> {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
  },

  /**
   * Devuelve el estado actual del permiso de ubicación.
   */
  async estadoPermisos(): Promise<
    'granted' | 'denied' | 'undetermined'
  > {
    const { status } = await Location.getForegroundPermissionsAsync();
    if (status === 'granted') return 'granted';
    if (status === 'denied') return 'denied';
    return 'undetermined';
  },

  /**
   * Obtiene la ubicación actual una vez.
   */
  async obtenerUbicacionActual(): Promise<Coordenada> {
    console.warn(PENDIENTE, 'obtenerUbicacionActual()');
    throw new Error('Pendiente: Fase 9.3');
  },

  /**
   * Inicia tracking continuo de ubicación.
   * El intervalo adaptativo (10s movimiento / 30s detenido) se implementa
   * en Fase 9.3.
   */
  async iniciarTracking(
    _callback: TrackingCallback,
    _intervaloMs?: number
  ): Promise<void> {
    console.warn(PENDIENTE, 'iniciarTracking()');
    throw new Error('Pendiente: Fase 9.3');
  },

  /**
   * Detiene el tracking continuo.
   */
  async detenerTracking(): Promise<void> {
    console.warn(PENDIENTE, 'detenerTracking()');
  },
};