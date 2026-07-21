'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Loader2, 
  Car, 
  User, 
  MapPin, 
  Clock,
  Eye,
  Filter,
  Search
} from 'lucide-react'
import Link from 'next/link'
import { PipelineEstados } from '@/components/operativo/PipelineEstados'

interface Solicitud {
  id: string
  pasajero_nombre: string
  direccion_origen: string
  direccion_destino: string
  tipo_vehiculo: string
  estado: string
  precio_estimado: number
  created_at: string
}

export default function SolicitudesPage() {
  const [estadoFilter, setEstadoFilter] = useState('todos')
  const [searchTerm, setSearchTerm] = useState('')

  const { data: solicitudes, isLoading } = useQuery({
    queryKey: ['solicitudes-turno', estadoFilter, searchTerm],
    queryFn: async () => {
      const response = await apiClient.get('/api/reservas', {
        params: {
          estado: estadoFilter !== 'todos' ? estadoFilter : undefined,
          search: searchTerm || undefined,
        },
      })
      return response.data
    },
  })

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
          <Car className="h-6 w-6" />
          Solicitudes Activas
        </h1>
        <p className="text-muted-foreground">Monitorea los viajes en curso de tu turno</p>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={estadoFilter} onValueChange={setEstadoFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos</SelectItem>
              <SelectItem value="reservado">Reservado</SelectItem>
              <SelectItem value="despachado">Despachado</SelectItem>
              <SelectItem value="vehiculo_llego">Vehículo llegó</SelectItem>
              <SelectItem value="pasajero_a_bordo">Pasajero a bordo</SelectItem>
              <SelectItem value="completado">Completado</SelectItem>
              <SelectItem value="cancelado">Cancelado</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex-1 max-w-sm">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por pasajero..."
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Lista de solicitudes */}
      <div className="space-y-4">
        {solicitudes?.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No hay solicitudes en este turno</p>
            </CardContent>
          </Card>
        ) : (
          solicitudes?.map((solicitud: Solicitud) => (
            <Card key={solicitud.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{solicitud.pasajero_nombre || 'No especificado'}</span>
                      </div>
                      {getEstadoBadge(solicitud.estado)}
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(solicitud.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row gap-2 text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-3 w-3 text-green-500" />
                        <span className="truncate max-w-[200px]">{solicitud.direccion_origen}</span>
                      </div>
                      <span className="text-muted-foreground hidden sm:inline">→</span>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-3 w-3 text-red-500" />
                        <span className="truncate max-w-[200px]">{solicitud.direccion_destino}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-primary">
                      ${solicitud.precio_estimado?.toFixed(2) || '0'}
                    </span>
                    <Link href={`/operativo/solicitudes/${solicitud.id}`}>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        Ver
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Pipeline de estados */}
                <div className="mt-4 pt-4 border-t">
                  <PipelineEstados estado={solicitud.estado} />
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}