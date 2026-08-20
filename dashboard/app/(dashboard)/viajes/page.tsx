'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Eye, 
  FileText, 
  FileSpreadsheet, 
  Calendar, 
  MapPin, 
  User, 
  Car, 
  Search, 
  Map, 
  Clock, 
  Building2, 
  UserCog, 
  Hash,
  AlertCircle,
  CheckCircle,
  Clock as ClockIcon,
  XCircle,
  Loader2
} from 'lucide-react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { viajesAPI } from '@/lib/api'
import { format, isValid } from 'date-fns'
import { es } from 'date-fns/locale'

// ============================================
// INTERFACES
// ============================================

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
  // ✅ NUEVOS CAMPOS
  fecha?: string        // DD/MM/YYYY
  hora?: string         // HH24:MI
  empresa?: string      // tenant.control_base.nombre
  propietario_nombre?: string
  patente?: string
  marca?: string
  modelo?: string
  calificacion?: number
}

// ============================================
// UTILIDADES
// ============================================

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500 hover:bg-yellow-600',
    aceptado: 'bg-blue-500 hover:bg-blue-600',
    en_curso: 'bg-purple-500 hover:bg-purple-600',
    finalizado: 'bg-green-500 hover:bg-green-600',
    cancelado: 'bg-red-500 hover:bg-red-600',
    programada: 'bg-orange-500 hover:bg-orange-600',
  }
  return estados[estado] || 'bg-gray-500 hover:bg-gray-600'
}

