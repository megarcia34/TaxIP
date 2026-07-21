'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Wrench, Calendar, Car, Bell } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AlertaMantenimiento {
  tipo_servicio: string
  tipo_nombre: string
  km_restante: number | null
  dias_restantes: number | null
  alerta_a: string
  urgencia: 'alta' | 'media'
}

interface AlertaVehiculo {
  vehiculo_id: string
  patente: string
  km_actual: number
  mantenimientos_proximos: AlertaMantenimiento[]
}

interface AlertasResponse {
  total_alertas: number
  vehiculos_con_alertas: AlertaVehiculo[]
}

const TIPO_NOMBRES: Record<string, string> = {
  SERVICE_MENOR: 'Service menor',
  SERVICE_MAYOR: 'Service mayor',
  NEUMATICOS: 'Neumáticos',
  FRENOS: 'Frenos',
  DISTRIBUCION: 'Distribución',
  ALINEACION: 'Alineación',
  CAMBIO_ACEITE: 'Cambio de aceite',
  LUBRICACION: 'Lubricación',
  ELECTRICO: 'Sistema eléctrico',
  GENERAL: 'Mantenimiento general'
}

export default function AlertasMantenimiento() {
  const [alertas, setAlertas] = useState<AlertasResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const cargarAlertas = async () => {
    const token = localStorage.getItem('prop_token')
    try {
      const res = await fetch(`${API_URL}/api/propietario/mantenimientos/alertas`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setAlertas(data)
      }
    } catch (error) {
      console.error('Error cargando alertas:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarAlertas()
    // Recargar cada 30 segundos
    const interval = setInterval(cargarAlertas, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Bell className="h-4 w-4 animate-pulse" />
            <span>Cargando alertas...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!alertas || alertas.total_alertas === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-green-600">
            <Bell className="h-4 w-4" />
            <span>Todos los vehículos están al día con sus mantenimientos</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-yellow-200 bg-yellow-50/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2 text-yellow-800">
          <AlertTriangle className="h-5 w-5" />
          Alertas de mantenimiento ({alertas.total_alertas})
        </CardTitle>
        <CardDescription>
          Servicios próximos a vencer en tus vehículos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {alertas.vehiculos_con_alertas.map((vehiculo) => (
            <div key={vehiculo.vehiculo_id} className="border-b pb-3 last:border-0">
              <div className="flex items-center gap-2 mb-2">
                <Car className="h-4 w-4 text-muted-foreground" />
                <span className="font-semibold">{vehiculo.patente}</span>
                <span className="text-xs text-muted-foreground">
                  (km actual: {vehiculo.km_actual.toLocaleString()})
                </span>
              </div>
              <div className="space-y-2 pl-6">
                {vehiculo.mantenimientos_proximos.map((m, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Wrench className="h-3 w-3 text-muted-foreground" />
                      <span className="text-sm">{TIPO_NOMBRES[m.tipo_servicio] || m.tipo_nombre}</span>
                      {m.km_restante !== null && (
                        <span className="text-xs text-muted-foreground">
                          (a {m.km_restante.toLocaleString()} km)
                        </span>
                      )}
                      {m.dias_restantes !== null && (
                        <span className="text-xs text-muted-foreground">
                          ({m.dias_restantes} días)
                        </span>
                      )}
                    </div>
                    <Badge variant={m.urgencia === 'alta' ? 'destructive' : 'default'}>
                      {m.urgencia === 'alta' ? '⚠️ Urgente' : '📋 Programar'}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}