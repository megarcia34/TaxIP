'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { 
  Car, TrendingUp, DollarSign, CreditCard, 
  Calendar, Loader2, Briefcase, FileText, MapPin,
  AlertTriangle, XCircle, Clock, AlertCircle, ArrowRight,
  BarChart3, Wrench
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

// COMPONENTES DEL DASHBOARD
import { KPICard } from '@/components/propietario/dashboard/KPICard'
import { PaymentChart } from '@/components/propietario/dashboard/PaymentChart'
import { FlotaStatusWidget } from '@/components/propietario/dashboard/FlotaStatusWidget'

// ============================================================
// INTERFACES
// ============================================================

interface DashboardData {
  kpis: {
    total_vehiculos: number
    total_choferes_activos: number
    choferes_conectados: number
    choferes_disponibles: number
    choferes_ocupados: number
    ingresos_mes: number
    gastos_mes: number
    ganancia_mes: number
    viajes_mes: number
  }
  ultimos_viajes: {
    id: string
    direccion_origen: string
    direccion_destino: string
    precio_final: number
    created_at: string
    patente: string
    chofer_nombre: string
  }[]
  grafico_ingresos_gastos: {
    labels: string[]
    ingresos: number[]
    gastos: number[]
    utilidad: number[]
  }
  grafico_gastos_categoria: {
    labels: string[]
    values: number[]
    colors: string[]
  }
  proximos_mantenimientos: {
    vehiculo_id: string
    patente: string
    ultimo_servicio: string
    km_actual: number
    proximo_km: number
    km_restante: number
    urgencia: string
  }[]
}

interface Vehiculo {
  id: string
  patente: string
  estado?: string
  conductor?: { nombre: string } | null
  chofer_nombre?: string
  marca?: string
  modelo?: string
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export default function PropietarioDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [alertas, setAlertas] = useState<any[]>([])
  const [loadingAlertas, setLoadingAlertas] = useState(true)
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [pagosData, setPagosData] = useState<any[]>([])

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  // ============================================================
  // CARGAR DATOS DEL DASHBOARD
  // ============================================================

  const cargarDashboard = async () => {
    setLoading(true)
    try {
      const [
        flotaRes, 
        rentabilidadRes, 
        gastosRes, 
        graficoRes, 
        mantenimientosRes,
        vehiculosRes,
        pagosRes
      ] = await Promise.all([
        apiClient.get('/api/propietario/resumen-flota'),
        apiClient.get('/api/propietario/rentabilidad-widget?periodo=mes'),
        apiClient.get('/api/propietario/gastos-widget'),
        apiClient.get('/api/propietario/grafico-ingresos-gastos?meses=6'),
        apiClient.get('/api/propietario/proximos-mantenimientos?limit=5'),
        apiClient.get('/api/propietario/vehiculos'),
        apiClient.get('/api/propietario/pagos/medios').catch(() => ({ data: null })),
      ])

      const flota = flotaRes.data || {}
      const rentabilidad = rentabilidadRes.data || {}
      const gastos = gastosRes.data || {}
      const grafico = graficoRes.data || { labels: [], ingresos: [], gastos: [], utilidad: [] }
      const mantenimientos = mantenimientosRes.data || []
      const vehiculosData = vehiculosRes.data || []
      const pagos = pagosRes.data || null

      // Últimos viajes
      const viajesRes = await apiClient.get('/api/propietario/ultimos-viajes?limit=5').catch(() => ({ data: [] }))
      const ultimosViajes = viajesRes.data || []

      setVehiculos(vehiculosData)

      if (pagos && Array.isArray(pagos)) {
        setPagosData(pagos)
      }

      setData({
        kpis: {
          total_vehiculos: flota.total_vehiculos || vehiculosData.length || 0,
          total_choferes_activos: flota.total_choferes_activos || 0,
          choferes_conectados: flota.choferes_conectados || 0,
          choferes_disponibles: flota.choferes_disponibles || 0,
          choferes_ocupados: flota.choferes_ocupados || 0,
          ingresos_mes: rentabilidad.ingresos || 0,
          gastos_mes: gastos.total_gastos || 0,
          ganancia_mes: rentabilidad.utilidad || 0,
          viajes_mes: rentabilidad.total_viajes || 0
        },
        ultimos_viajes: ultimosViajes.map((v: any) => ({
          id: v.id,
          direccion_origen: v.origen || 'Viaje',
          direccion_destino: v.destino || 'Viaje',
          precio_final: v.monto || 0,
          created_at: v.fecha || new Date().toISOString(),
          patente: v.patente || 'N/A',
          chofer_nombre: v.chofer || 'N/A'
        })),
        grafico_ingresos_gastos: grafico,
        grafico_gastos_categoria: {
          labels: ['Combustible', 'Mantenimiento', 'Seguro', 'Impuestos', 'Otros'],
          values: [
            gastos.desglose?.combustible || 0,
            gastos.desglose?.mantenimiento || 0,
            gastos.desglose?.seguro || 0,
            0,
            gastos.desglose?.otros || 0
          ],
          colors: ['#F59E0B', '#3B82F6', '#10B981', '#EF4444', '#6B7280']
        },
        proximos_mantenimientos: mantenimientos
      })

    } catch (error) {
      console.error('Error cargando dashboard:', error)
      toast.error('Error al cargar el dashboard')
    } finally {
      setLoading(false)
    }
  }

