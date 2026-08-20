'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from 'sonner'
import { ArrowLeft, Loader2, RefreshCw, CircleDot, FileText, AlertTriangle, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { useVehiculo } from '@/hooks/useVehiculos'
import { useEstadoVehiculo } from '@/hooks/useEstadoVehiculo'
import { propietarioReportesAPI } from '@/lib/api'
import { ResumenEjecutivo } from '@/components/propietario/ResumenEjecutivo'
import { NeumaticosEnDetalle } from '@/components/propietario/neumaticos/NeumaticosEnDetalle'
import { DocumentosVehiculo } from '@/components/propietario/documentos/DocumentosVehiculo'
import { MantenimientosVehiculo } from '@/components/propietario/mantenimientos/MantenimientosVehiculo'
import { useNeumaticos } from '@/hooks/useNeumaticos'

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export default function VehiculoDetallePage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const vehiculoId = params.id as string
  const [propietario_id, setPropietario_id] = useState<string | null>(null)

  const [resumen, setResumen] = useState<any>(null)
  const [loadingResumen, setLoadingResumen] = useState(true)
  const [periodo, setPeriodo] = useState<'dia' | 'semana' | 'mes'>('mes')
  
  const tabFromUrl = searchParams?.get('tab') || 'resumen'
  const [activeTab, setActiveTab] = useState(tabFromUrl)

  const isAdmin = user?.rol === 'admin'

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search)
    setPropietario_id(searchParams.get('propietario_id'))
    const tab = searchParams.get('tab')
    if (tab) {
      setActiveTab(tab)
    }
  }, [])

  const propietarioId = propietario_id

  // ✅ Validar ID
  const isValidId = vehiculoId && UUID_REGEX.test(vehiculoId)

  // ✅ Hooks
  const { data: vehiculo, isLoading: loadingVehiculo } = useVehiculo(isValidId ? vehiculoId : undefined)
  const { activos, loading: loadingNeumaticos, recargar: recargarNeumaticos } = useNeumaticos(
    isValidId ? vehiculoId : undefined
  )
  
  // ✅ Hook para el estado completo del vehículo
  const { data: estadoVehiculo, isLoading: loadingEstado, refetch: refetchEstado } = useEstadoVehiculo(
    isValidId ? vehiculoId : undefined
  )

  // ✅ Verificar si la configuración está completa
  const configuracionCompleta = estadoVehiculo?.configuracion_completa || false
  const mostrarBanner = vehiculo && !configuracionCompleta

  // ✅ Datos para el banner
  const faltanNeumaticos = estadoVehiculo?.neumaticos?.completo === false
  const faltanDocumentos = estadoVehiculo?.documentos?.completo === false
  const faltanMantenimientos = estadoVehiculo?.mantenimientos?.completo === false
  const docsFaltantes = estadoVehiculo?.documentos?.faltantes || []

  useEffect(() => {
    if (!isValidId) {
      toast.error('ID de vehículo inválido')
      router.push('/dashboard-propietario/vehiculos')
      return
    }
  }, [isValidId, router])

  const cargarResumen = async () => {
    if (!isValidId) return

    setLoadingResumen(true)
    try {
      const data = await propietarioReportesAPI.getResumenEjecutivo(vehiculoId, periodo)
      setResumen(data)
    } catch (error: any) {
      console.error('Error cargando resumen:', error)
      setResumen({
        vehiculo: { id: vehiculoId, patente: 'Cargando...' },
        periodo: { desde: new Date().toISOString(), hasta: new Date().toISOString(), nombre: periodo },
        viajes: { total: 0, km_recorridos: 0, horas_operacion: 0, ingreso_promedio_viaje: 0 },
        ingresos: { brutos: 0, comision_plataforma: 0, netos: 0 },
        gastos: { combustible: 0, mantenimiento: 0, seguro: 0, otros: 0, total: 0 },
        rentabilidad: { margen_neto: 0, roi: 0, costo_por_km: 0, ganancia_por_km: 0 },
        benchmarking: {
          ingresos_netos: { valor: 0, promedio_flota: 0, comparativa: 'SIN_DATOS' },
          gastos: { valor: 0, promedio_flota: 0, comparativa: 'SIN_DATOS' },
          puesto: 0,
          total_vehiculos: 0,
        },
        alertas: {
          ultimo_service: null,
          ultimo_tipo: 'Sin datos',
          proximo_service_estimado: 'No programado',
          desgaste_neumaticos: 0,
          estado_neumaticos: 'BUENO',
        },
        zonas_activas: [],
      })
    } finally {
      setLoadingResumen(false)
    }
  }

  useEffect(() => {
    if (isValidId) {
      cargarResumen()
    }
  }, [vehiculoId, periodo])

  // ✅ Función para recargar todo
  const handleRecargar = () => {
    cargarResumen()
    refetchEstado()
    recargarNeumaticos(vehiculoId)
  }

  // ✅ Si el ID no es válido
  if (!isValidId) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (loadingVehiculo || loadingEstado) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!vehiculo) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Vehículo no encontrado</p>
        <Button className="mt-4" onClick={() => router.push('/dashboard-propietario/vehiculos')}>
          Volver
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <Link
            href={
              isAdmin && propietarioId
                ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
                : '/dashboard-propietario/vehiculos'
            }
          >
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              {vehiculo.patente || 'Vehículo'}
              {configuracionCompleta ? (
                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full font-normal">
                  ✅ Habilitado
                </span>
              ) : (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full font-normal">
                  ⚠️ Pendiente
                </span>
              )}
            </h1>
            <p className="text-muted-foreground">
              {vehiculo.marca || ''} {vehiculo.modelo || ''} ({vehiculo.anio || ''})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Tabs value={periodo} onValueChange={(v) => setPeriodo(v as any)} className="w-[180px]">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="dia">Día</TabsTrigger>
              <TabsTrigger value="semana">Semana</TabsTrigger>
              <TabsTrigger value="mes">Mes</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button variant="outline" size="sm" onClick={handleRecargar}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
        </div>
      </div>

      {/* ✅ Banner - Estado del vehículo */}
      {mostrarBanner ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-medium text-yellow-800">
                ⚠️ Vehículo pendiente de configuración
              </h4>
              <p className="text-sm text-yellow-700">
                Para que <strong>{vehiculo.patente}</strong> quede operativo, completa los siguientes pasos:
              </p>
              <div className="flex flex-wrap gap-4 mt-2 text-sm">
                {/* Neumáticos */}
                <div className="flex items-center gap-1.5">
                  <span className={faltanNeumaticos ? 'text-yellow-600' : 'text-green-600'}>
                    {faltanNeumaticos ? '⬜' : '✅'}
                  </span>
                  <span className={faltanNeumaticos ? 'text-yellow-700' : 'text-green-700'}>
                    Neumáticos ({estadoVehiculo?.neumaticos?.activos || 0}/4)
                  </span>
                  {faltanNeumaticos && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-6 px-2 text-xs border-yellow-300 text-yellow-700 hover:bg-yellow-100"
                      onClick={() => setActiveTab('neumaticos')}
                    >
                      Montar
                    </Button>
                  )}
                </div>

                {/* Documentos */}
                <div className="flex items-center gap-1.5">
                  <span className={faltanDocumentos ? 'text-yellow-600' : 'text-green-600'}>
                    {faltanDocumentos ? '⬜' : '✅'}
                  </span>
                  <span className={faltanDocumentos ? 'text-yellow-700' : 'text-green-700'}>
                    Documentación {faltanDocumentos && docsFaltantes.length > 0 ? `(faltan: ${docsFaltantes.join(', ')})` : '(Completa)'}
                  </span>
                  {faltanDocumentos && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-6 px-2 text-xs border-yellow-300 text-yellow-700 hover:bg-yellow-100"
                      onClick={() => setActiveTab('documentos')}
                    >
                      Subir
                    </Button>
                  )}
                </div>

                {/* Mantenimientos */}
                <div className="flex items-center gap-1.5">
                  <span className={faltanMantenimientos ? 'text-yellow-600' : 'text-green-600'}>
                    {faltanMantenimientos ? '⬜' : '✅'}
                  </span>
                  <span className={faltanMantenimientos ? 'text-yellow-700' : 'text-green-700'}>
                    Mantenimientos {faltanMantenimientos ? '(Ninguno registrado)' : `(${estadoVehiculo?.mantenimientos?.total || 0} registrados)`}
                  </span>
                  {faltanMantenimientos && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-6 px-2 text-xs border-yellow-300 text-yellow-700 hover:bg-yellow-100"
                      onClick={() => setActiveTab('mantenimientos')}
                    >
                      Registrar
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* ✅ Banner de éxito - Vehículo habilitado */
        vehiculo && configuracionCompleta && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium text-green-800">
                  ✅ Vehículo habilitado
                </h4>
                <p className="text-sm text-green-700">
                  <strong>{vehiculo.patente}</strong> está completamente configurado y listo para operar.
                </p>
                <div className="flex flex-wrap gap-4 mt-1 text-sm text-green-600">
                  <span>✅ {estadoVehiculo?.neumaticos?.activos || 0}/4 neumáticos</span>
                  <span>✅ Documentación completa</span>
                  <span>✅ {estadoVehiculo?.mantenimientos?.total || 0} mantenimientos registrados</span>
                </div>
              </div>
            </div>
          </div>
        )
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 md:grid-cols-4 max-w-2xl">
          <TabsTrigger value="resumen">Resumen</TabsTrigger>
          <TabsTrigger value="neumaticos" className="flex items-center gap-1">
            <CircleDot className="h-3.5 w-3.5" />
            Neumáticos
          </TabsTrigger>
          <TabsTrigger value="documentos" className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5" />
            Documentos
          </TabsTrigger>
          <TabsTrigger value="mantenimientos">Mantenimientos</TabsTrigger>
        </TabsList>

        <TabsContent value="resumen" className="mt-4">
          {resumen ? (
            <ResumenEjecutivo data={{ ...resumen, zonas_activas: resumen.zonas_activas || [] }} loading={loadingResumen} />
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p>No hay datos disponibles para este vehículo</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="neumaticos" className="mt-4">
          <NeumaticosEnDetalle
            vehiculoId={vehiculoId}
            activos={activos}
            loading={loadingNeumaticos}
            onRecargar={() => recargarNeumaticos(vehiculoId)}
          />
        </TabsContent>

        <TabsContent value="documentos" className="mt-4">
          {!activos || Object.values(activos.neumaticos).every(n => n === null) ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <CircleDot className="h-12 w-12 mx-auto text-yellow-500 mb-3" />
              <h3 className="text-lg font-medium text-yellow-800">⚠️ Documentos bloqueados</h3>
              <p className="text-yellow-700 mt-1">
                Para acceder a los documentos, primero debes registrar los neumáticos del vehículo.
              </p>
              <Button 
                className="mt-4"
                onClick={() => setActiveTab('neumaticos')}
              >
                Ir a Neumáticos
              </Button>
            </div>
          ) : (
            <DocumentosVehiculo vehiculoId={vehiculoId} />
          )}
        </TabsContent>

        <TabsContent value="mantenimientos" className="mt-4">
          <MantenimientosVehiculo vehiculoId={vehiculoId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}