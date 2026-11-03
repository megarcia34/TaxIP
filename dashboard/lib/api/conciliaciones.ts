// lib/api/conciliaciones.ts
import { apiClient } from './client'

// ============================================================
// TIPOS
// ============================================================

export interface ConciliacionPendienteItem {
  turno_id: string
  fin_turno: string | null
  vehiculo_patente: string
  chofer_nombre: string
  tipo_contrato: string
  recaudacion_declarada: number
  efectivo_en_mano: number
  gastos_declarados: number
  diferencia: number
  dias_restantes: number
  estado: string
}

export interface ConciliacionPendienteResponse {
  total: number
  turnos: ConciliacionPendienteItem[]
}

export interface GastoConciliacion {
  id: string
  tipo_gasto: string
  monto: number
  descripcion: string | null
  url_comprobante: string | null
  created_at: string
  estado_aprobacion: 'pendiente' | 'aprobado' | 'rechazado'
}

export interface DiferenciaConciliacion {
  id: string
  tipo: 'DEUDA_CHOFER' | 'DEUDA_PROPIETARIO' | 'NEUTRA'
  concepto: string
  monto: number
  descripcion: string | null
  estado: 'PENDIENTE' | 'SALDADA'
}

export interface ConciliacionDetalle {
  turno_id: string
  fin_turno: string | null
  vehiculo_patente: string
  chofer_nombre: string
  tipo_contrato: string
  porcentaje_chofer: number | null
  canon_diario: number | null
  tratamiento_gastos: string | null
  recaudacion_viajes: number
  recaudacion_manual: number
  recaudacion_total: number
  efectivo_en_mano: number
  recaudacion_electronico: number
  diferencia_efectivo: number
  gastos: GastoConciliacion[]
  gastos_total: number
  diferencias: DiferenciaConciliacion[]
  diferencias_total: number
  puede_cerrar: boolean
}

// ============================================================
// API
// ============================================================

export const conciliacionesAPI = {
  listar: async (): Promise<ConciliacionPendienteResponse> => {
    const res = await apiClient.get('/propietario/conciliaciones')
    return res.data
  },

  detalle: async (turnoId: string): Promise<ConciliacionDetalle> => {
    const res = await apiClient.get(`/propietario/conciliaciones/${turnoId}`)
    return res.data
  },

  historial: async (): Promise<{ total: number; conciliaciones: ConciliacionHistorialItem[] }> => {
    const res = await apiClient.get('/propietario/conciliaciones/historial/listado')
    return res.data
  },

  aprobarGasto: async (turnoId: string, gastoId: string): Promise<void> => {
    await apiClient.post(`/propietario/conciliaciones/${turnoId}/aprobar-gasto/${gastoId}`)
  },

  rechazarGasto: async (turnoId: string, gastoId: string, motivo: string): Promise<void> => {
    await apiClient.post(`/propietario/conciliaciones/${turnoId}/rechazar-gasto/${gastoId}`, { motivo })
  },

  cerrar: async (turnoId: string, observaciones?: string): Promise<void> => {
    await apiClient.post(`/propietario/conciliaciones/${turnoId}/cerrar`, { observaciones })
  },

  saldarDiferencia: async (turnoId: string, diferenciaId: string): Promise<void> => {
    await apiClient.post(`/propietario/conciliaciones/${turnoId}/saldar-diferencia/${diferenciaId}`, {})
  },
}
export interface ConciliacionHistorialItem {
  turno_id: string
  fin_turno: string | null
  conciliado_en: string | null
  tipo_conciliacion: string
  estado: string
  vehiculo_patente: string
  chofer_nombre: string
  recaudacion_total: number
  total_chofer: number
  total_propietario: number
  deuda_pendiente: number
}

