'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Loader2, Package, Search } from 'lucide-react'
import { toast } from 'sonner'

export default function ObjetosOlvidadosPage() {
  const [formData, setFormData] = useState({
    viaje_id: '',
    descripcion: '',
    foto_url: '',
  })

  const { data: viajes } = useQuery({
    queryKey: ['viajes-completados'],
    queryFn: async () => {
      const response = await apiClient.get('/api/operativo/viajes/completados')
      return response.data
    },
  })

  const mutationReportar = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/objeto-olvidado', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Objeto reportado. El chofer será notificado.')
      setFormData({ viaje_id: '', descripcion: '', foto_url: '' })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al reportar objeto')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.viaje_id || !formData.descripcion) {
      toast.warning('Completa todos los campos obligatorios')
      return
    }
    mutationReportar.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Package className="h-6 w-6" />
          Objetos Olvidados
        </h1>
        <p className="text-muted-foreground">Reporta objetos perdidos en los viajes</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Formulario */}
        <Card>
          <CardHeader>
            <CardTitle>Reportar Objeto Olvidado</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Viaje *</Label>
                <Select
                  value={formData.viaje_id}
                  onValueChange={(value) => setFormData({ ...formData, viaje_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar viaje" />
                  </SelectTrigger>
                  <SelectContent>
                    {viajes?.map((viaje: any) => (
                      <SelectItem key={viaje.id} value={viaje.id}>
                        {viaje.pasajero_nombre || 'Sin nombre'} - {new Date(viaje.completado_at).toLocaleDateString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Descripción del objeto *</Label>
                <Textarea
                  placeholder="Ej: Billetera negra, Celular Samsung, Lentes de sol..."
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Foto (opcional)</Label>
                <Input
                  type="text"
                  placeholder="URL de la imagen"
                  value={formData.foto_url}
                  onChange={(e) => setFormData({ ...formData, foto_url: e.target.value })}
                />
              </div>

              <Button type="submit" className="w-full" disabled={mutationReportar.isPending}>
                {mutationReportar.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Reportando...
                  </>
                ) : (
                  'Reportar Objeto'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Historial */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Search className="h-4 w-4" />
              Historial de Reportes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <Package className="mx-auto h-12 w-12" />
              <p className="mt-2">No hay objetos reportados en este turno</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}