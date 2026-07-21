'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Eye, Search, FileText, DollarSign, Car, Calendar, Filter } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { apiClient } from '@/lib/api'

// Tipos de gasto predefinidos
const TIPOS_GASTO = [
  'Combustible', 'Lubricantes', 'Seguros', 'Impuestos',
  'Reparaciones', 'Mantenimiento', 'Lavado', 'Peajes',
  'Neumáticos', 'Otros'
]

interface Gasto {
  id: string
  vehiculo_id: string
  vehiculo_patente: string
  tipo_gasto: string
  monto: number
  descripcion: string | null
  kilometraje: number | null
  comprobante_url: string | null
  fecha_gasto: string
  created_at: string
}

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface ResumenGastos {
  total_gastos: number
  por_tipo: Record<string, number>
  por_vehiculo: { patente: string; total: number }[]
  periodo_desde: string
  periodo_hasta: string
}

export default function GastosPage() {
  const router = useRouter()
  const [gastos, setGastos] = useState<Gasto[]>([])
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [resumen, setResumen] = useState<ResumenGastos | null>(null)
  const [loading, setLoading] = useState(true)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [modalEditar, setModalEditar] = useState(false)
  const [gastoAEliminar, setGastoAEliminar] = useState<Gasto | null>(null)
  const [gastoEditando, setGastoEditando] = useState<Gasto | null>(null)
  
  // Filtros
  const [filtroVehiculo, setFiltroVehiculo] = useState('')
  const [filtroTipo, setFiltroTipo] = useState('')
  const [filtroDesde, setFiltroDesde] = useState('')
  const [filtroHasta, setFiltroHasta] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(0)
  const [totalGastos, setTotalGastos] = useState(0)

  const [formData, setFormData] = useState({
    vehiculo_id: '',
    tipo_gasto: '',
    monto: '',
    descripcion: '',
    kilometraje: '',
    fecha_gasto: new Date().toISOString().split('T')[0]
  })

  const LIMIT = 20

  // Cargar vehículos
  const cargarVehiculos = async () => {
    try {
      const res = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(res.data)
    } catch (error: any) {
      console.error('Error cargando vehículos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar vehículos')
    }
  }

  // Cargar gastos con filtros
  const cargarGastos = async (pageNum = 0) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        limit: LIMIT.toString(),
        offset: (pageNum * LIMIT).toString()
      })
      if (filtroVehiculo) params.append('vehiculo_id', filtroVehiculo)
      if (filtroTipo) params.append('tipo_gasto', filtroTipo)
      if (filtroDesde) params.append('desde', filtroDesde)
      if (filtroHasta) params.append('hasta', filtroHasta)

      const res = await apiClient.get(`/api/propietario/gastos?${params.toString()}`)
      setGastos(res.data)
      setPage(pageNum)
    } catch (error: any) {
      console.error('Error cargando gastos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar los gastos')
    } finally {
      setLoading(false)
    }
  }

  // Cargar resumen
  const cargarResumen = async () => {
    try {
      const params = new URLSearchParams()
      if (filtroDesde) params.append('desde', filtroDesde)
      if (filtroHasta) params.append('hasta', filtroHasta)
      
      // Si no hay fechas, usar último mes
      if (!filtroDesde && !filtroHasta) {
        const hoy = new Date()
        const haceUnMes = new Date()
        haceUnMes.setMonth(hoy.getMonth() - 1)
        params.append('desde', haceUnMes.toISOString().split('T')[0])
        params.append('hasta', hoy.toISOString().split('T')[0])
      }

      const res = await apiClient.get(`/api/propietario/gastos/resumen?${params.toString()}`)
      setResumen(res.data)
    } catch (error: any) {
      console.error('Error cargando resumen:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar resumen')
    }
  }

  useEffect(() => {
    Promise.all([cargarVehiculos(), cargarGastos(), cargarResumen()])
  }, [])

  // Aplicar filtros
  const aplicarFiltros = () => {
    setPage(0)
    cargarGastos(0)
    cargarResumen()
  }

  // Limpiar filtros
  const limpiarFiltros = () => {
    setFiltroVehiculo('')
    setFiltroTipo('')
    setFiltroDesde('')
    setFiltroHasta('')
    setSearchTerm('')
    setPage(0)
    cargarGastos(0)
    cargarResumen()
  }

  // Registrar gasto
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.vehiculo_id) {
      toast.error('Selecciona un vehículo')
      return
    }

    try {
      await apiClient.post('/api/propietario/gasto', {
        vehiculo_id: formData.vehiculo_id,
        tipo_gasto: formData.tipo_gasto,
        monto: parseFloat(formData.monto),
        descripcion: formData.descripcion || undefined,
        kilometraje: parseInt(formData.kilometraje) || undefined,
        fecha_gasto: formData.fecha_gasto
      })

      toast.success('Gasto registrado correctamente')
      setModalAbierto(false)
      setFormData({
        vehiculo_id: '',
        tipo_gasto: '',
        monto: '',
        descripcion: '',
        kilometraje: '',
        fecha_gasto: new Date().toISOString().split('T')[0]
      })
      cargarGastos(page)
      cargarResumen()
    } catch (error: any) {
      console.error('Error al registrar gasto:', error)
      toast.error(error?.response?.data?.detail || 'Error al registrar gasto')
    }
  }

  // Editar gasto
  const handleEditar = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!gastoEditando) return

    try {
      await apiClient.put(`/api/propietario/gasto/${gastoEditando.id}`, {
        tipo_gasto: formData.tipo_gasto,
        monto: parseFloat(formData.monto),
        descripcion: formData.descripcion || undefined,
        kilometraje: parseInt(formData.kilometraje) || undefined,
        fecha_gasto: formData.fecha_gasto
      })

      toast.success('Gasto actualizado correctamente')
      setModalEditar(false)
      setGastoEditando(null)
      cargarGastos(page)
      cargarResumen()
    } catch (error: any) {
      console.error('Error al actualizar gasto:', error)
      toast.error(error?.response?.data?.detail || 'Error al actualizar gasto')
    }
  }

  // Eliminar gasto
  const handleEliminar = async () => {
    if (!gastoAEliminar) return

    try {
      await apiClient.delete(`/api/propietario/gasto/${gastoAEliminar.id}`)
      toast.success('Gasto eliminado correctamente')
      setGastoAEliminar(null)
      cargarGastos(page)
      cargarResumen()
    } catch (error: any) {
      console.error('Error al eliminar gasto:', error)
      toast.error(error?.response?.data?.detail || 'Error al eliminar gasto')
    }
  }

  // Abrir modal de edición
  const abrirEditar = (gasto: Gasto) => {
    setGastoEditando(gasto)
    setFormData({
      vehiculo_id: gasto.vehiculo_id,
      tipo_gasto: gasto.tipo_gasto,
      monto: gasto.monto.toString(),
      descripcion: gasto.descripcion || '',
      kilometraje: gasto.kilometraje?.toString() || '',
      fecha_gasto: gasto.fecha_gasto
    })
    setModalEditar(true)
  }

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const gastosFiltrados = gastos.filter(g =>
    g.vehiculo_patente.toLowerCase().includes(searchTerm.toLowerCase()) ||
    g.tipo_gasto.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (g.descripcion || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6 pb-24">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Gastos</h1>
          <p className="text-muted-foreground">Gestiona los gastos de tus vehículos</p>
        </div>
        <Button onClick={() => setModalAbierto(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo gasto
        </Button>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground">Total gastos</p>
              <p className="text-2xl font-bold text-red-600">{formatCurrency(resumen.total_gastos)}</p>
              <p className="text-xs text-muted-foreground">
                {resumen.periodo_desde} - {resumen.periodo_hasta}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground">Categorías</p>
              <p className="text-2xl font-bold">{Object.keys(resumen.por_tipo).length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground">Vehículos</p>
              <p className="text-2xl font-bold">{resumen.por_vehiculo.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground">Gasto promedio</p>
              <p className="text-2xl font-bold">
                {resumen.por_vehiculo.length > 0 
                  ? formatCurrency(resumen.total_gastos / resumen.por_vehiculo.length)
                  : '$0'
                }
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <Label>Vehículo</Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filtroVehiculo}
                onChange={(e) => setFiltroVehiculo(e.target.value)}
              >
                <option value="">Todos</option>
                {vehiculos.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.patente} - {v.marca} {v.modelo}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Tipo</Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
              >
                <option value="">Todos</option>
                {TIPOS_GASTO.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <Label>Desde</Label>
              <Input type="date" value={filtroDesde} onChange={(e) => setFiltroDesde(e.target.value)} />
            </div>
            <div>
              <Label>Hasta</Label>
              <Input type="date" value={filtroHasta} onChange={(e) => setFiltroHasta(e.target.value)} />
            </div>
            <div className="flex items-end gap-2">
              <Button onClick={aplicarFiltros}>Aplicar</Button>
              <Button variant="outline" onClick={limpiarFiltros}>Limpiar</Button>
            </div>
          </div>
          <div className="mt-4">
            <Input
              placeholder="Buscar por patente, tipo o descripción..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-md"
            />
          </div>
        </CardContent>
      </Card>

      {/* Tabla de gastos */}
      <Card>
        <CardHeader>
          <CardTitle>Historial de gastos</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Cargando gastos...</div>
          ) : gastosFiltrados.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto mb-3 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground">No hay gastos registrados</p>
              <Button variant="outline" className="mt-4" onClick={() => setModalAbierto(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Registrar primer gasto
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr className="text-left">
                    <th className="pb-2">Fecha</th>
                    <th className="pb-2">Vehículo</th>
                    <th className="pb-2">Categoría</th>
                    <th className="pb-2">Descripción</th>
                    <th className="pb-2 text-right">Monto</th>
                    <th className="pb-2 text-right">km</th>
                    <th className="pb-2 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {gastosFiltrados.map((g) => (
                    <tr key={g.id} className="border-b hover:bg-muted/50">
                      <td className="py-2 whitespace-nowrap">
                        {new Date(g.fecha_gasto).toLocaleDateString()}
                      </td>
                      <td className="py-2 font-medium">{g.vehiculo_patente}</td>
                      <td className="py-2">{g.tipo_gasto}</td>
                      <td className="py-2 max-w-[200px] truncate" title={g.descripcion || ''}>
                        {g.descripcion || '-'}
                      </td>
                      <td className="py-2 text-right font-medium text-red-600">
                        {formatCurrency(g.monto)}
                      </td>
                      <td className="py-2 text-right">{g.kilometraje ? `${g.kilometraje.toLocaleString()}` : '-'}</td>
                      <td className="py-2 text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => abrirEditar(g)}
                            title="Editar"
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700"
                            onClick={() => setGastoAEliminar(g)}
                            title="Eliminar"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de registro */}
      <Dialog open={modalAbierto} onOpenChange={setModalAbierto}>
        <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Registrar gasto</DialogTitle>
            <DialogDescription>
              Registra un nuevo gasto para tu vehículo
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Vehículo *</Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={formData.vehiculo_id}
                onChange={(e) => setFormData({ ...formData, vehiculo_id: e.target.value })}
                required
              >
                <option value="">Seleccionar vehículo</option>
                {vehiculos.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.patente} - {v.marca} {v.modelo}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label>Categoría *</Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={formData.tipo_gasto}
                onChange={(e) => setFormData({ ...formData, tipo_gasto: e.target.value })}
                required
              >
                <option value="">Seleccionar categoría</option>
                {TIPOS_GASTO.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>Monto ($) *</Label>
                <Input
                  type="number"
                  min="0"
                  step="100"
                  placeholder="0"
                  value={formData.monto}
                  onChange={(e) => setFormData({ ...formData, monto: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Fecha *</Label>
                <Input
                  type="date"
                  value={formData.fecha_gasto}
                  onChange={(e) => setFormData({ ...formData, fecha_gasto: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Kilometraje (km)</Label>
              <Input
                type="number"
                placeholder="km actual"
                value={formData.kilometraje}
                onChange={(e) => setFormData({ ...formData, kilometraje: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea
                placeholder="Detalles del gasto..."
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                rows={2}
              />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t sticky bottom-0 bg-white py-3">
              <Button type="button" variant="outline" onClick={() => setModalAbierto(false)}>
                Cancelar
              </Button>
              <Button type="submit" className="bg-green-600 hover:bg-green-700">
                ✅ Guardar gasto
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de edición */}
      <Dialog open={modalEditar} onOpenChange={setModalEditar}>
        <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar gasto</DialogTitle>
            <DialogDescription>
              Modifica los datos del gasto
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleEditar} className="space-y-4">
            <div className="space-y-2">
              <Label>Vehículo</Label>
              <p className="text-sm font-medium">{gastoEditando?.vehiculo_patente}</p>
            </div>

            <div className="space-y-2">
              <Label>Categoría *</Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={formData.tipo_gasto}
                onChange={(e) => setFormData({ ...formData, tipo_gasto: e.target.value })}
                required
              >
                <option value="">Seleccionar categoría</option>
                {TIPOS_GASTO.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>Monto ($) *</Label>
                <Input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.monto}
                  onChange={(e) => setFormData({ ...formData, monto: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Fecha *</Label>
                <Input
                  type="date"
                  value={formData.fecha_gasto}
                  onChange={(e) => setFormData({ ...formData, fecha_gasto: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Kilometraje (km)</Label>
              <Input
                type="number"
                placeholder="km actual"
                value={formData.kilometraje}
                onChange={(e) => setFormData({ ...formData, kilometraje: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea
                placeholder="Detalles del gasto..."
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                rows={2}
              />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t sticky bottom-0 bg-white py-3">
              <Button type="button" variant="outline" onClick={() => setModalEditar(false)}>
                Cancelar
              </Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                💾 Actualizar gasto
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={!!gastoAEliminar} onOpenChange={() => setGastoAEliminar(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar gasto?</AlertDialogTitle>
            <AlertDialogDescription>
              ¿Estás seguro de que deseas eliminar este gasto?
              <br />
              <span className="font-semibold">{gastoAEliminar?.vehiculo_patente}</span> - 
              <span className="font-semibold"> {gastoAEliminar?.tipo_gasto}</span> - 
              <span className="font-semibold text-red-600"> {formatCurrency(gastoAEliminar?.monto || 0)}</span>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleEliminar} className="bg-red-600 hover:bg-red-700">
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Botón flotante para móvil */}
      <Button
        onClick={() => setModalAbierto(true)}
        className="fixed bottom-6 right-6 rounded-full shadow-lg sm:hidden z-50"
        size="lg"
      >
        <Plus className="h-5 w-5 mr-2" />
        Nuevo
      </Button>
    </div>
  )
}