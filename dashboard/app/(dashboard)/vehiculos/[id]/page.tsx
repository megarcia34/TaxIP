'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { vehiculosAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Car, Calendar, User, QrCode } from 'lucide-react'
import { toast } from 'sonner'

export default function VehiculoDetallePage() {
  const params = useParams()
  const router = useRouter()
  const vehiculoId = params.id as string

  const { data: vehiculo, isLoading } = useQuery({
    queryKey: ['vehiculo', vehiculoId],
    queryFn: () => vehiculosAPI.getOne(vehiculoId),
    enabled: !!vehiculoId,
  })

  const handleGenerarQR = async () => {
    try {
      await vehiculosAPI.generarQR(vehiculoId)
      toast.success('QR generado correctamente')
    } catch (error) {
      toast.error('Error al generar el QR')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!vehiculo) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Vehículo no encontrado</p>
        <Button className="mt-4" onClick={() => router.back()}>Volver</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">
            {vehiculo.marca} {vehiculo.modelo}
          </h1>
          <Badge className={vehiculo.activo ? 'bg-green-500' : 'bg-red-500'}>
            {vehiculo.activo ? 'Activo' : 'Inactivo'}
          </Badge>
        </div>
        <Button variant="outline" onClick={handleGenerarQR}>
          <QrCode className="h-4 w-4 mr-2" />
          Generar QR
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Información del Vehículo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Car className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Patente</p>
                <p className="font-mono font-medium text-lg">{vehiculo.patente || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Car className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Marca / Modelo</p>
                <p className="font-medium">{vehiculo.marca} {vehiculo.modelo}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Año</p>
                <p className="font-medium">{vehiculo.anio || 'No especificado'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Asignación</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <User className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Chofer asignado</p>
                <p className="font-medium">{vehiculo.chofer_nombre || 'Sin asignar'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}