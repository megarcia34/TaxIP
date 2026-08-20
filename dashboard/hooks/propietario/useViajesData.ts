'use client'

import { useQuery } from '@tanstack/react-query'
import { ViajePropietario } from '@/types/propietario'
import { mockViajes } from '@/lib/mocks/propietario-data'

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

export function useViajesData(params: UseViajesDataParams) {
  const queryKey = ['propietario', 'viajes', JSON.stringify(params)]

  return useQuery<{ data: ViajePropietario[]; total: number }>({
    queryKey,
    queryFn: async () => {
      // TODO: Reemplazar con fetch real cuando el backend esté listo
      // const queryString = new URLSearchParams(
      //   Object.entries(params).filter(([_, v]) => v !== undefined && v !== '')
      // ).toString()
      // const res = await fetch(`/api/propietario/viajes?${queryString}`)
      // if (!res.ok) throw new Error('Error al cargar viajes')
      // return res.json()

      // Simular filtrado con mocks
      let filtered = [...mockViajes]

      if (params.vehiculoId) {
        filtered = filtered.filter((t) => t.vehiculo_id === params.vehiculoId)
      }
      if (params.estado) {
        filtered = filtered.filter((t) => t.estado === params.estado)
      }
      if (params.metodoPago) {
        filtered = filtered.filter((t) => t.metodo_pago === params.metodoPago)
      }
      if (params.fuente) {
        filtered = filtered.filter((t) => t.fuente === params.fuente)
      }
      if (params.search) {
        const search = params.search.toLowerCase()
        filtered = filtered.filter(
          (t) =>
            (t.pasajero_nombre?.toLowerCase() || '').includes(search) ||
            t.direccion_origen.toLowerCase().includes(search) ||
            t.direccion_destino.toLowerCase().includes(search) ||
            t.id.toLowerCase().includes(search)
        )
      }

      const start = ((params.page || 1) - 1) * (params.pageSize || 10)
      const end = start + (params.pageSize || 10)

      return {
        data: filtered.slice(start, end),
        total: filtered.length,
      }
    },
    staleTime: 1000 * 60, // 1 minuto
    placeholderData: (previousData) => previousData ?? {
  data: [],
  total: 0
},
  })
}