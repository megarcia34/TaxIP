'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { controlBaseAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Car, TrendingUp, Users, Star, Loader2 } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

interface KpiData {
  total_choferes_activos: number
  viajes_hoy: number
  ingresos_dia: number
  calificacion_promedio: number
}

export function KpiCards() {
  const { status } = useSession()

  const { data, isLoading, error } = useQuery<KpiData>({
    queryKey: ['estadisticas'],
    queryFn: controlBaseAPI.getEstadisticas,
    refetchInterval: 60000,
    enabled: status === 'authenticated', // ⬅️ NO ejecutar hasta tener sesión
    retry: (failureCount, error: any) => {
      // ⬅️ NO reintentar en 401
      if (error?.response?.status === 401) return false
      return failureCount < 3
    },
  })

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-1" />
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6 text-center text-muted-foreground">
              Error al cargar datos
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const kpis = [
    {
      title: 'Choferes Activos',
      value: data?.total_choferes_activos || 0,
      change: '+12%',
      icon: Car,
      color: 'text-blue-500',
    },
    {
      title: 'Viajes Hoy',
      value: data?.viajes_hoy || 0,
      change: '+8%',
      icon: TrendingUp,
      color: 'text-green-500',
    },
    {
      title: 'Ingresos del Día',
      value: `$${data?.ingresos_dia?.toLocaleString() || 0}`,
      change: '+15%',
      icon: Users,
      color: 'text-purple-500',
    },
    {
      title: 'Calificación Promedio',
      value: (data?.calificacion_promedio || 0).toFixed(1),
      change: '+0.2',
      icon: Star,
      color: 'text-yellow-500',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi) => (
        <Card key={kpi.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {kpi.title}
            </CardTitle>
            <kpi.icon className={`h-4 w-4 ${kpi.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpi.value}</div>
            <p className="text-xs text-muted-foreground">
              {kpi.change} vs semana pasada
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}