  // ============================================================
  // CARGAR ALERTAS DE VENCIMIENTO
  // ============================================================

  const cargarAlertas = async () => {
    setLoadingAlertas(true)
    try {
      const res = await apiClient.get('/api/propietario/documentos/vencimientos?dias_previos=30')
      const alertasData = res.data || []
      
      // Mostrar documentos con <= 30 días
      const urgentes = alertasData.filter((a: any) => a.dias_restantes <= 30)
      setAlertas(urgentes)
      
    } catch (error) {
      console.error('Error cargando alertas:', error)
    } finally {
      setLoadingAlertas(false)
    }
  }

  // ============================================================
  // EFECTOS
  // ============================================================

  useEffect(() => {
    cargarDashboard()
    cargarAlertas()
  }, [])

  // ============================================================
  // RENDER - LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-muted-foreground">Cargando dashboard...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No hay datos disponibles</p>
      </div>
    )
  }

  const kpis = data.kpis
  const hasAlertasCriticas = alertas.length > 0

  // ============================================================
  // DATOS PARA KPICard (usa TODOS los vehículos, no solo con GPS)
  // ============================================================

  const detalleVehiculos = vehiculos.map((v: any) => ({
    vehiculo_id: v.id,
    patente: v.patente,
    valor: kpis.ingresos_mes > 0 ? Math.round(kpis.ingresos_mes / (vehiculos.length || 1)) : 0,
    viajes: kpis.viajes_mes > 0 ? Math.round(kpis.viajes_mes / (vehiculos.length || 1)) : 0
  }))

  // ============================================================
  // MAPEO DE VEHÍCULOS PARA FLOTA STATUS
  // ============================================================

  const flotaDetalle = vehiculos.map((v: any) => ({
    vehiculo_id: v.id,
    patente: v.patente,
    chofer_nombre: v.conductor?.nombre || v.chofer_nombre || 'Sin chofer',
    estado: v.estado === 'ocupado' ? 'ocupado' as const : 
            v.estado === 'fuera_servicio' ? 'offline' as const : 'libre' as const,
  }))

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="space-y-6 pb-8">
      
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <Briefcase className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Mi Dashboard</h1>
            <p className="text-muted-foreground">Resumen general de tu flota</p>
          </div>
        </div>
        <Button variant="outline" onClick={() => { cargarDashboard(); cargarAlertas(); }} size="sm">
          <Calendar className="h-4 w-4 mr-2" />
          Actualizar
        </Button>
      </div>

      {/* ALERTAS DE VENCIMIENTO */}
      {!loadingAlertas && (
        <Card className={hasAlertasCriticas ? 'border-red-200 bg-red-50/30' : 'border-green-200 bg-green-50/30'}>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className={`h-5 w-5 ${hasAlertasCriticas ? 'text-red-600' : 'text-green-600'}`} />
              <span>Alertas de vencimientos</span>
              {hasAlertasCriticas && (
                <Badge variant="destructive" className="ml-2">
                  {alertas.length} urgentes
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {alertas.length === 0 ? (
              <p className="text-sm text-green-600">✅ Todos los documentos están al día</p>
            ) : (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">⚠️ Documentos por vencer:</p>
                {alertas.slice(0, 5).map((alerta: any) => {
                  const isVencido = alerta.dias_restantes < 0
                  const isCritico = alerta.dias_restantes >= 0 && alerta.dias_restantes <= 7
                  const isUrgente = alerta.dias_restantes > 7 && alerta.dias_restantes <= 30
                  
                  const colorClass = isVencido ? 'border-red-200 bg-red-50' : 
                                     isCritico ? 'border-orange-200 bg-orange-50' : 
                                     'border-yellow-200 bg-yellow-50'
                  
                  const icon = isVencido ? <XCircle className="h-4 w-4 text-red-500" /> :
                               isCritico ? <AlertCircle className="h-4 w-4 text-orange-500" /> :
                               <Clock className="h-4 w-4 text-yellow-500" />
                  
                  const label = isVencido ? 'Vencido' :
                                isCritico ? 'Crítico' :
                                'Urgente'
                  
                  const diasText = isVencido ? `Vencido hace ${Math.abs(alerta.dias_restantes)} días` :
                                    `${alerta.dias_restantes} días`
                  
                  return (
                    <div key={alerta.id} className={`flex justify-between items-center border p-2 rounded-lg ${colorClass}`}>
                      <div className="flex items-center gap-2 min-w-0">
                        {icon}
                        <div className="truncate">
                          <span className="font-medium text-sm">{alerta.tipo_documento?.replace('_', ' ').toUpperCase() || 'Documento'}</span>
                          <span className="text-xs text-muted-foreground ml-2">N°: {alerta.numero}</span>
                          {alerta.patente && (
                            <span className="text-xs text-muted-foreground ml-2">({alerta.patente})</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Badge variant="outline" className={`text-xs ${isVencido ? 'border-red-200 text-red-600' : isCritico ? 'border-orange-200 text-orange-600' : 'border-yellow-200 text-yellow-600'}`}>
                          {label}
                        </Badge>
                        <span className="text-xs font-medium whitespace-nowrap">{diasText}</span>
                      </div>
                    </div>
                  )
                })}
                
                {alertas.length > 5 && (
                  <p className="text-xs text-muted-foreground text-center">
                    + {alertas.length - 5} alertas más
                  </p>
                )}
              </div>
            )}

            <div className="mt-4">
              <Link 
                href="/dashboard-propietario/documentos" 
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                Ver todos los documentos →
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* KPIS CON DRILL-DOWN */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Ingresos Totales"
          value={kpis.ingresos_mes}
          trend={12.5}
          icon={<DollarSign className="h-4 w-4" />}
          detailData={detalleVehiculos}
          detailTitle="Ingresos por vehículo"
          detailValueLabel="Monto"
          detailSecondaryLabel="Viajes"
        />
        <KPICard
          title="Gastos Totales"
          value={kpis.gastos_mes}
          trend={8.3}
          icon={<CreditCard className="h-4 w-4" />}
          detailData={detalleVehiculos.map(v => ({ ...v, valor: Math.round(kpis.gastos_mes / (vehiculos.length || 1)) }))}
          detailTitle="Gastos por vehículo"
          detailValueLabel="Monto"
          detailSecondaryLabel="Viajes"
        />
        <KPICard
          title="Ganancia Neta"
          value={kpis.ganancia_mes}
          trend={15.7}
          icon={<TrendingUp className="h-4 w-4" />}
          detailData={detalleVehiculos.map(v => ({ ...v, valor: Math.round(kpis.ganancia_mes / (vehiculos.length || 1)) }))}
          detailTitle="Ganancia por vehículo"
          detailValueLabel="Monto"
          detailSecondaryLabel="Viajes"
        />
        <KPICard
          title="Margen de Ganancia"
          value={kpis.ingresos_mes > 0 ? Math.round((kpis.ganancia_mes / kpis.ingresos_mes) * 100) : 0}
          trend={2.1}
          icon={<BarChart3 className="h-4 w-4" />}
          detailData={detalleVehiculos.map(v => ({
            ...v,
            valor: kpis.ingresos_mes > 0 ? Math.round((kpis.ganancia_mes / kpis.ingresos_mes) * 100) : 0
          }))}
          detailTitle="Margen por vehículo"
          detailValueLabel="%"
          detailSecondaryLabel=""
        />
      </div>

      {/* GRÁFICO DE INGRESOS VS GASTOS */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Ingresos vs Gastos vs Ganancia (Últimos 6 meses)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[250px]">
            {loading ? (
              <div className="flex h-full items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.grafico_ingresos_gastos.labels.map((label, i) => ({
                  mes: label,
                  ingresos: data.grafico_ingresos_gastos.ingresos[i] || 0,
                  gastos: data.grafico_ingresos_gastos.gastos[i] || 0,
                  utilidad: data.grafico_ingresos_gastos.utilidad[i] || 0
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" />
                  <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                  <Tooltip 
                    formatter={(value: any) => {
                      if (value === undefined || value === null || value === 0) return '$0'
                      return `$${value.toLocaleString()}`
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="ingresos" name="💰 Ingresos" fill="#3B82F6" />
                  <Bar dataKey="gastos" name="📉 Gastos" fill="#EF4444" />
                  <Bar dataKey="utilidad" name="📈 Ganancia" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>

      {/* GASTOS POR CATEGORÍA + ESTADO FLOTA + PAGOS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* GASTOS POR CATEGORÍA */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Gastos por Categoría</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              {loading ? (
                <div className="flex h-full items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.grafico_gastos_categoria.labels.map((label, i) => ({
                        name: label,
                        value: data.grafico_gastos_categoria.values[i] || 0
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => {
                        if (percent === undefined || percent === null) return `${name} 0%`
                        return `${name} ${(percent * 100).toFixed(1)}%`
                      }}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {data.grafico_gastos_categoria.labels.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={data.grafico_gastos_categoria.colors[index] || '#6B7280'} />
                      ))}
                    </Pie>
                    <Tooltip 
                       formatter={(value: any) => {
                         if (value === undefined || value === null || value === 0) return '$0'
                         return `$${value.toLocaleString()}`
                       }} 
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ESTADO DE FLOTA - TODOS LOS VEHÍCULOS */}
        <FlotaStatusWidget 
          data={{
            total: kpis.total_vehiculos,
            activos: kpis.choferes_conectados,
            detalle: flotaDetalle
          }} 
          loading={loading} 
        />

        {/* MEDIOS DE PAGO */}
        {pagosData.length > 0 ? (
          <PaymentChart data={pagosData} loading={loading} />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Medios de Pago</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
                No hay datos de pagos disponibles
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* PRÓXIMOS MANTENIMIENTOS + ÚLTIMOS VIAJES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PRÓXIMOS MANTENIMIENTOS */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Próximos Mantenimientos
            </CardTitle>
            <Link href="/dashboard-propietario/mantenimientos">
              <Button variant="ghost" size="sm" className="gap-1">
                Ver todos <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {data.proximos_mantenimientos.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No hay mantenimientos próximos</p>
            ) : (
              <div className="space-y-3">
                {data.proximos_mantenimientos.map((m) => (
                  <div key={m.vehiculo_id} className="flex justify-between items-center border-b pb-2 last:border-0">
                    <div>
                      <span className="font-medium">{m.patente}</span>
                      <p className="text-xs text-muted-foreground">{m.ultimo_servicio || 'Sin servicios'}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant={m.km_restante <= 500 ? 'destructive' : m.km_restante <= 1000 ? 'default' : 'outline'}>
                        {m.km_restante > 0 ? `En ${m.km_restante} km` : 'Vencido'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* ÚLTIMOS VIAJES */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Últimos viajes</CardTitle>
            <Link href="/dashboard-propietario/viajes">
              <Button variant="ghost" size="sm" className="gap-1">
                Ver todos <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {data.ultimos_viajes.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No hay viajes recientes</p>
            ) : (
              <div className="space-y-3">
                {data.ultimos_viajes.map((v) => (
                  <div key={v.id} className="border-b pb-2 last:border-0">
                    <div className="flex justify-between">
                      <span className="font-medium">{v.patente}</span>
                      <span className="text-green-600 font-medium">{formatCurrency(v.precio_final)}</span>
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{v.direccion_origen}</p>
                    <p className="text-xs text-muted-foreground">
                      {v.chofer_nombre} · {new Date(v.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ACCESOS RÁPIDOS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link href="/dashboard-propietario/documentos">
          <Card className="hover:shadow-md transition-shadow cursor-pointer border-primary/20 hover:border-primary">
            <CardContent className="p-4 flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Documentos</p>
                <p className="text-xs text-muted-foreground">Gestionar vencimientos</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-propietario/vehiculos-tiempo-real">
          <Card className="hover:shadow-md transition-shadow cursor-pointer border-primary/20 hover:border-primary">
            <CardContent className="p-4 flex items-center gap-3">
              <MapPin className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Tiempo Real</p>
                <p className="text-xs text-muted-foreground">Vehículos en mapa</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-propietario/vehiculos">
          <Card className="hover:shadow-md transition-shadow cursor-pointer border-primary/20 hover:border-primary">
            <CardContent className="p-4 flex items-center gap-3">
              <Car className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Vehículos</p>
                <p className="text-xs text-muted-foreground">Gestionar flota</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-propietario/reportes">
          <Card className="hover:shadow-md transition-shadow cursor-pointer border-primary/20 hover:border-primary">
            <CardContent className="p-4 flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Reportes</p>
                <p className="text-xs text-muted-foreground">Análisis y estadísticas</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

    </div>
  )
}

// ============================================================
// IMPORTACIÓN DE RECHARTS
// ============================================================

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts'