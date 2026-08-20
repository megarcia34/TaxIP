'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Car, 
  Calendar, 
  DollarSign, 
  TrendingUp,
  Fuel,
  Wrench,
  Shield,
  FileText,
  Loader2,
  AlertCircle,
  RefreshCw,
  Users,
  PieChart,
  BarChart3,
  Eye,
  Settings,
  UserCog,
  ClipboardList,
  Plus,
  Edit,
  Crown,
  ShieldCheck,
  UserCheck
} from 'lucide-react'
import Link from 'next/link'

// ============================================
// INTERFACES
// ============================================

interface TenantData {
  tenant_id: string
  tenant_nombre: string
  total_vehiculos: number
  total_viajes: number
  total_recaudacion: number
  promedio_por_viaje: number
  total_gastos: number
  utilidad_neta: number
  margen: number
}

interface DashboardData {
  totalTenants: number
  totalVehiculos: number
  totalViajes: number
  totalRecaudacion: number
  totalPropietarios?: number
  tenants: TenantData[]
  mediosPago: Array<{
    medio_pago: string
    total_viajes: number
    total_ingresos: number
    porcentaje: number
  }>
  gastosOperativos: Array<{
    tipo_gasto: string
    total: number
  }>
  evolucionMensual: Array<{
    mes: string
    total_viajes: number
    total_recaudacion: number
  }>
  periodo: {
    tipo: string
    desde: string
    hasta: string
  }
  volumenTransacciones?: {
    total: number
    por_tipo: Array<{ tipo: string; total: number }>
  }
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

const formatCurrency = (value: number): string => {
  if (value === undefined || value === null || isNaN(value)) return '$ 0,00'
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const formatNumber = (value: number): string => {
  if (value === undefined || value === null || isNaN(value)) return '0'
  return new Intl.NumberFormat('es-AR').format(value)
}

const formatPercentage = (value: number): string => {
  if (value === undefined || value === null || isNaN(value)) return '0,00%'
  return new Intl.NumberFormat('es-AR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100)
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-AR')
  } catch {
    return dateStr
  }
}

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

const getMargenColor = (margen: number) => {
  if (margen >= 30) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
  if (margen >= 15) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
  if (margen >= 0) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
}

const getEstadoColor = (deuda: number) => {
  if (deuda === 0) return { color: '🟢', texto: 'Al día', badge: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' }
  if (deuda <= 10000) return { color: '🟡', texto: 'Riesgo', badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' }
  return { color: '🔴', texto: 'Mora', badge: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export default function SuperAdminDashboard() {
  const { data: session } = useSession()
  const [periodo, setPeriodo] = useState<'dia' | 'semana' | 'mes'>('mes')

  // Detectar permisos según rol
  const user = session?.user as any
  const tipoUsuario = user?.tipo_usuario?.toLowerCase() || ''
  const controlBaseId = user?.control_base_id

  // ✅ Super Admin Maestro (Dueño de la plataforma)
  const isSuperAdminMaestro = tipoUsuario === 'super_admin' || tipoUsuario === 'superadmin'

  // ✅ Super Admin (Empleado administrativo)
  const isSuperAdmin = tipoUsuario === 'admin' && !controlBaseId

  // ✅ PERMISOS ESPECÍFICOS
  const puedeVerResultadosEconomicos = isSuperAdminMaestro
  const puedeGestionarSuperAdmins = isSuperAdminMaestro
  const puedeVerConfiguracionGlobal = isSuperAdminMaestro

  // ✅ PERMISOS COMPARTIDOS
  const puedeVerKPIsBasicos = isSuperAdminMaestro || isSuperAdmin
  const puedeVerRankingTenants = isSuperAdminMaestro || isSuperAdmin
  const puedeVerIngresosPorTenant = isSuperAdminMaestro || isSuperAdmin
  const puedeVerEvolucionMensual = isSuperAdminMaestro || isSuperAdmin
  const puedeVerAuditoria = isSuperAdminMaestro || isSuperAdmin
  const puedeGestionarTenants = isSuperAdminMaestro || isSuperAdmin

  const { data, isLoading, error, refetch } = useQuery<DashboardData>({
    queryKey: ['super-admin-dashboard', periodo],
    queryFn: async () => {
      const res = await fetch(`/api/super-admin/dashboard?periodo=${periodo}`)
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.error || 'Error al cargar datos')
      }
      return res.json()
    },
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-muted-foreground">Error al cargar el dashboard</p>
          <p className="text-sm text-muted-foreground">{(error as Error)?.message}</p>
          <Button onClick={() => refetch()} variant="outline" className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            Reintentar
          </Button>
        </div>
      </div>
    )
  }

  const stats = data || {
    totalTenants: 0,
    totalVehiculos: 0,
    totalViajes: 0,
    totalRecaudacion: 0,
    totalPropietarios: 0,
    tenants: [],
    mediosPago: [],
    gastosOperativos: [],
    evolucionMensual: [],
    periodo: { tipo: 'mes', desde: '', hasta: '' }
  }

  const totalGastos = stats.gastosOperativos.reduce((sum, g) => sum + g.total, 0)

  return (
    <div className="space-y-6">
      {/* ============================================
          HEADER - Con badge de rol
      ============================================ */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">
              {isSuperAdminMaestro ? 'Dashboard Dueño' : 'Dashboard Administrativo'}
            </h1>
            {isSuperAdminMaestro ? (
              <Badge className="bg-yellow-500 text-white hover:bg-yellow-600">
                <Crown className="h-3 w-3 mr-1" />
                Dueño
              </Badge>
            ) : (
              <Badge className="bg-blue-500 text-white hover:bg-blue-600">
                <ShieldCheck className="h-3 w-3 mr-1" />
                Super Admin
              </Badge>
            )}
          </div>
          <p className="text-muted-foreground mt-1">
            {isSuperAdminMaestro 
              ? 'Control total de la plataforma - Acceso a resultados económicos' 
              : 'Gestión administrativa y técnica de la plataforma'}
            {stats.periodo?.desde && (
              <span className="ml-2 text-sm">
                ({formatDate(stats.periodo.desde)} - {formatDate(stats.periodo.hasta)})
              </span>
            )}
          </p>
          {isSuperAdmin && !isSuperAdminMaestro && (
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
              <UserCheck className="h-3 w-3" />
              Acceso a gestión administrativa - Sin resultados económicos
            </p>
          )}
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
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* ============================================
          KPIs BÁSICOS
      ============================================ */}
      {puedeVerKPIsBasicos && (
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tenants</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(stats.totalTenants)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Propietarios</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(stats.totalPropietarios || 0)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Vehículos</CardTitle>
              <Car className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(stats.totalVehiculos)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Viajes</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(stats.totalViajes)}</div>
            </CardContent>
          </Card>
          
          {/* Recaudación - SOLO Super Admin Maestro */}
          {puedeVerResultadosEconomicos && (
            <Card className="border-2 border-yellow-200 dark:border-yellow-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-1">
                  <DollarSign className="h-4 w-4 text-yellow-600" />
                  Recaudación
                </CardTitle>
                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                  Dueño
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{formatCurrency(stats.totalRecaudacion)}</div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ============================================
          RANKING DE TENANTS
      ============================================ */}
      {puedeVerRankingTenants && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Rendimiento por Tenant</CardTitle>
              <div className="flex gap-2">
                {puedeGestionarTenants && (
                  <Link href="/super-admin/tenants/nuevo">
                    <Button variant="outline" size="sm">
                      <Plus className="h-3 w-3 mr-1" />
                      Nuevo Tenant
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium">Tenant</th>
                    <th className="pb-3 font-medium text-center">Vehículos</th>
                    <th className="pb-3 font-medium text-center">Viajes</th>
                    {puedeVerIngresosPorTenant && (
                      <>
                        <th className="pb-3 font-medium text-right">Ingresos</th>
                        <th className="pb-3 font-medium text-right">Gastos</th>
                        <th className="pb-3 font-medium text-right">Utilidad</th>
                        <th className="pb-3 font-medium text-center">Margen</th>
                      </>
                    )}
                    <th className="pb-3 font-medium text-center">Estado</th>
                    <th className="pb-3 font-medium text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.tenants.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-muted-foreground">
                        No hay datos disponibles
                      </td>
                    </tr>
                  ) : (
                    stats.tenants.map((tenant) => {
                      const deuda = tenant.total_gastos > tenant.total_recaudacion 
                        ? tenant.total_gastos - tenant.total_recaudacion 
                        : 0
                      const estado = getEstadoColor(deuda)
                      return (
                        <tr key={tenant.tenant_id} className="border-b hover:bg-muted/50">
                          <td className="py-3 font-medium">{tenant.tenant_nombre}</td>
                          <td className="py-3 text-center">{formatNumber(tenant.total_vehiculos)}</td>
                          <td className="py-3 text-center">{formatNumber(tenant.total_viajes)}</td>
                          {puedeVerIngresosPorTenant && (
                            <>
                              <td className="py-3 text-right">{formatCurrency(tenant.total_recaudacion)}</td>
                              <td className="py-3 text-right">{formatCurrency(tenant.total_gastos)}</td>
                              <td className={`py-3 text-right font-medium ${tenant.utilidad_neta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(tenant.utilidad_neta)}
                              </td>
                              <td className="py-3 text-center">
                                <Badge className={getMargenColor(tenant.margen)}>
                                  {formatPercentage(tenant.margen)}
                                </Badge>
                              </td>
                            </>
                          )}
                          <td className="py-3 text-center">
                            <Badge className={estado.badge}>
                              {estado.color} {estado.texto}
                            </Badge>
                          </td>
                          <td className="py-3 text-center">
                            <div className="flex gap-1 justify-center">
                              {puedeGestionarTenants && (
                                <Link href={`/super-admin/tenants/${tenant.tenant_id}/editar`}>
                                  <Button variant="ghost" size="sm" title="Editar">
                                    <Edit className="h-4 w-4" />
                                  </Button>
                                </Link>
                              )}
                              <Link href={`/super-admin/tenants/${tenant.tenant_id}`}>
                                <Button variant="ghost" size="sm" title="Ver detalle">
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </Link>
                            </div>
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ============================================
          VOLUMEN DE TRANSACCIONES - SOLO Maestro
      ============================================ */}
      {puedeVerResultadosEconomicos && stats.volumenTransacciones && (
        <Card className="border-2 border-yellow-200 dark:border-yellow-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-yellow-600" />
                Volumen de Transacciones
              </CardTitle>
              <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                Dueño
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg border border-yellow-100 dark:border-yellow-800">
                <div className="text-2xl font-bold text-yellow-600">{formatNumber(stats.volumenTransacciones.total)}</div>
                <div className="text-xs text-muted-foreground">Total Transacciones</div>
              </div>
              {stats.volumenTransacciones.por_tipo.map((tipo) => (
                <div key={tipo.tipo} className="text-center p-4 bg-muted/30 rounded-lg">
                  <div className="text-2xl font-bold">{formatNumber(tipo.total)}</div>
                  <div className="text-xs text-muted-foreground capitalize">{tipo.tipo}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ============================================
          MEDIOS DE PAGO - SOLO Maestro
      ============================================ */}
      {puedeVerResultadosEconomicos && (
        <Card className="border-2 border-yellow-200 dark:border-yellow-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <PieChart className="h-4 w-4 text-yellow-600" />
                Medios de Pago
              </CardTitle>
              <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                Dueño
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {stats.mediosPago.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
            ) : (
              <div className="space-y-3">
                {stats.mediosPago.map((medio) => (
                  <div key={medio.medio_pago} className="flex items-center gap-2">
                    <span className="text-lg">{getMedioIcono(medio.medio_pago)}</span>
                    <span className="text-sm font-medium flex-1 capitalize">{medio.medio_pago}</span>
                    <span className="text-sm text-muted-foreground">{formatNumber(medio.total_viajes)} viajes</span>
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${medio.porcentaje}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{formatPercentage(medio.porcentaje)}</span>
                    <span className="text-sm font-medium text-yellow-600">{formatCurrency(medio.total_ingresos)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ============================================
          GASTOS OPERATIVOS - SOLO Maestro
      ============================================ */}
      {puedeVerResultadosEconomicos && (
        <Card className="border-2 border-yellow-200 dark:border-yellow-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4 text-yellow-600" />
                Gastos Operativos
              </CardTitle>
              <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                Dueño
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {stats.gastosOperativos.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
            ) : (
              <div className="space-y-3">
                {stats.gastosOperativos.map((gasto) => {
                  const porcentaje = totalGastos > 0 ? (gasto.total / totalGastos) * 100 : 0
                  return (
                    <div key={gasto.tipo_gasto} className="flex items-center gap-2">
                      {getGastoIcono(gasto.tipo_gasto)}
                      <span className="text-sm font-medium flex-1 capitalize">{gasto.tipo_gasto}</span>
                      <span className="text-sm text-muted-foreground">{formatPercentage(porcentaje)}</span>
                      <span className="text-sm font-medium text-yellow-600">{formatCurrency(gasto.total)}</span>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ============================================
          EVOLUCIÓN MENSUAL
      ============================================ */}
      {puedeVerEvolucionMensual && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Evolución Mensual</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.evolucionMensual.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
            ) : (
              <div className="space-y-2">
                {stats.evolucionMensual.map((item) => (
                  <div key={item.mes} className="flex items-center gap-4 border-b pb-2">
                    <span className="text-sm font-medium w-20">{item.mes}</span>
                    <span className="text-sm text-muted-foreground flex-1">{formatNumber(item.total_viajes)} viajes</span>
                    {puedeVerResultadosEconomicos && (
                      <span className="text-sm font-medium text-yellow-600">{formatCurrency(item.total_recaudacion)}</span>
                    )}
                    <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${Math.min((item.total_viajes / (stats.evolucionMensual[stats.evolucionMensual.length - 1]?.total_viajes || 1)) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ============================================
          CONFIGURACIÓN GLOBAL - SOLO Maestro
      ============================================ */}
      {puedeVerConfiguracionGlobal && (
        <Card className="border-2 border-yellow-200 dark:border-yellow-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                <Settings className="h-4 w-4" />
                Configuración Global
              </CardTitle>
              <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                <Crown className="h-3 w-3 mr-1" />
                Dueño
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Link href="/super-admin/configuracion">
                <Button variant="outline" className="w-full justify-start">
                  <Settings className="h-4 w-4 mr-2" />
                  Configuración General
                </Button>
              </Link>
              <Link href="/super-admin/configuracion/tarifas">
                <Button variant="outline" className="w-full justify-start">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Tarifas Globales
                </Button>
              </Link>
              <Link href="/super-admin/configuracion/comisiones">
                <Button variant="outline" className="w-full justify-start">
                  <PieChart className="h-4 w-4 mr-2" />
                  Comisiones
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ============================================
          GESTIÓN DE SUPER ADMINS - SOLO Maestro
      ============================================ */}
      {puedeGestionarSuperAdmins && (
        <Card className="border-2 border-yellow-200 dark:border-yellow-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                <UserCog className="h-4 w-4" />
                Gestión de Super Admins
              </CardTitle>
              <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                <Crown className="h-3 w-3 mr-1" />
                Dueño
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <Link href="/super-admin/super-admins">
                <Button variant="outline" className="w-full justify-start">
                  <Users className="h-4 w-4 mr-2" />
                  Listar Super Admins
                </Button>
              </Link>
              <Link href="/super-admin/super-admins/nuevo">
                <Button variant="outline" className="w-full justify-start">
                  <Plus className="h-4 w-4 mr-2" />
                  Crear Super Admin
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ============================================
          AUDITORÍA GLOBAL
      ============================================ */}
      {puedeVerAuditoria && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <ClipboardList className="h-4 w-4" />
                Auditoría Global
              </CardTitle>
              <Link href="/super-admin/auditoria">
                <Button variant="outline" size="sm">
                  Ver todos
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Últimos eventos registrados en la plataforma.
            </p>
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-sm border-b pb-2">
                <span className="text-green-600">✅ Login</span>
                <span className="text-muted-foreground">super@taxip.com</span>
                <span className="text-xs text-muted-foreground">Hace 2 min</span>
              </div>
              <div className="flex items-center justify-between text-sm border-b pb-2">
                <span className="text-blue-600">📝 Creación</span>
                <span className="text-muted-foreground">Nuevo tenant</span>
                <span className="text-xs text-muted-foreground">Hace 15 min</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-yellow-600">⚙️ Configuración</span>
                <span className="text-muted-foreground">Tarifas actualizadas</span>
                <span className="text-xs text-muted-foreground">Hace 1 hora</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}