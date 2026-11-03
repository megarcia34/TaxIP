'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search, Plus, DollarSign, Loader2, Filter, Wallet, TrendingUp, BarChart3
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'

// ============================================================
// TIPOS
// ============================================================

interface Ingreso {
  id: string
  tipo: 'viaje' | 'recaudacion_manual'
  monto: number
  fecha: string
  descripcion: string
  vehiculo_patente: string
  chofer_nombre: string
  metodo_pago: string
  origen_tipo: string
}

interface ResumenIngresos {
  periodo: { desde: string; hasta: string }
  totales: {
    viajes: number
    manuales: number
    general: number
  }
  por_metodo_pago: Record<string, number>
  por_canal: Record<string, number>
}

interface VehiculoSimple {
  id: string
  patente: string
  marca: string
  modelo: string
}

// ============================================================
// HELPERS
// ============================================================

const fmtMoney = (n: number) => `$${n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`

// Convierte cualquier fecha (ISO o DD/MM/YYYY) a YYYY-MM-DD
const formatFechaISO = (fecha: string): string => {
  if (!fecha) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(fecha)) return fecha
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(fecha)) {
    const [d, m, y] = fecha.split('/')
    return `${y}-${m}-${d}`
  }
  return fecha
}

const CANAL_LABELS: Record<string, string> = {
  plataforma: 'App / Landing',
  app_usuario: 'App / Landing',
  via_publica: 'Calle',
  qr: 'QR',
  corporativo: 'Corporativo',
  despacho_manual: 'Despacho Manual',
  manual: 'Manual',
  desconocido: 'Sin origen',
}

