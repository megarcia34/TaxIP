'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loader2, Calendar, Clock, User, MapPin, ChevronLeft, ChevronRight } from 'lucide-react'
import Link from 'next/link'

interface Reserva {
  id: string
  pasajero_nombre: string
  direccion_origen: string
  direccion_destino: string
  tipo_vehiculo: string
  estado: string
  fecha_programada: string
  precio_estimado: number
}

export default function ReservasPage() {
  const [fecha, setFecha] = useState(new Date())
  const [view, setView] = useState<'dia' | 'mes'>('dia')

  // 🔥 CORREGIDO: Ahora usa /reservas (coincide con el backend)
  const { data: reservas, isLoading } = useQuery({
    queryKey: ['reservas', fecha.toISOString().split('T')[0]],
    queryFn: async () => {
      const response = await apiClient.get('/reservas', {
        params: {
          fecha: fecha.toISOString().split('T')[0],
        },
      })
      return response.data
    },
  })

  const cambiarFecha = (dias: number) => {
    const nuevaFecha = new Date(fecha)
    nuevaFecha.setDate(nuevaFecha.getDate() + dias)
    setFecha(nuevaFecha)
  }

  const getEstadoBadge = (estado: string) => {
  const estados: Record<string, { label: string, className: string }> = {
    'pendiente': { label: 'Pendiente', className: 'bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-200' },
    'confirmada': { label: 'Confirmada', className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-200' },
    'en_curso': { label: 'En curso', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200' },
    'completada': { label: 'Completada', className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200' },
    'cancelada': { label: 'Cancelada', className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-200' },
  }
  const info = estados[estado] || { label: estado, className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200' }
  return <Badge className={info.className}>{info.label}</Badge>
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
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Calendar className="h-6 w-6" />
          Agenda de Reservas
        </h1>
        <p className="text-muted-foreground">Viajes programados para hoy y próximos días</p>
      </div>

      {/* Controles de fecha */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => cambiarFecha(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="font-semibold">
            {fecha.toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </span>
          <Button variant="outline" size="sm" onClick={() => cambiarFecha(1)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => setFecha(new Date())}>
            Hoy
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant={view === 'dia' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setView('dia')}
          >
            Día
          </Button>
          <Button 
            variant={view === 'mes' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setView('mes')}
          >
            Mes
          </Button>
        </div>
      </div>

      {/* Lista de reservas */}
      <div className="space-y-4">
        {reservas?.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Calendar className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="text-muted-foreground mt-2">No hay reservas para esta fecha</p>
              <Link href="/operativo/nueva-solicitud">
                <Button className="mt-4">Crear nueva solicitud</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          reservas?.map((reserva: Reserva) => (
            <Card key={reserva.id}>
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{reserva.pasajero_nombre || 'No especificado'}</span>
                      </div>
                      {getEstadoBadge(reserva.estado)}
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(reserva.fecha_programada).toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row gap-2 text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-3 w-3 text-green-500" />
                        <span className="truncate max-w-[200px]">{reserva.direccion_origen}</span>
                      </div>
                      <span className="text-muted-foreground hidden sm:inline">→</span>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-3 w-3 text-red-500" />
                        <span className="truncate max-w-[200px]">{reserva.direccion_destino}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-primary">
                      ${reserva.precio_estimado?.toFixed(2) || '0'}
                    </span>
                    <Link href={`/operativo/solicitudes/${reserva.id}`}>
                      <Button variant="outline" size="sm">
                        Ver
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}