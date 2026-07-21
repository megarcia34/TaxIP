'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Search,
  Plus,
  Edit,
  Trash2,
  Eye,
  QrCode,
  Loader2,
  Store,
  MapPin,
  Phone,
  Mail,
  BarChart3,
  Download,
  EyeOff,
  CheckCircle,
  XCircle,
} from 'lucide-react'
import Link from 'next/link'
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

interface Comercio {
  id: string
  nombre: string
  rubro: string
  direccion: string
  latitud: number
  longitud: number
  codigo_qr: string
  email_contacto: string
  telefono: string
  activo: boolean
  created_at: string
  updated_at: string
  total_escaneos: number
  total_viajes: number
}

const formatFecha = (fecha: string | undefined | null) => {
  if (!fecha) return 'N/A'
  try {
    return format(new Date(fecha), "dd/MM/yyyy HH:mm", { locale: es })
  } catch {
    return 'N/A'
  }
}

export default function ComerciosPage() {
  const [search, setSearch] = useState('')
  const [activoFilter, setActivoFilter] = useState<'todos' | 'activos' | 'inactivos'>('todos')
  const [selectedComercio, setSelectedComercio] = useState<Comercio | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [showQR, setShowQR] = useState<string | null>(null)
  const [qrImage, setQrImage] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    nombre: '',
    rubro: '',
    direccion: '',
    latitud: '',
    longitud: '',
    email_contacto: '',
    telefono: '',
  })

  const queryClient = useQueryClient()

  // Queries
  const { data: comercios, isLoading } = useQuery({
    queryKey: ['comercios', search, activoFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (activoFilter !== 'todos') params.append('activo', String(activoFilter === 'activos'))
      const response = await apiClient.get(`/api/comercios/lista?${params.toString()}`)
      return response.data
    },
  })

  const { data: estadisticas, refetch: refetchEstadisticas } = useQuery({
    queryKey: ['comercio-estadisticas', selectedComercio?.id],
    queryFn: async () => {
      if (!selectedComercio) return null
      const response = await apiClient.get(`/api/comercios/${selectedComercio.id}/estadisticas`)
      return response.data
    },
    enabled: !!selectedComercio && showDetail,
  })

  // Mutations
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/comercios/crear', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Comercio creado correctamente')
      queryClient.invalidateQueries({ queryKey: ['comercios'] })
      setShowCreate(false)
      resetForm()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al crear el comercio'
      toast.error(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await apiClient.put(`/api/comercios/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Comercio actualizado correctamente')
      queryClient.invalidateQueries({ queryKey: ['comercios'] })
      setShowEdit(false)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al actualizar el comercio'
      toast.error(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/api/comercios/${id}`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Comercio eliminado correctamente')
      queryClient.invalidateQueries({ queryKey: ['comercios'] })
      setDeleteId(null)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al eliminar el comercio'
      toast.error(message)
    },
  })

  const resetForm = () => {
    setFormData({
      nombre: '',
      rubro: '',
      direccion: '',
      latitud: '',
      longitud: '',
      email_contacto: '',
      telefono: '',
    })
  }

  const handleViewQR = async (comercioId: string) => {
    try {
      const response = await apiClient.get(`/api/comercios/${comercioId}/qr?format=base64`)
      setQrImage(`data:image/png;base64,${response.data.qr_base64}`)
      setShowQR(comercioId)
    } catch (error) {
      toast.error('Error al cargar el QR')
    }
  }

  const handleViewDetail = (comercio: Comercio) => {
    setSelectedComercio(comercio)
    setShowDetail(true)
  }

  const handleEditClick = (comercio: Comercio) => {
    setSelectedComercio(comercio)
    setFormData({
      nombre: comercio.nombre || '',
      rubro: comercio.rubro || '',
      direccion: comercio.direccion || '',
      latitud: comercio.latitud?.toString() || '',
      longitud: comercio.longitud?.toString() || '',
      email_contacto: comercio.email_contacto || '',
      telefono: comercio.telefono || '',
    })
    setShowEdit(true)
  }

  const handleCreate = () => {
    const data = {
      ...formData,
      latitud: parseFloat(formData.latitud),
      longitud: parseFloat(formData.longitud),
    }
    createMutation.mutate(data)
  }

  const handleUpdate = () => {
    if (!selectedComercio) return
    const data = {
      ...formData,
      latitud: parseFloat(formData.latitud),
      longitud: parseFloat(formData.longitud),
    }
    updateMutation.mutate({ id: selectedComercio.id, data })
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
            <Store className="h-6 w-6" />
            Comercios QR
          </h1>
          <p className="text-muted-foreground">
            Gestión de puntos de venta/pedido de taxis con QR
          </p>
        </div>
        <Button onClick={() => { resetForm(); setShowCreate(true) }}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Comercio
        </Button>
      </div>

      {/* Listado */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Listado de Comercios</CardTitle>
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre, rubro o dirección..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-full sm:w-64"
                />
              </div>
              <div className="flex gap-1">
                <Button
                  variant={activoFilter === 'todos' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActivoFilter('todos')}
                >
                  Todos
                </Button>
                <Button
                  variant={activoFilter === 'activos' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActivoFilter('activos')}
                  className="text-green-600"
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Activos
                </Button>
                <Button
                  variant={activoFilter === 'inactivos' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActivoFilter('inactivos')}
                  className="text-red-600"
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Inactivos
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Comercio</TableHead>
                <TableHead>Ubicación</TableHead>
                <TableHead>Contacto</TableHead>
                <TableHead>Escaneos</TableHead>
                <TableHead>Viajes</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {comercios?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    No hay comercios registrados
                  </TableCell>
                </TableRow>
              ) : (
                comercios?.map((comercio: Comercio) => (
                  <TableRow key={comercio.id}>
                    <TableCell>
                      <div className="font-medium">{comercio.nombre}</div>
                      <div className="text-xs text-muted-foreground">{comercio.rubro || 'Sin rubro'}</div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1 text-sm">
                        <MapPin className="h-3 w-3 text-muted-foreground" />
                        {comercio.direccion}
                      </div>
                    </TableCell>
                    <TableCell>
                      {comercio.telefono && (
                        <div className="flex items-center gap-1 text-sm">
                          <Phone className="h-3 w-3 text-muted-foreground" />
                          {comercio.telefono}
                        </div>
                      )}
                      {comercio.email_contacto && (
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Mail className="h-3 w-3" />
                          {comercio.email_contacto}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-sm">
                        {comercio.total_escaneos || 0}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-sm">
                        {comercio.total_viajes || 0}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={comercio.activo ? 'bg-green-500' : 'bg-red-500'}>
                        {comercio.activo ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Ver QR"
                          onClick={() => handleViewQR(comercio.id)}
                        >
                          <QrCode className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Ver detalles"
                          onClick={() => handleViewDetail(comercio)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Editar"
                          onClick={() => handleEditClick(comercio)}
                        >
                          <Edit className="h-4 w-4 text-blue-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Eliminar"
                          onClick={() => setDeleteId(comercio.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* ========== MODAL QR ========== */}
      <Dialog open={!!showQR} onOpenChange={() => setShowQR(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>QR del Comercio</DialogTitle>
            <DialogDescription>
              Escanea este QR para solicitar un viaje desde el comercio
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center py-4">
            {qrImage ? (
              <img src={qrImage} alt="QR Comercio" className="w-64 h-64" />
            ) : (
              <Loader2 className="h-12 w-12 animate-spin" />
            )}
            <p className="mt-4 text-sm text-muted-foreground">
              {selectedComercio?.nombre}
            </p>
            <Button variant="outline" className="mt-4" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Descargar QR
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* ========== MODAL DETALLE ========== */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Store className="h-5 w-5" />
              {selectedComercio?.nombre}
            </DialogTitle>
            <DialogDescription>
              Detalle completo del comercio y sus estadísticas
            </DialogDescription>
          </DialogHeader>
          {selectedComercio && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Nombre</Label>
                  <p className="text-sm font-medium">{selectedComercio.nombre}</p>
                </div>
                <div>
                  <Label>Rubro</Label>
                  <p className="text-sm">{selectedComercio.rubro || 'N/A'}</p>
                </div>
                <div className="col-span-2">
                  <Label>Dirección</Label>
                  <p className="text-sm">{selectedComercio.direccion}</p>
                </div>
                <div>
                  <Label>Teléfono</Label>
                  <p className="text-sm">{selectedComercio.telefono || 'N/A'}</p>
                </div>
                <div>
                  <Label>Email</Label>
                  <p className="text-sm">{selectedComercio.email_contacto || 'N/A'}</p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Estadísticas
                </h4>
                {estadisticas ? (
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-2xl font-bold">{estadisticas.total_escaneos}</p>
                      <p className="text-xs text-muted-foreground">Total Escaneos</p>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-2xl font-bold">{estadisticas.total_viajes}</p>
                      <p className="text-xs text-muted-foreground">Total Viajes</p>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-2xl font-bold">${estadisticas.facturacion_total?.toFixed(0) || 0}</p>
                      <p className="text-xs text-muted-foreground">Facturación Total</p>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-lg font-bold">{estadisticas.escaneos_ultimo_mes}</p>
                      <p className="text-xs text-muted-foreground">Escaneos (30 días)</p>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-lg font-bold">{estadisticas.viajes_ultimo_mes}</p>
                      <p className="text-xs text-muted-foreground">Viajes (30 días)</p>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-lg font-bold">${estadisticas.promedio_por_viaje?.toFixed(0) || 0}</p>
                      <p className="text-xs text-muted-foreground">Promedio por Viaje</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin" />
                  </div>
                )}
              </div>

              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => handleViewQR(selectedComercio.id)}>
                  <QrCode className="h-4 w-4 mr-2" />
                  Ver QR
                </Button>
                <Button variant="outline" onClick={() => setShowDetail(false)}>
                  Cerrar
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ========== MODAL CREAR ========== */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Nuevo Comercio</DialogTitle>
            <DialogDescription>
              Complete los datos del comercio para generar su QR
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Nombre *</Label>
              <Input
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                placeholder="Nombre del comercio"
              />
            </div>
            <div>
              <Label>Rubro</Label>
              <Input
                value={formData.rubro}
                onChange={(e) => setFormData({ ...formData, rubro: e.target.value })}
                placeholder="Ej: Restaurante, Hotel, Farmacia..."
              />
            </div>
            <div>
              <Label>Dirección *</Label>
              <Input
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                placeholder="Dirección completa"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Latitud *</Label>
                <Input
                  type="number"
                  step="any"
                  value={formData.latitud}
                  onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                  placeholder="-34.6037"
                />
              </div>
              <div>
                <Label>Longitud *</Label>
                <Input
                  type="number"
                  step="any"
                  value={formData.longitud}
                  onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                  placeholder="-58.3816"
                />
              </div>
            </div>
            <div>
              <Label>Teléfono de Contacto</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                placeholder="Teléfono del comercio"
              />
            </div>
            <div>
              <Label>Email de Contacto</Label>
              <Input
                type="email"
                value={formData.email_contacto}
                onChange={(e) => setFormData({ ...formData, email_contacto: e.target.value })}
                placeholder="contacto@comercio.com"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreate(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending || !formData.nombre}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Crear Comercio
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ========== MODAL EDITAR ========== */}
      <Dialog open={showEdit} onOpenChange={setShowEdit}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Comercio</DialogTitle>
            <DialogDescription>
              Modifique los datos del comercio
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Nombre *</Label>
              <Input
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              />
            </div>
            <div>
              <Label>Rubro</Label>
              <Input
                value={formData.rubro}
                onChange={(e) => setFormData({ ...formData, rubro: e.target.value })}
              />
            </div>
            <div>
              <Label>Dirección *</Label>
              <Input
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Latitud *</Label>
                <Input
                  type="number"
                  step="any"
                  value={formData.latitud}
                  onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                />
              </div>
              <div>
                <Label>Longitud *</Label>
                <Input
                  type="number"
                  step="any"
                  value={formData.longitud}
                  onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                />
              </div>
            </div>
            <div>
              <Label>Teléfono de Contacto</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>
            <div>
              <Label>Email de Contacto</Label>
              <Input
                type="email"
                value={formData.email_contacto}
                onChange={(e) => setFormData({ ...formData, email_contacto: e.target.value })}
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

      {/* ========== ALERTA ELIMINAR ========== */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar comercio?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. El comercio será desactivado.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && deleteMutation.mutate(deleteId)}
              className="bg-red-500 hover:bg-red-600"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}