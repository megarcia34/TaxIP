'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminAPI, controlBaseAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Car, 
  Calendar, 
  DollarSign, 
  Building2, 
  TrendingUp, 
  UserCog,
  AlertCircle,
  Loader2,
  Clock,
  CheckCircle,
  XCircle,
  Fuel,
  Wrench,
  Shield,
  FileText,
  RefreshCw,
  MapPin
} from 'lucide-react'

// ✅ IMPORTAR EL MAPA
import { MapSimple } from '@/components/dashboard/MapSimple'

// ============================================
// INTERFACES
// ============================================

interface TenantResumen {
  total_vehiculos: number
  total_viajes: number
  ingresos_brutos: string
  comision_plataforma: string
  ingresos_netos: string
  total_gastos: string
  utilidad_neta: string
  margen: string
}

interface VehiculoResumen {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  conductor: string
  total_viajes: number
  total_ingresos: string
  total_gastos: string
  utilidad: string
  margen: string
}

interface MedioPago {
  medio_pago: string
  total_viajes: number
  total_ingresos: string
  porcentaje: string
}

interface GastoOperativo {
  tipo_gasto: string
  total: string
  porcentaje: string
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

const getMedioIcono = (medio: string) => {
  const iconos: Record<string, string> = {
    efectivo: '💵',
    transferencia: '🏦',
    qr: '📱',
    debito: '💳',
    credito: '💳'
  }
  return iconos[medio] || '💰'
}

const getGastoIcono = (tipo: string) => {
  const iconos: Record<string, React.ReactNode> = {
    combustible: <Fuel className="h-4 w-4" />,
    mantenimiento: <Wrench className="h-4 w-4" />,
    seguro: <Shield className="h-4 w-4" />,
    impuesto: <FileText className="h-4 w-4" />,
    patente: <FileText className="h-4 w-4" />,
  }
  return iconos[tipo] || <FileText className="h-4 w-4" />
}

const getMargenColor = (margen: string) => {
  const valor = parseFloat(margen.replace('%', '').replace(',', '.'))
  if (isNaN(valor)) return 'bg-gray-100 text-gray-800'
  if (valor >= 30) return 'bg-green-100 text-green-800'
  if (valor >= 15) return 'bg-yellow-100 text-yellow-800'
  if (valor >= 0) return 'bg-orange-100 text-orange-800'
  return 'bg-red-100 text-red-800'
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export default function AdminDashboardPage() {
  const [periodo, setPeriodo] = useState<'dia' | 'semana' | 'mes'>('mes')
  const [selectedVehiculo, setSelectedVehiculo] = useState<string | null>(null)

  // ============================================
  // QUERIES EXISTENTES (Dashboard operativo)
  // ============================================

  const { data: statsData, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['admin-estadisticas'],
    queryFn: controlBaseAPI.getEstadisticas,
    retry: 1,
  })

  const { data: choferesData } = useQuery({
    queryKey: ['admin-choferes-online'],
    queryFn: controlBaseAPI.getChoferesOnline,
    retry: 1,
  })

  const { data: solicitudesData } = useQuery({
    queryKey: ['admin-solicitudes-activas'],
    queryFn: controlBaseAPI.getSolicitudesActivas,
    retry: 1,
  })

  // ============================================
  // NUEVAS QUERIES PARA ADMIN TENANT (Rentabilidad)
  // ============================================

  // Resumen del tenant
  const { data: resumenData, isLoading: resumenLoading } = useQuery({
    queryKey: ['admin-tenant-resumen', periodo],
    queryFn: async () => {
      const res = await fetch(`/admin/tenant/resumen?periodo=${periodo}`)
      if (!res.ok) throw new Error('Error al cargar resumen')
      return res.json()
    },
    retry: 1,
  })

  // Vehículos del tenant
  const { data: vehiculosData, isLoading: vehiculosLoading } = useQuery({
    queryKey: ['admin-tenant-vehiculos', periodo],
    queryFn: async () => {
      const res = await fetch(`/admin/tenant/vehiculos?periodo=${periodo}`)
      if (!res.ok) throw new Error('Error al cargar vehículos')
      return res.json()
    },
    retry: 1,
  })

  // Medios de pago
  const { data: mediosData, isLoading: mediosLoading } = useQuery({
    queryKey: ['admin-tenant-medios-pago'],
    queryFn: async () => {
      const res = await fetch('/admin/tenant/medios-pago')
      if (!res.ok) throw new Error('Error al cargar medios de pago')
      return res.json()
    },
    retry: 1,
  })

  // Gastos operativos
  const { data: gastosData, isLoading: gastosLoading } = useQuery({
    queryKey: ['admin-tenant-gastos'],
    queryFn: async () => {
      const res = await fetch('/admin/tenant/gastos')
      if (!res.ok) throw new Error('Error al cargar gastos')
      return res.json()
    },
    retry: 1,
  })

  // Detalle de vehículo (al hacer clic)
  const { data: vehiculoDetalleData, isLoading: vehiculoDetalleLoading } = useQuery({
    queryKey: ['admin-tenant-vehiculo', selectedVehiculo],
    queryFn: async () => {
      if (!selectedVehiculo) return null
      const res = await fetch(`/admin/tenant/vehiculo/${selectedVehiculo}`)
      if (!res.ok) throw new Error('Error al cargar detalle del vehículo')
      return res.json()
    },
    enabled: !!selectedVehiculo,
    retry: 1,
  })

  const isLoading = statsLoading || resumenLoading || vehiculosLoading
  const resumen = resumenData?.resumen || {}
  const vehiculos = vehiculosData?.vehiculos || []
  const medios = mediosData?.medios || []
  const gastos = gastosData?.gastos || []
  const stats = statsData || {}

  if (statsLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (statsError) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-muted-foreground">Error al cargar el dashboard</p>
          <p className="text-sm text-muted-foreground">{(statsError as Error)?.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* ============================================
          HEADER
      ============================================ */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard Administrativo</h1>
          <p className="text-muted-foreground">
            Admin Tenant - Vista general de la plataforma
            {stats.tenant_nombre && <span className="ml-2 text-sm">| Tenant: {stats.tenant_nombre}</span>}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={periodo === 'dia' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriodo('dia')}
          >
            Día
          </Button>
          <Button
            variant={periodo === 'semana' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriodo('semana')}
          >
            Semana
          </Button>
          <Button
            variant={periodo === 'mes' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriodo('mes')}
          >
            Mes
          </Button>
        </div>
      </div>

      {/* ============================================
          KPI - RESULTADOS FINANCIEROS
      ============================================ */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vehículos</CardTitle>
            <Car className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumen.total_vehiculos || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Viajes</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumen.total_viajes || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ingresos Brutos</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resumen.ingresos_brutos || '$ 0,00'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utilidad Neta</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${resumen.utilidad_neta?.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
              {resumen.utilidad_neta || '$ 0,00'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ============================================
          MAPA DE VEHÍCULOS EN PLATAFORMA
      ============================================ */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <MapPin className="h-4 w-4 text-primary" />
                Vehículos en Plataforma
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-1">
                Ubicación en tiempo real de los vehículos activos
              </p>
            </div>
            <Badge variant="outline" className="text-xs">
              {choferesData?.choferes?.filter((c: any) => c.estado === 'libre').length || 0} libres / {choferesData?.choferes?.length || 0} total
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[500px] w-full rounded-lg overflow-hidden border">
            <MapSimple />
          </div>
        </CardContent>
      </Card>

      {/* ============================================
          RENDIMIENTO POR VEHÍCULO
      ============================================ */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">Rendimiento por Vehículo</CardTitle>
            <span className="text-xs text-muted-foreground">Período: {periodo}</span>
          </div>
        </CardHeader>
        <CardContent>
          {vehiculosLoading ? (
            <div className="flex h-[200px] items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : vehiculos.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay vehículos registrados</p>
          ) : (
            <div className="relative overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium">Vehículo</th>
                    <th className="pb-3 font-medium">Conductor</th>
                    <th className="pb-3 font-medium text-center">Viajes</th>
                    <th className="pb-3 font-medium text-right">Ingresos</th>
                    <th className="pb-3 font-medium text-right">Gastos</th>
                    <th className="pb-3 font-medium text-right">Utilidad</th>
                    <th className="pb-3 font-medium text-center">Margen</th>
                    <th className="pb-3 font-medium text-center">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {vehiculos.map((vehiculo: VehiculoResumen) => (
                    <tr key={vehiculo.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 font-medium">
                        {vehiculo.patente}
                        <div className="text-xs text-muted-foreground">{vehiculo.marca} {vehiculo.modelo}</div>
                      </td>
                      <td className="py-3">{vehiculo.conductor}</td>
                      <td className="py-3 text-center">{vehiculo.total_viajes}</td>
                      <td className="py-3 text-right">{vehiculo.total_ingresos}</td>
                      <td className="py-3 text-right">{vehiculo.total_gastos}</td>
                      <td className={`py-3 text-right font-medium ${vehiculo.utilidad.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>
                        {vehiculo.utilidad}
                      </td>
                      <td className="py-3 text-center">
                        <Badge className={getMargenColor(vehiculo.margen)}>
                          {vehiculo.margen}
                        </Badge>
                      </td>
                      <td className="py-3 text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedVehiculo(selectedVehiculo === vehiculo.id ? null : vehiculo.id)}
                        >
                          {selectedVehiculo === vehiculo.id ? 'Cerrar' : 'Ver'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ============================================
          DETALLE DE VEHÍCULO (expandido)
      ============================================ */}
      {selectedVehiculo && vehiculoDetalleData && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Detalle: {vehiculoDetalleData.vehiculo?.patente}
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setSelectedVehiculo(null)}>
                <XCircle className="h-4 w-4 mr-1" />
                Cerrar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {vehiculoDetalleLoading ? (
              <div className="flex h-[200px] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-3">
                {/* Ingresos */}
                <Card className="border border-blue-100">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-blue-600">Ingresos</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    <div className="flex justify-between"><span>Viajes:</span><span className="font-medium">{vehiculoDetalleData.ingresos?.viajes || 0}</span></div>
                    <div className="flex justify-between"><span>Brutos:</span><span className="font-medium">{vehiculoDetalleData.ingresos?.brutos}</span></div>
                    <div className="flex justify-between"><span>Comisión:</span><span className="font-medium">{vehiculoDetalleData.ingresos?.comision_plataforma}</span></div>
                    <div className="flex justify-between border-t pt-1"><span>Netos:</span><span className="font-medium">{vehiculoDetalleData.ingresos?.netos}</span></div>
                  </CardContent>
                </Card>

                {/* Gastos */}
                <Card className="border border-red-100">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-red-600">Gastos</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    <div className="flex justify-between"><span>Combustible:</span><span className="font-medium">{vehiculoDetalleData.gastos?.combustible}</span></div>
                    <div className="flex justify-between"><span>Mantenimiento:</span><span className="font-medium">{vehiculoDetalleData.gastos?.mantenimiento}</span></div>
                    <div className="flex justify-between"><span>Seguro:</span><span className="font-medium">{vehiculoDetalleData.gastos?.seguro}</span></div>
                    <div className="flex justify-between border-t pt-1"><span>Total:</span><span className="font-medium">{vehiculoDetalleData.gastos?.total}</span></div>
                  </CardContent>
                </Card>

                {/* Rentabilidad */}
                <Card className="border border-green-100">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-green-600">Rentabilidad</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    <div className="flex justify-between"><span>Margen Neto:</span><span className={`font-medium ${vehiculoDetalleData.rentabilidad?.margen_neto?.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>{vehiculoDetalleData.rentabilidad?.margen_neto}</span></div>
                    <div className="flex justify-between"><span>Margen %:</span><span className={`font-medium ${vehiculoDetalleData.rentabilidad?.margen_porcentaje?.startsWith('-') ? 'text-red-600' : 'text-green-600'}`}>{vehiculoDetalleData.rentabilidad?.margen_porcentaje}</span></div>
                    <div className="flex justify-between"><span>Benchmarking:</span><span className={`font-medium capitalize ${vehiculoDetalleData.benchmarking?.comparacion === 'superior' ? 'text-green-600' : vehiculoDetalleData.benchmarking?.comparacion === 'inferior' ? 'text-red-600' : 'text-yellow-600'}`}>{vehiculoDetalleData.benchmarking?.comparacion}</span></div>
                    <div className="flex justify-between"><span>Promedio flota:</span><span className="font-medium">{vehiculoDetalleData.benchmarking?.promedio_flota}</span></div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ============================================
          MEDIOS DE PAGO Y GASTOS OPERATIVOS
      ============================================ */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Medios de Pago */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Medios de Pago</CardTitle>
          </CardHeader>
          <CardContent>
            {mediosLoading ? (
              <div className="flex h-[150px] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : medios.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
            ) : (
              <div className="space-y-3">
                {medios.map((medio: MedioPago) => (
                  <div key={medio.medio_pago} className="flex items-center gap-2">
                    <span className="text-lg">{getMedioIcono(medio.medio_pago)}</span>
                    <span className="text-sm font-medium flex-1 capitalize">{medio.medio_pago}</span>
                    <span className="text-sm text-muted-foreground">{medio.total_viajes} viajes</span>
                    <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full"
                        style={{ width: medio.porcentaje }}
                      />
                    </div>
                    <span className="text-sm font-medium">{medio.porcentaje}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Gastos Operativos */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Gastos Operativos</CardTitle>
          </CardHeader>
          <CardContent>
            {gastosLoading ? (
              <div className="flex h-[150px] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : gastos.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
            ) : (
              <div className="space-y-3">
                {gastos.map((gasto: GastoOperativo) => (
                  <div key={gasto.tipo_gasto} className="flex items-center gap-2">
                    {getGastoIcono(gasto.tipo_gasto)}
                    <span className="text-sm font-medium flex-1 capitalize">{gasto.tipo_gasto}</span>
                    <span className="text-sm text-muted-foreground">{gasto.porcentaje}</span>
                    <span className="text-sm font-medium">{gasto.total}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ============================================
          SOLICITUDES ACTIVAS (EXISTENTE)
      ============================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Solicitudes Activas</CardTitle>
        </CardHeader>
        <CardContent>
          {solicitudesData?.solicitudes?.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay solicitudes activas</p>
          ) : (
            <div className="space-y-2">
              {(solicitudesData?.solicitudes || []).map((solicitud: any) => (
                <div key={solicitud.id} className="flex items-center justify-between border-b pb-2 text-sm">
                  <div>
                    <span className="font-medium">{solicitud.pasajero}</span>
                    <span className="text-muted-foreground"> → </span>
                    <span className="text-muted-foreground">{solicitud.destino}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      solicitud.estado === 'pendiente' ? 'bg-yellow-100 text-yellow-700' :
                      solicitud.estado === 'aceptado' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {solicitud.estado}
                    </span>
                    <span className="text-xs text-muted-foreground">{solicitud.hora}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ============================================
          CHOFERES ONLINE (EXISTENTE)
      ============================================ */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Choferes Online</CardTitle>
        </CardHeader>
        <CardContent>
          {(choferesData?.choferes || []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No hay choferes online</p>
          ) : (
            <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
              {(choferesData?.choferes || []).map((chofer: any) => (
                <div key={chofer.id} className="flex items-center gap-2 border rounded-lg p-2">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium">{chofer.nombre}</span>
                  <span className="text-xs text-muted-foreground">{chofer.patente}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}