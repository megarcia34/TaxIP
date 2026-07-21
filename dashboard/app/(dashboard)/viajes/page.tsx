'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Eye, FileText, FileSpreadsheet, Calendar, MapPin, User, Car, Search, Map, Clock, Building2, UserCog, Hash } from 'lucide-react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { viajesAPI } from '@/lib/api'
import { format, isValid } from 'date-fns'
import { es } from 'date-fns/locale'

interface Viaje {
  id: string
  estado: string
  direccion_origen: string
  direccion_destino: string
  precio_estimado: number
  precio_final: number
  created_at: string
  aceptado_en?: string
  iniciado_en?: string
  finalizado_en?: string
  pasajero_nombre: string
  chofer_nombre?: string
  distancia_metros?: number
  tiempo_estimado_segundos?: number
  origen_lat?: number
  origen_lng?: number
  destino_lat?: number
  destino_lng?: number
  // NUEVOS CAMPOS
  numero_viaje?: number
  tenant_nombre?: string
  patente?: string
  propietario_id?: string
  propietario_nombre?: string
}

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    aceptado: 'bg-blue-500',
    en_curso: 'bg-purple-500',
    finalizado: 'bg-green-500',
    cancelado: 'bg-red-500',
    programada: 'bg-orange-500',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoTexto = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'Pendiente',
    aceptado: 'Aceptado',
    en_curso: 'En curso',
    finalizado: 'Finalizado',
    cancelado: 'Cancelado',
    programada: 'Programada',
  }
  return estados[estado] || estado
}

