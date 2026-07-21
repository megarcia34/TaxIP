'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, FileText, CheckCircle, XCircle, Car, DollarSign } from 'lucide-react'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'

interface ReporteTurno {
  total_viajes: number
  completados: number
  cancelados: number
  facturado_total: number
  promedio_viaje: number
  tiempo_turno: string
  viajes: Array<{
    id: string
    pasajero_nombre: string
    estado: string
    precio_final: number
    centro_costo: string
  }>
}

export default function CierreTurnoPage() {
  const router = useRouter()
  const [cerrando, setCerrando] = useState(false)

  const { data: reporte, isLoading, refetch } = useQuery({
    queryKey: ['reporte-turno'],
    queryFn: async () => {
      const response = await apiClient.get('/api/operativo/reporte/turno')
      return response.data as ReporteTurno
    },
  })

  const mutationCerrarTurno = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/api/empleado/turnos/check-out', {})
      return response.data
    },
    onSuccess: () => {
      toast.success('✅ Turno cerrado correctamente')
      router.push('/operativo')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al cerrar turno')
      setCerrando(false)
    },
  })

  const handleCerrarTurno = () => {
    if (confirm('¿Estás seguro que deseas cerrar el turno?')) {
      setCerrando(true)
      mutationCerrarTurno.mutate()
    }
  }

  // ✅ Función para renderizar Badge con className en lugar de variant
  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string, className: string }> = {
      'completado': {
        label: 'Completado',
        className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-200'
      },
      'cancelado': {
        label: 'Cancelado',
        className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-200'
      },
      'en_curso': {
        label: 'En curso',
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200'
      },
      'pendiente': {
        label: 'Pendiente',
        className: 'bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-200'
      }
    }
    const info = estados[estado] || {
      label: estado || 'Desconocido',
      className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200'
    }
    return <Badge className={info.className}>{info.label}</Badge>
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!reporte) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No hay datos del turno</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-6 w-6" />
          Cierre de Turno
        </h1>
        <p className="text-muted-foreground">Resumen completo de tu jornada laboral</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Viajes</p>
                <p className="text-2xl font-bold">{reporte.total_viajes}</p>
              </div>
              <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                <Car className="h-5 w-5 text-blue-600 dark:text-blue-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Completados</p>
                <p className="text-2xl font-bold text-green-600">{reporte.completados}</p>
              </div>
              <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Cancelados</p>
                <p className="text-2xl font-bold text-red-600">{reporte.cancelados}</p>
              </div>
              <div className="rounded-full bg-red-100 p-3 dark:bg-red-900">
                <XCircle className="h-5 w-5 text-red-600 dark:text-red-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Facturado Total</p>
                <p className="text-2xl font-bold text-primary">
                  ${reporte.facturado_total.toFixed(2)}
                </p>
              </div>
              <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
                <DollarSign className="h-5 w-5 text-yellow-600 dark:text-yellow-300" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detalle del turno */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Resumen del Turno</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between border-b py-2">
              <span className="text-muted-foreground">Duración</span>
              <span className="font-medium">{reporte.tiempo_turno}</span>
            </div>
            <div className="flex justify-between border-b py-2">
              <span className="text-muted-foreground">Promedio por viaje</span>
              <span className="font-medium">${reporte.promedio_viaje.toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b py-2">
              <span className="text-muted-foreground">Tasa de completitud</span>
              <span className="font-medium">
                {reporte.total_viajes > 0 
                  ? Math.round((reporte.completados / reporte.total_viajes) * 100)
                  : 0}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Acciones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full" 
              size="lg"
              onClick={handleCerrarTurno}
              disabled={cerrando}
            >
              {cerrando ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Cerrando turno...
                </>
              ) : (
                'Cerrar Turno'
              )}
            </Button>
            <Button variant="outline" className="w-full">
              Descargar Reporte PDF
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Lista de viajes */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Viajes Gestionados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Pasajero</th>
                  <th className="text-left py-2">Estado</th>
                  <th className="text-right py-2">Precio</th>
                  <th className="text-left py-2">Centro de Costo</th>
                </tr>
              </thead>
              <tbody>
                {reporte.viajes.map((viaje) => (
                  <tr key={viaje.id} className="border-b">
                    <td className="py-2">{viaje.pasajero_nombre || 'Sin nombre'}</td>
                    <td className="py-2">
                      {/* ✅ CORREGIDO: Usa getEstadoBadge en lugar de variant */}
                      {getEstadoBadge(viaje.estado)}
                    </td>
                    <td className="py-2 text-right">${viaje.precio_final?.toFixed(2) || '0'}</td>
                    <td className="py-2">{viaje.centro_costo || 'Sin asignar'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}