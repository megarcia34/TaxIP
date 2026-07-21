'use client'

import { useEffect, useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Plus, Wrench, AlertTriangle, Car, Calendar, DollarSign, MapPin } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Mantenimiento {
  id: string
  vehiculo_id: string
  vehiculo_patente: string
  tipo_servicio: string
  taller_nombre: string
  taller_direccion: string | null
  costo: number | null
  kilometraje: number | null
  observaciones: string | null
  fecha_servicio: string
  created_at: string
}

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface AlertaMantenimiento {
  tipo_servicio: string
  tipo_nombre: string
  km_restante: number | null
  dias_restantes: number | null
  alerta_a: string
  urgencia: 'alta' | 'media'
}

interface AlertaVehiculo {
  vehiculo_id: string
  patente: string
  km_actual: number
  mantenimientos_proximos: AlertaMantenimiento[]
}

const TIPO_NOMBRES: Record<string, string> = {
  SERVICE_MENOR: '🔧 Service menor (5.000 km)',
  SERVICE_MAYOR: '🔧 Service mayor (20.000 km)',
  NEUMATICOS: '⭕ Neumáticos',
  FRENOS: '🛑 Frenos',
  DISTRIBUCION: '⏱️ Distribución',
  ALINEACION: '⚙️ Alineación y balanceo',
  CAMBIO_ACEITE: '🛢️ Cambio de aceite',
  LUBRICACION: '🛢️ Lubricación',
  ELECTRICO: '⚡ Sistema eléctrico',
  GENERAL: '📋 Mantenimiento general'
}

const TIPO_SERVICIOS = [
  { value: 'SERVICE_MENOR', label: '🔧 Service menor (5.000 km)' },
  { value: 'SERVICE_MAYOR', label: '🔧 Service mayor (20.000 km)' },
  { value: 'CAMBIO_ACEITE', label: '🛢️ Cambio de aceite' },
  { value: 'FRENOS', label: '🛑 Frenos' },
  { value: 'NEUMATICOS', label: '⭕ Neumáticos' },
  { value: 'ALINEACION', label: '⚙️ Alineación y balanceo' },
  { value: 'LUBRICACION', label: '🛢️ Lubricación' },
  { value: 'ELECTRICO', label: '⚡ Sistema eléctrico' },
  { value: 'DISTRIBUCION', label: '⏱️ Distribución' },
  { value: 'GENERAL', label: '📋 Mantenimiento general' }
]

