'use client'

import { useState, useCallback, useMemo, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  FileText,
  Loader2,
  Plus,
  XCircle,
  Calendar,
  Clock,
  User,
  Car,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Ban,
  Clock as ClockIcon,
  CalendarDays,
  MapPin,
  Fuel,
  Gauge,
  CreditCard,
  Users,
} from 'lucide-react'
import { toast } from 'sonner'
import CrearContratoModal from '@/components/propietario/contratos/CrearContratoModal'
import { useContratos, useFinalizarContrato } from '@/hooks/propietario/useContratos'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface Contrato {
  id: string
  vehiculo_id: string
  patente: string
  marca: string
  modelo: string
  chofer_id: string
  chofer_nombre: string
  chofer_apellido: string
  tipo_contrato: string
  turno_asignado: string
  porcentaje_chofer: number | null
  canon_diario: number | null
  km_incluidos_dia: number | null
  valor_km_excedente: number | null
  modalidad_computo: string | null
  dias_contractuales: string[] | null
  tratamiento_dia_no_trabajado: string | null
  fecha_inicio: string
  fecha_fin: string | null
  activo: boolean
  estado_contrato: string
  hora_inicio?: string
  hora_fin?: string
}

export default function PropietarioContratosPage() {
  const router = useRouter()
  const { user } = useAuth()

  const [propietarioId, setPropietarioId] = useState<string | null>(null)
  const [filterActivo, setFilterActivo] = useState<boolean | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [selectedContrato, setSelectedContrato] = useState<Contrato | null>(null)

  const isAdmin = user?.rol === 'admin'

  const { data: contratos = [], isLoading, refetch } = useContratos(filterActivo)
  const finalizarMutation = useFinalizarContrato()

 useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const pid = params.get('propietario_id')
      setPropietarioId(pid)
    }
  }, [])

  const handleFinalizar = async (contratoId: string) => {
    if (!confirm('¿Estás seguro de que deseas finalizar este contrato?')) return
    finalizarMutation.mutate(contratoId)
  }

  const handleSuccess = useCallback(() => {
    setShowModal(false)
    refetch()
  }, [refetch])

  // ✅ Estadísticas
  const estadisticas = useMemo(() => {
  const total = contratos.length
  const activos = contratos.filter((c: Contrato) => c.activo).length
  const finalizados = contratos.filter((c: Contrato) => !c.activo).length
  const alquiler = contratos.filter((c: Contrato) => c.tipo_contrato === 'ALQUILER').length
  const porcentaje = contratos.filter((c: Contrato) => c.tipo_contrato === 'PORCENTAJE').length
  const autogestion = contratos.filter((c: Contrato) => c.tipo_contrato === 'AUTO_GESTION').length
  
  return { total, activos, finalizados, alquiler, porcentaje, autogestion }
}, [contratos])

  const getTipoContratoLabel = (tipo: string) => {
    const tipos: Record<string, string> = {
      AUTO_GESTION: 'Auto-gestión',
      PORCENTAJE: 'A porcentaje',
      ALQUILER: 'Alquiler'
    }
    return tipos[tipo] || tipo
  }

  const getTipoContratoColor = (tipo: string) => {
    const colores: Record<string, string> = {
      AUTO_GESTION: 'bg-blue-100 text-blue-800 border-blue-200',
      PORCENTAJE: 'bg-purple-100 text-purple-800 border-purple-200',
      ALQUILER: 'bg-green-100 text-green-800 border-green-200'
    }
    return colores[tipo] || 'bg-gray-100 text-gray-800'
  }

  const getTurnoLabel = (turno: string) => {
    const turnos: Record<string, string> = {
      DIURNO: 'Diurno',
      NOCTURNO: 'Nocturno',
      COMPLETO: 'Completo'
    }
    return turnos[turno] || turno
  }

  const getDetalleContrato = (contrato: Contrato) => {
    if (contrato.tipo_contrato === 'PORCENTAJE') {
      return `${contrato.porcentaje_chofer}% para el chofer`
    }
    if (contrato.tipo_contrato === 'ALQUILER') {
      let detalle = `$${contrato.canon_diario?.toLocaleString() || 0}/día`
      if (contrato.km_incluidos_dia) {
        detalle += ` • ${contrato.km_incluidos_dia} km incluidos`
      }
      if (contrato.valor_km_excedente && contrato.valor_km_excedente > 0) {
        detalle += ` • $${contrato.valor_km_excedente}/km excedente`
      }
      if (contrato.modalidad_computo === 'SEMANAL') {
        detalle += ' • Cómputo semanal'
      }
      return detalle
    }
    return 'Dueño conduce'
  }

  const getDiasAbreviados = (dias: string[] | null) => {
    if (!dias || dias.length === 0) return '—'
    const abreviaturas: Record<string, string> = {
      lunes: 'Lun',
      martes: 'Mar',
      miercoles: 'Mié',
      jueves: 'Jue',
      viernes: 'Vie',
      sabado: 'Sáb',
      domingo: 'Dom'
    }
    return dias.map(d => abreviaturas[d] || d).join(', ')
  }

  const getEstadoBadge = (contrato: Contrato) => {
    if (!contrato.activo) {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-700">Finalizado</Badge>
    }
    
    switch (contrato.estado_contrato) {
      case 'ACTIVO':
        return <Badge className="bg-green-500 hover:bg-green-600">Activo</Badge>
      case 'PROGRAMADO':
        return <Badge className="bg-yellow-500 hover:bg-yellow-600">Programado</Badge>
      case 'PENDIENTE_CONFIGURACION':
        return <Badge className="bg-orange-500 hover:bg-orange-600">Pendiente Config.</Badge>
      default:
        return <Badge>Activo</Badge>
    }
  }

  // ✅ Formatear fecha
  const formatFecha = (fecha: string | null) => {
    if (!fecha) return '—'
    try {
      return format(new Date(fecha), 'dd/MM/yyyy', { locale: es })
    } catch {
      return fecha
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Contratos</h1>
          <p className="text-muted-foreground">
            Gestión de contratos de vehículos
            {isAdmin && propietarioId && ' (vista de administrador)'}
          </p>
        </div>
        <Button onClick={() => setShowModal(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Nuevo Contrato
        </Button>
      </div>

      {/* ESTADÍSTICAS RÁPIDAS */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card className="bg-blue-50 border-blue-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-blue-600 font-medium">Total</p>
                <p className="text-2xl font-bold text-blue-700">{estadisticas.total}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-green-50 border-green-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-green-600 font-medium">Activos</p>
                <p className="text-2xl font-bold text-green-700">{estadisticas.activos}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-red-50 border-red-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-red-600 font-medium">Finalizados</p>
                <p className="text-2xl font-bold text-red-700">{estadisticas.finalizados}</p>
              </div>
              <Ban className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-green-50 border-green-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-green-600 font-medium">Alquiler</p>
                <p className="text-2xl font-bold text-green-700">{estadisticas.alquiler}</p>
              </div>
              <DollarSign className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-purple-50 border-purple-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-purple-600 font-medium">Porcentaje</p>
                <p className="text-2xl font-bold text-purple-700">{estadisticas.porcentaje}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-blue-50 border-blue-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-blue-600 font-medium">Auto-gestión</p>
                <p className="text-2xl font-bold text-blue-700">{estadisticas.autogestion}</p>
              </div>
              <Users className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* LISTADO */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle className="flex items-center gap-2">
              Listado de Contratos
              <Badge variant="outline" className="ml-2">
                {contratos.length} contratos
              </Badge>
            </CardTitle>
            <Tabs
              value={filterActivo === null ? 'todos' : filterActivo ? 'activos' : 'inactivos'}
              onValueChange={(v) => {
                if (v === 'todos') setFilterActivo(null)
                else if (v === 'activos') setFilterActivo(true)
                else setFilterActivo(false)
              }}
            >
              <TabsList>
                <TabsTrigger value="todos">Todos</TabsTrigger>
                <TabsTrigger value="activos">Activos</TabsTrigger>
                <TabsTrigger value="inactivos">Finalizados</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          {contratos.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground/30" />
              <p className="text-lg font-medium">No hay contratos registrados</p>
              <p className="text-sm">Haz clic en "Nuevo Contrato" para comenzar</p>
            </div>
          ) : (
            <div className="space-y-4">
              {contratos.map((c: Contrato) => (
                <div
                  key={c.id}
                  className={`border rounded-lg p-4 transition-all hover:shadow-md ${
                    c.activo ? 'bg-white' : 'bg-gray-50/50'
                  }`}
                >
                  {/* Cabecera del contrato */}
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                    {/* Izquierda: Vehículo + Chofer */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap">
                        <div className="flex items-center gap-2">
                          <Car className="h-4 w-4 text-muted-foreground" />
                          <span className="font-semibold text-lg">{c.patente}</span>
                          <span className="text-sm text-muted-foreground">
                            {c.marca} {c.modelo}
                          </span>
                        </div>
                        <Badge variant="outline" className={getTipoContratoColor(c.tipo_contrato)}>
                          {getTipoContratoLabel(c.tipo_contrato)}
                        </Badge>
                        {getEstadoBadge(c)}
                      </div>
                      
                      <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground flex-wrap">
                        <span className="flex items-center gap-1">
                          <User className="h-3.5 w-3.5" />
                          {c.tipo_contrato === 'AUTO_GESTION' ? (
                            <span className="text-xs">(dueño conduce)</span>
                          ) : (
                            `${c.chofer_nombre} ${c.chofer_apellido || ''}`
                          )}
                        </span>
                        
                        {c.hora_inicio && c.hora_fin && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            {c.hora_inicio} - {c.hora_fin}
                          </span>
                        )}
                        
                        <span className="flex items-center gap-1">
                          <CalendarDays className="h-3.5 w-3.5" />
                          {getDiasAbreviados(c.dias_contractuales)}
                        </span>
                      </div>
                    </div>

                    {/* Derecha: Acciones */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {c.activo && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleFinalizar(c.id)}
                          className="text-red-500 hover:text-red-600 hover:bg-red-50"
                          disabled={finalizarMutation.isPending}
                        >
                          {finalizarMutation.isPending ? (
                            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <XCircle className="h-4 w-4 mr-1" />
                          )}
                          Finalizar
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Detalles del contrato */}
                  <div className="mt-3 pt-3 border-t grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="text-muted-foreground">Detalle:</span>
                      <span className="font-medium">{getDetalleContrato(c)}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="text-muted-foreground">Inicio:</span>
                      <span className="font-medium">{formatFecha(c.fecha_inicio)}</span>
                      {c.fecha_fin && (
                        <>
                          <span className="text-muted-foreground">→</span>
                          <span className="font-medium">{formatFecha(c.fecha_fin)}</span>
                        </>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Gauge className="h-4 w-4 text-purple-600" />
                      <span className="text-muted-foreground">KM:</span>
                      <span className="font-medium">
                        {c.km_incluidos_dia || 0} km/día
                        {c.valor_km_excedente && c.valor_km_excedente > 0 && (
                          <span className="text-muted-foreground text-xs ml-1">
                            (excedente ${c.valor_km_excedente})
                          </span>
                        )}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <ClockIcon className="h-4 w-4 text-orange-600" />
                      <span className="text-muted-foreground">Tratamiento:</span>
                      <span className="font-medium">
                        {c.tratamiento_dia_no_trabajado === 'POR_DISPONIBILIDAD' 
                          ? 'Por disponibilidad' 
                          : 'Por uso efectivo'}
                      </span>
                    </div>
                  </div>

                  {/* Badge de "Programado" si es futuro */}
                  {c.estado_contrato === 'PROGRAMADO' && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-yellow-600 bg-yellow-50 px-3 py-1 rounded-md">
                      <AlertCircle className="h-3.5 w-3.5" />
                      Este contrato comenzará el {formatFecha(c.fecha_inicio)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* MODAL */}
      <CrearContratoModal
        open={showModal}
        onOpenChange={setShowModal}
        onSuccess={handleSuccess}
      />
    </div>
  )
}