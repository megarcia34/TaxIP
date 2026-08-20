'use client'

import { useQuery } from '@tanstack/react-query'
import { PropietarioDashboardData } from '@/types/propietario'
import { mockDashboardData } from '@/lib/mocks/propietario-data'

export function useDashboardData() {
  return useQuery<PropietarioDashboardData>({
    queryKey: ['propietario', 'dashboard'],
    queryFn: async () => {
      // TODO: Reemplazar con fetch real cuando el backend esté listo
      // const res = await fetch('/api/propietario/dashboard/resumen')
      // if (!res.ok) throw new Error('Error al cargar el dashboard')
      // return res.json()
      return mockDashboardData
    },
    staleTime: 1000 * 60 * 5, // 5 minutos
    refetchOnWindowFocus: false,
  })
}