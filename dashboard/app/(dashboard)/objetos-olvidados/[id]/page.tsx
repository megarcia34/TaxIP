'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Package, User, Calendar, MessageSquare, Loader2 } from 'lucide-react'

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    reportado: 'bg-yellow-500',
    encontrado: 'bg-blue-500',
    entregado: 'bg-green-500',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoTexto = (estado: string) => {
  const estados: Record<string, string> = {
    reportado: 'Reportado',
    encontrado: 'Encontrado',
    entregado: 'Entregado',
  }
  return estados[estado] || estado
}

export default function ObjetoDetallePage() {
  const params = useParams()
  const router = useRouter()
  const objetoId = params.id as string

  const { data: objeto, isLoading } = useQuery({
    queryKey: ['objeto-olvidado', objetoId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/viajes/objeto-olvidado/${objetoId}`)
      return response.data
    },
    enabled: !!objetoId,
  })

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!objeto) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Objeto no encontrado</p>
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
        <h1 className="text-2xl font-bold tracking-tight">Detalle del Objeto</h1>
        <Badge className={getEstadoColor(objeto.estado)}>
          {getEstadoTexto(objeto.estado)}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Información del Objeto</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Package className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Descripción</p>
                <p className="font-medium">{objeto.descripcion}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Fecha de reporte</p>
                <p className="font-medium">
                  {new Date(objeto.fecha_reporte).toLocaleString('es-AR')}
                </p>
              </div>
            </div>
            {objeto.fecha_entrega && (
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Fecha de entrega</p>
                  <p className="font-medium">
                    {new Date(objeto.fecha_entrega).toLocaleString('es-AR')}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Información del Viaje</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <User className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Pasajero</p>
                <p className="font-medium">{objeto.pasajero_nombre || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <User className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Chofer</p>
                <p className="font-medium">{objeto.chofer_nombre || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MessageSquare className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">ID del Viaje</p>
                <p className="font-mono text-sm">{objeto.viaje_id}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}