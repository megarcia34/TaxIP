'use client'

import { useParams, useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

interface Empresa {
  id: string
  nombre: string
  tipo: string
  email_facturacion: string
  telefono: string
  direccion: string
  latitud: number
  longitud: number
  tarifa_preferencial: number
  activo: boolean
}

export default function AdminEmpresaEditarPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const empresaId = params.id as string
  const [formData, setFormData] = useState({
    nombre: '',
    tipo: '',
    email_facturacion: '',
    telefono: '',
    direccion: '',
    latitud: '',
    longitud: '',
    tarifa_preferencial: '',
    activo: true,
  })

  const { data: empresa, isLoading } = useQuery({
    queryKey: ['empresa', empresaId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/empresa/${empresaId}`)
      return response.data as Empresa
    },
    enabled: !!empresaId,
  })

  useEffect(() => {
    if (empresa) {
      setFormData({
        nombre: empresa.nombre || '',
        tipo: empresa.tipo || '',
        email_facturacion: empresa.email_facturacion || '',
        telefono: empresa.telefono || '',
        direccion: empresa.direccion || '',
        latitud: empresa.latitud?.toString() || '',
        longitud: empresa.longitud?.toString() || '',
        tarifa_preferencial: empresa.tarifa_preferencial?.toString() || '',
        activo: empresa.activo,
      })
    }
  }, [empresa])

  const updateMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.put(`/api/empresa/${empresaId}`, {
        nombre: data.nombre,
        tipo: data.tipo,
        email_facturacion: data.email_facturacion,
        telefono: data.telefono,
        direccion: data.direccion,
        latitud: parseFloat(data.latitud),
        longitud: parseFloat(data.longitud),
        tarifa_preferencial: parseFloat(data.tarifa_preferencial),
        activo: data.activo,
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa actualizada correctamente')
      queryClient.invalidateQueries({ queryKey: ['empresa', empresaId] })
      queryClient.invalidateQueries({ queryKey: ['admin-empresas'] })
      router.push(`/admin/empresas/${empresaId}`)
    },
    onError: () => {
      toast.error('Error al actualizar la empresa')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
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
        <h1 className="text-2xl font-bold tracking-tight">Editar Empresa</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Editar {empresa?.nombre}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nombre">Nombre *</Label>
                <Input
                  id="nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo</Label>
                <select
                  id="tipo"
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={formData.tipo}
                  onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                >
                  <option value="hotel">Hotel / Hospedaje</option>
                  <option value="empresa">Empresa</option>
                  <option value="institucion">Institución</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email_facturacion">Email Facturación *</Label>
                <Input
                  id="email_facturacion"
                  type="email"
                  value={formData.email_facturacion}
                  onChange={(e) => setFormData({ ...formData, email_facturacion: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="telefono">Teléfono</Label>
                <Input
                  id="telefono"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
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
                <Label htmlFor="latitud">Latitud *</Label>
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
                <Label htmlFor="tarifa_preferencial">Descuento (%)</Label>
                <Input
                  id="tarifa_preferencial"
                  type="number"
                  step="1"
                  value={formData.tarifa_preferencial}
                  onChange={(e) => setFormData({ ...formData, tarifa_preferencial: e.target.value })}
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