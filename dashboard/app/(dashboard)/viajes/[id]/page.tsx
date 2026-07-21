'use client'

import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { viajesAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, MapPin, User, Car, Clock, DollarSign, Calendar, Map } from 'lucide-react'
import { RouteMap } from '@/components/viajes/RouteMap'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    aceptado: 'bg-blue-500',
    en_curso: 'bg-purple-500',
    finalizado: 'bg-green-500',
    cancelado: 'bg-red-500',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoTexto = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'Pendiente',
    aceptado: 'Aceptado',
    en_curso: 'En curso',
    finalizado: 'Finalizado',
    cancelado: 'Cancelado',
  }
  return estados[estado] || estado
}

export default function ViajeDetallePage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const viewRoute = searchParams.get('view') === 'route'
  const viajeId = params.id as string

  const { data: viaje, isLoading } = useQuery({
    queryKey: ['viaje', viajeId],
    queryFn: () => viajesAPI.getEstado(viajeId),
    enabled: !!viajeId,
  })

  const formatFecha = (fecha: string) => {
    if (!fecha) return 'N/A'
    return format(new Date(fecha), "dd 'de' MMMM 'de' yyyy, HH:mm", { locale: es })
  }

  const hasRouteCoordinates = () => {
    return viaje?.origen_lat && viaje?.origen_lng && viaje?.destino_lat && viaje?.destino_lng
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!viaje) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Viaje no encontrado</p>
        <Button className="mt-4" onClick={() => router.back()}>Volver</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Detalle del Viaje</h1>
        <Badge className={getEstadoColor(viaje.estado)}>
          {getEstadoTexto(viaje.estado)}
        </Badge>
      </div>

      <Tabs defaultValue={viewRoute ? 'route' : 'info'} className="space-y-4">
        <TabsList>
          <TabsTrigger value="info" className="gap-2">
            <Calendar className="h-4 w-4" />
            Información
          </TabsTrigger>
          {hasRouteCoordinates() && (
            <TabsTrigger value="route" className="gap-2">
              <Map className="h-4 w-4" />
              Ver Ruta
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="info">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Información del Viaje</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-green-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Origen</p>
                    <p className="font-medium">{viaje.direccion_origen || viaje.origen || 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-red-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Destino</p>
                    <p className="font-medium">{viaje.direccion_destino || viaje.destino || 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <DollarSign className="h-5 w-5 text-yellow-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Precio</p>
                    <p className="font-medium text-lg">
                      ${viaje.precio_final || viaje.precio_estimado || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Fecha y hora</p>
                    <p className="font-medium">{formatFecha(viaje.created_at)}</p>
                  </div>
                </div>
                {viaje.distancia_metros && (
                  <div className="flex items-start gap-3">
                    <span className="h-5 w-5 text-gray-500">📏</span>
                    <div>
                      <p className="text-sm text-muted-foreground">Distancia</p>
                      <p className="font-medium">{(viaje.distancia_metros / 1000).toFixed(1)} km</p>
                    </div>
                  </div>
                )}
                {viaje.tiempo_estimado_segundos && (
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-muted-foreground">Tiempo estimado</p>
                      <p className="font-medium">{Math.floor(viaje.tiempo_estimado_segundos / 60)} minutos</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Participantes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <User className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Pasajero</p>
                    <p className="font-medium">{viaje.pasajero_nombre || 'N/A'}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Car className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Chofer</p>
                    <p className="font-medium">{viaje.chofer_nombre || 'No asignado'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Timeline */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Línea de tiempo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {viaje.created_at && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 mt-2 rounded-full bg-green-500" />
                    <div>
                      <p className="font-medium">Solicitado</p>
                      <p className="text-sm text-muted-foreground">{formatFecha(viaje.created_at)}</p>
                    </div>
                  </div>
                )}
                {viaje.aceptado_en && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 mt-2 rounded-full bg-blue-500" />
                    <div>
                      <p className="font-medium">Aceptado</p>
                      <p className="text-sm text-muted-foreground">{formatFecha(viaje.aceptado_en)}</p>
                    </div>
                  </div>
                )}
                {viaje.iniciado_en && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 mt-2 rounded-full bg-purple-500" />
                    <div>
                      <p className="font-medium">Iniciado</p>
                      <p className="text-sm text-muted-foreground">{formatFecha(viaje.iniciado_en)}</p>
                    </div>
                  </div>
                )}
                {viaje.finalizado_en && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 mt-2 rounded-full bg-green-500" />
                    <div>
                      <p className="font-medium">Finalizado</p>
                      <p className="text-sm text-muted-foreground">{formatFecha(viaje.finalizado_en)}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="route">
          <Card>
            <CardHeader>
              <CardTitle>Ruta del Viaje</CardTitle>
            </CardHeader>
            <CardContent>
              <RouteMap
                origen={{
                  lat: viaje.origen_lat,
                  lng: viaje.origen_lng,
                  direccion: viaje.direccion_origen
                }}
                destino={{
                  lat: viaje.destino_lat,
                  lng: viaje.destino_lng,
                  direccion: viaje.direccion_destino
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}