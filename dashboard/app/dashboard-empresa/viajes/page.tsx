'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Search, 
  Eye, 
  Loader2,
  Plus,
  Calendar
} from 'lucide-react'
import Link from 'next/link'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface ViajeEmpresa {
  id: string
  estado: string
  origen: string
  destino: string
  precio_final: number
  created_at: string
  finalizado_en: string
  pasajero_nombre: string
  chofer_nombre: string
  patente: string
  distancia_metros: number
  tiempo_estimado: number
}

const formatFecha = (fecha: string | undefined | null) => {
  if (!fecha) return 'N/A'
  try {
    return format(new Date(fecha), "dd/MM/yyyy HH:mm", { locale: es })
  } catch {
    return 'N/A'
  }
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    aceptado: 'bg-blue-500',
    en_curso: 'bg-purple-500',
    finalizado: 'bg-green-500',
    cancelado: 'bg-red-500',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoLabel = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'Pendiente',
    aceptado: 'Aceptado',
    en_curso: 'En Curso',
    finalizado: 'Finalizado',
    cancelado: 'Cancelado',
  }
  return estados[estado] || estado
}

export default function EmpresaViajesPage() {
  const [search, setSearch] = useState('')
  const [filterEstado, setFilterEstado] = useState<string>('todos')

  const { data: viajes, isLoading } = useQuery<ViajeEmpresa[]>({
    queryKey: ['empresa-viajes', filterEstado],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filterEstado !== 'todos') params.append('estado', filterEstado)
      const response = await apiClient.get(`/api/empresa/dashboard/viajes?${params.toString()}`)
      return response.data
    },
  })

  const filteredViajes = viajes?.filter((viaje) => {
    const searchLower = search.toLowerCase()
    return (
      viaje.pasajero_nombre?.toLowerCase().includes(searchLower) ||
      viaje.origen?.toLowerCase().includes(searchLower) ||
      viaje.destino?.toLowerCase().includes(searchLower) ||
      viaje.chofer_nombre?.toLowerCase().includes(searchLower) ||
      viaje.patente?.toLowerCase().includes(searchLower)
    )
  })

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Viajes Corporativos</h1>
          <p className="text-muted-foreground">
            Historial y seguimiento de viajes de la empresa
          </p>
        </div>
        <Link href="/dashboard-empresa/viajes/nuevo">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Solicitar Viaje
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Listado de Viajes</CardTitle>
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-full sm:w-48"
                />
              </div>
              <Select value={filterEstado} onValueChange={setFilterEstado}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="pendiente">Pendientes</SelectItem>
                  <SelectItem value="aceptado">Aceptados</SelectItem>
                  <SelectItem value="en_curso">En Curso</SelectItem>
                  <SelectItem value="finalizado">Finalizados</SelectItem>
                  <SelectItem value="cancelado">Cancelados</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>Pasajero</TableHead>
                <TableHead>Origen → Destino</TableHead>
                <TableHead>Chofer</TableHead>
                <TableHead>Precio</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredViajes?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    No hay viajes para mostrar
                  </TableCell>
                </TableRow>
              ) : (
                filteredViajes?.map((viaje, idx) => (
                  <TableRow key={viaje.id}>
                    <TableCell>#{idx + 1}</TableCell>
                    <TableCell>{viaje.pasajero_nombre || 'N/A'}</TableCell>
                    <TableCell>
                      <div className="max-w-xs truncate">
                        {viaje.origen || 'N/A'} → {viaje.destino || 'N/A'}
                      </div>
                      {viaje.distancia_metros && (
                        <div className="text-xs text-muted-foreground">
                          {Math.round(viaje.distancia_metros / 1000)} km
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      {viaje.chofer_nombre ? (
                        <div>
                          <div>{viaje.chofer_nombre}</div>
                          {viaje.patente && (
                            <div className="text-xs text-muted-foreground">{viaje.patente}</div>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">Sin asignar</span>
                      )}
                    </TableCell>
                    <TableCell>{formatMoneda(viaje.precio_final)}</TableCell>
                    <TableCell>
                      <Badge className={getEstadoColor(viaje.estado)}>
                        {getEstadoLabel(viaje.estado)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatFecha(viaje.created_at)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Link href={`/dashboard-empresa/viajes/${viaje.id}`}>
                        <Button variant="ghost" size="sm" title="Ver detalle">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}