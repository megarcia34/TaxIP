// D:\ataxip\dashboard\lib\api\tarifaService.ts
import apiClient from './client';

export interface ConfiguracionTarifa {
  id: string;
  control_base_id: string;
  nombre: string;
  modo_calculo: 'ficha_argentina' | 'por_km' | 'por_minuto' | 'mixto';
  tarifa_base: number;
  precio_por_km: number;
  precio_por_minuto: number;
  distancia_por_ficha: number;
  precio_por_ficha: number;
  precio_por_minuto_espera: number;
  recargo_nocturno: number;
  recargo_feriado: number;
  recargo_domingo: number;
  hora_inicio_nocturno: string;
  hora_fin_nocturno: string;
  moneda: string;
  descripcion: string | null;
  activo: boolean;
  created_at: string;
  updated_at: string;
  tenant_nombre?: string;
}

export interface CreateTarifaData {
  control_base_id: string;
  nombre: string;
  modo_calculo: string;
  tarifa_base: number;
  precio_por_km: number;
  precio_por_minuto: number;
  distancia_por_ficha: number;
  precio_por_ficha: number;
  precio_por_minuto_espera: number;
  recargo_nocturno: number;
  recargo_feriado: number;
  recargo_domingo: number;
  hora_inicio_nocturno: string;
  hora_fin_nocturno: string;
  moneda?: string;
  descripcion?: string;
  activo?: boolean;
}

export const tarifaService = {
  // Obtener configuración del tenant actual (Admin Tenant)
  getMiTenant: async (): Promise<ConfiguracionTarifa> => {
    const response = await apiClient.get('/admin/tarifas/mi-tenant');
    return response.data;
  },

  // Obtener configuración por ID (Super Admin / Admin Tenant)
  getById: async (id: string): Promise<ConfiguracionTarifa> => {
    const response = await apiClient.get(`/admin/tarifas/${id}`);
    return response.data;
  },

  // Obtener configuración por tenant (Super Admin / Admin Tenant)
  getByTenant: async (control_base_id: string): Promise<ConfiguracionTarifa> => {
    const response = await apiClient.get(`/admin/tarifas/control-base/${control_base_id}`);
    return response.data;
  },

  // Listar todas (Super Admin)
  listAll: async (params?: { activo?: boolean; limit?: number; offset?: number }): Promise<ConfiguracionTarifa[]> => {
    const response = await apiClient.get('/admin/tarifas', { params });
    return response.data;
  },

  // Crear nueva configuración (Super Admin / Admin Tenant)
  create: async (data: CreateTarifaData): Promise<ConfiguracionTarifa> => {
    const response = await apiClient.post('/admin/tarifas', data);
    return response.data;
  },

  // Actualizar configuración (Super Admin / Admin Tenant)
  update: async (id: string, data: Partial<CreateTarifaData>): Promise<ConfiguracionTarifa> => {
    const response = await apiClient.put(`/admin/tarifas/${id}`, data);
    return response.data;
  },

  // Eliminar (soft delete) (Super Admin / Admin Tenant)
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/tarifas/${id}`);
  },
};