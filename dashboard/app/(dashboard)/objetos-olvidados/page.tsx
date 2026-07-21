'use client'

import { useEffect, useState, useMemo } from 'react'
import { useSession } from 'next-auth/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { 
  Search, 
  Eye, 
  Package, 
  Loader2, 
  Filter, 
  X, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Users,
  Calendar,
  Download,
  FileText,
  Bell,
  User,
  Car,
  MapPin
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

interface ObjetoOlvidado {
  id: string
  viaje_id: string
  descripcion: string
  estado: 'reportado' | 'encontrado' | 'entregado'
  reportado_por: string
  fecha_reporte: string
  fecha_entrega?: string
  pasajero_nombre?: string
  pasajero_email?: string
  chofer_nombre?: string
  origen?: string
  destino?: string
  foto_url?: string
  observaciones?: string
}

interface Viaje {
  id: string
  pasajero_nombre: string
  origen: string
  destino: string
  created_at: string
}

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    reportado: 'bg-yellow-500 hover:bg-yellow-600',
    encontrado: 'bg-blue-500 hover:bg-blue-600',
    entregado: 'bg-green-500 hover:bg-green-600',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoTexto = (estado: string) => {
  const estados: Record<string, string> = {
    reportado: 'Reportado',
    encontrado: 'Encontrado',
    entregado: 'Entregado',
  }
  return estados[estado] || estado
}

const getEstadoIcon = (estado: string) => {
  switch (estado) {
    case 'reportado': return <AlertCircle className="h-4 w-4" />
    case 'encontrado': return <CheckCircle className="h-4 w-4" />
    case 'entregado': return <CheckCircle className="h-4 w-4" />
    default: return <Package className="h-4 w-4" />
  }
}

