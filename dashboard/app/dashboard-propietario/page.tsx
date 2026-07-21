'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import Link from 'next/link'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Car, TrendingUp, TrendingDown, Wallet, DollarSign, 
  AlertTriangle, Users, Calendar,
  ArrowRight, Clock, Loader2,
  Building2, Briefcase
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { propietarioAPI, apiClient } from '@/lib/api'

interface DashboardData {
  kpis: {
    total_vehiculos: number
    total_contratos_activos: number
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
  vehiculos_activos: {
    id: string
    patente: string
    modelo: string
    estado_laboral: string
    chofer_nombre: string | null
  }[]
  alertas: {
    mantenimientos: number
    documentos: number
    deudas: number
  }
}

interface Propietario {
  id: string
  usuario_id: string
  nombre: string
  email: string
  total_vehiculos?: number
}

export default function PropietarioDashboardPage() {
  const router = useRouter()
  const { user } = useAuth()
  
  // ✅ Estado para propietario_id (leído desde la URL)
  const [propietarioId, setPropietarioId] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])
  
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [periodo, setPeriodo] = useState('mes')
  const [propietarios, setPropietarios] = useState<Propietario[]>([])
  const [selectedPropietarioId, setSelectedPropietarioId] = useState<string | null>(null)
  const [loadingPropietarios, setLoadingPropietarios] = useState(true)

  const isAdmin = user?.rol === 'admin'

  // ============================================
  // CARGAR PROPIETARIOS (SOLO ADMIN)
  // ============================================
  useEffect(() => {
    const loadPropietarios = async () => {
      if (isAdmin) {
        try {
          const data = await propietarioAPI.getAll()
          setPropietarios(data || [])
          
          // ✅ Usar propietarioId del estado (no searchParams)
          if (propietarioId && data?.some((p: any) => p.id === propietarioId)) {
            setSelectedPropietarioId(propietarioId)
            localStorage.setItem('selectedPropietarioId', propietarioId)
          } else if (data && data.length > 0) {
            setSelectedPropietarioId(data[0].id)
            localStorage.setItem('selectedPropietarioId', data[0].id)
          }
        } catch (error) {
          console.error('Error cargando propietarios:', error)
          toast.error('Error al cargar propietarios')
        } finally {
          setLoadingPropietarios(false)
        }
      } else {
        setLoadingPropietarios(false)
      }
    }

    if (user) {
      loadPropietarios()
    }
  }, [isAdmin, user, propietarioId])  // ✅ Dependencia: propietarioId

  // ============================================
  // CARGAR DASHBOARD
  // ============================================
  const cargarDashboard = async () => {
    setLoading(true)
    
    try {
      if (isAdmin && !selectedPropietarioId) {
        setData({
          kpis: {
            total_vehiculos: 0,
            total_contratos_activos: 0,
            ingresos_mes: 0,
            gastos_mes: 0,
            ganancia_mes: 0,
            viajes_mes: 0
          },
          ultimos_viajes: [],
          vehiculos_activos: [],
          alertas: { mantenimientos: 0, documentos: 0, deudas: 0 }
        })
        setLoading(false)
        return
      }

      const [vehiculosRes, contratosRes, finanzasRes, alertasMRes, alertasDRes, viajesRes] = await Promise.all([
        apiClient.get('/api/propietario/vehiculos'),
        apiClient.get('/api/propietario/contratos?activo=true'),
        apiClient.get(`/api/propietario/resumen-financiero?periodo=${periodo}`),
        apiClient.get('/api/propietario/mantenimientos/alertas'),
        apiClient.get('/api/propietario/documentos/vencimientos?dias_previos=30'),
        apiClient.get('/api/propietario/ingresos?limit=5')
      ])

      const vehiculos = vehiculosRes.data || []
      const contratos = contratosRes.data || []
      const finanzas = finanzasRes.data || { kpis: {}, flujo: {} }
      const alertasM = alertasMRes.data || { total_alertas: 0 }
      const alertasD = alertasDRes.data || []
      const viajes = viajesRes.data || []

      setData({
        kpis: {
          total_vehiculos: vehiculos.length || 0,
          total_contratos_activos: contratos.length || 0,
          ingresos_mes: finanzas.kpis?.total_ingresos || 0,
          gastos_mes: finanzas.kpis?.total_gastos || 0,
          ganancia_mes: finanzas.kpis?.ganancia_neta || 0,
          viajes_mes: viajes.filter((v: any) => v.tipo === 'viaje').length || 0
        },
        ultimos_viajes: viajes.filter((v: any) => v.tipo === 'viaje').slice(0, 5).map((v: any) => ({
          id: v.id,
          direccion_origen: v.descripcion || 'Viaje',
          direccion_destino: v.descripcion || 'Viaje',
          precio_final: v.monto || 0,
          created_at: v.fecha || new Date().toISOString(),
          patente: v.vehiculo_patente || 'N/A',
          chofer_nombre: v.chofer_nombre || 'N/A'
        })),
        vehiculos_activos: vehiculos.map((v: any) => ({
          id: v.id,
          patente: v.patente,
          modelo: `${v.marca} ${v.modelo}`,
          estado_laboral: v.estado_laboral || 'disponible',
          chofer_nombre: v.chofer_asignado || null
        })),
        alertas: {
          mantenimientos: alertasM.total_alertas || 0,
          documentos: alertasD.length || 0,
          deudas: 0
        }
      })
    } catch (error: any) {
      console.error('Error cargando dashboard:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar el dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!loadingPropietarios) {
      cargarDashboard()
    }
  }, [periodo, selectedPropietarioId, loadingPropietarios])

  const handlePropietarioChange = (id: string) => {
    setSelectedPropietarioId(id)
    localStorage.setItem('selectedPropietarioId', id)
    router.push(`/dashboard-propietario?propietario_id=${id}`)
  }

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  // ✅ CORREGIDO: Usa className en lugar de variant para Badge
  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string, className: string }> = {
      'libre': { 
        label: 'Disponible', 
        className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-200' 
      },
      'ocupado': { 
        label: 'Ocupado', 
        className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-200' 
      },
      'en_viaje': { 
        label: 'En viaje', 
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200' 
      },
      'fuera_servicio': { 
        label: 'Fuera de servicio', 
        className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200' 
      }
    }
    const info = estados[estado] || { 
      label: estado, 
      className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200' 
    }
    return <Badge className={info.className}>{info.label}</Badge>
  }

  if (loadingPropietarios) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-muted-foreground">Cargando propietarios...</p>
        </div>
      </div>
    )
  }

  if (isAdmin && propietarios.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Módulo Propietarios</h1>
          <p className="text-muted-foreground">No hay propietarios registrados en el sistema</p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Sin propietarios</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Registra un propietario para comenzar a gestionar su flota desde el panel de administración
            </p>
            <Button className="mt-4" onClick={() => router.push('/admin/propietarios/nuevo')}>
              Registrar Propietario
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isAdmin && !selectedPropietarioId && propietarios.length > 0) {
    setSelectedPropietarioId(propietarios[0].id)
    return null
  }

  if (loading && !data) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Car className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-muted-foreground">Cargando datos...</p>
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <Briefcase className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">
              {isAdmin ? 'Dashboard de Propietarios' : 'Mi Dashboard'}
            </h1>
            <p className="text-muted-foreground">
              {isAdmin 
                ? `Gestionando flota de ${propietarios.find(p => p.id === selectedPropietarioId)?.nombre || ''}`
                : 'Resumen general de tu flota'
              }
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {isAdmin && propietarios.length > 0 && (
            <Select
              value={selectedPropietarioId || undefined}
              onValueChange={handlePropietarioChange}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Seleccionar propietario" />
              </SelectTrigger>
              <SelectContent>
                {propietarios.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    <div className="flex items-center gap-2">
                      <Users className="h-3 w-3" />
                      {p.nombre}
                      {p.total_vehiculos !== undefined && (
                        <span className="text-xs text-muted-foreground">
                          ({p.total_vehiculos} vehículos)
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          <Tabs value={periodo} onValueChange={setPeriodo} className="w-[180px]">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="dia">Día</TabsTrigger>
              <TabsTrigger value="mes">Mes</TabsTrigger>
              <TabsTrigger value="ano">Año</TabsTrigger>
            </TabsList>
          </Tabs>

          <Button variant="outline" onClick={cargarDashboard} size="sm">
            <Clock className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
        </div>
      </div>

      {(data.alertas.mantenimientos > 0 || data.alertas.documentos > 0) && (
        <Card className="border-yellow-200 bg-yellow-50/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              Alertas pendientes ({data.alertas.mantenimientos + data.alertas.documentos})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              {data.alertas.mantenimientos > 0 && (
                <Link 
                  href={`/dashboard-propietario/mantenimientos${isAdmin && selectedPropietarioId ? `?propietario_id=${selectedPropietarioId}` : ''}`} 
                  className="text-sm hover:underline"
                >
                  🔧 {data.alertas.mantenimientos} mantenimientos próximos
                </Link>
              )}
              {data.alertas.documentos > 0 && (
                <Link 
                  href={`/dashboard-propietario/vehiculos${isAdmin && selectedPropietarioId ? `?propietario_id=${selectedPropietarioId}` : ''}`} 
                  className="text-sm hover:underline"
                >
                  📄 {data.alertas.documentos} documentos por vencer
                </Link>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Car className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Vehículos</p>
            </div>
            <p className="text-xl font-bold">{kpis.total_vehiculos}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Contratos</p>
            </div>
            <p className="text-xl font-bold">{kpis.total_contratos_activos}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <p className="text-xs text-muted-foreground">Ingresos</p>
            </div>
            <p className="text-xl font-bold text-green-600">{formatCurrency(kpis.ingresos_mes)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <p className="text-xs text-muted-foreground">Gastos</p>
            </div>
            <p className="text-xl font-bold text-red-600">{formatCurrency(kpis.gastos_mes)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Wallet className={`h-4 w-4 ${kpis.ganancia_mes >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              <p className="text-xs text-muted-foreground">Ganancia</p>
            </div>
            <p className={`text-xl font-bold ${kpis.ganancia_mes >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(kpis.ganancia_mes)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Viajes</p>
            </div>
            <p className="text-xl font-bold">{kpis.viajes_mes}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Vehículos activos</CardTitle>
            <CardDescription>Estado actual de la flota</CardDescription>
          </CardHeader>
          <CardContent>
            {data.vehiculos_activos.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No hay vehículos registrados</p>
            ) : (
              <div className="space-y-2">
                {data.vehiculos_activos.map((v) => (
                  <div key={v.id} className="flex items-center justify-between border-b pb-2">
                    <div className="flex items-center gap-3">
                      <Car className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{v.patente}</p>
                        <p className="text-xs text-muted-foreground">{v.modelo}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {v.chofer_nombre && (
                        <span className="text-xs text-muted-foreground">{v.chofer_nombre}</span>
                      )}
                      {getEstadoBadge(v.estado_laboral)}
                      <Link href={`/dashboard-propietario/vehiculos/${v.id}${isAdmin && selectedPropietarioId ? `?propietario_id=${selectedPropietarioId}` : ''}`}>
                        <Button variant="ghost" size="sm">
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-4">
              <Link href={`/dashboard-propietario/vehiculos${isAdmin && selectedPropietarioId ? `?propietario_id=${selectedPropietarioId}` : ''}`}>
                <Button variant="outline" size="sm">
                  Ver todos <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Últimos viajes</CardTitle>
            <CardDescription>Actividad reciente</CardDescription>
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
            <div className="mt-4">
              <Link href={`/dashboard-propietario/ingresos${isAdmin && selectedPropietarioId ? `?propietario_id=${selectedPropietarioId}` : ''}`}>
                <Button variant="outline" size="sm">
                  Ver todos <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}