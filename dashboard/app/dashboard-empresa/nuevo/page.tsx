'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { ArrowLeft, Loader2, MapPin, Car } from 'lucide-react'
import Link from 'next/link'

export default function NuevoViajeEmpresaPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    direccion_origen: '',
    direccion_destino: '',
    origen_lat: '',
    origen_lng: '',
    destino_lat: '',
    destino_lng: '',
    nombre_pasajero: '',
    notas: '',
  })

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      const payload = {
        ...data,
        origen_lat: parseFloat(data.origen_lat),
        origen_lng: parseFloat(data.origen_lng),
        destino_lat: parseFloat(data.destino_lat),
        destino_lng: parseFloat(data.destino_lng),
      }
      const response = await apiClient.post('/api/empresa/dashboard/viajes/solicitar', payload)
      return response.data
    },
    onSuccess: () => {
      toast.success('Viaje solicitado exitosamente')
      router.push('/dashboard-empresa/viajes')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al solicitar el viaje'
      toast.error(message)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.direccion_origen || !formData.direccion_destino) {
      toast.error('La dirección de origen y destino son requeridas')
      return
    }
    
    if (!formData.origen_lat || !formData.origen_lng || !formData.destino_lat || !formData.destino_lng) {
      toast.error('Las coordenadas son requeridas')
      return
    }

    mutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard-empresa/viajes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Solicitar Viaje Corporativo</h1>
          <p className="text-muted-foreground">
            Complete los datos para solicitar un viaje para la empresa
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Datos del Viaje</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="nombre_pasajero">Nombre del Pasajero</Label>
                <Input
                  id="nombre_pasajero"
                  value={formData.nombre_pasajero}
                  onChange={(e) => setFormData({ ...formData, nombre_pasajero: e.target.value })}
                  placeholder="Nombre de la persona que viaja"
                />
              </div>

              <div className="border rounded-lg p-4 space-y-4">
                <h3 className="font-medium flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-blue-500" />
                  Origen
                </h3>
                <div>
                  <Label htmlFor="direccion_origen">Dirección *</Label>
                  <Input
                    id="direccion_origen"
                    value={formData.direccion_origen}
                    onChange={(e) => setFormData({ ...formData, direccion_origen: e.target.value })}
                    placeholder="Ej: Av. Corrientes 1234"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="origen_lat">Latitud *</Label>
                    <Input
                      id="origen_lat"
                      type="number"
                      step="any"
                      value={formData.origen_lat}
                      onChange={(e) => setFormData({ ...formData, origen_lat: e.target.value })}
                      placeholder="-34.6037"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="origen_lng">Longitud *</Label>
                    <Input
                      id="origen_lng"
                      type="number"
                      step="any"
                      value={formData.origen_lng}
                      onChange={(e) => setFormData({ ...formData, origen_lng: e.target.value })}
                      placeholder="-58.3816"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="border rounded-lg p-4 space-y-4">
                <h3 className="font-medium flex items-center gap-2">
                  <Car className="h-4 w-4 text-green-500" />
                  Destino
                </h3>
                <div>
                  <Label htmlFor="direccion_destino">Dirección *</Label>
                  <Input
                    id="direccion_destino"
                    value={formData.direccion_destino}
                    onChange={(e) => setFormData({ ...formData, direccion_destino: e.target.value })}
                    placeholder="Ej: Av. 9 de Julio 1234"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="destino_lat">Latitud *</Label>
                    <Input
                      id="destino_lat"
                      type="number"
                      step="any"
                      value={formData.destino_lat}
                      onChange={(e) => setFormData({ ...formData, destino_lat: e.target.value })}
                      placeholder="-34.6037"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="destino_lng">Longitud *</Label>
                    <Input
                      id="destino_lng"
                      type="number"
                      step="any"
                      value={formData.destino_lng}
                      onChange={(e) => setFormData({ ...formData, destino_lng: e.target.value })}
                      placeholder="-58.3816"
                      required
                    />
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="notas">Notas (Opcional)</Label>
                <Textarea
                  id="notas"
                  value={formData.notas}
                  onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                  placeholder="Información adicional para el conductor"
                  rows={3}
                />
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/dashboard-empresa/viajes')}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Solicitar Viaje
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}