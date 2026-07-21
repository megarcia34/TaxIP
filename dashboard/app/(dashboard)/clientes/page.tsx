'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Search,
  Users,
  Loader2,
  Eye,
  Edit,
  Ban,
  Play,
  Mail,
  Phone,
  Calendar,
  Car,
  Star,
  Wallet,
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign,
} from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
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

interface Pasajero {
  id: string
  email: string
  nombre: string
  apellido: string
  telefono: string
  documento: string
  tipo: string
  activo: boolean
  created_at: string
  foto_perfil_url?: string
  total_viajes?: number
  calificacion_promedio?: number
  saldo?: number
}

interface ViajePasajero {
  id: string
  estado: string
  origen: string
  destino: string
  precio_final: number
  created_at: string
  chofer_nombre: string
  calificacion?: number
}

const formatFecha = (fecha: string | undefined | null) => {
  if (!fecha) return 'N/A'
  try {
    return format(new Date(fecha), "dd/MM/yyyy HH:mm", { locale: es })
  } catch {
    return 'N/A'
  }
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

const getEstadoColor = (activo: boolean) => {
  return activo ? 'bg-green-500' : 'bg-red-500'
}

const getEstadoLabel = (activo: boolean) => {
  return activo ? 'Activo' : 'Inactivo'
}

const getViajeEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    aceptado: 'bg-blue-500',
    en_curso: 'bg-purple-500',
    finalizado: 'bg-green-500',
    cancelado: 'bg-red-500'
  }
  return estados[estado] || 'bg-gray-500'
}

