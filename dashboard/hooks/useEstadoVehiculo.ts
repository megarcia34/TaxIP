'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export interface EstadoVehiculo {
  vehiculo_id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  estado: 'COMPLETO' | 'PENDIENTE'
  configuracion_completa: boolean
  neumaticos: {
    total: number
    activos: number
    requeridos: number
    completo: boolean
  }
  documentos: {
    total: number
    requeridos: string[]
    faltantes: string[]
    completo: boolean
    lista: Record<string, {
      presente: boolean
      vencimiento: string | null
      vigente: boolean
    }>
  }
  mantenimientos: {
    total: number
    ultimo: string | null
    completo: boolean
  }
}

export function useEstadoVehiculo(vehiculoId: string | undefined) {
  return useQuery({
    queryKey: ['vehiculo-estado', vehiculoId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/propietario/vehiculos/${vehiculoId}/estado`)
      return response.data as EstadoVehiculo
    },
    enabled: !!vehiculoId,
    staleTime: 1000 * 60 * 5, // 5 minutos
  })
}