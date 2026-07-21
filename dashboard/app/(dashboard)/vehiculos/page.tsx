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
  Plus, 
  Search, 
  Filter, 
  X, 
  Eye, 
  Edit2, 
  Trash2, 
  Car, 
  User,
  Users,
  AlertCircle,
  Loader2,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import Link from 'next/link'
import { apiClient } from '@/lib/api'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  numero_licencia: string
  activo: boolean
  chofer?: {
    id: string
    nombre: string
    apellido: string
  }
  propietario?: {
    id: string
    nombre: string
  }
  created_at: string
}

export default function VehiculosPage() {
  const { status } = useSession()
  const router = useRouter()
  const { toast } = useToast()
  
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filtroEstado, setFiltroEstado] = useState('')
  const [filtroPropietario, setFiltroPropietario] = useState('')
  const [filtroChofer, setFiltroChofer] = useState('')
  const [filtroMarca, setFiltroMarca] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // ============================================
  // OBTENER VEHÍCULOS
  // ============================================
  const fetchVehiculos = async () => {
    try {
      setLoading(true)
      
      const response = await apiClient.get('/api/vehiculos/lista')
      
      console.log('✅ Vehículos obtenidos:', response.data)
      
      const data = response.data
      const vehiculosData = Array.isArray(data) ? data : (data.data || data || [])
      
      setVehiculos(vehiculosData)
      
    } catch (error: any) {
      console.error('Error fetching vehiculos:', error)
      
      if (error.response?.status === 401) {
        toast({
          title: 'Sesión expirada',
          description: 'Por favor, vuelve a iniciar sesión',
          variant: 'destructive',
        })
      } else {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'No se pudieron cargar los vehículos',
          variant: 'destructive',
        })
      }
      setVehiculos([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchVehiculos()
    }
  }, [status])

  // Filtrar vehículos
  const filteredVehiculos = useMemo(() => {
    let result = vehiculos

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(v => 
        (v.patente || '').toLowerCase().includes(term) ||
        (v.marca || '').toLowerCase().includes(term) ||
        (v.modelo || '').toLowerCase().includes(term) ||
        (v.numero_licencia || '').toLowerCase().includes(term) ||
        (v.chofer?.nombre || '').toLowerCase().includes(term) ||
        (v.chofer?.apellido || '').toLowerCase().includes(term) ||
        (v.propietario?.nombre || '').toLowerCase().includes(term)
      )
    }

    if (filtroEstado) {
      result = result.filter(v => {
        if (filtroEstado === 'activo') return v.activo === true
        if (filtroEstado === 'inactivo') return v.activo === false
        return true
      })
    }

    if (filtroChofer) {
      if (filtroChofer === 'con_chofer') {
        result = result.filter(v => v.chofer !== undefined && v.chofer !== null)
      } else if (filtroChofer === 'sin_chofer') {
        result = result.filter(v => v.chofer === undefined || v.chofer === null)
      }
    }

    if (filtroPropietario) {
      result = result.filter(v => v.propietario?.id === filtroPropietario)
    }

    if (filtroMarca) {
      result = result.filter(v => (v.marca || '').toLowerCase().includes(filtroMarca.toLowerCase()))
    }

    return result
  }, [vehiculos, searchTerm, filtroEstado, filtroPropietario, filtroChofer, filtroMarca])

  // KPIs
  const kpis = useMemo(() => {
    const total = vehiculos.length
    const activos = vehiculos.filter(v => v.activo === true)
    const inactivos = vehiculos.filter(v => v.activo === false)
    const conChofer = vehiculos.filter(v => v.chofer !== undefined && v.chofer !== null)
    const sinChofer = vehiculos.filter(v => v.chofer === undefined || v.chofer === null)

    return {
      total,
      activos: activos.length,
      inactivos: inactivos.length,
      conChofer: conChofer.length,
      sinChofer: sinChofer.length,
    }
  }, [vehiculos])

  const getEstadoBadge = (activo: boolean) => {
    if (activo) {
      return <Badge className="bg-green-500 hover:bg-green-600">🟢 Activo</Badge>
    }
    return <Badge variant="destructive">🔴 Inactivo</Badge>
  }

  const getChoferBadge = (chofer?: { nombre: string; apellido: string }) => {
    if (chofer) {
      return <Badge className="bg-blue-100 text-blue-800">{chofer.nombre} {chofer.apellido}</Badge>
    }
    return <Badge className="bg-yellow-100 text-yellow-800">Sin chofer</Badge>
  }

  const clearFilters = () => {
    setSearchTerm('')
    setFiltroEstado('')
    setFiltroPropietario('')
    setFiltroChofer('')
    setFiltroMarca('')
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
          <h1 className="text-2xl font-bold tracking-tight">Vehículos</h1>
          <p className="text-muted-foreground">
            Gestión de la flota de vehículos
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchVehiculos} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button size="sm" onClick={() => router.push('/vehiculos/crear')}>
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Vehículo
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1">
              <Car className="h-4 w-4" />
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
              <CheckCircle className="h-4 w-4" />
              Activos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{kpis.activos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-red-500">
              <XCircle className="h-4 w-4" />
              Inactivos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{kpis.inactivos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-blue-500">
              <User className="h-4 w-4" />
              Con Chofer
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">{kpis.conChofer}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-1 text-yellow-500">
              <AlertCircle className="h-4 w-4" />
              Sin Chofer
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500">{kpis.sinChofer}</div>
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
              {(searchTerm || filtroEstado || filtroPropietario || filtroChofer || filtroMarca) && (
                <Badge variant="secondary" className="ml-2">
                  {filteredVehiculos.length} resultados
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
              placeholder="Buscar por patente, marca, modelo, licencia, chofer, propietario..."
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
              <Label htmlFor="estado">Estado</Label>
              <Select value={filtroEstado} onValueChange={setFiltroEstado}>
                <SelectTrigger id="estado">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="activo">🟢 Activo</SelectItem>
                  <SelectItem value="inactivo">🔴 Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="chofer">Chofer</Label>
              <Select value={filtroChofer} onValueChange={setFiltroChofer}>
                <SelectTrigger id="chofer">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="con_chofer">Con chofer</SelectItem>
                  <SelectItem value="sin_chofer">Sin chofer</SelectItem>
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
            <div className="grid gap-4 md:grid-cols-2 pt-4 border-t">
              <div className="space-y-1">
                <Label htmlFor="marca">Marca</Label>
                <Input
                  id="marca"
                  placeholder="Ej: Toyota, Ford, Chevrolet..."
                  value={filtroMarca}
                  onChange={(e) => setFiltroMarca(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <Label>Año</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input type="number" placeholder="Desde" />
                  <Input type="number" placeholder="Hasta" />
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
            <span>Listado de Vehículos</span>
            <Badge variant="secondary">{filteredVehiculos.length} vehículos</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patente</TableHead>
                  <TableHead>Vehículo</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Chofer</TableHead>
                  <TableHead>Propietario</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredVehiculos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                      {vehiculos.length === 0 ? 'No hay vehículos registrados' : 'No se encontraron vehículos con los filtros aplicados'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredVehiculos.map((vehiculo) => (
                    <TableRow key={vehiculo.id}>
                      <TableCell>
                        <div className="font-medium text-sm">{vehiculo.patente}</div>
                        {vehiculo.numero_licencia && (
                          <div className="text-xs text-muted-foreground">
                            Lic: {vehiculo.numero_licencia}
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium text-sm">
                            {vehiculo.marca} {vehiculo.modelo}
                          </p>
                          <p className="text-xs text-muted-foreground">{vehiculo.anio || 'Año N/A'}</p>
                        </div>
                      </TableCell>
                      <TableCell>{getEstadoBadge(vehiculo.activo)}</TableCell>
                      <TableCell>{getChoferBadge(vehiculo.chofer)}</TableCell>
                      <TableCell>
                        {vehiculo.propietario ? (
                          <span className="text-sm">{vehiculo.propietario.nombre}</span>
                        ) : (
                          <span className="text-xs text-muted-foreground">No asignado</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button asChild variant="ghost" size="icon" className="h-8 w-8">
                            <Link href={`/vehiculos/${vehiculo.id}`} title="Ver">
                              <Eye className="h-4 w-4" />
                            </Link>
                          </Button>
                          <Button asChild variant="ghost" size="icon" className="h-8 w-8">
                            <Link href={`/vehiculos/${vehiculo.id}/editar`} title="Editar">
                              <Edit2 className="h-4 w-4" />
                            </Link>
                          </Button>
                          {!vehiculo.chofer && (
                            <Button variant="outline" size="sm" className="h-8 text-xs">
                              <User className="h-3 w-3 mr-1" />
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