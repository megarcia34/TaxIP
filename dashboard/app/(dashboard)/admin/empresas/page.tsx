'use client'

import { useState, useEffect } from 'react'
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
  DialogFooter,
  DialogDescription,
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
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Phone, 
  Mail, 
  Building2, 
  Loader2,
  DollarSign,
  CreditCard,
  Users,
  MapPin,
  CheckCircle,
  XCircle,
  Calendar,
  FileText,
  TrendingUp,
  UserCog,
  Building,
  Wallet,
  AlertCircle,
  Ban,
  Play
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

interface Empresa {
  id: string
  nombre: string
  tipo: string
  email_facturacion: string
  telefono: string
  direccion: string
  latitud: number
  longitud: number
  tarifa_preferencial: number
  condiciones_pago: string
  limite_credito: number
  estado: string
  created_at: string
  updated_at: string
  contacto_nombre: string
  contacto_telefono: string
  contacto_email: string
  total_viajes: number
  deuda_pendiente: number
  empleados_activos: number
  fecha_suspension?: string
  motivo_suspension?: string
  suspendido_por?: string
}

interface CuentaCorriente {
  empresa_id: string
  empresa_nombre: string
  limite_credito: number
  saldo_disponible: number
  deuda_total: number
  viajes_pendientes: number
  facturas_pendientes: number
}

interface Empleado {
  id: string
  email: string
  nombre: string
  apellido: string
  telefono: string
  rol: string
  activo: boolean
  usuario_activo: boolean
  created_at: string
}

interface ViajeEmpresa {
  id: string
  estado: string
  origen: string
  destino: string
  precio_final: number
  created_at: string
  finalizado_en: string
  pasajero: string
  chofer: string
  patente: string
}

const getTipoColor = (tipo: string) => {
  const tipos: Record<string, string> = {
    hotel: 'bg-blue-500',
    sanatorio: 'bg-red-500',
    restaurante: 'bg-orange-500',
    oficina: 'bg-purple-500',
    otro: 'bg-gray-500'
  }
  return tipos[tipo] || 'bg-gray-500'
}

const getTipoLabel = (tipo: string) => {
  const tipos: Record<string, string> = {
    hotel: 'Hotel',
    sanatorio: 'Sanatorio',
    restaurante: 'Restaurante',
    oficina: 'Oficina',
    otro: 'Otro'
  }
  return tipos[tipo] || tipo
}

const getEstadoColor = (estado: string) => {
  const colores: Record<string, string> = {
    activo: 'bg-green-500',
    inactivo: 'bg-red-500',
    suspendido: 'bg-orange-500'
  }
  return colores[estado] || 'bg-gray-500'
}

const getEstadoLabel = (estado: string) => {
  const labels: Record<string, string> = {
    activo: 'Activo',
    inactivo: 'Inactivo',
    suspendido: 'Suspendido'
  }
  return labels[estado] || estado
}

