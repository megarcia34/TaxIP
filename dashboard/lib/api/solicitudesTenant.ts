// D:\aTaxip\dashboard\lib\api\solicitudesTenant.ts
import { apiClient } from './client';

// ============================================
// URL BASE PARA DOCUMENTOS
// ============================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Convierte una URL relativa (ej: /uploads/documentos/...) en URL absoluta.
 * Si ya es absoluta (empieza con http), la devuelve tal cual.
 */
export function getDocumentoUrl(url: string | null): string | null {
  if (!url) return null;
  if (url.startsWith('http')) return url;
  return `${API_BASE}${url}`;
}

// ============================================
// TIPOS
// ============================================

export interface DocumentoChofer {
  url: string | null;
  numero: string | null;
  fecha_vencimiento: string | null;
}

export interface ChoferPendiente {
  chofer_vehiculo_id: string;
  usuario_id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string | null;
  vehiculo: {
    patente: string;
    marca: string;
    modelo: string;
    anio: number;
  } | null;
  fecha_registro: string;
  es_propietario: boolean;
  cantidad_vehiculos: number;
  documentos: Record<string, DocumentoChofer>;  // NUEVO
}

export interface DocumentoVehiculo {
  url: string | null;           // NUEVO
  numero: string | null;
  fecha_vencimiento: string | null;
}

export interface PropietarioInfo {
  usuario_id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string | null;
}

export interface VehiculoPendiente {
  vehiculo_id: string;
  patente: string;
  marca: string;
  modelo: string;
  anio: number;
  numero_licencia: string | null;
  fecha_vencimiento_taxi: string | null;
  created_at: string;
  propietario: PropietarioInfo;
  documentos: Record<string, DocumentoVehiculo>;
  documentacion_completa: true;
}

export interface VehiculoIncompleto {
  vehiculo_id: string;
  patente: string;
  marca: string;
  modelo: string;
  anio: number;
  numero_licencia: string | null;
  fecha_vencimiento_taxi: string | null;
  created_at: string;
  estado_aprobacion: string;
  propietario: PropietarioInfo;
  documentos_faltantes: string[];
  documentacion_completa: false;
}

// ============================================
// API
// ============================================

export const solicitudesTenantAPI = {
  // ---- Choferes ----
  getChoferesPendientes: async (): Promise<ChoferPendiente[]> => {
    const response = await apiClient.get('/control-base/choferes-pendientes');
    return response.data;
  },

  aprobarChofer: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.put(`/control-base/aprobar-chofer/${id}`);
    return response.data;
  },

  rechazarChofer: async (id: string, motivo: string): Promise<{ success: boolean; message: string }> => {
    // AHORA acepta motivo (migracion m3_025)
    const response = await apiClient.put(`/control-base/rechazar-chofer/${id}`, { motivo });
    return response.data;
  },

  // ---- Vehiculos ----
  getVehiculosPendientes: async (): Promise<VehiculoPendiente[]> => {
    const response = await apiClient.get('/control-base/vehiculos-pendientes');
    return response.data;
  },

  getVehiculosIncompletos: async (): Promise<VehiculoIncompleto[]> => {
    const response = await apiClient.get('/control-base/vehiculos-incompletos');
    return response.data;
  },

  aprobarVehiculo: async (id: string): Promise<{ success: boolean; message: string; vehiculo_id: string }> => {
    const response = await apiClient.put(`/control-base/aprobar-vehiculo/${id}`);
    return response.data;
  },

  rechazarVehiculo: async (id: string, motivo: string): Promise<{ success: boolean; message: string; vehiculo_id: string }> => {
    const response = await apiClient.put(`/control-base/rechazar-vehiculo/${id}`, { motivo });
    return response.data;
  },
};