'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  FileText,
  Download,
  Loader2,
  Calendar,
  BarChart3,
  FileSpreadsheet,
  Eye,
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============================================================
// TIPOS
// ============================================================

interface Gasto {
  fecha: string
  vehiculo: string
  categoria: string
  monto: number
  descripcion: string
  kilometraje: number
}

interface ResumenFinanciero {
  periodo: { desde: string; hasta: string; tipo: string }
  resumen: {
    ingresos_brutos: number
    gastos_totales: number
    utilidad_neta: number
    vehiculos_activos: number
    total_liquidaciones: number
    utilidad_promedio: number
    comisiones: number
    canon_total: number
  }
  ultimas_liquidaciones: Array<{
    id: string
    monto_bruto: number
    utilidad: number
    estado: string
    fecha: string
    patente: string
  }>
}

interface ComparativoVehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  ingresos: number
  gastos: number
  utilidad: number
  liquidaciones: number
  utilidad_promedio: number
  margen_porcentaje: number
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export default function PropietarioReportesPage() {
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [periodo, setPeriodo] = useState('mes')
  const [formato, setFormato] = useState('csv')
  const [fechaDesde, setFechaDesde] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [fechaHasta, setFechaHasta] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [anio, setAnio] = useState(new Date().getFullYear())
  const [gastos, setGastos] = useState<Gasto[]>([])
  const [showPreview, setShowPreview] = useState(false)
  const [resumenFinanciero, setResumenFinanciero] = useState<ResumenFinanciero | null>(null)
  const [comparativo, setComparativo] = useState<ComparativoVehiculo[]>([])
  const [loadingResumen, setLoadingResumen] = useState(false)
  const [loadingComparativo, setLoadingComparativo] = useState(false)
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState<string>('')
  const [vehiculos, setVehiculos] = useState<{ id: string; patente: string }[]>([])

  // ============================================================
  // CARGA INICIAL
  // ============================================================

  useEffect(() => {
    cargarGastos()
    cargarResumenFinanciero()
    cargarComparativo()
    cargarVehiculos()
  }, [])

  const cargarVehiculos = async () => {
    try {
      const response = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(response.data || [])
    } catch (error) {
      console.error('Error cargando vehículos:', error)
    }
  }

  // ============================================================
  // GASTOS
  // ============================================================

  const cargarGastos = async () => {
    setLoadingData(true)
    try {
      const params = new URLSearchParams()
      if (fechaDesde) params.append('desde', fechaDesde)
      if (fechaHasta) params.append('hasta', fechaHasta)
      if (vehiculoSeleccionado) params.append('vehiculo_id', vehiculoSeleccionado)
      params.append('limit', '50')

      const response = await apiClient.get(`/api/propietario/gastos?${params.toString()}`)
      setGastos(response.data || [])
      setShowPreview(true)
    } catch (error) {
      console.error('Error cargando gastos:', error)
      toast.error('Error al cargar los gastos')
    } finally {
      setLoadingData(false)
    }
  }

  const exportarGastos = async (formato: 'csv' | 'excel') => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (fechaDesde) params.append('desde', fechaDesde)
      if (fechaHasta) params.append('hasta', fechaHasta)
      if (vehiculoSeleccionado) params.append('vehiculo_id', vehiculoSeleccionado)

      const response = await apiClient.get(
        `/api/propietario/reportes/gastos/${formato}?${params.toString()}`,
        { responseType: 'blob' }
      )

      const blob = new Blob([response.data], {
        type:
          formato === 'csv'
            ? 'text/csv'
            : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })

      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `gastos_${new Date().toISOString().split('T')[0]}.${formato === 'csv' ? 'csv' : 'xlsx'}`
      document.body.appendChild(a)
      a.click()
      a.remove()

      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  // ============================================================
  // RESUMEN FINANCIERO (D9)
  // ============================================================

  const cargarResumenFinanciero = async () => {
    setLoadingResumen(true)
    try {
      const response = await apiClient.get('/api/propietario/reportes/resumen-financiero', {
        params: { periodo: 'mensual' },
      })
      setResumenFinanciero(response.data)
    } catch (error) {
      console.error('Error cargando resumen financiero:', error)
      toast.error('Error al cargar el resumen financiero')
    } finally {
      setLoadingResumen(false)
    }
  }

  // ============================================================
  // COMPARATIVO (D9)
  // ============================================================

  const cargarComparativo = async () => {
    setLoadingComparativo(true)
    try {
      const response = await apiClient.get('/api/propietario/reportes/comparativo')
      setComparativo(response.data.vehiculos || [])
    } catch (error) {
      console.error('Error cargando comparativo:', error)
      toast.error('Error al cargar el comparativo de vehículos')
    } finally {
      setLoadingComparativo(false)
    }
  }

  // ============================================================
  // EXPORTACIONES
  // ============================================================

  const exportarMantenimientos = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (vehiculoSeleccionado) params.append('vehiculo_id', vehiculoSeleccionado)

      const response = await apiClient.get(
        `/api/propietario/reportes/mantenimientos/csv?${params.toString()}`,
        { responseType: 'blob' }
      )

      const blob = new Blob([response.data], { type: 'text/csv' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `mantenimientos_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()

      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const exportarRentabilidad = async (formato: 'csv' | 'json') => {
    setLoading(true)
    try {
      const response = await apiClient.get(
        `/api/propietario/reportes/rentabilidad?formato=${formato}&periodo=${periodo}`,
        { responseType: formato === 'csv' ? 'blob' : 'json' }
      )

      if (formato === 'csv') {
        const blob = new Blob([response.data], { type: 'text/csv' })
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `rentabilidad_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        a.remove()
      } else {
        const data = response.data
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `rentabilidad_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        a.remove()
      }

      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const exportarReporteAnual = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/api/propietario/reportes/anual?anio=${anio}`)

      const data = response.data
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `reporte_anual_${anio}.json`
      document.body.appendChild(a)
      a.click()
      a.remove()

      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  // ============================================================
  // UTILIDADES
  // ============================================================

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reportes y Finanzas</h1>
        <p className="text-muted-foreground">
          Exporta reportes y estadísticas de tu flota
        </p>
      </div>

      {/* ============================================================
          RESUMEN FINANCIERO (NUEVO D9)
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LayoutDashboard className="h-5 w-5 text-primary" />
            Resumen Financiero
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingResumen ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : resumenFinanciero ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Ingresos Brutos</p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(resumenFinanciero.resumen.ingresos_brutos)}
                  </p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Gastos Totales</p>
                  <p className="text-2xl font-bold text-red-600">
                    {formatCurrency(resumenFinanciero.resumen.gastos_totales)}
                  </p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Utilidad Neta</p>
                  <p
                    className={`text-2xl font-bold ${
                      resumenFinanciero.resumen.utilidad_neta >= 0
                        ? 'text-blue-600'
                        : 'text-red-600'
                    }`}
                  >
                    {formatCurrency(resumenFinanciero.resumen.utilidad_neta)}
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Liquidaciones</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {resumenFinanciero.resumen.total_liquidaciones}
                  </p>
                </div>
              </div>

              {resumenFinanciero.ultimas_liquidaciones.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Últimas Liquidaciones</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-4 py-2 text-left">Patente</th>
                          <th className="px-4 py-2 text-right">Monto</th>
                          <th className="px-4 py-2 text-right">Utilidad</th>
                          <th className="px-4 py-2 text-center">Estado</th>
                          <th className="px-4 py-2 text-left">Fecha</th>
                        </tr>
                      </thead>
                      <tbody>
                        {resumenFinanciero.ultimas_liquidaciones.map((item) => (
                          <tr key={item.id} className="border-t hover:bg-muted/30">
                            <td className="px-4 py-2 font-medium">{item.patente}</td>
                            <td className="px-4 py-2 text-right">
                              {formatCurrency(item.monto_bruto)}
                            </td>
                            <td
                              className={`px-4 py-2 text-right ${
                                item.utilidad >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}
                            >
                              {formatCurrency(item.utilidad)}
                            </td>
                            <td className="px-4 py-2 text-center">
                              <span
                                className={`px-2 py-1 rounded-full text-xs ${
                                  item.estado === 'APROBADA'
                                    ? 'bg-blue-100 text-blue-600'
                                    : item.estado === 'PAGADA'
                                    ? 'bg-green-100 text-green-600'
                                    : 'bg-yellow-100 text-yellow-600'
                                }`}
                              >
                                {item.estado}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-muted-foreground">
                              {new Date(item.fecha).toLocaleDateString('es-AR')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No hay datos disponibles
            </div>
          )}
        </CardContent>
      </Card>

      {/* ============================================================
          REPORTE DE GASTOS
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Reporte de Gastos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Fecha Desde</Label>
              <Input
                type="date"
                value={fechaDesde}
                onChange={(e) => setFechaDesde(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Fecha Hasta</Label>
              <Input
                type="date"
                value={fechaHasta}
                onChange={(e) => setFechaHasta(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Vehículo</Label>
              <Select value={vehiculoSeleccionado} onValueChange={setVehiculoSeleccionado}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los vehículos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos los vehículos</SelectItem>
                  {vehiculos.map((v) => (
                    <SelectItem key={v.id} value={v.id}>
                      {v.patente}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end gap-2">
              <Button
                onClick={cargarGastos}
                disabled={loadingData}
                variant="outline"
                className="flex-1"
              >
                <Eye className="h-4 w-4 mr-2" />
                {loadingData ? 'Cargando...' : 'Ver Datos'}
              </Button>
              <Button
                onClick={() => exportarGastos('csv')}
                disabled={loading}
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button
                onClick={() => exportarGastos('excel')}
                disabled={loading}
                variant="outline"
                className="flex-1"
              >
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Excel
              </Button>
            </div>
          </div>

          {showPreview && (
            <div className="mt-6">
              <h3 className="text-sm font-medium mb-2">
                Vista Previa de Gastos ({gastos.length} registros)
              </h3>
              {loadingData ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              ) : gastos.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground border rounded-lg">
                  No hay gastos en el período seleccionado
                </div>
              ) : (
                <div className="border rounded-lg overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-4 py-2 text-left">Fecha</th>
                        <th className="px-4 py-2 text-left">Vehículo</th>
                        <th className="px-4 py-2 text-left">Categoría</th>
                        <th className="px-4 py-2 text-left">Descripción</th>
                        <th className="px-4 py-2 text-right">Monto</th>
                      </tr>
                    </thead>
                    <tbody>
                      {gastos.map((gasto, index) => (
                        <tr key={index} className="border-t hover:bg-muted/30">
                          <td className="px-4 py-2">{gasto.fecha}</td>
                          <td className="px-4 py-2 font-medium">{gasto.vehiculo}</td>
                          <td className="px-4 py-2 capitalize">{gasto.categoria}</td>
                          <td className="px-4 py-2 text-muted-foreground">
                            {gasto.descripcion || '-'}
                          </td>
                          <td className="px-4 py-2 text-right font-semibold text-red-600">
                            {formatCurrency(gasto.monto)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ============================================================
          REPORTE DE MANTENIMIENTOS
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Reporte de Mantenimientos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-2">
            <Select value={vehiculoSeleccionado} onValueChange={setVehiculoSeleccionado}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Todos los vehículos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos los vehículos</SelectItem>
                {vehiculos.map((v) => (
                  <SelectItem key={v.id} value={v.id}>
                    {v.patente}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={exportarMantenimientos} disabled={loading}>
              <Download className="h-4 w-4 mr-2" />
              Exportar CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* ============================================================
          REPORTE DE RENTABILIDAD
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Reporte de Rentabilidad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Período</Label>
              <Tabs value={periodo} onValueChange={setPeriodo}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="dia">Día</TabsTrigger>
                  <TabsTrigger value="mes">Mes</TabsTrigger>
                  <TabsTrigger value="ano">Año</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            <div className="space-y-2">
              <Label>Formato</Label>
              <Select value={formato} onValueChange={setFormato}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button
                onClick={() => exportarRentabilidad(formato as 'csv' | 'json')}
                disabled={loading}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ============================================================
          COMPARATIVO DE VEHÍCULOS (NUEVO D9)
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Comparativo de Vehículos
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingComparativo ? (
            <div className="flex justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : comparativo.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No hay datos disponibles
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left">Patente</th>
                    <th className="px-4 py-2 text-left">Vehículo</th>
                    <th className="px-4 py-2 text-right">Ingresos</th>
                    <th className="px-4 py-2 text-right">Gastos</th>
                    <th className="px-4 py-2 text-right">Utilidad</th>
                    <th className="px-4 py-2 text-right">Margen</th>
                    <th className="px-4 py-2 text-center">Liquidaciones</th>
                  </tr>
                </thead>
                <tbody>
                  {comparativo.map((item) => (
                    <tr key={item.id} className="border-t hover:bg-muted/30">
                      <td className="px-4 py-2 font-medium">{item.patente}</td>
                      <td className="px-4 py-2">
                        {item.marca} {item.modelo}
                      </td>
                      <td className="px-4 py-2 text-right">{formatCurrency(item.ingresos)}</td>
                      <td className="px-4 py-2 text-right text-red-600">
                        {formatCurrency(item.gastos)}
                      </td>
                      <td
                        className={`px-4 py-2 text-right ${
                          item.utilidad >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {formatCurrency(item.utilidad)}
                      </td>
                      <td
                        className={`px-4 py-2 text-right ${
                          item.margen_porcentaje >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {item.margen_porcentaje.toFixed(1)}%
                      </td>
                      <td className="px-4 py-2 text-center">{item.liquidaciones}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ============================================================
          REPORTE ANUAL
          ============================================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            Reporte Anual Consolidado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Año</Label>
              <Input
                type="number"
                value={anio}
                onChange={(e) => setAnio(Number(e.target.value))}
                min={2020}
                max={new Date().getFullYear()}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={exportarReporteAnual} disabled={loading} className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Exportar Reporte
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="flex justify-center items-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="ml-2">Generando reporte...</span>
        </div>
      )}
    </div>
  )
}