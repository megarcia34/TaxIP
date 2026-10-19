// D:\ataxip\dashboard\app\dashboard-propietario\vehiculos\page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Search,
  Plus,
  Eye,
  Edit,
  Trash2,
  Car,
  Loader2,
  Send,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useVehiculos, useDeleteVehiculo } from '@/hooks/useVehiculos'
import { useEnviarVehiculosARevision } from '@/hooks/propietario/useVehiculosRevision'
import { useDeteccionCambiosEstadoVehiculos } from '@/hooks/propietario/useDeteccionCambiosEstadoVehiculos'
import ModalEstadoVehiculos from '@/components/propietario/vehiculos/ModalEstadoVehiculos'
import { format, parseISO, differenceInDays } from 'date-fns'
import { es } from 'date-fns/locale'

type EstadoAprobacion = 'pendiente' | 'en_revision' | 'aprobado' | 'rechazado'

export default function PropietarioVehiculosPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [propietario_id, setPropietario_id] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  // Modales
  const [showModalEnviado, setShowModalEnviado] = useState(false)

  const isAdmin = user?.rol === 'admin'

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietario_id(params.get('propietario_id'))
  }, [])

  const { data: vehiculos = [], isLoading, refetch } = useVehiculos()
  const deleteMutation = useDeleteVehiculo()
  const enviarMutation = useEnviarVehiculosARevision()
  const { cambios, marcarComoVisto } = useDeteccionCambiosEstadoVehiculos(vehiculos)

  const handleDelete = async (id: string) => {
    await deleteMutation.mutateAsync(id)
    setDeleteId(null)
  }

  const handleEnviarARevision = async () => {
    if (!confirm('Enviar todos los vehiculos activos a revision del municipio?')) {
      return
    }
    try {
      await enviarMutation.mutateAsync()
      setShowModalEnviado(true)
      refetch()
    } catch {
      // El hook ya muestra el toast
    }
  }

  // Boton visible solo si hay vehiculos pendientes con docs completas
  const hayParaEnviar = vehiculos.some(
    (v: any) => v.documentacion_completa === true && v.estado_aprobacion === 'pendiente'
  )

  const filteredVehiculos = vehiculos.filter((v: any) =>
    v.patente?.toLowerCase().includes(search.toLowerCase()) ||
    v.marca?.toLowerCase().includes(search.toLowerCase()) ||
    v.modelo?.toLowerCase().includes(search.toLowerCase())
  )

  const getEstadoLaboralBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      libre: {
        label: 'Disponible',
        className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-200',
      },
      ocupado: {
        label: 'Ocupado',
        className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-200',
      },
      en_viaje: {
        label: 'En viaje',
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200',
      },
      fuera_servicio: {
        label: 'Fuera de servicio',
        className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200',
      },
    }
    const info = estados[estado] || {
      label: estado || 'Desconocido',
      className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200',
    }
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const getAprobacionBadge = (estado: EstadoAprobacion) => {
    const config: Record<EstadoAprobacion, { label: string; className: string; icon: any }> = {
      pendiente: {
        label: 'Pendiente',
        className: 'bg-gray-100 text-gray-700 border-gray-300',
        icon: Clock,
      },
      en_revision: {
        label: 'En revisión',
        className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: Clock,
      },
      aprobado: {
        label: 'Aprobado',
        className: 'bg-green-100 text-green-800 border-green-300',
        icon: CheckCircle2,
      },
      rechazado: {
        label: 'Rechazado',
        className: 'bg-red-100 text-red-800 border-red-300',
        icon: XCircle,
      },
    }
    const c = config[estado] || config.pendiente
    const Icon = c.icon
    return (
      <Badge variant="outline" className={`${c.className} gap-1`}>
        <Icon className="h-3 w-3" />
        {c.label}
      </Badge>
    )
  }

  const getDocsBadge = (completa: boolean) => {
    return completa ? (
      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300 gap-1">
        <CheckCircle2 className="h-3 w-3" />
        Completa
      </Badge>
    ) : (
      <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-300 gap-1">
        <AlertCircle className="h-3 w-3" />
        Incompleta
      </Badge>
    )
  }

  const getVencimientoTaxi = (fecha: string | null) => {
    if (!fecha) return <span className="text-muted-foreground">—</span>
    try {
      const d = parseISO(fecha)
      const dias = differenceInDays(d, new Date())
      const fechaFormateada = format(d, 'dd/MM/yyyy', { locale: es })
      if (dias < 0) {
        return (
          <span className="text-red-600 font-medium text-xs">
            Vencido ({fechaFormateada})
          </span>
        )
      }
      if (dias <= 90) {
        return (
          <span className="text-orange-600 font-medium text-xs">
            {fechaFormateada} ({dias}d)
          </span>
        )
      }
      return <span className="text-xs">{fechaFormateada}</span>
    } catch {
      return <span>{fecha}</span>
    }
  }

  // Modales de aprobacion / rechazo
  const cambiosAprobado = cambios.filter((c) => c.estado_actual === 'aprobado')
  const cambiosRechazado = cambios.filter((c) => c.estado_actual === 'rechazado')

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">Vehiculos</h1>
          <p className="text-muted-foreground">Gestion de vehiculos de la flota</p>
        </div>
        <div className="flex gap-2">
          {hayParaEnviar && (
            <Button
              onClick={handleEnviarARevision}
              variant="outline"
              disabled={enviarMutation.isPending}
            >
              {enviarMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Enviar a revision
            </Button>
          )}
          <Link
            href={`/dashboard-propietario/vehiculos/nuevo${isAdmin && propietario_id ? `?propietario_id=${propietario_id}` : ''}`}
          >
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Vehiculo
            </Button>
          </Link>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Listado de Vehiculos</CardTitle>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por patente, marca o modelo..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredVehiculos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Car className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay vehiculos registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 w-12">#</th>
                    <th className="text-left py-3">Patente</th>
                    <th className="text-left py-3">Marca / Modelo</th>
                    <th className="text-left py-3">Año</th>
                    <th className="text-left py-3">Chofer</th>
                    <th className="text-left py-3">Laboral</th>
                    <th className="text-left py-3">Aprobación</th>
                    <th className="text-left py-3">Documentación</th>
                    <th className="text-left py-3">Vence taxi</th>
                    <th className="text-left py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredVehiculos.map((v: any, index: number) => (
                    <tr key={v.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 text-center text-sm text-muted-foreground">
                        {index + 1}
                      </td>
                      <td className="py-3 font-medium">
                        <TooltipProvider delayDuration={300}>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Link
                                href={`/dashboard-propietario/vehiculos/${v.id}${isAdmin && propietario_id ? `?propietario_id=${propietario_id}` : ''}`}
                                className="hover:text-primary hover:underline transition-colors cursor-pointer"
                              >
                                {v.patente}
                              </Link>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="text-sm">
                              <p>Haz clic para ver el detalle completo</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </td>
                      <td className="py-3">{v.marca} {v.modelo}</td>
                      <td className="py-3">{v.anio || '-'}</td>
                      <td className="py-3">{v.chofer_asignado || 'Sin asignar'}</td>
                      <td className="py-3">{getEstadoLaboralBadge(v.estado_laboral || '')}</td>
                      <td className="py-3">{getAprobacionBadge(v.estado_aprobacion)}</td>
                      <td className="py-3">{getDocsBadge(v.documentacion_completa)}</td>
                      <td className="py-3">{getVencimientoTaxi(v.fecha_vencimiento_taxi)}</td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          <Link
                            href={`/dashboard-propietario/vehiculos/${v.id}${isAdmin && propietario_id ? `?propietario_id=${propietario_id}` : ''}`}
                          >
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link
                            href={`/dashboard-propietario/vehiculos/${v.id}/editar${isAdmin && propietario_id ? `?propietario_id=${propietario_id}` : ''}`}
                          >
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteId(v.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* MODAL: vehiculos enviados */}
      <ModalEstadoVehiculos
        open={showModalEnviado}
        onOpenChange={setShowModalEnviado}
        variante="enviado"
      />

      {/* MODAL: aprobado */}
      {cambiosAprobado.length > 0 && (
        <ModalEstadoVehiculos
          open={true}
          onOpenChange={() => marcarComoVisto()}
          variante="aprobado"
          patentes={cambiosAprobado.map((c) => c.patente)}
          onAceptar={() => {
            marcarComoVisto()
            router.push('/dashboard-propietario')
          }}
        />
      )}

      {/* MODAL: rechazado */}
      {cambiosRechazado.length > 0 && (
        <ModalEstadoVehiculos
          open={true}
          onOpenChange={() => marcarComoVisto()}
          variante="rechazado"
          patentes={cambiosRechazado.map((c) => c.patente)}
          onReintentar={() => {
            marcarComoVisto()
            router.push('/dashboard-propietario/vehiculos')
          }}
        />
      )}

      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eliminar vehiculo?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta accion no se puede deshacer.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && handleDelete(deleteId)}
              className="bg-red-500 hover:bg-red-600"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}