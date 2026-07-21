'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Loader2, XCircle, User, MapPin } from 'lucide-react'
import { toast } from 'sonner'

export default function CancelacionesPage() {
  const [viajeSeleccionado, setViajeSeleccionado] = useState<string | null>(null)
  const [motivo, setMotivo] = useState('')

  const { data: viajes, isLoading, refetch } = useQuery({
    queryKey: ['viajes-cancelables'],
    queryFn: async () => {
      const response = await apiClient.get('/api/operativo/viajes/cancelables')
      return response.data
    },
  })

  const mutationCancelar = useMutation({
    mutationFn: async ({ id, motivo }: { id: string; motivo: string }) => {
      const response = await apiClient.post(`/api/reservas/${id}/cancelar`, { motivo })
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Viaje cancelado correctamente')
      setViajeSeleccionado(null)
      setMotivo('')
      refetch()
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al cancelar')
    },
  })

  const handleCancelar = () => {
    if (!viajeSeleccionado || !motivo) {
      toast.warning('Selecciona un viaje y escribe el motivo')
      return
    }
    mutationCancelar.mutate({ id: viajeSeleccionado, motivo })
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <XCircle className="h-6 w-6" />
          Cancelaciones
        </h1>
        <p className="text-muted-foreground">Gestiona la cancelación de viajes en curso</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Lista de viajes cancelables */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Viajes Activos</CardTitle>
          </CardHeader>
          <CardContent>
            {viajes?.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No hay viajes para cancelar</p>
            ) : (
              <div className="space-y-3">
                {viajes?.map((viaje: any) => (
                  <div
                    key={viaje.id}
                    className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                      viajeSeleccionado === viaje.id ? 'border-primary bg-primary/5' : 'hover:bg-muted'
                    }`}
                    onClick={() => setViajeSeleccionado(viaje.id)}
                  >
                    <div className="flex justify-between">
                      <span className="font-medium">{viaje.pasajero_nombre || 'Sin nombre'}</span>
                      <Badge variant="outline">{viaje.estado}</Badge>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                      <MapPin className="h-3 w-3" />
                      <span className="truncate">{viaje.direccion_origen}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Formulario de cancelación */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Cancelar Viaje</CardTitle>
          </CardHeader>
          <CardContent>
            {!viajeSeleccionado ? (
              <p className="text-center text-muted-foreground py-8">
                Selecciona un viaje para cancelar
              </p>
            ) : (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Motivo de cancelación *</Label>
                  <Textarea
                    placeholder="¿Por qué se cancela el viaje?"
                    value={motivo}
                    onChange={(e) => setMotivo(e.target.value)}
                    rows={3}
                  />
                </div>
                <Button
                  variant="destructive"
                  className="w-full"
                  disabled={!motivo || mutationCancelar.isPending}
                  onClick={handleCancelar}
                >
                  {mutationCancelar.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Cancelando...
                    </>
                  ) : (
                    'Cancelar Viaje'
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}