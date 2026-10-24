'use client'

import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api/client' // Ajustá la ruta si es distinta

interface UseViajesDataParams {
  vehiculoId?: string
  choferId?: string
  fechaDesde?: string
  fechaHasta?: string
  estado?: string
  metodoPago?: string
  fuente?: string
  search?: string
  page?: number
  pageSize?: number
}

interface ViajeHistorial {
  id: string
  estado: string
  direccion_origen: string
  direccion_destino: string
  precio_estimado: number | null
  precio_final: number | null
  created_at: string
  aceptado_en: string | null
  iniciado_en: string | null
  finalizado_en: string | null
  distancia_metros: number | null
  tiempo_estimado_segundos: number | null
  pasajero_nombre: string | null
  chofer_nombre: string
  fecha: string
  hora: string
  precio_mostrado: number | null
  empresa: string
  propietario_nombre: string
  patente: string
  marca: string
  modelo: string
  calificacion: number | null
  origen_lat: number | null
  origen_lng: number | null
  destino_lat: number | null
  destino_lng: number | null
}

export function useViajesData(params: UseViajesDataParams) {
  const queryKey = ['propietario', 'viajes', JSON.stringify(params)]

  return useQuery<{ viajes: ViajeHistorial[]; total: number }>({
    queryKey,
    queryFn: async () => {
      const queryParams = new URLSearchParams()

      if (params.fechaDesde) queryParams.append('fecha_desde', params.fechaDesde)
      if (params.fechaHasta) queryParams.append('fecha_hasta', params.fechaHasta)
      if (params.estado) queryParams.append('estado', params.estado)
      if (params.page) queryParams.append('offset', String((params.page - 1) * (params.pageSize || 10)))
      if (params.pageSize) queryParams.append('limit', String(params.pageSize))

      const queryString = queryParams.toString()
      const url = `/viajes/historial${queryString ? `?${queryString}` : ''}`

      const response = await apiClient.get(url)
      const data = response.data

      // El backend devuelve { total, limit, offset, viajes: [...] }
      return {
        viajes: data.viajes || [],
        total: data.total || 0,
      }
    },
    staleTime: 1000 * 60,
    placeholderData: (previousData) => previousData ?? {
      viajes: [],
      total: 0,
    },
  })
}