export default function MantenimientosPage() {
  const [mantenimientos, setMantenimientos] = useState<Mantenimiento[]>([])
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [alertas, setAlertas] = useState<AlertaVehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [page, setPage] = useState(0)
  const [totalMantenimientos, setTotalMantenimientos] = useState(0)
  const [filtroVehiculo, setFiltroVehiculo] = useState('')
  const [filtroTipo, setFiltroTipo] = useState('')
  const [formData, setFormData] = useState({
    vehiculo_id: '',
    tipo_servicio: '',
    taller_nombre: '',
    taller_direccion: '',
    costo: '',
    kilometraje: '',
    observaciones: '',
    fecha_servicio: new Date().toISOString().split('T')[0]
  })
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Funciones para formatear
  const formatCurrency = (value: number | null) => (value ? `$${value.toLocaleString('es-AR')}` : '-')
  const formatKilometraje = (value: number | null) => (value ? `${value.toLocaleString()} km` : '-')
  const getTipoNombre = (tipo: string) => TIPO_NOMBRES[tipo] || tipo.replace('_', ' ').toLowerCase()

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

  // Cargar mantenimientos con filtros y paginación
  const cargarMantenimientos = async (pageNum = 0, vehiculoId = filtroVehiculo, tipoServicio = filtroTipo) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        limit: '20',
        offset: (pageNum * 20).toString()
      })
      if (vehiculoId) params.append('vehiculo_id', vehiculoId)
      if (tipoServicio) params.append('tipo_servicio', tipoServicio)

      const res = await apiClient.get(`/api/propietario/mantenimientos?${params.toString()}`)
      setMantenimientos(res.data)
      setPage(pageNum)
    } catch (error: any) {
      console.error('Error cargando mantenimientos:', error)
      toast.error(error?.response?.data?.detail || 'Error cargando mantenimientos')
    } finally {
      setLoading(false)
    }
  }

  // Cargar alertas
  const cargarAlertas = async () => {
    try {
      const res = await apiClient.get('/api/propietario/mantenimientos/alertas')
      setAlertas(res.data?.vehiculos_con_alertas || [])
    } catch (error: any) {
      console.error('Error cargando alertas:', error)
      toast.error(error?.response?.data?.detail || 'Error cargando alertas')
    }
  }

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      await Promise.all([cargarVehiculos(), cargarMantenimientos(), cargarAlertas()])
    }
    loadData()
  }, [])

  // Buscar con filtros
  const aplicarFiltros = () => {
    setPage(0)
    cargarMantenimientos(0, filtroVehiculo, filtroTipo)
  }

  // Registrar mantenimiento
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.vehiculo_id) {
      toast.error('Selecciona un vehículo')
      return
    }
    if (!formData.tipo_servicio) {
      toast.error('Selecciona un tipo de servicio')
      return
    }

    try {
      // Crear mantenimiento (sin comprobante)
      const res = await apiClient.post('/api/propietario/mantenimiento', {
        vehiculo_id: formData.vehiculo_id,
        tipo_servicio: formData.tipo_servicio,
        taller_nombre: formData.taller_nombre,
        taller_direccion: formData.taller_direccion || undefined,
        costo: parseFloat(formData.costo) || undefined,
        kilometraje: parseInt(formData.kilometraje) || undefined,
        observaciones: formData.observaciones || undefined,
        fecha_servicio: formData.fecha_servicio
      })

      const registro = res.data

      // Si hay archivo para el comprobante, subirlo
      if (fileInputRef.current && fileInputRef.current.files?.length) {
        const formDataFile = new FormData()
        formDataFile.append('file', fileInputRef.current.files[0])
        
        try {
          await apiClient.post(`/api/propietario/mantenimientos/${registro.id}/comprobante`, formDataFile, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
        } catch (uploadError: any) {
          toast.error(uploadError?.response?.data?.detail || 'Error al subir comprobante')
        }
      }

      toast.success('✅ Mantenimiento registrado correctamente')
      setModalAbierto(false)
      setFormData({
        vehiculo_id: '',
        tipo_servicio: '',
        taller_nombre: '',
        taller_direccion: '',
        costo: '',
        kilometraje: '',
        observaciones: '',
        fecha_servicio: new Date().toISOString().split('T')[0]
      })
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      cargarMantenimientos(page, filtroVehiculo, filtroTipo)
      cargarAlertas()
    } catch (error: any) {
      console.error('Error:', error)
      toast.error(error?.response?.data?.detail || 'Error de conexión')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Wrench className="h-8 w-8 animate-spin mx-auto mb-2 text-muted-foreground" />
          <p className="text-muted-foreground">Cargando mantenimientos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-24">

      {/* Header y filtros */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Mantenimientos</h1>
          <p className="text-muted-foreground">Registra y consulta el historial de servicios</p>
        </div>
        <Button onClick={() => setModalAbierto(true)} className="hidden sm:inline-flex">
          <Plus className="h-4 w-4 mr-2" />
          Nuevo mantenimiento
        </Button>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <Label htmlFor="filtroVehiculo">Filtrar por vehículo</Label>
          <select
            id="filtroVehiculo"
            className="border border-gray-300 rounded px-3 py-1"
            value={filtroVehiculo}
            onChange={(e) => setFiltroVehiculo(e.target.value)}
          >
            <option value="">Todos</option>
            {vehiculos.map(v => (
              <option key={v.id} value={v.id}>
                {v.patente} - {v.marca} {v.modelo}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="filtroTipo">Filtrar por servicio</Label>
          <select
            id="filtroTipo"
            className="border border-gray-300 rounded px-3 py-1"
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
          >
            <option value="">Todos</option>
            {TIPO_SERVICIOS.map(t => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <Button onClick={aplicarFiltros}>Aplicar filtros</Button>
      </div>

      {/* Alertas de mantenimiento */}
      {alertas.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              Alertas de mantenimiento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alertas.map((vehiculo) => (
                <div key={vehiculo.vehiculo_id} className="border-b pb-3 last:border-0">
                  <div className="flex items-center gap-2 mb-2">
                    <Car className="h-4 w-4 text-muted-foreground" />
                    <span className="font-semibold">{vehiculo.patente}</span>
                    <span className="text-xs text-muted-foreground">
                      (km: {vehiculo.km_actual.toLocaleString()})
                    </span>
                  </div>
                  <div className="space-y-1 pl-6">
                    {vehiculo.mantenimientos_proximos.map((m, idx) => {
                      const color = m.urgencia === 'alta' ? 'text-red-600' : 'text-yellow-700'
                      return (
                        <div key={idx} className={`flex items-center justify-between text-sm ${color}`}>
                          <span>{getTipoNombre(m.tipo_servicio)}</span>
                          <div className="flex gap-2">
                            {m.km_restante !== null && <span>a {m.km_restante.toLocaleString()} km</span>}
                            {m.dias_restantes !== null && <span>en {m.dias_restantes} días</span>}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabla de mantenimientos */}
      <Card>
        <CardHeader>
          <CardTitle>Historial de mantenimientos</CardTitle>
        </CardHeader>
        <CardContent>
          {mantenimientos.length === 0 ? (
            <div className="text-center py-12">
              <Wrench className="h-12 w-12 mx-auto mb-3 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground">No hay mantenimientos registrados</p>
              <Button variant="outline" className="mt-4" onClick={() => setModalAbierto(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Registrar primer mantenimiento
              </Button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr className="text-left">
                      <th className="pb-2">Fecha</th>
                      <th className="pb-2">Vehículo</th>
                      <th className="pb-2">Servicio</th>
                      <th className="pb-2">Taller</th>
                      <th className="pb-2 text-right">Costo</th>
                      <th className="pb-2 text-right">km</th>
                      <th className="pb-2">Observaciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mantenimientos.map((m) => (
                      <tr key={m.id} className="border-b hover:bg-muted/50">
                        <td className="py-2 whitespace-nowrap">{new Date(m.fecha_servicio).toLocaleDateString()}</td>
                        <td className="py-2 font-medium whitespace-nowrap">{m.vehiculo_patente}</td>
                        <td className="py-2 whitespace-nowrap">{getTipoNombre(m.tipo_servicio)}</td>
                        <td className="py-2 max-w-[150px] truncate" title={m.taller_nombre}>{m.taller_nombre}</td>
                        <td className="py-2 text-right whitespace-nowrap">{formatCurrency(m.costo)}</td>
                        <td className="py-2 text-right whitespace-nowrap">{formatKilometraje(m.kilometraje)}</td>
                        <td className="py-2 max-w-[200px] truncate text-muted-foreground" title={m.observaciones || ''}>{m.observaciones || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginación simple */}
              <div className="flex justify-between mt-4">
                <Button disabled={page === 0} onClick={() => { setPage(page - 1); cargarMantenimientos(page - 1) }}>
                  Anterior
                </Button>
                <Button onClick={() => { setPage(page + 1); cargarMantenimientos(page + 1) }}>
                  Siguiente
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Botón flotante para móvil */}
      <Button
        onClick={() => setModalAbierto(true)}
        className="fixed bottom-6 right-6 rounded-full shadow-lg sm:hidden z-50"
        size="lg"
      >
        <Plus className="h-5 w-5 mr-2" />
        Nuevo
      </Button>

      {/* Modal registro mantenimiento */}
      <Dialog open={modalAbierto} onOpenChange={setModalAbierto}>
        <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Registrar mantenimiento</DialogTitle>
            <DialogDescription>
              Completa los datos del servicio realizado en tu vehículo
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4" encType="multipart/form-data">
            {/* Vehículo */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Car className="h-4 w-4" />
                Vehículo *
              </Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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

            {/* Tipo servicio */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Wrench className="h-4 w-4" />
                Tipo de servicio *
              </Label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.tipo_servicio}
                onChange={(e) => setFormData({ ...formData, tipo_servicio: e.target.value })}
                required
              >
                <option value="">Seleccionar tipo</option>
                {TIPO_SERVICIOS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Taller y fecha */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <MapPin className="h-3 w-3" />
                  Taller
                </Label>
                <Input
                  placeholder="Nombre del taller"
                  value={formData.taller_nombre}
                  onChange={(e) => setFormData({ ...formData, taller_nombre: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Calendar className="h-3 w-3" />
                  Fecha *
                </Label>
                <Input
                  type="date"
                  value={formData.fecha_servicio}
                  onChange={(e) => setFormData({ ...formData, fecha_servicio: e.target.value })}
                  required
                />
              </div>
            </div>

            {/* Costo y kilometraje */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <DollarSign className="h-3 w-3" />
                  Costo ($)
                </Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={formData.costo}
                  onChange={(e) => setFormData({ ...formData, costo: e.target.value })}
                />
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
            </div>

            {/* Observaciones */}
            <div className="space-y-2">
              <Label>Observaciones</Label>
              <Textarea
                placeholder="Detalles del servicio realizado..."
                value={formData.observaciones}
                onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                rows={2}
              />
            </div>

            {/* Subir comprobante */}
            <div className="space-y-2">
              <Label>Subir comprobante (opcional)</Label>
              <Input type="file" accept="image/*,.pdf" ref={fileInputRef} />
            </div>

            {/* Botones - Sticky */}
            <div className="flex justify-end gap-2 pt-4 border-t sticky bottom-0 bg-white py-3 mt-2">
              <Button type="button" variant="outline" onClick={() => setModalAbierto(false)}>
                Cancelar
              </Button>
              <Button type="submit" className="bg-green-600 hover:bg-green-700">
                ✅ Guardar mantenimiento
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}