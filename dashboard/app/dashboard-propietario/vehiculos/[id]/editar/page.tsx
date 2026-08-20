'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useVehiculo, useUpdateVehiculo } from '@/hooks/useVehiculos'

export default function EditarVehiculoPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const vehiculoId = params.id as string
  const [propietario_id, setPropietario_id] = useState<string | null>(null)

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search)
    setPropietario_id(searchParams.get('propietario_id'))
  }, [])

  const isAdmin = user?.rol === 'admin'
  const propietarioId = propietario_id

  const { data: vehiculo, isLoading } = useVehiculo(vehiculoId)
  const updateMutation = useUpdateVehiculo()

  const [formData, setFormData] = useState({
    patente: '',
    marca: '',
    modelo: '',
    anio: '',
    numero_licencia: '',
  })

  useEffect(() => {
    if (vehiculo) {
      setFormData({
        patente: vehiculo.patente || '',
        marca: vehiculo.marca || '',
        modelo: vehiculo.modelo || '',
        anio: vehiculo.anio?.toString() || '',
        numero_licencia: vehiculo.numero_licencia || '',
      })
    }
  }, [vehiculo])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.patente || !formData.marca || !formData.modelo) {
      toast.error('Completa todos los campos obligatorios')
      return
    }

    updateMutation.mutate(
      {
        id: vehiculoId,
        data: {
          patente: formData.patente.toUpperCase(),
          marca: formData.marca,
          modelo: formData.modelo,
          anio: formData.anio ? parseInt(formData.anio) : null,
          numero_licencia: formData.numero_licencia || null,
        },
      },
      {
        onSuccess: () => {
          const redirectPath =
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos/${vehiculoId}?propietario_id=${propietarioId}`
              : `/dashboard-propietario/vehiculos/${vehiculoId}`
          router.push(redirectPath)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!vehiculo) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Vehículo no encontrado</p>
        <Button className="mt-4" onClick={() => router.push('/dashboard-propietario/vehiculos')}>
          Volver
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos/${vehiculoId}?propietario_id=${propietarioId}`
              : `/dashboard-propietario/vehiculos/${vehiculoId}`
          }
        >
          <Button variant="outline" size="icon" type="button">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Editar Vehículo</h1>
          <p className="text-muted-foreground">Modifica los datos del vehículo {vehiculo.patente}</p>
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
                placeholder="Ej: ABC123"
                value={formData.patente}
                onChange={(e) => setFormData({ ...formData, patente: e.target.value.toUpperCase() })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input
                  id="marca"
                  required
                  placeholder="Ej: Toyota"
                  value={formData.marca}
                  onChange={(e) => setFormData({ ...formData, marca: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Input
                  id="modelo"
                  required
                  placeholder="Ej: Corolla"
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
                  placeholder="Ej: 2024"
                  min="1900"
                  max="2100"
                  value={formData.anio}
                  onChange={(e) => setFormData({ ...formData, anio: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_licencia">Número de Licencia</Label>
                <Input
                  id="numero_licencia"
                  placeholder="Ej: LIC-123456"
                  value={formData.numero_licencia}
                  onChange={(e) => setFormData({ ...formData, numero_licencia: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t">
              <Link
                href={
                  isAdmin && propietarioId
                    ? `/dashboard-propietario/vehiculos/${vehiculoId}?propietario_id=${propietarioId}`
                    : `/dashboard-propietario/vehiculos/${vehiculoId}`
                }
              >
                <Button type="button" variant="outline">
                  Cancelar
                </Button>
              </Link>
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