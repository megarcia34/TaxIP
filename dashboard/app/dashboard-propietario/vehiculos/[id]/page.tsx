'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Loader2, Car, Calendar, User, Key } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  numero_licencia: string
  activo: boolean
  chofer_actual: string | null
}

export default function VehiculoDetailPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const [vehiculo, setVehiculo] = useState<Vehiculo | null>(null)
  const [loading, setLoading] = useState(true)
  const [updatingKm, setUpdatingKm] = useState(false)
  const [kilometraje, setKilometraje] = useState('')

  const isAdmin = user?.rol === 'admin'
  const propietarioId = searchParams?.get('propietario_id')

  useEffect(() => {
    cargarVehiculo()
  }, [params.id])

  const cargarVehiculo = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/api/propietario/vehiculos/${params.id}`)
      setVehiculo(res.data)
    } catch (error: any) {
      console.error('Error cargando vehículo:', error)
      toast.error(error.response?.data?.detail || 'Error al cargar el vehículo')
    } finally {
      setLoading(false)
    }
  }

  const actualizarKilometraje = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!kilometraje) return

    setUpdatingKm(true)
    try {
      await apiClient.put(`/api/propietario/vehiculos/${params.id}/kilometraje`, {
        kilometraje: parseInt(kilometraje),
      })
      
      toast.success('Kilometraje actualizado correctamente')
      setKilometraje('')
      cargarVehiculo()
    } catch (error: any) {
      console.error('Error actualizando kilometraje:', error)
      toast.error(error.response?.data?.detail || 'Error al actualizar kilometraje')
    } finally {
      setUpdatingKm(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!vehiculo) {
    return (
      <div className="text-center py-12">
        <Car className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-muted-foreground">Vehículo no encontrado</p>
        <Link
          href={
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
              : '/dashboard-propietario/vehiculos'
          }
        >
          <Button className="mt-4">Volver</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
              : '/dashboard-propietario/vehiculos'
          }
        >
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{vehiculo.patente}</h1>
          <p className="text-muted-foreground">
            {vehiculo.marca} {vehiculo.modelo} - {vehiculo.anio || 'Año no especificado'}
          </p>
        </div>
        <Badge className={vehiculo.activo ? 'bg-green-500' : 'bg-red-500'}>
          {vehiculo.activo ? 'Activo' : 'Inactivo'}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Información del Vehículo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Patente</Label>
                <p className="font-medium">{vehiculo.patente}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Marca</Label>
                <p className="font-medium">{vehiculo.marca}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Modelo</Label>
                <p className="font-medium">{vehiculo.modelo}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Año</Label>
                <p className="font-medium">{vehiculo.anio || 'N/A'}</p>
              </div>
              <div className="col-span-2">
                <Label className="text-muted-foreground">Número de Licencia</Label>
                <p className="font-medium">{vehiculo.numero_licencia || 'N/A'}</p>
              </div>
              <div className="col-span-2">
                <Label className="text-muted-foreground">Chofer Actual</Label>
                <p className="font-medium">{vehiculo.chofer_actual || 'Sin asignar'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Actualizar Kilometraje</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={actualizarKilometraje} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="kilometraje">Kilometraje Actual</Label>
                <Input
                  id="kilometraje"
                  type="number"
                  placeholder="Ingresa el kilometraje actual"
                  value={kilometraje}
                  onChange={(e) => setKilometraje(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" disabled={updatingKm}>
                {updatingKm && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Actualizar Kilometraje
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}