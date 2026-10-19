// D:\ataxip\dashboard\lib\api\metricasPropietario.ts
import { apiClient } from './client';

// ============================================================
// TIPOS
// ============================================================

export interface FallbackPrecio {
  id: string;
  viaje_id: string;
  vehiculo_id: string | null;
  patente: string | null;
  precio_estimado: number | null;
  precio_cobrado: number | null;
  motivo: string;
  fecha: string;
  origen: string | null;
  destino: string | null;
}

export interface MetricasFallbacks {
  total: number;
  fallbacks: FallbackPrecio[];
}

// ============================================================
// API
// ============================================================

export const metricasPropietarioAPI = {
  getFallbacks: async (): Promise<MetricasFallbacks> => {
    const response = await apiClient.get('/propietario/metricas/fallbacks');
    return response.data;
  },
};