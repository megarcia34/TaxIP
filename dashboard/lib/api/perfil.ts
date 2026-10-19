// D:\ataxip\dashboard\lib\api\perfil.ts
import { apiClient } from './client';

// ============================================================
// TIPOS
// ============================================================

export interface TenantInfo {
  control_base_id: string;
  nombre: string;
  antiguedad_maxima_taxi_anios: number;
  dias_revision_documentos: number;
}

export interface PerfilPropietario {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string | null;
  documento: string | null;
  direccion: string | null;
  ciudad_id: string | null;
  ciudad_nombre: string | null;
  foto_perfil_url: string | null;
  codigo_postal: string | null;
  fecha_nacimiento: string | null;
  cuit_cuil: string | null;
  condicion_impositiva: CondicionImpositiva | null;
  tenant: TenantInfo | null;
}

export type CondicionImpositiva =
  | 'responsable_inscripto'
  | 'monotributo'
  | 'exento'
  | 'consumidor_final'
  | 'no_categorizado';

export interface PerfilUpdate {
  nombre?: string;
  apellido?: string;
  telefono?: string | null;
  documento?: string | null;
  direccion?: string | null;
  ciudad_id?: string | null;
  foto_perfil_url?: string | null;
  codigo_postal?: string | null;
  fecha_nacimiento?: string | null;
  cuit_cuil?: string | null;
  condicion_impositiva?: CondicionImpositiva | null;
}

export interface CiudadOperativa {
  id: string;
  nombre: string;
  provincia?: string;
}

// ============================================================
// API
// ============================================================

export const perfilAPI = {
  get: async (): Promise<PerfilPropietario> => {
    const response = await apiClient.get('/propietario/perfil');
    return response.data;
  },

  update: async (data: PerfilUpdate): Promise<PerfilPropietario> => {
    const response = await apiClient.put('/propietario/perfil', data);
    return response.data;
  },

  getCiudadesOperativas: async (): Promise<CiudadOperativa[]> => {
    const response = await apiClient.get('/geo/ciudades-operativas');
    return response.data;
  },
};