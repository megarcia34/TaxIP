'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  numero_licencia: string
}

export default function EditarVehiculoPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [formData, setFormData] = useState<Partial<Vehiculo>>({
    patente: '',
    marca: '',
    modelo: '',
    anio: undefined,
    numero_licencia: '',
  })

  const isAdmin = user?.rol === 'admin'
  const propietarioId = searchParams?.get('propietario_id')

  useEffect(() => {
    cargarVehiculo()
  }, [params.id])

  const cargarVehiculo = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/api/propietario/vehiculos/${params.id}`)
      const data = res.data
      setFormData({
        patente: data.patente,
        marca: data.marca,
        modelo: data.modelo,
        anio: data.anio,
        numero_licencia: data.numero_licencia,
      })
    } catch (error: any) {
      console.error('Error cargando vehículo:', error)
      toast.error(error.response?.data?.detail || 'Error al cargar el vehículo')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUpdating(true)

    try {
      await apiClient.put(`/api/propietario/vehiculos/${params.id}`, {
        patente: formData.patente?.toUpperCase(),
        marca: formData.marca,
        modelo: formData.modelo,
        anio: formData.anio ? parseInt(String(formData.anio)) : null,
        numero_licencia: formData.numero_licencia,
      })
      
      toast.success('Vehículo actualizado correctamente')
      
      const redirectPath = isAdmin && propietarioId 
        ? `/dashboard-propietario/vehiculos/${params.id}?propietario_id=${propietarioId}`
        : `/dashboard-propietario/vehiculos/${params.id}`
      router.push(redirectPath)
    } catch (error: any) {
      console.error('Error actualizando vehículo:', error)
      toast.error(error.response?.data?.detail || 'Error al actualizar el vehículo')
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos/${params.id}?propietario_id=${propietarioId}`
              : `/dashboard-propietario/vehiculos/${params.id}`
          }
        >
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Editar Vehículo</h1>
          <p className="text-muted-foreground">
            Modifica los datos del vehículo {formData.patente}
          </p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Datos del Vehículo</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="patente">Patente *</Label>
              <Input
                id="patente"
                required
                value={formData.patente}
                onChange={(e) => setFormData({ ...formData, patente: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input
                  id="marca"
                  required
                  value={formData.marca}
                  onChange={(e) => setFormData({ ...formData, marca: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Input
                  id="modelo"
                  required
                  value={formData.modelo}
                  onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anio">Año</Label>
                <Input
                  id="anio"
                  type="number"
                  value={formData.anio || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, anio: e.target.value ? parseInt(e.target.value) : undefined })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_licencia">Número de Licencia</Label>
                <Input
                  id="numero_licencia"
                  value={formData.numero_licencia || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, numero_licencia: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <Link
                href={
                  isAdmin && propietarioId
                    ? `/dashboard-propietario/vehiculos/${params.id}?propietario_id=${propietarioId}`
                    : `/dashboard-propietario/vehiculos/${params.id}`
                }
              >
                <Button type="button" variant="outline">
                  Cancelar
                </Button>
              </Link>
              <Button type="submit" disabled={updating}>
                {updating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Guardar Cambios
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}