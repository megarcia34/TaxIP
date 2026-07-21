// D:\ataxip\dashboard\types\tarifa.ts
export type ModoCalculo = 'ficha_argentina' | 'por_km' | 'por_minuto' | 'mixto';

export interface ConfiguracionTarifa {
  id: string;
  control_base_id: string;
  nombre: string;
  modo_calculo: ModoCalculo;
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