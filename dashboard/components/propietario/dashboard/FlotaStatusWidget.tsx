// components/propietario/dashboard/FlotaStatusWidget.tsx

'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Car } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FlotaStatusWidgetProps {
  data?: {
    total: number
    activos: number
    detalle: Array<{
      vehiculo_id: string
      patente: string
      chofer_nombre: string
      estado: 'libre' | 'ocupado' | 'offline'
    }>
  }
  loading?: boolean
}

export function FlotaStatusWidget({ data, loading = false }: FlotaStatusWidgetProps) {
  const estadoColors = {
    ocupado: 'bg-blue-500',
    libre: 'bg-green-500',
    offline: 'bg-gray-400',
  }

  const estadoLabels = {
    ocupado: 'Ocupado',
    libre: 'Libre',
    offline: 'Fuera de servicio',
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Estado de Flota</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[100px] items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        </CardContent>
      </Card>
    )
  }

  const flota = data || { total: 0, activos: 0, detalle: [] }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Estado de Flota</CardTitle>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">
              {flota.activos}/{flota.total} activos
            </span>
            <Badge variant={flota.activos === flota.total ? 'default' : 'destructive'}>
              {flota.activos === flota.total ? '✅ Completa' : `⚠️ ${flota.total - flota.activos} fuera de servicio`}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {flota.detalle.length === 0 ? (
            <p className="text-center text-sm text-muted-foreground">No hay vehículos registrados</p>
          ) : (
            flota.detalle.map((vehiculo) => (
              <div
                key={vehiculo.vehiculo_id}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <Car className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-medium">{vehiculo.patente}</p>
                    <p className="text-xs text-muted-foreground">{vehiculo.chofer_nombre || 'Sin chofer'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={cn('text-xs text-white', estadoColors[vehiculo.estado])}>
                    {estadoLabels[vehiculo.estado]}
                  </Badge>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}