'use client'

import { useEffect, useState, useMemo } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { 
  RefreshCw, 
  UserPlus, 
  Search, 
  Filter, 
  X, 
  Eye, 
  Edit2, 
  Car, 
  Star,
  Users,
  UserCheck,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import Link from 'next/link'
import { apiClient } from '@/lib/api'  // ✅ IMPORTAR apiClient

interface Chofer {
  id: string
  usuario_id: string
  nombre: string
  apellido: string
  email: string
  telefono: string
  documento: string
  estado_laboral: string
  estado_aprobacion: string
  calificacion_promedio: number
  total_viajes: number
  total_calificaciones: number
  vehiculo?: {
    id: string
    patente: string
    marca: string
    modelo: string
    anio: number
  }
  propietario?: {
    id: string
    nombre: string
  }
  ultima_conexion: string
  activo: boolean
  foto_perfil_url?: string
}

export default function ChoferesPage() {
  const { status } = useSession()
  const router = useRouter()
  const { toast } = useToast()
  
  const [choferes, setChoferes] = useState<Chofer[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filtroEstado, setFiltroEstado] = useState('')
  const [filtroAprobacion, setFiltroAprobacion] = useState('')
  const [filtroPropietario, setFiltroPropietario] = useState('')
  const [filtroCalificacion, setFiltroCalificacion] = useState(0)
  const [showFilters, setShowFilters] = useState(false)

  // ============================================
  // ✅ USAR apiClient EN VEZ DE fetch
  // ============================================
  const fetchChoferes = async () => {
    try {
      setLoading(true)
      
      // ✅ Usar apiClient (tiene el interceptor con el token correcto)
      const response = await apiClient.get('/api/choferes/lista')
      
      console.log('✅ Choferes obtenidos:', response.data)
      
      const data = response.data
      const choferesData = Array.isArray(data) ? data : (data.data || data || [])
      
      const choferesTransformados = choferesData.map((item: any) => ({
        id: item.id,
        usuario_id: item.id,
        nombre: item.nombre || 'Sin nombre',
        apellido: item.apellido || '',
        email: item.email || '',
        telefono: item.telefono || '',
        documento: item.documento || '',
        estado_laboral: item.estado_laboral || 'inactivo',
        estado_aprobacion: item.estado_aprobacion || 'aprobado',
        calificacion_promedio: item.calificacion_promedio || 0,
        total_viajes: item.total_viajes || 0,
        total_calificaciones: item.total_calificaciones || 0,
        vehiculo: item.vehiculo_patente ? {
          id: item.vehiculo_id || '',
          patente: item.vehiculo_patente || '',
          marca: item.vehiculo_marca || '',
          modelo: item.vehiculo_modelo || '',
          anio: item.vehiculo_anio || 0,
        } : undefined,
        propietario: item.propietario_nombre ? {
          id: '',
          nombre: item.propietario_nombre || '',
        } : undefined,
        ultima_conexion: item.ultima_conexion || '',
        activo: item.activo !== false,
        foto_perfil_url: item.foto_perfil_url || '',
      }))
      
      setChoferes(choferesTransformados)
      
    } catch (error: any) {
      console.error('Error fetching choferes:', error)
      
      if (error.response?.status === 401) {
        toast({
          title: 'Sesión expirada',
          description: 'Por favor, vuelve a iniciar sesión',
          variant: 'destructive',
        })
      } else {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'No se pudieron cargar los choferes',
          variant: 'destructive',
        })
      }
      setChoferes([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchChoferes()
    }
  }, [status])

  // Filtrar choferes
  const filteredChoferes = useMemo(() => {
    let result = choferes

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(c => 
        `${c.nombre || ''} ${c.apellido || ''}`.toLowerCase().includes(term) ||
        (c.email || '').toLowerCase().includes(term) ||
        (c.documento || '').toLowerCase().includes(term) ||
        (c.vehiculo?.patente || '').toLowerCase().includes(term)
      )
    }

    if (filtroEstado) {
      result = result.filter(c => c.estado_laboral === filtroEstado)
    }

    if (filtroAprobacion) {
      result = result.filter(c => c.estado_aprobacion === filtroAprobacion)
    }

    if (filtroPropietario) {
      result = result.filter(c => c.propietario?.id === filtroPropietario)
    }

    if (filtroCalificacion > 0) {
      result = result.filter(c => (c.calificacion_promedio || 0) >= filtroCalificacion)
    }

    return result
  }, [choferes, searchTerm, filtroEstado, filtroAprobacion, filtroPropietario, filtroCalificacion])

  // KPIs
  const kpis = useMemo(() => {
    const activos = choferes.filter(c => c.activo !== false && c.estado_aprobacion !== 'rechazado')
    const libres = activos.filter(c => c.estado_laboral === 'libre')
    const ocupados = activos.filter(c => c.estado_laboral === 'ocupado')
    const sinVehiculo = activos.filter(c => !c.vehiculo)
    
    const calif = activos.reduce((sum, c) => sum + (c.calificacion_promedio || 0), 0)
    const califPromedio = activos.length > 0 ? calif / activos.length : 0

    return {
      total: choferes.length,
      activos: activos.length,
      libres: libres.length,
      ocupados: ocupados.length,
      sinVehiculo: sinVehiculo.length,
      calificacionPromedio: califPromedio,
    }
  }, [choferes])

  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      libre: { label: '🟢 Libre', className: 'bg-green-100 text-green-800' },
      ocupado: { label: '🟡 Ocupado', className: 'bg-yellow-100 text-yellow-800' },
      inactivo: { label: '🔴 Inactivo', className: 'bg-red-100 text-red-800' },
    }
    const info = estados[estado] || estados.inactivo
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const getAprobacionBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      aprobado: { label: 'Aprobado', className: 'bg-green-500 hover:bg-green-600' },
      pendiente: { label: '⏳ Pendiente', className: 'bg-yellow-500 hover:bg-yellow-600' },
      rechazado: { label: '❌ Rechazado', className: 'bg-red-500 hover:bg-red-600' },
    }
    const info = estados[estado] || estados.pendiente
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const clearFilters = () => {
    setSearchTerm('')
    setFiltroEstado('')
    setFiltroAprobacion('')
    setFiltroPropietario('')
    setFiltroCalificacion(0)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Choferes</h1>
          <p className="text-muted-foreground">
            Gestión de conductores de la flota
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchChoferes} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button size="sm" onClick={() => router.push('/choferes/crear')}>
            <UserPlus className="h-4 w-4 mr-2" />
            Nuevo Chofer
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1">
              <Users className="h-4 w-4" />
              Total
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-green-600">
              <UserCheck className="h-4 w-4" />
              Activos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{kpis.activos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-green-500">
              🟢 Libres
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.libres}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-yellow-500">
              🟡 Ocupados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.ocupados}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-red-500">
              <AlertCircle className="h-4 w-4" />
              Sin Vehículo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{kpis.sinVehiculo}</div>
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
              {(searchTerm || filtroEstado || filtroAprobacion || filtroPropietario || filtroCalificacion > 0) && (
                <Badge variant="secondary" className="ml-2">
                  {filteredChoferes.length} resultados
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
              placeholder="Buscar por nombre, email, patente, documento..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
              </button>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="estado-laboral">Estado Laboral</Label>
              <Select value={filtroEstado} onValueChange={setFiltroEstado}>
                <SelectTrigger id="estado-laboral">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="libre">🟢 Libre</SelectItem>
                  <SelectItem value="ocupado">🟡 Ocupado</SelectItem>
                  <SelectItem value="inactivo">🔴 Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="aprobacion">Estado Aprobación</Label>
              <Select value={filtroAprobacion} onValueChange={setFiltroAprobacion}>
                <SelectTrigger id="aprobacion">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="pendiente">⏳ Pendiente</SelectItem>
                  <SelectItem value="aprobado">✅ Aprobado</SelectItem>
                  <SelectItem value="rechazado">❌ Rechazado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="propietario">Propietario</Label>
              <Select value={filtroPropietario} onValueChange={setFiltroPropietario}>
                <SelectTrigger id="propietario">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {showFilters && (
            <div className="grid gap-4 md:grid-cols-3 pt-4 border-t">
              <div className="space-y-1">
                <Label>Calificación Mínima</Label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={filtroCalificacion}
                    onChange={(e) => setFiltroCalificacion(parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium min-w-[40px]">
                    {filtroCalificacion} ⭐
                  </span>
                </div>
              </div>
              <div className="space-y-1">
                <Label>Total Viajes</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input type="number" placeholder="Mín" />
                  <Input type="number" placeholder="Máx" />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Fecha de Registro</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input type="date" />
                  <Input type="date" />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabla */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <span>Listado de Choferes</span>
            <Badge variant="secondary">{filteredChoferes.length} choferes</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Chofer</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Vehículo</TableHead>
                  <TableHead>Calificación</TableHead>
                  <TableHead>Viajes</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredChoferes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      {choferes.length === 0 ? 'No hay choferes registrados' : 'No se encontraron choferes con los filtros aplicados'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredChoferes.map((chofer) => (
                    <TableRow key={chofer.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {chofer.foto_perfil_url ? (
                            <img
                              src={chofer.foto_perfil_url}
                              alt={chofer.nombre}
                              className="w-8 h-8 rounded-full object-cover"
                            />
                          ) : (
                            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                              {chofer.nombre?.charAt(0) || '?'}
                            </div>
                          )}
                          <div>
                            <p className="font-medium text-sm">
                              {chofer.nombre} {chofer.apellido}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {chofer.documento || 'Sin DNI'}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{chofer.email}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {getEstadoBadge(chofer.estado_laboral)}
                          <div>{getAprobacionBadge(chofer.estado_aprobacion)}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {chofer.vehiculo ? (
                          <div>
                            <p className="font-medium text-sm">{chofer.vehiculo.patente}</p>
                            <p className="text-xs text-muted-foreground">
                              {chofer.vehiculo.marca} {chofer.vehiculo.modelo}
                            </p>
                          </div>
                        ) : (
                          <span className="text-xs text-red-500">Sin vehículo</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">
                            {chofer.calificacion_promedio?.toFixed(1) || 'N/A'}
                          </span>
                          {chofer.total_calificaciones > 0 && (
                            <span className="text-xs text-muted-foreground">
                              ({chofer.total_calificaciones})
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{chofer.total_viajes || 0}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button asChild variant="ghost" size="icon" className="h-8 w-8">
                            <Link href={`/choferes/${chofer.id}`} title="Ver">
                              <Eye className="h-4 w-4" />
                            </Link>
                          </Button>
                          <Button asChild variant="ghost" size="icon" className="h-8 w-8">
                            <Link href={`/choferes/${chofer.id}/editar`} title="Editar">
                              <Edit2 className="h-4 w-4" />
                            </Link>
                          </Button>
                          {!chofer.vehiculo && (
                            <Button variant="outline" size="sm" className="h-8 text-xs">
                              <Car className="h-3 w-3 mr-1" />
                              Asignar
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