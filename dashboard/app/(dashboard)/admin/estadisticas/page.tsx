'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import {
  Loader2,
  Download,
  Car,
  DollarSign,
  Users,
  Store,
  Building2,
  Star,
} from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

interface EstadisticasData {
  resumen: {
    total_viajes: number
    viajes_completados: number
    viajes_cancelados: number
    viajes_activos: number
    ingresos_totales: number
    promedio_viaje: number
    pasajeros_unicos: number
    choferes_activos: number
    calificacion_promedio: number
  }
  tendencia: Array<{
    fecha: string
    total_viajes: number
    completados: number
    cancelados: number
    ingresos: number
  }>
  estados: Record<string, number>
  calificaciones: Record<number, number>
  top_comercios: Array<{
    nombre: string
    rubro: string
    total_viajes: number
    ingresos: number
  }>
  top_empresas: Array<{
    nombre: string
    tipo: string
    total_viajes: number
    ingresos: number
  }>
  ingresos_mensuales: Array<{
    mes: string
    fecha: string
    total_viajes: number
    ingresos: number
  }>
  periodo: {
    desde: string
    hasta: string
  }
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

export default function EstadisticasPage() {
  const { status } = useSession()
  const [fechaDesde, setFechaDesde] = useState(
    format(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd')
  )
  const [fechaHasta, setFechaHasta] = useState(
    format(new Date(), 'yyyy-MM-dd')
  )
  const [activeTab, setActiveTab] = useState('resumen')

  const { data, isLoading, refetch, error } = useQuery<EstadisticasData>({
    queryKey: ['estadisticas-avanzadas', fechaDesde, fechaHasta],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('fecha_desde', fechaDesde)
      params.append('fecha_hasta', fechaHasta)
      const response = await apiClient.get(`/api/control-base/estadisticas-avanzadas?${params.toString()}`)
      return response.data
    },
    enabled: status === 'authenticated',
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 401) return false
      return failureCount < 3
    },
  })

  const handleExport = async (formato: string) => {
    try {
      const params = new URLSearchParams()
      params.append('fecha_desde', fechaDesde)
      params.append('fecha_hasta', fechaHasta)
      params.append('formato', formato)
      
      const response = await apiClient.get(
        `/api/control-base/estadisticas-avanzadas/exportar?${params.toString()}`,
        { responseType: 'blob' }
      )
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `estadisticas.${formato === 'excel' ? 'xlsx' : 'csv'}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error al exportar:', error)
    }
  }

  if (status === 'loading') {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-[400px] items-center justify-center flex-col gap-4">
        <p className="text-muted-foreground">Error al cargar estadísticas</p>
        <Button variant="outline" onClick={() => refetch()}>Reintentar</Button>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <p className="text-muted-foreground">No hay datos disponibles</p>
      </div>
    )
  }

  const estadoData = Object.entries(data.estados || {}).map(([name, value]) => ({
    name: name === 'pendiente' ? 'Pendiente' :
          name === 'aceptado' ? 'Aceptado' :
          name === 'en_curso' ? 'En Curso' :
          name === 'finalizado' ? 'Finalizado' :
          name === 'cancelado' ? 'Cancelado' : name,
    value,
  }))

  const calificacionData = Object.entries(data.calificaciones || {}).map(([name, value]) => ({
    name: `${name} ⭐`,
    value,
  }))

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Estadísticas Avanzadas</h1>
          <p className="text-muted-foreground">
            Análisis detallado de viajes, ingresos y rendimiento
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('excel')}>
            <Download className="h-4 w-4 mr-2" />
            Excel
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            CSV
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="text-sm font-medium">Fecha Desde</label>
              <input
                type="date"
                value={fechaDesde}
                onChange={(e) => setFechaDesde(e.target.value)}
                className="ml-2 border rounded-md px-3 py-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Fecha Hasta</label>
              <input
                type="date"
                value={fechaHasta}
                onChange={(e) => setFechaHasta(e.target.value)}
                className="ml-2 border rounded-md px-3 py-1"
              />
            </div>
            <Button onClick={() => refetch()}>Actualizar</Button>
          </div>
        </CardContent>
      </Card>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Viajes</p>
                <p className="text-2xl font-bold">{data.resumen.total_viajes}</p>
              </div>
              <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                <Car className="h-5 w-5 text-blue-600 dark:text-blue-300" />
              </div>
            </div>
            <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
              <span>Completados: {data.resumen.viajes_completados}</span>
              <span>Cancelados: {data.resumen.viajes_cancelados}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ingresos Totales</p>
                <p className="text-2xl font-bold">{formatMoneda(data.resumen.ingresos_totales)}</p>
              </div>
              <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
                <DollarSign className="h-5 w-5 text-green-600 dark:text-green-300" />
              </div>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              <span>Promedio por viaje: {formatMoneda(data.resumen.promedio_viaje)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Usuarios Únicos</p>
                <p className="text-2xl font-bold">{data.resumen.pasajeros_unicos}</p>
              </div>
              <div className="rounded-full bg-purple-100 p-3 dark:bg-purple-900">
                <Users className="h-5 w-5 text-purple-600 dark:text-purple-300" />
              </div>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              <span>Choferes activos: {data.resumen.choferes_activos}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Calificación Promedio</p>
                <p className="text-2xl font-bold">{data.resumen.calificacion_promedio.toFixed(1)}</p>
              </div>
              <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
                <Star className="h-5 w-5 text-yellow-600 dark:text-yellow-300" />
              </div>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              <span>Basado en {data.resumen.total_viajes} viajes</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs de gráficos */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4">
          <TabsTrigger value="resumen">Resumen</TabsTrigger>
          <TabsTrigger value="tendencia">Tendencia</TabsTrigger>
          <TabsTrigger value="top">Top Rankings</TabsTrigger>
          <TabsTrigger value="ingresos">Ingresos</TabsTrigger>
        </TabsList>

        {/* Tab: Resumen */}
        <TabsContent value="resumen" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Distribución de Estados</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={estadoData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {estadoData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Distribución de Calificaciones</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={calificacionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8884D8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab: Tendencia */}
        <TabsContent value="tendencia" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Evolución Diaria</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.tendencia}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" tick={{ fontSize: 10 }} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="total_viajes" stroke="#0088FE" name="Total Viajes" />
                  <Line type="monotone" dataKey="completados" stroke="#00C49F" name="Completados" />
                  <Line type="monotone" dataKey="ingresos" stroke="#FFBB28" name="Ingresos" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Top Rankings */}
        <TabsContent value="top" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Store className="h-4 w-4" />
                  Top Comercios
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.top_comercios?.map((comercio, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b py-2">
                      <div>
                        <p className="font-medium">{comercio.nombre}</p>
                        <p className="text-xs text-muted-foreground">{comercio.rubro}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{comercio.total_viajes} viajes</p>
                        <p className="text-xs text-muted-foreground">{formatMoneda(comercio.ingresos)}</p>
                      </div>
                    </div>
                  ))}
                  {data.top_comercios?.length === 0 && (
                    <p className="text-center text-muted-foreground">No hay datos</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Top Empresas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.top_empresas?.map((empresa, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b py-2">
                      <div>
                        <p className="font-medium">{empresa.nombre}</p>
                        <p className="text-xs text-muted-foreground">{empresa.tipo}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{empresa.total_viajes} viajes</p>
                        <p className="text-xs text-muted-foreground">{formatMoneda(empresa.ingresos)}</p>
                      </div>
                    </div>
                  ))}
                  {data.top_empresas?.length === 0 && (
                    <p className="text-center text-muted-foreground">No hay datos</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab: Ingresos */}
        <TabsContent value="ingresos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Ingresos Mensuales</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data.ingresos_mensuales}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="ingresos" fill="#8884D8" name="Ingresos" />
                  <Bar dataKey="total_viajes" fill="#82CA9D" name="Total Viajes" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}