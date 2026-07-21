'use client'

import { useParams, useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2, MapPin } from 'lucide-react'
import { toast } from 'sonner'

interface Comercio {
  id: string
  nombre: string
  rubro: string
  direccion: string
  latitud: number
  longitud: number
  email_contacto: string
  telefono: string
  activo: boolean
}

export default function AdminComercioEditarPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const comercioId = params.id as string
  const [formData, setFormData] = useState({
    nombre: '',
    rubro: '',
    direccion: '',
    latitud: '',
    longitud: '',
    email_contacto: '',
    telefono: '',
    activo: true,
  })

  const { data: comercio, isLoading } = useQuery({
    queryKey: ['comercio', comercioId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/comercio/${comercioId}`)
      return response.data as Comercio
    },
    enabled: !!comercioId,
  })

  useEffect(() => {
    if (comercio) {
      setFormData({
        nombre: comercio.nombre || '',
        rubro: comercio.rubro || '',
        direccion: comercio.direccion || '',
        latitud: comercio.latitud?.toString() || '',
        longitud: comercio.longitud?.toString() || '',
        email_contacto: comercio.email_contacto || '',
        telefono: comercio.telefono || '',
        activo: comercio.activo,
      })
    }
  }, [comercio])

  const updateMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.put(`/api/comercio/${comercioId}`, {
        nombre: data.nombre,
        rubro: data.rubro,
        direccion: data.direccion,
        latitud: parseFloat(data.latitud),
        longitud: parseFloat(data.longitud),
        email_contacto: data.email_contacto,
        telefono: data.telefono,
        activo: data.activo,
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('Comercio actualizado correctamente')
      queryClient.invalidateQueries({ queryKey: ['comercio', comercioId] })
      queryClient.invalidateQueries({ queryKey: ['admin-comercios'] })
      router.push(`/admin/comercios/${comercioId}`)
    },
    onError: () => {
      toast.error('Error al actualizar el comercio')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nombre || !formData.direccion || !formData.latitud || !formData.longitud) {
      toast.error('Complete los campos obligatorios')
      return
    }
    updateMutation.mutate(formData)
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
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Editar Comercio</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Editar {comercio?.nombre}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="nombre">Nombre del comercio *</Label>
                <Input
                  id="nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="rubro">Rubro</Label>
                <select
                  id="rubro"
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={formData.rubro}
                  onChange={(e) => setFormData({ ...formData, rubro: e.target.value })}
                >
                  <option value="">Seleccionar rubro</option>
                  <option value="restaurante">Restaurante / Bar</option>
                  <option value="hotel">Hotel / Hospedaje</option>
                  <option value="comercio">Comercio / Tienda</option>
                  <option value="oficina">Oficina / Empresa</option>
                  <option value="turismo">Punto turístico</option>
                  <option value="evento">Salón de eventos</option>
                  <option value="otro">Otro</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="telefono">Teléfono</Label>
                <Input
                  id="telefono"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email_contacto">Email de contacto</Label>
                <Input
                  id="email_contacto"
                  type="email"
                  value={formData.email_contacto}
                  onChange={(e) => setFormData({ ...formData, email_contacto: e.target.value })}
                />
              </div>
              
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="direccion">Dirección *</Label>
                <Input
                  id="direccion"
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="latitud" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Latitud *
                </Label>
                <Input
                  id="latitud"
                  type="number"
                  step="0.000001"
                  value={formData.latitud}
                  onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="longitud">Longitud *</Label>
                <Input
                  id="longitud"
                  type="number"
                  step="0.000001"
                  value={formData.longitud}
                  onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="activo">Estado</Label>
                <select
                  id="activo"
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={formData.activo ? 'true' : 'false'}
                  onChange={(e) => setFormData({ ...formData, activo: e.target.value === 'true' })}
                >
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-4">
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancelar
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Guardar Cambios
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}