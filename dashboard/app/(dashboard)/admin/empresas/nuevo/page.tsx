'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

export default function AdminNuevaEmpresaPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    nombre: '',
    tipo: 'hotel',
    email_facturacion: '',
    telefono: '',
    direccion: '',
    latitud: '',
    longitud: '',
  })

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.post('/api/empresa/registro', {
        nombre: data.nombre,
        tipo: data.tipo,
        email_facturacion: data.email_facturacion,
        telefono: data.telefono,
        direccion: data.direccion,
        latitud: parseFloat(data.latitud),
        longitud: parseFloat(data.longitud),
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa registrada correctamente')
      router.push('/admin/empresas')
    },
    onError: (error: any) => {
      console.error('Error:', error)
      toast.error(error.response?.data?.detail || 'Error al registrar la empresa')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nombre || !formData.email_facturacion || !formData.direccion || !formData.latitud || !formData.longitud) {
      toast.error('Complete los campos obligatorios')
      return
    }
    createMutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Nueva Empresa</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Registrar Empresa Corporativa</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="nombre">Nombre de la empresa *</Label>
                <Input
                  id="nombre"
                  placeholder="Hotel Ejecutivo"
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
                  placeholder="facturacion@empresa.com"
                  value={formData.email_facturacion}
                  onChange={(e) => setFormData({ ...formData, email_facturacion: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="telefono">Teléfono</Label>
                <Input
                  id="telefono"
                  placeholder="3811234567"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
              </div>
              
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="direccion">Dirección *</Label>
                <Input
                  id="direccion"
                  placeholder="Av. Principal 123"
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
                  placeholder="-26.8363"
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
                  placeholder="-65.2055"
                  value={formData.longitud}
                  onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-4">
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancelar
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Registrar Empresa
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}