'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Car, DollarSign, TrendingUp, Users, Calendar, Briefcase, MapPin } from 'lucide-react'

// ============================================================
// INTERFACES
// ============================================================

interface ResumenEjecutivoData {
  vehiculos?: {
    total: number
    activos: number
    en_servicio: number
  }
  viajes?: {
    total: number
    completados: number
    en_curso: number
  }
  finanzas?: {
    ingresos: number
    gastos: number
    ganancia: number
  }
  contratos?: {
    activos: number
    vencidos: number
  }
  zonas_activas?: Array<{
    nombre: string
    viajes: number
    ingresos: number
  }>
  propietario?: {
    nombre: string
    vehiculos: number
  }
}

interface ResumenEjecutivoProps {
  data: ResumenEjecutivoData
  loading?: boolean
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export function ResumenEjecutivo({ data, loading = false }: ResumenEjecutivoProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="h-4 w-24 animate-pulse rounded bg-muted" />
              <div className="mt-2 h-6 w-16 animate-pulse rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // Valores por defecto para evitar errores
  const viajes = data?.viajes ?? { total: 0, completados: 0, en_curso: 0 }
  const finanzas = data?.finanzas ?? { ingresos: 0, gastos: 0, ganancia: 0 }
  const vehiculos = data?.vehiculos ?? { total: 0, activos: 0, en_servicio: 0 }
  const contratos = data?.contratos ?? { activos: 0, vencidos: 0 }

  const stats = [
    {
      title: 'Vehículos',
      value: vehiculos.total,
      subtitle: `${vehiculos.activos} activos • ${vehiculos.en_servicio} en servicio`,
      icon: Car,
      color: 'text-blue-500',
    },
    {
      title: 'Contratos Activos',
      value: contratos.activos,
      subtitle: `${contratos.vencidos} vencidos`,
      icon: Briefcase,
      color: 'text-green-500',
    },
    {
      title: 'Viajes',
      value: viajes.total,
      subtitle: `${viajes.completados} completados • ${viajes.en_curso} en curso`,
      icon: Calendar,
      color: 'text-purple-500',
    },
    {
      title: 'Ganancia',
      value: `$${finanzas.ganancia.toLocaleString()}`,
      subtitle: `Ingresos: $${finanzas.ingresos.toLocaleString()}`,
      icon: TrendingUp,
      color: 'text-green-600',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
              <div className="mt-2">
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.subtitle}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Zonas activas - si existen */}
      {data?.zonas_activas && data.zonas_activas.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Zonas Activas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.zonas_activas.map((zona, index) => (
                <div key={index} className="flex items-center justify-between border-b pb-2 last:border-0">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{zona.nombre}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span>{zona.viajes} viajes</span>
                    <span className="font-medium">${zona.ingresos.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}