export default function ObjetosOlvidadosPage() {
  const { status } = useSession()
  const [search, setSearch] = useState('')
  const [estadoFilter, setEstadoFilter] = useState('todos')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [pasajeroFilter, setPasajeroFilter] = useState('')
  const [choferFilter, setChoferFilter] = useState('')
  const queryClient = useQueryClient()

  // Obtener objetos olvidados
  const { data: objetos, isLoading, refetch } = useQuery({
    queryKey: ['objetos-olvidados'],
    queryFn: async () => {
      const response = await apiClient.get('/api/viajes/objeto-olvidado')
      return response.data
    },
    enabled: status === 'authenticated',
  })

  // Obtener viajes para el selector
  const { data: viajes } = useQuery({
    queryKey: ['viajes-para-objetos'],
    queryFn: async () => {
      const response = await apiClient.get('/api/viajes/historial?limit=100')
      return response.data
    },
    enabled: status === 'authenticated',
  })

  // Actualizar estado
  const updateEstadoMutation = useMutation({
    mutationFn: async ({ id, estado }: { id: string; estado: string }) => {
      const response = await apiClient.put(`/api/viajes/objeto-olvidado/${id}`, { estado })
      return response.data
    },
    onSuccess: () => {
      toast.success('Estado actualizado correctamente')
      queryClient.invalidateQueries({ queryKey: ['objetos-olvidados'] })
    },
    onError: () => {
      toast.error('Error al actualizar el estado')
    },
  })

  // Notificar pasajero
  const notificarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/api/viajes/objeto-olvidado/${id}/notificar`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Notificación enviada al pasajero')
    },
    onError: () => {
      toast.error('Error al enviar la notificación')
    },
  })

  // Filtrar objetos
  const filteredObjetos = useMemo(() => {
    if (!objetos) return []

    let result = objetos

    // Búsqueda
    if (search) {
      const term = search.toLowerCase()
      result = result.filter((obj: ObjetoOlvidado) =>
        obj.descripcion?.toLowerCase().includes(term) ||
        obj.pasajero_nombre?.toLowerCase().includes(term) ||
        obj.chofer_nombre?.toLowerCase().includes(term)
      )
    }

    // Estado
    if (estadoFilter !== 'todos') {
      result = result.filter((obj: ObjetoOlvidado) => obj.estado === estadoFilter)
    }

    // Fechas
    if (fechaDesde) {
      result = result.filter((obj: ObjetoOlvidado) =>
        new Date(obj.fecha_reporte) >= new Date(fechaDesde)
      )
    }
    if (fechaHasta) {
      const hasta = new Date(fechaHasta)
      hasta.setHours(23, 59, 59)
      result = result.filter((obj: ObjetoOlvidado) =>
        new Date(obj.fecha_reporte) <= hasta
      )
    }

    // Pasajero
    if (pasajeroFilter) {
      result = result.filter((obj: ObjetoOlvidado) =>
        obj.pasajero_nombre?.toLowerCase().includes(pasajeroFilter.toLowerCase())
      )
    }

    // Chofer
    if (choferFilter) {
      result = result.filter((obj: ObjetoOlvidado) =>
        obj.chofer_nombre?.toLowerCase().includes(choferFilter.toLowerCase())
      )
    }

    return result
  }, [objetos, search, estadoFilter, fechaDesde, fechaHasta, pasajeroFilter, choferFilter])

  // KPIs
  const kpis = useMemo(() => {
    if (!objetos) return { total: 0, reportados: 0, encontrados: 0, entregados: 0, tasaResolucion: 0 }

    const total = objetos.length
    const reportados = objetos.filter((o: ObjetoOlvidado) => o.estado === 'reportado').length
    const encontrados = objetos.filter((o: ObjetoOlvidado) => o.estado === 'encontrado').length
    const entregados = objetos.filter((o: ObjetoOlvidado) => o.estado === 'entregado').length
    const resolucion = total > 0 ? Math.round((entregados / total) * 100) : 0

    return { total, reportados, encontrados, entregados, tasaResolucion: resolucion }
  }, [objetos])

  const clearFilters = () => {
    setSearch('')
    setEstadoFilter('todos')
    setFechaDesde('')
    setFechaHasta('')
    setPasajeroFilter('')
    setChoferFilter('')
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Package className="h-6 w-6" />
            Objetos Olvidados
          </h1>
          <p className="text-muted-foreground">
            Gestión de objetos perdidos en viajes
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1">
              <Package className="h-4 w-4" />
              Total
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-yellow-500">
              <Clock className="h-4 w-4" />
              Reportados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500">{kpis.reportados}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-blue-500">
              <AlertCircle className="h-4 w-4" />
              Encontrados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">{kpis.encontrados}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-green-500">
              <CheckCircle className="h-4 w-4" />
              Entregados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-green-500">{kpis.entregados}</span>
              <Badge className="bg-green-100 text-green-800">
                {kpis.tasaResolucion}% resuelto
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filtros
              {(search || estadoFilter !== 'todos' || fechaDesde || fechaHasta || pasajeroFilter || choferFilter) && (
                <Badge variant="secondary" className="ml-2">
                  {filteredObjetos.length} resultados
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowFilters(!showFilters)}>
                {showFilters ? 'Simplificar' : 'Avanzado'}
              </Button>
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4 mr-1" />
                Limpiar
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por descripción, pasajero o chofer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
              </button>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="estado">Estado</Label>
              <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                <SelectTrigger id="estado">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="reportado">🟡 Reportados</SelectItem>
                  <SelectItem value="encontrado">🔵 Encontrados</SelectItem>
                  <SelectItem value="entregado">🟢 Entregados</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="pasajero">Pasajero</Label>
              <Input
                id="pasajero"
                placeholder="Nombre del pasajero..."
                value={pasajeroFilter}
                onChange={(e) => setPasajeroFilter(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="chofer">Chofer</Label>
              <Input
                id="chofer"
                placeholder="Nombre del chofer..."
                value={choferFilter}
                onChange={(e) => setChoferFilter(e.target.value)}
              />
            </div>
          </div>

          {showFilters && (
            <div className="grid gap-4 md:grid-cols-2 pt-4 border-t">
              <div className="space-y-1">
                <Label>Rango de Fechas</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="date"
                    value={fechaDesde}
                    onChange={(e) => setFechaDesde(e.target.value)}
                  />
                  <Input
                    type="date"
                    value={fechaHasta}
                    onChange={(e) => setFechaHasta(e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Viaje</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar viaje..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    {viajes?.slice(0, 10).map((viaje: Viaje) => (
                      <SelectItem key={viaje.id} value={viaje.id}>
                        {viaje.pasajero_nombre} - {viaje.origen} → {viaje.destino}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabla */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <span>Listado de Objetos</span>
            <Badge variant="secondary">{filteredObjetos.length} objetos</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Pasajero</TableHead>
                  <TableHead>Chofer</TableHead>
                  <TableHead>Viaje</TableHead>
                  <TableHead>Fecha Reporte</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredObjetos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      {objetos?.length === 0 ? 'No hay objetos reportados' : 'No se encontraron objetos con los filtros aplicados'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredObjetos.map((obj: ObjetoOlvidado) => (
                    <TableRow key={obj.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {obj.foto_url ? (
                            <img
                              src={obj.foto_url}
                              alt="Objeto"
                              className="w-10 h-10 rounded object-cover"
                            />
                          ) : (
                            <div className="w-10 h-10 rounded bg-muted flex items-center justify-center">
                              <Package className="h-5 w-5 text-muted-foreground" />
                            </div>
                          )}
                          <div>
                            <p className="font-medium text-sm line-clamp-2">
                              {obj.descripcion}
                            </p>
                            {obj.observaciones && (
                              <p className="text-xs text-muted-foreground line-clamp-1">
                                {obj.observaciones}
                              </p>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm font-medium">{obj.pasajero_nombre || 'N/A'}</p>
                          {obj.pasajero_email && (
                            <p className="text-xs text-muted-foreground">{obj.pasajero_email}</p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{obj.chofer_nombre || 'N/A'}</TableCell>
                      <TableCell>
                        <div className="text-xs">
                          {obj.origen && obj.destino ? (
                            <>
                              <p className="line-clamp-1">{obj.origen}</p>
                              <p className="text-muted-foreground">→ {obj.destino}</p>
                            </>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="whitespace-nowrap">
                        {new Date(obj.fecha_reporte).toLocaleDateString('es-AR')}
                        <p className="text-xs text-muted-foreground">
                          {new Date(obj.fecha_reporte).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-1">
                          <Badge className={getEstadoColor(obj.estado)}>
                            {getEstadoIcon(obj.estado)}
                            <span className="ml-1">{getEstadoTexto(obj.estado)}</span>
                          </Badge>
                          {obj.estado !== 'entregado' && (
                            <Select
                              value={obj.estado}
                              onValueChange={(value) =>
                                updateEstadoMutation.mutate({ id: obj.id, estado: value })
                              }
                            >
                              <SelectTrigger className="h-7 text-xs w-28">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="reportado">Reportado</SelectItem>
                                <SelectItem value="encontrado">Encontrado</SelectItem>
                                <SelectItem value="entregado">Entregado</SelectItem>
                              </SelectContent>
                            </Select>
                          )}
                          {obj.estado === 'entregado' && obj.fecha_entrega && (
                            <p className="text-xs text-muted-foreground">
                              Entregado: {new Date(obj.fecha_entrega).toLocaleDateString('es-AR')}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Link href={`/objetos-olvidados/${obj.id}`}>
                            <Button variant="ghost" size="icon" className="h-8 w-8" title="Ver detalle">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          {obj.estado !== 'entregado' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              title="Notificar pasajero"
                              onClick={() => notificarMutation.mutate(obj.id)}
                              disabled={notificarMutation.isPending}
                            >
                              <Bell className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}