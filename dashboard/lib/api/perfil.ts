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
  // ✅ NUEVO: Manejar el 403 devolviendo un perfil vacío
  get: async (): Promise<PerfilPropietario> => {
    try {
      const response = await apiClient.get('/propietario/perfil');
      return response.data;
    } catch (error: any) {
      // Si es 403 (sin vehículos) o 404 (sin perfil), devolver un perfil vacío
      if (error.response?.status === 403 || error.response?.status === 404) {
        console.log('ℹ️ Perfil no encontrado o sin permisos. Devolviendo perfil vacío.')
        return {
          id: '',
          email: '',
          nombre: '',
          apellido: '',
          telefono: null,
          documento: null,
          direccion: null,
          ciudad_id: null,
          ciudad_nombre: null,
          foto_perfil_url: null,
          codigo_postal: null,
          fecha_nacimiento: null,
          cuit_cuil: null,
          condicion_impositiva: null,
          tenant: null,
        };
      }
      // Para otros errores, lanzar el error
      throw error;
    }
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