import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export interface DisponibilidadParams {
  vehiculo_id?: string
  chofer_id?: string
  hora_inicio?: string
  hora_fin?: string
  dias_contractuales?: string[]
  fecha_inicio?: string
  fecha_fin?: string
}

export interface ContratoDetalle {
  contrato_id: string
  patente: string
  hora_inicio: string | null
  hora_fin: string | null
  dias_contractuales: string[]
  estado: string
  chofer?: string
  vehiculo_id?: string
}

export interface DisponibilidadResponse {
  vehiculo_disponible: boolean
  chofer_disponible: boolean
  conflictos: string[]
  vehiculo_detalle: ContratoDetalle | null
  chofer_detalle: ContratoDetalle | null
}

export function useVerificarDisponibilidad(params: DisponibilidadParams) {
  const isEnabled = !!(params.vehiculo_id || params.chofer_id)
  
  return useQuery({
    queryKey: ['disponibilidad', params],
    queryFn: async () => {
      const queryParams = new URLSearchParams()
      
      if (params.vehiculo_id) {
        queryParams.append('vehiculo_id', params.vehiculo_id)
      }
      if (params.chofer_id) {
        queryParams.append('chofer_id', params.chofer_id)
      }
      if (params.hora_inicio) {
        queryParams.append('hora_inicio', params.hora_inicio)
      }
      if (params.hora_fin) {
        queryParams.append('hora_fin', params.hora_fin)
      }
      if (params.dias_contractuales && params.dias_contractuales.length > 0) {
        queryParams.append('dias_contractuales', JSON.stringify(params.dias_contractuales))
      }
      if (params.fecha_inicio) {
        queryParams.append('fecha_inicio', params.fecha_inicio)
      }
      if (params.fecha_fin) {
        queryParams.append('fecha_fin', params.fecha_fin)
      }
      
      const response = await apiClient.get(
        `/api/propietario/contratos/verificar-disponibilidad?${queryParams.toString()}`
      )
      return response.data as DisponibilidadResponse
    },
    enabled: isEnabled,
    staleTime: 5000, // 5 segundos
    refetchOnWindowFocus: false,
  })
}