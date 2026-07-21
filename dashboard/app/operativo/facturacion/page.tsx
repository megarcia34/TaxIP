'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loader2, Wallet, DollarSign, User, MapPin, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'sonner'

interface ViajeFacturacion {
  id: string
  pasajero_nombre: string
  direccion_origen: string
  direccion_destino: string
  precio_final: number
  centro_costo: string | null
  completado_at: string
}

export default function FacturacionPage() {
  const [centroCosto, setCentroCosto] = useState<Record<string, string>>({})

  const { data: viajes, isLoading, refetch } = useQuery({
    queryKey: ['viajes-facturacion'],
    queryFn: async () => {
      const response = await apiClient.get('/api/operativo/viajes/facturacion')
      return response.data
    },
  })

  const mutationAsignar = useMutation({
    mutationFn: async ({ viajeId, centro }: { viajeId: string; centro: string }) => {
      const response = await apiClient.patch(`/api/viajes/${viajeId}/centro-costo`, {
        centro_costo: centro,
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Centro de costo asignado')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al asignar')
    },
  })

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const sinAsignar = viajes?.filter((v: ViajeFacturacion) => !v.centro_costo) || []
  const asignados = viajes?.filter((v: ViajeFacturacion) => v.centro_costo) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Wallet className="h-6 w-6" />
          Facturación Operativa
        </h1>
        <p className="text-muted-foreground">Asigna centros de costo a los viajes completados</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Viajes sin asignar */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" />
              Sin Asignar ({sinAsignar.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
            {sinAsignar.length === 0 ? (
              <p className="text-muted-foreground text-sm text-center py-4">
                Todos los viajes tienen centro de costo asignado
              </p>
            ) : (
              sinAsignar.map((viaje: ViajeFacturacion) => (
                <div key={viaje.id} className="border-b pb-3">
                  <div className="flex justify-between">
                    <span className="font-medium">{viaje.pasajero_nombre || 'Sin nombre'}</span>
                    <span className="text-sm font-semibold text-primary">
                      ${viaje.precio_final?.toFixed(2) || '0'}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{viaje.direccion_origen}</p>
                  <div className="flex gap-2 mt-2">
                    <Input
                      placeholder="Ej: Habitación 304"
                      className="flex-1 text-sm"
                      value={centroCosto[viaje.id] || ''}
                      onChange={(e) => setCentroCosto(prev => ({
                        ...prev,
                        [viaje.id]: e.target.value
                      }))}
                    />
                    <Button
                      size="sm"
                      disabled={!centroCosto[viaje.id] || mutationAsignar.isPending}
                      onClick={() => {
                        if (centroCosto[viaje.id]) {
                          mutationAsignar.mutate({
                            viajeId: viaje.id,
                            centro: centroCosto[viaje.id]
                          })
                        }
                      }}
                    >
                      Asignar
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Viajes asignados */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              Asignados ({asignados.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
            {asignados.length === 0 ? (
              <p className="text-muted-foreground text-sm text-center py-4">
                No hay viajes con centro de costo asignado
              </p>
            ) : (
              asignados.map((viaje: ViajeFacturacion) => (
                <div key={viaje.id} className="border-b pb-3">
                  <div className="flex justify-between">
                    <span className="font-medium">{viaje.pasajero_nombre || 'Sin nombre'}</span>
                    <span className="text-sm font-semibold text-primary">
                      ${viaje.precio_final?.toFixed(2) || '0'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {viaje.centro_costo}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(viaje.completado_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}