const getCondicionPagoLabel = (condicion: string) => {
  const condiciones: Record<string, string> = {
    mensual: 'Mensual',
    quincenal: 'Quincenal',
    prepago: 'Prepago'
  }
  return condiciones[condicion] || condicion
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

export default function AdminEmpresasPage() {
  const [search, setSearch] = useState('')
  const [estadoFilter, setEstadoFilter] = useState<'todos' | 'activo' | 'inactivo' | 'suspendido'>('todos')
  const [selectedEmpresa, setSelectedEmpresa] = useState<Empresa | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [showEdit, setShowEdit] = useState(false)
  const [showSuspensionDialog, setShowSuspensionDialog] = useState(false)
  const [suspensionMotivo, setSuspensionMotivo] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('info')
  
  // Formularios
  const [formData, setFormData] = useState({
    nombre: '',
    tipo: 'hotel',
    email_facturacion: '',
    telefono: '',
    direccion: '',
    latitud: '',
    longitud: '',
    tarifa_preferencial: '0',
    condiciones_pago: 'mensual',
    limite_credito: '0',
    contacto_nombre: '',
    contacto_telefono: '',
    contacto_email: ''
  })

  const queryClient = useQueryClient()

  // ========== QUERIES ==========
  const { data: empresas, isLoading, refetch } = useQuery({
    queryKey: ['admin-empresas-completo', search, estadoFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (estadoFilter !== 'todos') params.append('estado', estadoFilter)
      const response = await apiClient.get(`/api/admin/empresas?${params.toString()}`)
      return response.data
    },
  })

  const { data: cuentaCorriente, refetch: refetchCuenta } = useQuery({
    queryKey: ['cuenta-corriente', selectedEmpresa?.id],
    queryFn: async () => {
      if (!selectedEmpresa) return null
      const response = await apiClient.get(`/api/admin/empresas/${selectedEmpresa.id}/cuenta-corriente`)
      return response.data
    },
    enabled: !!selectedEmpresa && showDetail,
  })

  const { data: empleados, refetch: refetchEmpleados } = useQuery({
    queryKey: ['empresa-empleados', selectedEmpresa?.id],
    queryFn: async () => {
      if (!selectedEmpresa) return null
      const response = await apiClient.get(`/api/admin/empresas/${selectedEmpresa.id}/empleados`)
      return response.data
    },
    enabled: !!selectedEmpresa && showDetail,
  })

  const { data: viajesEmpresa, refetch: refetchViajes } = useQuery({
    queryKey: ['empresa-viajes', selectedEmpresa?.id],
    queryFn: async () => {
      if (!selectedEmpresa) return null
      const response = await apiClient.get(`/api/admin/empresas/${selectedEmpresa.id}/viajes?limit=20`)
      return response.data
    },
    enabled: !!selectedEmpresa && showDetail,
  })

  // ========== MUTATIONS ==========
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/admin/empresas', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa creada correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo'] })
      setShowCreate(false)
      resetForm()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al crear la empresa'
      toast.error(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await apiClient.put(`/api/admin/empresas/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa actualizada correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo'] })
      setShowEdit(false)
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al actualizar la empresa'
      toast.error(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/api/admin/empresas/${id}`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa eliminada correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo'] })
      setDeleteId(null)
      if (showDetail) setShowDetail(false)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al eliminar la empresa'
      toast.error(message)
    },
  })

  const suspenderMutation = useMutation({
    mutationFn: async ({ id, motivo }: { id: string; motivo: string }) => {
      const response = await apiClient.post(`/api/admin/empresas/${id}/suspender`, { motivo })
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa suspendida correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo'] })
      setShowSuspensionDialog(false)
      setSuspensionMotivo('')
      if (showDetail) {
        queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo', selectedEmpresa?.id] })
      }
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al suspender la empresa'
      toast.error(message)
    },
  })

  const activarMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/api/admin/empresas/${id}/activar`)
      return response.data
    },
    onSuccess: () => {
      toast.success('Empresa activada correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo'] })
      if (showDetail) {
        queryClient.invalidateQueries({ queryKey: ['admin-empresas-completo', selectedEmpresa?.id] })
      }
      refetch()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al activar la empresa'
      toast.error(message)
    },
  })

  // ========== FUNCIONES ==========
  const resetForm = () => {
    setFormData({
      nombre: '',
      tipo: 'hotel',
      email_facturacion: '',
      telefono: '',
      direccion: '',
      latitud: '',
      longitud: '',
      tarifa_preferencial: '0',
      condiciones_pago: 'mensual',
      limite_credito: '0',
      contacto_nombre: '',
      contacto_telefono: '',
      contacto_email: ''
    })
  }

  const handleViewDetail = (empresa: Empresa) => {
    setSelectedEmpresa(empresa)
    setShowDetail(true)
    setActiveTab('info')
  }

  const handleEditClick = (empresa: Empresa) => {
    setSelectedEmpresa(empresa)
    setFormData({
      nombre: empresa.nombre || '',
      tipo: empresa.tipo || 'hotel',
      email_facturacion: empresa.email_facturacion || '',
      telefono: empresa.telefono || '',
      direccion: empresa.direccion || '',
      latitud: empresa.latitud?.toString() || '',
      longitud: empresa.longitud?.toString() || '',
      tarifa_preferencial: empresa.tarifa_preferencial?.toString() || '0',
      condiciones_pago: empresa.condiciones_pago || 'mensual',
      limite_credito: empresa.limite_credito?.toString() || '0',
      contacto_nombre: empresa.contacto_nombre || '',
      contacto_telefono: empresa.contacto_telefono || '',
      contacto_email: empresa.contacto_email || ''
    })
    setShowEdit(true)
  }

  const handleSuspender = (empresa: Empresa) => {
    setSelectedEmpresa(empresa)
    setSuspensionMotivo('')
    setShowSuspensionDialog(true)
  }

  const handleCreate = () => {
    const data = {
      ...formData,
      latitud: formData.latitud ? parseFloat(formData.latitud) : null,
      longitud: formData.longitud ? parseFloat(formData.longitud) : null,
      tarifa_preferencial: parseFloat(formData.tarifa_preferencial) || 0,
      limite_credito: parseFloat(formData.limite_credito) || 0
    }
    createMutation.mutate(data)
  }

  const handleUpdate = () => {
    if (!selectedEmpresa) return
    const data = {
      ...formData,
      latitud: formData.latitud ? parseFloat(formData.latitud) : null,
      longitud: formData.longitud ? parseFloat(formData.longitud) : null,
      tarifa_preferencial: parseFloat(formData.tarifa_preferencial) || 0,
      limite_credito: parseFloat(formData.limite_credito) || 0
    }
    updateMutation.mutate({ id: selectedEmpresa.id, data })
  }

  const handleDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId)
    }
  }

  const handleConfirmSuspension = () => {
    if (selectedEmpresa && suspensionMotivo.trim()) {
      suspenderMutation.mutate({ id: selectedEmpresa.id, motivo: suspensionMotivo })
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
            <Building2 className="h-6 w-6" />
            Empresas Corporativas
          </h1>
          <p className="text-muted-foreground">
            Gestión completa de empresas, hoteles y sanatorios que utilizan el servicio de taxis
          </p>
        </div>
        <Button onClick={() => { resetForm(); setShowCreate(true) }}>
          <Plus className="h-4 w-4 mr-2" />
          Nueva Empresa
        </Button>
      </div>

      {/* Listado */}
      <Card>
        <CardHeader>
          <CardTitle className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <span>Listado de Empresas</span>
            <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:flex-none">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre, email, contacto..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-full sm:w-64"
                />
              </div>
              <div className="flex gap-1 flex-wrap">
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
                  variant={estadoFilter === 'suspendido' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setEstadoFilter('suspendido')}
                  className="text-orange-600"
                >
                  <Ban className="h-4 w-4 mr-1" />
                  Suspendidos
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
                  <th className="pb-3 font-medium">Empresa</th>
                  <th className="pb-3 font-medium">Contacto</th>
                  <th className="pb-3 font-medium">Tipo</th>
                  <th className="pb-3 font-medium">Empleados</th>
                  <th className="pb-3 font-medium">Cuenta Corriente</th>
                  <th className="pb-3 font-medium">Viajes</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {empresas?.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-muted-foreground">
                      No hay empresas registradas
                    </td>
                  </tr>
                ) : (
                  empresas?.map((empresa: Empresa) => (
                    <tr key={empresa.id} className="border-b hover:bg-muted/50">
                      <td className="py-3">
                        <div className="font-medium">{empresa.nombre}</div>
                        {empresa.direccion && (
                          <div className="text-xs text-muted-foreground flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {empresa.direccion}
                          </div>
                        )}
                      </td>
                      <td className="py-3">
                        {empresa.contacto_nombre ? (
                          <div>
                            <div className="text-sm">{empresa.contacto_nombre}</div>
                            <div className="text-xs text-muted-foreground flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {empresa.contacto_email || empresa.email_facturacion || 'N/A'}
                            </div>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Sin contacto</span>
                        )}
                      </td>
                      <td className="py-3">
                        <Badge className={getTipoColor(empresa.tipo)}>
                          {getTipoLabel(empresa.tipo)}
                        </Badge>
                      </td>
                      <td className="py-3 text-center">
                        <span className="font-medium">{empresa.empleados_activos || 0}</span>
                      </td>
                      <td className="py-3">
                        <div className="flex flex-col">
                          <span className="text-sm font-medium">
                            {formatMoneda(empresa.limite_credito)}
                          </span>
                          {empresa.deuda_pendiente > 0 && (
                            <span className="text-xs text-red-500">
                              Deuda: {formatMoneda(empresa.deuda_pendiente)}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 text-center">
                        <span className="font-medium">{empresa.total_viajes || 0}</span>
                      </td>
                      <td className="py-3">
                        <Badge className={getEstadoColor(empresa.estado)}>
                          {getEstadoLabel(empresa.estado)}
                        </Badge>
                        {empresa.estado === 'suspendido' && empresa.motivo_suspension && (
                          <div className="text-xs text-orange-600 mt-1 max-w-[150px] truncate">
                            {empresa.motivo_suspension}
                          </div>
                        )}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-1 flex-wrap">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Ver detalles"
                            onClick={() => handleViewDetail(empresa)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Editar"
                            onClick={() => handleEditClick(empresa)}
                          >
                            <Edit className="h-4 w-4 text-blue-500" />
                          </Button>
                          {empresa.estado === 'activo' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Suspender"
                              onClick={() => handleSuspender(empresa)}
                            >
                              <Ban className="h-4 w-4 text-orange-500" />
                            </Button>
                          )}
                          {empresa.estado === 'suspendido' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Activar"
                              onClick={() => activarMutation.mutate(empresa.id)}
                              disabled={activarMutation.isPending}
                            >
                              <Play className="h-4 w-4 text-green-500" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Eliminar"
                            onClick={() => setDeleteId(empresa.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
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
              <Building2 className="h-5 w-5" />
              {selectedEmpresa?.nombre}
              {selectedEmpresa && (
                <Badge className={getEstadoColor(selectedEmpresa.estado)}>
                  {getEstadoLabel(selectedEmpresa.estado)}
                </Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              Detalle completo de la empresa corporativa
            </DialogDescription>
          </DialogHeader>

          {selectedEmpresa && (
            <div className="space-y-4">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-4">
                  <TabsTrigger value="info">Información</TabsTrigger>
                  <TabsTrigger value="cuenta">Cuenta Corriente</TabsTrigger>
                  <TabsTrigger value="viajes">Viajes</TabsTrigger>
                  <TabsTrigger value="empleados">Empleados</TabsTrigger>
                </TabsList>

                {/* Tab 1: Información */}
                <TabsContent value="info" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nombre</Label>
                      <p className="text-sm font-medium">{selectedEmpresa.nombre}</p>
                    </div>
                    <div>
                      <Label>Tipo</Label>
                      <Badge className={getTipoColor(selectedEmpresa.tipo)}>
                        {getTipoLabel(selectedEmpresa.tipo)}
                      </Badge>
                    </div>
                    <div>
                      <Label>Email Facturación</Label>
                      <p className="text-sm">{selectedEmpresa.email_facturacion || 'N/A'}</p>
                    </div>
                    <div>
                      <Label>Teléfono</Label>
                      <p className="text-sm">{selectedEmpresa.telefono || 'N/A'}</p>
                    </div>
                    <div className="col-span-2">
                      <Label>Dirección</Label>
                      <p className="text-sm">{selectedEmpresa.direccion || 'N/A'}</p>
                    </div>
                    <div>
                      <Label>Tarifa Preferencial</Label>
                      <p className="text-sm font-medium text-green-600">
                        {selectedEmpresa.tarifa_preferencial > 0 ? `-${selectedEmpresa.tarifa_preferencial}%` : 'Sin descuento'}
                      </p>
                    </div>
                    <div>
                      <Label>Condiciones de Pago</Label>
                      <p className="text-sm">{getCondicionPagoLabel(selectedEmpresa.condiciones_pago)}</p>
                    </div>
                    <div>
                      <Label>Límite de Crédito</Label>
                      <p className="text-sm font-medium">{formatMoneda(selectedEmpresa.limite_credito)}</p>
                    </div>
                    <div>
                      <Label>Total Viajes</Label>
                      <p className="text-sm font-medium">{selectedEmpresa.total_viajes || 0}</p>
                    </div>
                    <div className="col-span-2">
                      <Label>Contacto</Label>
                      <div className="text-sm">
                        {selectedEmpresa.contacto_nombre ? (
                          <div>
                            <p><strong>Nombre:</strong> {selectedEmpresa.contacto_nombre}</p>
                            <p><strong>Teléfono:</strong> {selectedEmpresa.contacto_telefono || 'N/A'}</p>
                            <p><strong>Email:</strong> {selectedEmpresa.contacto_email || 'N/A'}</p>
                          </div>
                        ) : (
                          <p className="text-muted-foreground">Sin contacto registrado</p>
                        )}
                      </div>
                    </div>
                    {selectedEmpresa.estado === 'suspendido' && (
                      <div className="col-span-2 border border-orange-200 bg-orange-50 p-3 rounded-lg">
                        <p className="text-sm font-medium text-orange-700">Motivo de suspensión:</p>
                        <p className="text-sm text-orange-600">{selectedEmpresa.motivo_suspension || 'No especificado'}</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                {/* Tab 2: Cuenta Corriente */}
                <TabsContent value="cuenta">
                  {cuentaCorriente ? (
                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Wallet className="h-4 w-4" />
                            <span>Límite de Crédito</span>
                          </div>
                          <p className="text-2xl font-bold">{formatMoneda(cuentaCorriente.limite_credito)}</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <DollarSign className="h-4 w-4" />
                            <span>Saldo Disponible</span>
                          </div>
                          <p className={`text-2xl font-bold ${cuentaCorriente.saldo_disponible >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatMoneda(cuentaCorriente.saldo_disponible)}
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <CreditCard className="h-4 w-4" />
                            <span>Deuda Total</span>
                          </div>
                          <p className="text-2xl font-bold text-red-600">
                            {formatMoneda(cuentaCorriente.deuda_total)}
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <AlertCircle className="h-4 w-4" />
                            <span>Facturas Pendientes</span>
                          </div>
                          <p className="text-2xl font-bold">{cuentaCorriente.facturas_pendientes}</p>
                        </CardContent>
                      </Card>
                    </div>
                  ) : (
                    <div className="py-8 text-center text-muted-foreground">
                      <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                      <p>Cargando cuenta corriente...</p>
                    </div>
                  )}
                </TabsContent>

                {/* Tab 3: Viajes */}
                <TabsContent value="viajes">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">Últimos Viajes</h3>
                    </div>
                    {viajesEmpresa ? (
                      <div className="relative overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left py-2">Pasajero</th>
                              <th className="text-left py-2">Destino</th>
                              <th className="text-left py-2">Chofer</th>
                              <th className="text-left py-2">Precio</th>
                              <th className="text-left py-2">Estado</th>
                              <th className="text-left py-2">Fecha</th>
                            </tr>
                          </thead>
                          <tbody>
                            {viajesEmpresa.map((viaje: ViajeEmpresa) => (
                              <tr key={viaje.id} className="border-b hover:bg-muted/50">
                                <td className="py-2">{viaje.pasajero || 'N/A'}</td>
                                <td className="py-2">{viaje.destino || 'N/A'}</td>
                                <td className="py-2">{viaje.chofer || 'Sin asignar'}</td>
                                <td className="py-2">{formatMoneda(viaje.precio_final)}</td>
                                <td className="py-2">
                                  <Badge className={getViajeEstadoColor(viaje.estado)}>
                                    {viaje.estado}
                                  </Badge>
                                </td>
                                <td className="py-2 text-xs">{formatFecha(viaje.created_at)}</td>
                              </tr>
                            ))}
                            {viajesEmpresa.length === 0 && (
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

                {/* Tab 4: Empleados */}
                <TabsContent value="empleados">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">Empleados</h3>
                    </div>
                    {empleados ? (
                      <div className="relative overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left py-2">Nombre</th>
                              <th className="text-left py-2">Email</th>
                              <th className="text-left py-2">Rol</th>
                              <th className="text-left py-2">Estado</th>
                            </tr>
                          </thead>
                          <tbody>
                            {empleados.map((emp: Empleado) => (
                              <tr key={emp.id} className="border-b hover:bg-muted/50">
                                <td className="py-2">{emp.nombre} {emp.apellido}</td>
                                <td className="py-2">{emp.email}</td>
                                <td className="py-2">
                                  <Badge variant="outline">{emp.rol}</Badge>
                                </td>
                                <td className="py-2">
                                  <Badge className={emp.activo && emp.usuario_activo ? 'bg-green-500' : 'bg-red-500'}>
                                    {emp.activo && emp.usuario_activo ? 'Activo' : 'Inactivo'}
                                  </Badge>
                                </td>
                              </tr>
                            ))}
                            {empleados.length === 0 && (
                              <tr>
                                <td colSpan={4} className="py-8 text-center text-muted-foreground">
                                  No hay empleados registrados
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="py-8 text-center text-muted-foreground">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                        <p>Cargando empleados...</p>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ========== MODAL CREAR ========== */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Nueva Empresa Corporativa</DialogTitle>
            <DialogDescription>
              Complete los datos de la empresa que desea registrar
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-4">
            <div className="col-span-2">
              <Label>Nombre *</Label>
              <Input
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                placeholder="Nombre de la empresa"
              />
            </div>
            <div>
              <Label>Tipo</Label>
              <Select
                value={formData.tipo}
                onValueChange={(value) => setFormData({ ...formData, tipo: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hotel">Hotel</SelectItem>
                  <SelectItem value="sanatorio">Sanatorio</SelectItem>
                  <SelectItem value="restaurante">Restaurante</SelectItem>
                  <SelectItem value="oficina">Oficina</SelectItem>
                  <SelectItem value="otro">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Email Facturación</Label>
              <Input
                value={formData.email_facturacion}
                onChange={(e) => setFormData({ ...formData, email_facturacion: e.target.value })}
                placeholder="facturacion@empresa.com"
              />
            </div>
            <div>
              <Label>Teléfono</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                placeholder="Teléfono de contacto"
              />
            </div>
            <div className="col-span-2">
              <Label>Dirección</Label>
              <Input
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                placeholder="Dirección de la empresa"
              />
            </div>
            <div>
              <Label>Tarifa Preferencial (%)</Label>
              <Input
                type="number"
                step="0.1"
                value={formData.tarifa_preferencial}
                onChange={(e) => setFormData({ ...formData, tarifa_preferencial: e.target.value })}
                placeholder="0"
              />
            </div>
            <div>
              <Label>Condiciones de Pago</Label>
              <Select
                value={formData.condiciones_pago}
                onValueChange={(value) => setFormData({ ...formData, condiciones_pago: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mensual">Mensual</SelectItem>
                  <SelectItem value="quincenal">Quincenal</SelectItem>
                  <SelectItem value="prepago">Prepago</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Límite de Crédito ($)</Label>
              <Input
                type="number"
                step="100"
                value={formData.limite_credito}
                onChange={(e) => setFormData({ ...formData, limite_credito: e.target.value })}
                placeholder="0"
              />
            </div>
            <div className="col-span-2 border-t pt-4">
              <h4 className="font-medium mb-2">Contacto</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label>Nombre</Label>
                  <Input
                    value={formData.contacto_nombre}
                    onChange={(e) => setFormData({ ...formData, contacto_nombre: e.target.value })}
                    placeholder="Nombre del contacto"
                  />
                </div>
                <div>
                  <Label>Teléfono</Label>
                  <Input
                    value={formData.contacto_telefono}
                    onChange={(e) => setFormData({ ...formData, contacto_telefono: e.target.value })}
                    placeholder="Teléfono del contacto"
                  />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input
                    value={formData.contacto_email}
                    onChange={(e) => setFormData({ ...formData, contacto_email: e.target.value })}
                    placeholder="Email del contacto"
                  />
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreate(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending || !formData.nombre}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Crear Empresa
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ========== MODAL EDITAR ========== */}
      <Dialog open={showEdit} onOpenChange={setShowEdit}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar Empresa</DialogTitle>
            <DialogDescription>
              Modifique los datos de la empresa
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-4">
            <div className="col-span-2">
              <Label>Nombre *</Label>
              <Input
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              />
            </div>
            <div>
              <Label>Tipo</Label>
              <Select
                value={formData.tipo}
                onValueChange={(value) => setFormData({ ...formData, tipo: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hotel">Hotel</SelectItem>
                  <SelectItem value="sanatorio">Sanatorio</SelectItem>
                  <SelectItem value="restaurante">Restaurante</SelectItem>
                  <SelectItem value="oficina">Oficina</SelectItem>
                  <SelectItem value="otro">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Email Facturación</Label>
              <Input
                value={formData.email_facturacion}
                onChange={(e) => setFormData({ ...formData, email_facturacion: e.target.value })}
              />
            </div>
            <div>
              <Label>Teléfono</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>
            <div className="col-span-2">
              <Label>Dirección</Label>
              <Input
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
              />
            </div>
            <div>
              <Label>Tarifa Preferencial (%)</Label>
              <Input
                type="number"
                step="0.1"
                value={formData.tarifa_preferencial}
                onChange={(e) => setFormData({ ...formData, tarifa_preferencial: e.target.value })}
              />
            </div>
            <div>
              <Label>Condiciones de Pago</Label>
              <Select
                value={formData.condiciones_pago}
                onValueChange={(value) => setFormData({ ...formData, condiciones_pago: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mensual">Mensual</SelectItem>
                  <SelectItem value="quincenal">Quincenal</SelectItem>
                  <SelectItem value="prepago">Prepago</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Límite de Crédito ($)</Label>
              <Input
                type="number"
                step="100"
                value={formData.limite_credito}
                onChange={(e) => setFormData({ ...formData, limite_credito: e.target.value })}
              />
            </div>
            <div className="col-span-2 border-t pt-4">
              <h4 className="font-medium mb-2">Contacto</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label>Nombre</Label>
                  <Input
                    value={formData.contacto_nombre}
                    onChange={(e) => setFormData({ ...formData, contacto_nombre: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Teléfono</Label>
                  <Input
                    value={formData.contacto_telefono}
                    onChange={(e) => setFormData({ ...formData, contacto_telefono: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input
                    value={formData.contacto_email}
                    onChange={(e) => setFormData({ ...formData, contacto_email: e.target.value })}
                  />
                </div>
              </div>
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

      {/* ========== DIALOG SUSPENSIÓN ========== */}
      <Dialog open={showSuspensionDialog} onOpenChange={setShowSuspensionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-orange-600">
              <Ban className="h-5 w-5" />
              Suspender Empresa
            </DialogTitle>
            <DialogDescription>
              {selectedEmpresa?.nombre} será suspendida y no podrá realizar viajes hasta que sea reactivada.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label>Motivo de suspensión *</Label>
            <Input
              value={suspensionMotivo}
              onChange={(e) => setSuspensionMotivo(e.target.value)}
              placeholder="Ej: Falta de pago, incumplimiento de contrato..."
              className="mt-1"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSuspensionDialog(false)}>
              Cancelar
            </Button>
            <Button
              onClick={handleConfirmSuspension}
              disabled={suspenderMutation.isPending || !suspensionMotivo.trim()}
              className="bg-orange-500 hover:bg-orange-600"
            >
              {suspenderMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Suspender Empresa
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ========== ALERTA ELIMINAR ========== */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar empresa?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. La empresa será desactivada y no podrá realizar viajes.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
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