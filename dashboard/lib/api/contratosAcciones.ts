// D:\ataxip\dashboard\lib\api\contratosAcciones.ts
import { apiClient } from './client';

// ============================================================
// TIPOS
// ============================================================

export interface CodigoGenerado {
  success: boolean;
  codigo: string;
  contrato_id: string;
  vehiculo_id: string;
  patente: string;
  expira_en: string;
  mensaje: string;
}

// ============================================================
// API
// ============================================================

export const contratosAccionesAPI = {
  generarCodigo: async (
    contratoId: string,
    diasValidez: number = 30
  ): Promise<CodigoGenerado> => {
    const response = await apiClient.post(
      `/propietario/contratos/${contratoId}/generar-codigo`,
      { dias_validez: diasValidez }
    );
    return response.data;
  },
};