export default function PasajerosPage() {
  const [search, setSearch] = useState('')
  const [estadoFilter, setEstadoFilter] = useState<'todos' | 'activo' | 'inactivo'>('todos')
  const [selectedPasajero, setSelectedPasajero] = useState<Pasajero | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [activeTab, setActiveTab] = useState('info')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    telefono: '',
    documento: '',
  })

  const queryClient = useQueryClient()

  // ========== QUERIES ==========
  const { data: pasajeros, isLoading, refetch } = useQuery({
    queryKey: ['pasajeros-lista', search, estadoFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      params.append('tipo', 'pasajero')
      const response = await apiClient.get(`/api/usuarios/lista?${params.toString()}`)
      return response.data
    },
  })

  const { data: viajesPasajero } = useQuery({
    queryKey: ['pasajero-viajes', selectedPasajero?.id],
    queryFn: async () => {
      if (!selectedPasajero) return null
      const response = await apiClient.get(`/api/viajes/historial?limit=20`)
      // Filtrar por pasajero
      const allViajes = response.data || []
      return allViajes.filter((v: any) => v.pasajero_id === selectedPasajero.id)
    },
    enabled: !!selectedPasajero && showDetail,
  })

  // ========== MUTATIONS ==========
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await apiClient.put(`/api/usuarios/perfil/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Perfil actualizado correctamente')
      queryClient.invalidateQueries({ queryKey: ['pasajeros-lista'] })
      setShowEdit(false)
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al actualizar el perfil'
      toast.error(message)
    },
  })

  const suspenderMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.put(`/api/usuarios/suspender/${id}`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Pasajero suspendido correctamente')
      queryClient.invalidateQueries({ queryKey: ['pasajeros-lista'] })
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al suspender el pasajero'
      toast.error(message)
    },
  })

  const activarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.put(`/api/usuarios/activar/${id}`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Pasajero activado correctamente')
      queryClient.invalidateQueries({ queryKey: ['pasajeros-lista'] })
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al activar el pasajero'
      toast.error(message)
    },
  })

  // ========== FUNCIONES ==========
  const handleViewDetail = (pasajero: Pasajero) => {
    setSelectedPasajero(pasajero)
    setShowDetail(true)
    setActiveTab('info')
  }

  const handleEditClick = (pasajero: Pasajero) => {
    setSelectedPasajero(pasajero)
    setFormData({
      nombre: pasajero.nombre || '',
      apellido: pasajero.apellido || '',
      telefono: pasajero.telefono || '',
      documento: pasajero.documento || '',
    })
    setShowEdit(true)
  }

  const handleUpdate = () => {
    if (!selectedPasajero) return
    updateMutation.mutate({ id: selectedPasajero.id, data: formData })
  }

  const handleToggleEstado = (pasajero: Pasajero) => {
    if (pasajero.activo) {
      suspenderMutation.mutate(pasajero.id)
    } else {
      activarMutation.mutate(pasajero.id)
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-6 w-6" />
            Pasajeros
          </h1>
          <p className="text-muted-foreground">
            Gestión de pasajeros que utilizan la plataforma
          </p>
        </div>
      </div>

      {/* Listado */}
      <Card>
        <CardHeader>
          <CardTitle className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <span>Listado de Pasajeros</span>
            <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:flex-none">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre, email, documento..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-full sm:w-64"
                />
              </div>
              <div className="flex gap-1">
                <Button
                  variant={estadoFilter === 'todos' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEstadoFilter('todos')}
                >
                  Todos
                </Button>
                <Button
                  variant={estadoFilter === 'activo' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEstadoFilter('activo')}
                  className="text-green-600"
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Activos
                </Button>
                <Button
                  variant={estadoFilter === 'inactivo' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEstadoFilter('inactivo')}
                  className="text-red-600"
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Inactivos
                </Button>
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-3 font-medium">Pasajero</th>
                  <th className="pb-3 font-medium">Contacto</th>
                  <th className="pb-3 font-medium">Documento</th>
                  <th className="pb-3 font-medium">Viajes</th>
                  <th className="pb-3 font-medium">Saldo</th>
                  <th className="pb-3 font-medium">Calificación</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pasajeros?.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-muted-foreground">
                      No hay pasajeros registrados
                    </td>
                  </tr>
                ) : (
                  pasajeros?.map((pasajero: Pasajero) => (
                    <tr key={pasajero.id} className="border-b hover:bg-muted/50">
                      <td className="py-3">
                        <div className="font-medium">
                          {pasajero.nombre} {pasajero.apellido}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {pasajero.email}
                        </div>
                      </td>
                      <td className="py-3">
                        {pasajero.telefono ? (
                          <div className="flex items-center gap-1 text-sm">
                            <Phone className="h-3 w-3 text-muted-foreground" />
                            {pasajero.telefono}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">Sin teléfono</span>
                        )}
                      </td>
                      <td className="py-3 text-sm">
                        {pasajero.documento || 'N/A'}
                      </td>
                      <td className="py-3 text-center">
                        <span className="font-medium">{pasajero.total_viajes || 0}</span>
                      </td>
                      <td className="py-3">
                        <span className="font-medium">{formatMoneda(pasajero.saldo)}</span>
                      </td>
                      <td className="py-3">
                        {pasajero.calificacion_promedio ? (
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                            <span>{pasajero.calificacion_promedio.toFixed(1)}</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">Sin calificaciones</span>
                        )}
                      </td>
                      <td className="py-3">
                        <Badge className={getEstadoColor(pasajero.activo)}>
                          {getEstadoLabel(pasajero.activo)}
                        </Badge>
                      </td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Ver detalles"
                            onClick={() => handleViewDetail(pasajero)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Editar"
                            onClick={() => handleEditClick(pasajero)}
                          >
                            <Edit className="h-4 w-4 text-blue-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title={pasajero.activo ? 'Suspender' : 'Activar'}
                            onClick={() => handleToggleEstado(pasajero)}
                          >
                            {pasajero.activo ? (
                              <Ban className="h-4 w-4 text-orange-500" />
                            ) : (
                              <Play className="h-4 w-4 text-green-500" />
                            )}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ========== MODAL DETALLE ========== */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              {selectedPasajero?.nombre} {selectedPasajero?.apellido}
              {selectedPasajero && (
                <Badge className={getEstadoColor(selectedPasajero.activo)}>
                  {getEstadoLabel(selectedPasajero.activo)}
                </Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              Detalle completo del pasajero
            </DialogDescription>
          </DialogHeader>

          {selectedPasajero && (
            <div className="space-y-4">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-3">
                  <TabsTrigger value="info">Información</TabsTrigger>
                  <TabsTrigger value="viajes">Historial de Viajes</TabsTrigger>
                  <TabsTrigger value="wallet">Billetera</TabsTrigger>
                </TabsList>

                {/* Tab 1: Información */}
                <TabsContent value="info" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nombre</Label>
                      <p className="text-sm font-medium">{selectedPasajero.nombre} {selectedPasajero.apellido}</p>
                    </div>
                    <div>
                      <Label>Email</Label>
                      <p className="text-sm">{selectedPasajero.email}</p>
                    </div>
                    <div>
                      <Label>Teléfono</Label>
                      <p className="text-sm">{selectedPasajero.telefono || 'N/A'}</p>
                    </div>
                    <div>
                      <Label>Documento</Label>
                      <p className="text-sm">{selectedPasajero.documento || 'N/A'}</p>
                    </div>
                    <div>
                      <Label>Fecha de Registro</Label>
                      <p className="text-sm">{formatFecha(selectedPasajero.created_at)}</p>
                    </div>
                    <div>
                      <Label>Estado</Label>
                      <Badge className={getEstadoColor(selectedPasajero.activo)}>
                        {getEstadoLabel(selectedPasajero.activo)}
                      </Badge>
                    </div>
                    <div>
                      <Label>Total Viajes</Label>
                      <p className="text-sm font-medium">{selectedPasajero.total_viajes || 0}</p>
                    </div>
                    <div>
                      <Label>Calificación Promedio</Label>
                      {selectedPasajero.calificacion_promedio ? (
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                          <span className="text-sm font-medium">{selectedPasajero.calificacion_promedio.toFixed(1)}</span>
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">Sin calificaciones</p>
                      )}
                    </div>
                  </div>
                </TabsContent>

                {/* Tab 2: Viajes */}
                <TabsContent value="viajes">
                  <div className="space-y-4">
                    <h3 className="font-semibold">Historial de Viajes</h3>
                    {viajesPasajero ? (
                      <div className="relative overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left py-2">Origen</th>
                              <th className="text-left py-2">Destino</th>
                              <th className="text-left py-2">Chofer</th>
                              <th className="text-left py-2">Precio</th>
                              <th className="text-left py-2">Estado</th>
                              <th className="text-left py-2">Fecha</th>
                            </tr>
                          </thead>
                          <tbody>
                            {viajesPasajero.map((viaje: ViajePasajero) => (
                              <tr key={viaje.id} className="border-b hover:bg-muted/50">
                                <td className="py-2">{viaje.origen || 'N/A'}</td>
                                <td className="py-2">{viaje.destino || 'N/A'}</td>
                                <td className="py-2">{viaje.chofer_nombre || 'Sin asignar'}</td>
                                <td className="py-2">{formatMoneda(viaje.precio_final)}</td>
                                <td className="py-2">
                                  <Badge className={getViajeEstadoColor(viaje.estado)}>
                                    {viaje.estado}
                                  </Badge>
                                </td>
                                <td className="py-2 text-xs">{formatFecha(viaje.created_at)}</td>
                              </tr>
                            ))}
                            {viajesPasajero.length === 0 && (
                              <tr>
                                <td colSpan={6} className="py-8 text-center text-muted-foreground">
                                  No hay viajes registrados
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="py-8 text-center text-muted-foreground">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                        <p>Cargando viajes...</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                {/* Tab 3: Billetera */}
                <TabsContent value="wallet">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Wallet className="h-4 w-4" />
                            <span>Saldo Actual</span>
                          </div>
                          <p className="text-2xl font-bold text-green-600">
                            {formatMoneda(selectedPasajero.saldo)}
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <DollarSign className="h-4 w-4" />
                            <span>Total Gastado</span>
                          </div>
                          <p className="text-2xl font-bold">
                            {formatMoneda(selectedPasajero.total_viajes ? selectedPasajero.total_viajes * 200 : 0)}
                          </p>
                          <p className="text-xs text-muted-foreground">Estimado</p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ========== MODAL EDITAR ========== */}
      <Dialog open={showEdit} onOpenChange={setShowEdit}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Pasajero</DialogTitle>
            <DialogDescription>
              Modifique los datos del pasajero
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div>
              <Label>Nombre</Label>
              <Input
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              />
            </div>
            <div>
              <Label>Apellido</Label>
              <Input
                value={formData.apellido}
                onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
              />
            </div>
            <div>
              <Label>Teléfono</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>
            <div>
              <Label>Documento</Label>
              <Input
                value={formData.documento}
                onChange={(e) => setFormData({ ...formData, documento: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEdit(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Guardar Cambios
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}