'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2, MapPin, User, Car, Clock, DollarSign, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { PipelineEstados } from '@/components/operativo/PipelineEstados'

interface SolicitudDetalle {
  id: string
  pasajero_nombre: string
  pasajero_telefono: string
  direccion_origen: string
  latitud_origen: number
  longitud_origen: number
  direccion_destino: string
  latitud_destino: number
  longitud_destino: number
  tipo_vehiculo: string
  estado: string
  precio_estimado: number
  precio_final: number
  metodo_pago: string
  created_at: string
  centro_costo: string
  nota_conductor: string
}

export default function SolicitudDetallePage() {
  const params = useParams()
  const router = useRouter()
  const [centroCosto, setCentroCosto] = useState('')

  const { data: solicitud, isLoading, refetch } = useQuery({
    queryKey: ['solicitud', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/reservas/${params.id}`)
      return response.data as SolicitudDetalle
    },
  })

  const mutationActualizarEstado = useMutation({
    mutationFn: async (estado: string) => {
      const response = await apiClient.patch(`/api/reservas/${params.id}/estado?estado=${estado}`, {})
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Estado actualizado correctamente')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al actualizar estado')
    },
  })

  const mutationAsignarCentroCosto = useMutation({
    mutationFn: async () => {
      const response = await apiClient.patch(`/api/viajes/${params.id}/centro-costo`, {
        centro_costo: centroCosto,
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Centro de costo asignado correctamente')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al asignar centro de costo')
    },
  })

  const handleCambioEstado = (estado: string) => {
    mutationActualizarEstado.mutate(estado)
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!solicitud) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Solicitud no encontrada</p>
        <Link href="/operativo/solicitudes">
          <Button className="mt-4">Volver a solicitudes</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/operativo/solicitudes">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Detalle de Solicitud</h1>
          <Badge>{solicitud.estado}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">ID: {solicitud.id.substring(0, 8)}</span>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Información del viaje */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Información del Viaje</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Pasajero</p>
                <p className="font-medium">{solicitud.pasajero_nombre || 'No especificado'}</p>
                {solicitud.pasajero_telefono && (
                  <p className="text-sm">{solicitud.pasajero_telefono}</p>
                )}
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Tipo de Vehículo</p>
                <p className="font-medium capitalize">{solicitud.tipo_vehiculo}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <MapPin className="h-3 w-3 text-green-500" />
                Origen
              </p>
              <p className="font-medium">{solicitud.direccion_origen}</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <MapPin className="h-3 w-3 text-red-500" />
                Destino
              </p>
              <p className="font-medium">{solicitud.direccion_destino}</p>
            </div>

            {solicitud.nota_conductor && (
              <div>
                <p className="text-sm text-muted-foreground">Notas para el conductor</p>
                <p className="text-sm">{solicitud.nota_conductor}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Panel de acciones */}
        <Card>
          <CardHeader>
            <CardTitle>Acciones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Estado actual</p>
              <p className="text-lg font-semibold capitalize">{solicitud.estado}</p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Cambiar estado</p>
              <div className="flex flex-wrap gap-2">
                {solicitud.estado === 'reservado' && (
                  <Button size="sm" onClick={() => handleCambioEstado('despachado')}>
                    Despachar
                  </Button>
                )}
                {solicitud.estado === 'despachado' && (
                  <Button size="sm" onClick={() => handleCambioEstado('vehiculo_llego')}>
                    Vehículo llegó
                  </Button>
                )}
                {solicitud.estado === 'vehiculo_llego' && (
                  <Button size="sm" onClick={() => handleCambioEstado('pasajero_a_bordo')}>
                    Pasajero a bordo
                  </Button>
                )}
                {solicitud.estado === 'pasajero_a_bordo' && (
                  <Button size="sm" onClick={() => handleCambioEstado('completado')}>
                    Completar viaje
                  </Button>
                )}
                {!['completado', 'cancelado'].includes(solicitud.estado) && (
                  <Button size="sm" variant="destructive" onClick={() => handleCambioEstado('cancelado')}>
                    Cancelar
                  </Button>
                )}
              </div>
            </div>

            <hr />

            <div>
              <p className="text-sm text-muted-foreground">Centro de Costo</p>
              <p className="font-medium">{solicitud.centro_costo || 'No asignado'}</p>
              {!solicitud.centro_costo && (
                <div className="mt-2 flex gap-2">
                  <Input
                    placeholder="Ej: Habitación 304"
                    value={centroCosto}
                    onChange={(e) => setCentroCosto(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    size="sm"
                    disabled={!centroCosto || mutationAsignarCentroCosto.isPending}
                    onClick={() => mutationAsignarCentroCosto.mutate()}
                  >
                    Asignar
                  </Button>
                </div>
              )}
            </div>

            <hr />

            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Precio estimado</span>
              <span className="font-semibold">${solicitud.precio_estimado?.toFixed(2) || '0'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Método de pago</span>
              <span className="capitalize">{solicitud.metodo_pago}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Creado</span>
              <span className="text-sm">{new Date(solicitud.created_at).toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline de estados */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline del Viaje</CardTitle>
        </CardHeader>
        <CardContent>
          <PipelineEstados estado={solicitud.estado} />
        </CardContent>
      </Card>
    </div>
  )
}