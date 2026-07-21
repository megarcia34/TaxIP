'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Clock, MapPin, User, RefreshCw, AlertCircle } from 'lucide-react'

interface Solicitud {
  id: string
  pasajero: string
  origen: string
  destino: string
  estado: string
  horasEspera: number
  creadoEn: string
}

export function SolicitudesActivas() {
  const { status } = useSession()
  const [solicitudes, setSolicitudes] = useState<Solicitud[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSolicitudes = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await fetch('/api/tenant/dashboard/solicitudes')
      if (!res.ok) throw new Error('Error al cargar solicitudes')
      const data = await res.json()
      setSolicitudes(data)
    } catch (err) {
      setError('No se pudieron cargar las solicitudes')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchSolicitudes()
      const interval = setInterval(fetchSolicitudes, 15000)
      return () => clearInterval(interval)
    }
  }, [status])

  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      pendiente: { label: 'Pendiente', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
      aceptado: { label: 'Aceptado', className: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' },
      en_curso: { label: 'En Curso', className: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' },
      en_ruta: { label: 'En Ruta', className: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300' },
      completado: { label: 'Completado', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
      cancelado: { label: 'Cancelado', className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' },
    }
    const info = estados[estado] || estados.pendiente
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const formatTiempoEspera = (horas: number) => {
    if (horas < 1) {
      const minutos = Math.round(horas * 60)
      return `${minutos} min`
    }
    if (horas < 24) {
      return `${Math.round(horas)} h`
    }
    const dias = Math.floor(horas / 24)
    return `${dias} d ${Math.round(horas % 24)} h`
  }

  if (loading && solicitudes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Solicitudes Activas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="h-4 w-32 animate-pulse rounded bg-muted" />
                <div className="h-3 w-24 animate-pulse rounded bg-muted" />
              </div>
              <div className="h-8 w-16 animate-pulse rounded bg-muted" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Solicitudes Activas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-3 py-4">
            <AlertCircle className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground text-center">{error}</p>
            <Button variant="outline" size="sm" onClick={fetchSolicitudes}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Reintentar
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          Solicitudes Activas
          <Badge variant="secondary">{solicitudes.length}</Badge>
        </CardTitle>
        <Button variant="ghost" size="icon" onClick={fetchSolicitudes} title="Actualizar">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
        {solicitudes.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-8 text-muted-foreground">
            <div className="text-4xl">✅</div>
            <p className="text-sm">No hay solicitudes activas</p>
            <p className="text-xs">Todas las solicitudes han sido atendidas</p>
          </div>
        ) : (
          solicitudes.map((solicitud) => (
            <div
              key={solicitud.id}
              className="rounded-lg border p-3 space-y-2 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{solicitud.pasajero}</span>
                </div>
                {getEstadoBadge(solicitud.estado)}
              </div>

              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground">Origen</p>
                  <p className="text-sm line-clamp-2">{solicitud.origen}</p>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground">Destino</p>
                  <p className="text-sm line-clamp-2">{solicitud.destino}</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Clock className="h-3 w-3" />
                  <span>Espera: {formatTiempoEspera(solicitud.horasEspera)}</span>
                </div>
                <span>{solicitud.creadoEn}</span>
              </div>

              <Button
                size="sm"
                className="w-full mt-1"
                variant="outline"
                onClick={() => window.location.href = `/viajes/${solicitud.id}`}
              >
                Ver Detalle
              </Button>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}