const getEstadoIcono = (estado: string) => {
  const iconos: Record<string, React.ReactNode> = {
    pendiente: <ClockIcon className="h-3 w-3" />,
    aceptado: <CheckCircle className="h-3 w-3" />,
    en_curso: <Loader2 className="h-3 w-3 animate-spin" />,
    finalizado: <CheckCircle className="h-3 w-3" />,
    cancelado: <XCircle className="h-3 w-3" />,
    programada: <Calendar className="h-3 w-3" />,
  }
  return iconos[estado] || <AlertCircle className="h-3 w-3" />
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

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export default function ViajesPage() {
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('active')

  // ✅ CORREGIDO: viajesAPI.getHistorial ahora devuelve directamente el array
  const { data: viajes, isLoading, error } = useQuery<Viaje[]>({
    queryKey: ['viajes', 'historial'],
    queryFn: viajesAPI.getHistorial,
  })

  // Calcular total
  const total = viajes?.length || 0

  // Filtrar viajes
  const filteredViajes = (viajes || []).filter((viaje: Viaje) => {
    const matchesSearch = 
      viaje.pasajero_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.chofer_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.direccion_origen?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.direccion_destino?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.empresa?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.propietario_nombre?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.patente?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.marca?.toLowerCase().includes(search.toLowerCase()) ||
      viaje.modelo?.toLowerCase().includes(search.toLowerCase())
    
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

  // ============================================
  // EXPORTAR A CSV
  // ============================================

  const exportToCSV = () => {
    const headers = [
      '#', 
      'Pasajero', 
      'Chofer', 
      'Origen', 
      'Destino', 
      'Fecha', 
      'Hora', 
      'Precio', 
      'Estado', 
      'Empresa', 
      'Propietario',
      'Patente',
      'Marca',
      'Modelo'
    ]
    
    const rows = filteredViajes.map((viaje: Viaje) => [
      viaje.id.slice(0, 8) || 'N/A',
      viaje.pasajero_nombre || 'N/A',
      viaje.chofer_nombre || 'N/A',
      viaje.direccion_origen || 'N/A',
      viaje.direccion_destino || 'N/A',
      viaje.fecha || formatFecha(viaje.created_at),
      viaje.hora || formatHora(viaje.created_at),
      `$${viaje.precio_final || viaje.precio_estimado || 0}`,
      getEstadoTexto(viaje.estado),
      viaje.empresa || 'N/A',
      viaje.propietario_nombre || 'N/A',
      viaje.patente || 'N/A',
      viaje.marca || 'N/A',
      viaje.modelo || 'N/A'
    ])
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `viajes_${activeTab}_${format(new Date(), 'yyyy-MM-dd')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // ============================================
  // FORMATEADORES
  // ============================================

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

  const formatTiempo = (segundos: number | undefined | null) => {
    if (!segundos) return 'N/A'
    const minutos = Math.floor(segundos / 60)
    const segs = segundos % 60
    if (minutos > 0) {
      return `${minutos}m ${segs}s`
    }
    return `${segs}s`
  }

  const hasRouteCoordinates = (viaje: Viaje) => {
    return viaje.origen_lat && viaje.origen_lng && viaje.destino_lat && viaje.destino_lng
  }

  // ============================================
  // RENDER
  // ============================================

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-muted-foreground">Error al cargar los viajes</p>
          <p className="text-sm text-muted-foreground">{(error as Error)?.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Viajes</h1>
          <p className="text-muted-foreground">
            Gestión y seguimiento de todos los viajes de la flota
            {total > 0 && <span className="ml-2 text-sm">({total} viajes)</span>}
          </p>
        </div>
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
                placeholder="Buscar por pasajero, chofer, dirección, empresa..."
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
              <TabsTrigger value="active">
                Viajes Activos
                <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded-full">
                  {(viajes || []).filter(v => ['pendiente', 'aceptado', 'en_curso'].includes(v.estado)).length}
                </span>
              </TabsTrigger>
              <TabsTrigger value="completed">
                Completados
                <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded-full">
                  {(viajes || []).filter(v => v.estado === 'finalizado').length}
                </span>
              </TabsTrigger>
              <TabsTrigger value="booked">
                Reservados
                <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded-full">
                  {(viajes || []).filter(v => v.estado === 'programada').length}
                </span>
              </TabsTrigger>
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
                        <th className="pb-3 font-medium">Fecha/Hora</th>
                        <th className="pb-3 font-medium">Precio</th>
                        <th className="pb-3 font-medium">Estado</th>
                        <th className="pb-3 font-medium">Empresa</th>
                        <th className="pb-3 font-medium">Propietario</th>
                        <th className="pb-3 font-medium">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredViajes.length === 0 ? (
                        <tr>
                          <td colSpan={10} className="py-8 text-center text-muted-foreground">
                            No hay viajes para mostrar
                          </td>
                        </tr>
                      ) : (
                        filteredViajes.map((viaje: Viaje) => (
                          <tr key={viaje.id} className="border-b hover:bg-muted/50">
                            {/* # ID */}
                            <td className="py-3">
                              <div className="flex items-center gap-1">
                                <Hash className="h-3 w-3 text-muted-foreground" />
                                <span className="font-mono text-xs">
                                  {viaje.id.slice(0, 8)}
                                </span>
                              </div>
                            </td>

                            {/* Pasajero */}
                            <td className="py-3">
                              <div className="flex items-center gap-2">
                                <User className="h-3 w-3 text-muted-foreground" />
                                <span>{viaje.pasajero_nombre || 'N/A'}</span>
                              </div>
                            </td>

                            {/* Chofer */}
                            <td className="py-3">
                              {viaje.chofer_nombre && viaje.chofer_nombre !== 'Sin asignar' ? (
                                <div className="flex items-center gap-2">
                                  <Car className="h-3 w-3 text-muted-foreground" />
                                  <span>{viaje.chofer_nombre}</span>
                                  {viaje.patente && (
                                    <Badge variant="outline" className="text-xs">
                                      {viaje.patente}
                                    </Badge>
                                  )}
                                </div>
                              ) : (
                                <span className="text-muted-foreground text-xs">Sin asignar</span>
                              )}
                            </td>

                            {/* Origen → Destino */}
                            <td className="py-3 max-w-md">
                              <div className="truncate max-w-[200px]">
                                <span className="text-xs">{viaje.direccion_origen || 'N/A'}</span>
                                <span className="mx-1 text-muted-foreground">→</span>
                                <span className="text-xs">{viaje.direccion_destino || 'N/A'}</span>
                              </div>
                              {viaje.distancia_metros && (
                                <div className="text-xs text-muted-foreground">
                                  {formatDistancia(viaje.distancia_metros)}
                                  {viaje.tiempo_estimado_segundos && (
                                    <span className="ml-2">
                                      • {formatTiempo(viaje.tiempo_estimado_segundos)}
                                    </span>
                                  )}
                                </div>
                              )}
                            </td>

                            {/* Fecha/Hora */}
                            <td className="py-3 whitespace-nowrap">
                              <div className="flex flex-col">
                                <div className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3 text-muted-foreground" />
                                  <span className="text-xs font-mono">
                                    {viaje.fecha || formatFecha(viaje.created_at)}
                                  </span>
                                </div>
                                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <Clock className="h-3 w-3" />
                                  {viaje.hora || formatHora(viaje.created_at)}
                                </div>
                              </div>
                            </td>

                            {/* Precio */}
                            <td className="py-3">
                              <div className="font-mono">
                                {formatMoneda(viaje.precio_final || viaje.precio_estimado)}
                              </div>
                              {viaje.precio_estimado && viaje.precio_final && 
                               viaje.precio_estimado !== viaje.precio_final && (
                                <div className="text-xs text-muted-foreground line-through">
                                  {formatMoneda(viaje.precio_estimado)}
                                </div>
                              )}
                            </td>

                            {/* Estado */}
                            <td className="py-3">
                              <Badge className={getEstadoColor(viaje.estado)}>
                                <span className="flex items-center gap-1">
                                  {getEstadoIcono(viaje.estado)}
                                  {getEstadoTexto(viaje.estado)}
                                </span>
                              </Badge>
                            </td>

                            {/* Empresa */}
                            <td className="py-3">
                              {viaje.empresa ? (
                                <div className="flex items-center gap-1">
                                  <Building2 className="h-3 w-3 text-muted-foreground" />
                                  <span className="text-xs">{viaje.empresa}</span>
                                </div>
                              ) : (
                                <span className="text-xs text-muted-foreground">N/A</span>
                              )}
                            </td>

                            {/* Propietario */}
                            <td className="py-3">
                              {viaje.propietario_nombre && viaje.propietario_nombre !== 'No asignado' ? (
                                <div className="flex items-center gap-1">
                                  <UserCog className="h-3 w-3 text-muted-foreground" />
                                  <span className="text-xs">{viaje.propietario_nombre}</span>
                                </div>
                              ) : (
                                <span className="text-xs text-muted-foreground">N/A</span>
                              )}
                            </td>

                            {/* Acciones */}
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

                {/* Resumen de resultados */}
                {filteredViajes.length > 0 && (
                  <div className="mt-4 text-sm text-muted-foreground">
                    Mostrando {filteredViajes.length} de {viajes?.length || 0} viajes
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}