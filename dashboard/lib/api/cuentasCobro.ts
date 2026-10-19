// D:\ataxip\dashboard\lib\api\cuentasCobro.ts
import { apiClient } from './client';

// ============================================================
// TIPOS
// ============================================================

export type TipoCuenta = 'cbu' | 'cvu';

export interface CuentaCobro {
  id: string;
  usuario_id: string;
  tipo: TipoCuenta;
  numero: string;
  alias: string | null;
  banco: string;
  titular: string | null;
  predeterminada: boolean;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface CuentaCobroCreate {
  tipo: TipoCuenta;
  numero: string;
  alias?: string | null;
  banco: string;
  titular?: string | null;
  predeterminada?: boolean;
}

export interface CuentaCobroUpdate {
  tipo?: TipoCuenta;
  numero?: string;
  alias?: string | null;
  banco?: string;
  titular?: string | null;
}

// ============================================================
// API
// ============================================================

export const cuentasCobroAPI = {
  list: async (): Promise<CuentaCobro[]> => {
    const response = await apiClient.get('/propietario/cuentas-cobro');
    return response.data;
  },

  create: async (data: CuentaCobroCreate): Promise<CuentaCobro> => {
    const response = await apiClient.post('/propietario/cuentas-cobro', data);
    return response.data;
  },

  update: async (id: string, data: CuentaCobroUpdate): Promise<CuentaCobro> => {
    const response = await apiClient.put(`/propietario/cuentas-cobro/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/propietario/cuentas-cobro/${id}`);
  },

  marcarPredeterminada: async (id: string): Promise<CuentaCobro> => {
    const response = await apiClient.put(`/propietario/cuentas-cobro/${id}/predeterminada`);
    return response.data;
  },
};