export default function ViajesPage() {
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('active')

  const { data: viajes, isLoading } = useQuery({
    queryKey: ['viajes', 'historial'],
    queryFn: viajesAPI.getHistorial,
  })

  const filteredViajes = viajes?.filter((viaje: Viaje) => {
    const matchesSearch = 
      viaje.pasajero_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.chofer_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.direccion_origen?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.direccion_destino?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.tenant_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.propietario_nombre?.toLowerCase().includes(search.toLowerCase())
    
    if (activeTab === 'active') {
      return matchesSearch && ['pendiente', 'aceptado', 'en_curso'].includes(viaje.estado)
    }
    if (activeTab === 'completed') {
      return matchesSearch && viaje.estado === 'finalizado'
    }
    if (activeTab === 'booked') {
      return matchesSearch && viaje.estado === 'programada'
    }
    return matchesSearch
  })

  const exportToCSV = () => {
    const headers = ['#', 'Pasajero', 'Chofer', 'Origen', 'Destino', 'Fecha', 'Hora', 'Precio', 'Estado', 'Empresa', 'Propietario']
    const rows = filteredViajes?.map((viaje: Viaje) => [
      viaje.numero_viaje || 'N/A',
      viaje.pasajero_nombre || 'N/A',
      viaje.chofer_nombre || 'N/A',
      viaje.direccion_origen || 'N/A',
      viaje.direccion_destino || 'N/A',
      formatFecha(viaje.created_at),
      formatHora(viaje.created_at),
      `$${viaje.precio_final || viaje.precio_estimado || 0}`,
      getEstadoTexto(viaje.estado),
      viaje.tenant_nombre || 'N/A',
      viaje.propietario_nombre || 'N/A'
    ])
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `viajes_${activeTab}_${format(new Date(), 'yyyy-MM-dd')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const formatFecha = (fecha: string | undefined | null) => {
    if (!fecha) return 'N/A'
    try {
      const date = new Date(fecha)
      if (!isValid(date)) return 'N/A'
      return format(date, "dd/MM/yyyy", { locale: es })
    } catch {
      return 'N/A'
    }
  }

  const formatHora = (fecha: string | undefined | null) => {
    if (!fecha) return 'N/A'
    try {
      const date = new Date(fecha)
      if (!isValid(date)) return 'N/A'
      return format(date, "HH:mm", { locale: es })
    } catch {
      return 'N/A'
    }
  }

  const formatMoneda = (monto: number | undefined | null) => {
    if (monto === undefined || monto === null) return '$0'
    return `$${monto.toFixed(2)}`
  }

  const formatDistancia = (metros: number | undefined | null) => {
    if (!metros) return 'N/A'
    if (metros >= 1000) {
      return `${(metros / 1000).toFixed(1)} km`
    }
    return `${metros} m`
  }

  const hasRouteCoordinates = (viaje: Viaje) => {
    return viaje.origen_lat && viaje.origen_lng && viaje.destino_lat && viaje.destino_lng
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Viajes</h1>
        <p className="text-muted-foreground">
          Gestión y seguimiento de todos los viajes de la flota
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={exportToCSV}>
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button variant="outline" size="sm">
                <FileText className="h-4 w-4 mr-2" />
                PDF
              </Button>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por pasajero, chofer o dirección..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 w-full sm:w-80"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="active">Viajes Activos</TabsTrigger>
              <TabsTrigger value="completed">Completados</TabsTrigger>
              <TabsTrigger value="booked">Reservados</TabsTrigger>
              <TabsTrigger value="all">Todos</TabsTrigger>
            </TabsList>

            {['active', 'completed', 'booked', 'all'].map((tab) => (
              <TabsContent key={tab} value={tab}>
                <div className="relative overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="pb-3 font-medium">#</th>
                        <th className="pb-3 font-medium">Pasajero</th>
                        <th className="pb-3 font-medium">Chofer</th>
                        <th className="pb-3 font-medium">Origen → Destino</th>
                        <th className="pb-3 font-medium">Fecha</th>
                        <th className="pb-3 font-medium">Hora</th>
                        <th className="pb-3 font-medium">Precio</th>
                        <th className="pb-3 font-medium">Estado</th>
                        <th className="pb-3 font-medium">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredViajes?.length === 0 ? (
                        <tr>
                          <td colSpan={9} className="py-8 text-center text-muted-foreground">
                            No hay viajes para mostrar
                          </td>
                        </tr>
                      ) : (
                        filteredViajes?.map((viaje: Viaje, idx: number) => (
                          <tr key={viaje.id} className="border-b hover:bg-muted/50">
                            <td className="py-3">
                              <div className="flex items-center gap-1">
                                <Hash className="h-3 w-3 text-muted-foreground" />
                                <span className="font-mono text-xs">
                                  {viaje.numero_viaje || 'N/A'}
                                </span>
                              </div>
                            </td>
                            <td className="py-3">
                              <div className="flex items-center gap-2">
                                <User className="h-3 w-3 text-muted-foreground" />
                                <span>{viaje.pasajero_nombre || 'N/A'}</span>
                              </div>
                            </td>
                            <td className="py-3">
                              {viaje.chofer_nombre ? (
                                <div className="flex items-center gap-2">
                                  <Car className="h-3 w-3 text-muted-foreground" />
                                  {viaje.chofer_nombre}
                                </div>
                              ) : (
                                <span className="text-muted-foreground">Sin asignar</span>
                              )}
                            </td>
                            <td className="py-3 max-w-md">
                              <div className="truncate">
                                {viaje.direccion_origen || 'N/A'} → {viaje.direccion_destino || 'N/A'}
                              </div>
                              {viaje.distancia_metros && (
                                <div className="text-xs text-muted-foreground">
                                  {formatDistancia(viaje.distancia_metros)}
                                </div>
                              )}
                            </td>
                            <td className="py-3 whitespace-nowrap">
                              <div className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {formatFecha(viaje.created_at)}
                              </div>
                            </td>
                            <td className="py-3 whitespace-nowrap">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatHora(viaje.created_at)}
                              </div>
                            </td>
                            <td className="py-3">
                              {formatMoneda(viaje.precio_final || viaje.precio_estimado)}
                            </td>
                            <td className="py-3">
                              <Badge className={getEstadoColor(viaje.estado)}>
                                {getEstadoTexto(viaje.estado)}
                              </Badge>
                              {viaje.tenant_nombre && (
                                <div className="text-xs text-muted-foreground mt-1">
                                  <Building2 className="h-3 w-3 inline mr-1" />
                                  {viaje.tenant_nombre}
                                </div>
                              )}
                            </td>
                            <td className="py-3">
                              <div className="flex gap-1">
                                <Link href={`/viajes/${viaje.id}`}>
                                  <Button variant="ghost" size="sm" title="Ver detalles">
                                    <Eye className="h-4 w-4" />
                                  </Button>
                                </Link>
                                {hasRouteCoordinates(viaje) && (
                                  <Link href={`/viajes/${viaje.id}?view=route`}>
                                    <Button variant="ghost" size="sm" title="Ver ruta en mapa">
                                      <Map className="h-4 w-4" />
                                    </Button>
                                  </Link>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}