const getDefaultDates = () => {
  const hoy = new Date()
  const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  return {
    desde: primerDia.toISOString().split('T')[0],
    hasta: hoy.toISOString().split('T')[0],
  }
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export default function PropietarioIngresosPage() {
  const { user } = useAuth()
  const [propietarioId, setPropietarioId] = useState<string | null>(null)

  const defaultDates = getDefaultDates()

  // Estado principal
  const [ingresos, setIngresos] = useState<Ingreso[]>([])
  const [resumen, setResumen] = useState<ResumenIngresos | null>(null)
  const [vehiculos, setVehiculos] = useState<VehiculoSimple[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [loadingForm, setLoadingForm] = useState(false)

  // Filtros
  const [filtroDesde, setFiltroDesde] = useState(defaultDates.desde)
  const [filtroHasta, setFiltroHasta] = useState(defaultDates.hasta)
  const [filtroVehiculo, setFiltroVehiculo] = useState('')
  const [filtroTipo, setFiltroTipo] = useState('')

  // Modal
  const [showRecaudacionModal, setShowRecaudacionModal] = useState(false)
  const [recaudacionData, setRecaudacionData] = useState({
    vehiculo_id: '',
    monto: 0,
    descripcion: '',
    fecha: new Date().toISOString().split('T')[0],
  })

  // ============================================================
  // CARGA DE DATOS
  // ============================================================

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])

  const cargarIngresos = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      const desdeISO = formatFechaISO(filtroDesde)
      const hastaISO = formatFechaISO(filtroHasta)
      if (desdeISO) params.append('desde', desdeISO)
      if (hastaISO) params.append('hasta', hastaISO)
      if (filtroVehiculo) params.append('vehiculo_id', filtroVehiculo)
      if (filtroTipo) params.append('tipo', filtroTipo)

      const res = await apiClient.get(`/api/propietario/ingresos?${params.toString()}`)
      setIngresos(res.data)
    } catch (error: any) {
      console.error('Error al cargar ingresos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar ingresos')
    } finally {
      setLoading(false)
    }
  }

  const cargarResumen = async () => {
    try {
      const params = new URLSearchParams()
      const desdeISO = formatFechaISO(filtroDesde)
      const hastaISO = formatFechaISO(filtroHasta)
      if (desdeISO) params.append('desde', desdeISO)
      if (hastaISO) params.append('hasta', hastaISO)

      const res = await apiClient.get(`/api/propietario/ingresos/resumen?${params.toString()}`)
      setResumen(res.data)
    } catch (error: any) {
      console.error('Error al cargar resumen:', error)
    }
  }

  const cargarVehiculos = async () => {
    try {
      const res = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(res.data)
    } catch (error: any) {
      console.error('Error al cargar vehículos:', error)
    }
  }

  useEffect(() => {
    if (user) {
      cargarIngresos()
      cargarResumen()
      cargarVehiculos()
    }
  }, [user, propietarioId])

  // ============================================================
  // ACCIONES
  // ============================================================

  const aplicarFiltros = () => {
    cargarIngresos()
    cargarResumen()
  }

  const limpiarFiltros = () => {
    const d = getDefaultDates()
    setFiltroDesde(d.desde)
    setFiltroHasta(d.hasta)
    setFiltroVehiculo('')
    setFiltroTipo('')
    setSearch('')
    setTimeout(() => {
      cargarIngresos()
      cargarResumen()
    }, 50)
  }

  const registrarRecaudacion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (recaudacionData.monto <= 0) {
      toast.error('El monto debe ser mayor a 0')
      return
    }
    setLoadingForm(true)
    try {
      await apiClient.post('/api/propietario/ingresos/recaudacion-manual', {
        vehiculo_id: recaudacionData.vehiculo_id || null,
        monto: recaudacionData.monto,
        descripcion: recaudacionData.descripcion,
        fecha: recaudacionData.fecha,
      })
      toast.success('Recaudación registrada')
      setShowRecaudacionModal(false)
      setRecaudacionData({
        vehiculo_id: '',
        monto: 0,
        descripcion: '',
        fecha: new Date().toISOString().split('T')[0],
      })
      cargarIngresos()
      cargarResumen()
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Error al registrar')
    } finally {
      setLoadingForm(false)
    }
  }

  // ============================================================
  // DERIVADOS
  // ============================================================

  const filteredIngresos = ingresos.filter(i =>
    i.vehiculo_patente?.toLowerCase().includes(search.toLowerCase()) ||
    i.descripcion?.toLowerCase().includes(search.toLowerCase()) ||
    i.chofer_nombre?.toLowerCase().includes(search.toLowerCase())
  )

  const getTipoBadge = (tipo: string) => {
    if (tipo === 'viaje') return { label: 'Viaje', variant: 'default' as const }
    if (tipo === 'recaudacion_manual') return { label: 'Manual', variant: 'secondary' as const }
    return { label: tipo, variant: 'outline' as const }
  }

  // ============================================================
  // RENDER
  // ============================================================

  if (loading && ingresos.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-24">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Ingresos</h1>
          <p className="text-muted-foreground">Gestión de ingresos de la flota</p>
        </div>
        <Button onClick={() => setShowRecaudacionModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Recaudación Manual
        </Button>
      </div>

      {/* KPIs */}
      {resumen && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <TrendingUp className="h-4 w-4" />
                Total del período
              </div>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {fmtMoney(resumen.totales.general)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {resumen.periodo.desde} → {resumen.periodo.hasta}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <DollarSign className="h-4 w-4" />
                Viajes
              </div>
              <p className="text-2xl font-bold mt-1">{fmtMoney(resumen.totales.viajes)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {resumen.totales.general > 0
                  ? `${((resumen.totales.viajes / resumen.totales.general) * 100).toFixed(1)}% del total`
                  : '0%'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <Wallet className="h-4 w-4" />
                Manuales
              </div>
              <p className="text-2xl font-bold mt-1">{fmtMoney(resumen.totales.manuales)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {resumen.totales.general > 0
                  ? `${((resumen.totales.manuales / resumen.totales.general) * 100).toFixed(1)}% del total`
                  : '0%'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <BarChart3 className="h-4 w-4" />
                Efectivo / Electrónico
              </div>
              <p className="text-sm font-semibold mt-1">
                <span className="text-green-600">{fmtMoney(resumen.por_metodo_pago['efectivo'] || 0)}</span>
                <span className="text-muted-foreground"> / </span>
                <span className="text-blue-600">
                  {fmtMoney(
                    Object.entries(resumen.por_metodo_pago)
                      .filter(([k]) => k !== 'efectivo')
                      .reduce((sum, [, v]) => sum + v, 0)
                  )}
                </span>
              </p>
              <p className="text-xs text-muted-foreground mt-1">efectivo / otros</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Split por canal */}
      {resumen && Object.keys(resumen.por_canal).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Desglose por Canal</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(resumen.por_canal).map(([canal, monto]) => {
                const total = Object.values(resumen.por_canal).reduce((s, v) => s + v, 0)
                const pct = total > 0 ? (monto / total) * 100 : 0
                return (
                  <div key={canal} className="flex items-center gap-3">
                    <span className="text-sm w-32">{CANAL_LABELS[canal] || canal}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                      <div
                        className="h-full bg-green-500 transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-28 text-right">{fmtMoney(monto)}</span>
                    <span className="text-xs text-muted-foreground w-12 text-right">{pct.toFixed(0)}%</span>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
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
              <Label>Desde</Label>
              <Input type="date" value={filtroDesde} onChange={(e) => setFiltroDesde(e.target.value)} />
            </div>
            <div>
              <Label>Hasta</Label>
              <Input type="date" value={filtroHasta} onChange={(e) => setFiltroHasta(e.target.value)} />
            </div>
            <div>
              <Label>Vehículo</Label>
              <Select value={filtroVehiculo || 'all'} onValueChange={(v) => setFiltroVehiculo(v === 'all' ? '' : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {vehiculos.map((v) => (
                    <SelectItem key={v.id} value={v.id}>
                      {v.patente}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Tipo</Label>
              <Select value={filtroTipo || 'all'} onValueChange={(v) => setFiltroTipo(v === 'all' ? '' : v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="viaje">Viajes</SelectItem>
                  <SelectItem value="recaudacion_manual">Manuales</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end gap-2">
              <Button onClick={aplicarFiltros}>Aplicar</Button>
              <Button variant="outline" onClick={limpiarFiltros}>Limpiar</Button>
            </div>
          </div>
          <div className="mt-4">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por vehículo, descripción o chofer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 max-w-md"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabla */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Listado de Ingresos ({filteredIngresos.length})</CardTitle>
            <span className="text-sm text-muted-foreground">
              Total filtrado: <span className="font-bold text-green-600">{fmtMoney(filteredIngresos.reduce((s, i) => s + i.monto, 0))}</span>
            </span>
          </div>
        </CardHeader>
        <CardContent>
          {filteredIngresos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <DollarSign className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay ingresos en el período seleccionado</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Fecha</th>
                    <th className="text-left py-3">Vehículo</th>
                    <th className="text-left py-3">Tipo</th>
                    <th className="text-left py-3">Descripción</th>
                    <th className="text-left py-3">Chofer</th>
                    <th className="text-left py-3">Método</th>
                    <th className="text-right py-3">Monto</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIngresos.map((i) => {
                    const tipo = getTipoBadge(i.tipo)
                    return (
                      <tr key={i.id} className="border-b hover:bg-muted/50">
                        <td className="py-3 whitespace-nowrap">
                          {new Date(i.fecha).toLocaleDateString('es-AR')}
                        </td>
                        <td className="py-3 font-medium">{i.vehiculo_patente}</td>
                        <td className="py-3">
                          <Badge variant={tipo.variant}>{tipo.label}</Badge>
                        </td>
                        <td className="py-3 text-muted-foreground max-w-[200px] truncate" title={i.descripcion}>
                          {i.descripcion}
                        </td>
                        <td className="py-3">{i.chofer_nombre}</td>
                        <td className="py-3">
                          <Badge variant="outline">{i.metodo_pago}</Badge>
                        </td>
                        <td className="py-3 text-right font-semibold text-green-600">
                          {fmtMoney(i.monto)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Recaudación Manual */}
      <Dialog open={showRecaudacionModal} onOpenChange={setShowRecaudacionModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Registrar Recaudación Manual</DialogTitle>
          </DialogHeader>
          <form onSubmit={registrarRecaudacion}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Vehículo (opcional)</Label>
                <Select
                  value={recaudacionData.vehiculo_id || 'none'}
                  onValueChange={(v) => setRecaudacionData({ ...recaudacionData, vehiculo_id: v === 'none' ? '' : v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sin vehículo específico" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Sin vehículo específico</SelectItem>
                    {vehiculos.map((v) => (
                      <SelectItem key={v.id} value={v.id}>
                        {v.patente} - {v.marca} {v.modelo}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Monto ($)</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={recaudacionData.monto}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, monto: Number(e.target.value) })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Descripción</Label>
                <Input
                  value={recaudacionData.descripcion}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, descripcion: e.target.value })}
                  placeholder="Descripción de la recaudación..."
                />
              </div>

              <div className="space-y-2">
                <Label>Fecha</Label>
                <Input
                  type="date"
                  value={recaudacionData.fecha}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, fecha: e.target.value })}
                  required
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowRecaudacionModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loadingForm}>
                {loadingForm && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Registrar
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}