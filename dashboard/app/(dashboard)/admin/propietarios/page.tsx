'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { propietarioAPI } from '@/lib/api'
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
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Search, Plus, Edit, Trash2, Eye, Phone, Mail, Building2, Loader2, Users } from 'lucide-react'
import Link from 'next/link'
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

interface Propietario {
  id: string
  usuario_id: string
  nombre: string
  email: string
  telefono: string
  estado: 'activo' | 'inactivo'
  total_vehiculos: number
  total_contratos: number
  fecha_registro: string
  vehiculos?: Array<{
    id: string
    patente: string
    marca: string
    modelo: string
  }>
}

export default function AdminPropietariosPage() {
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [editPropietario, setEditPropietario] = useState<Propietario | null>(null)
  const [viewPropietario, setViewPropietario] = useState<Propietario | null>(null)
  const [editForm, setEditForm] = useState({
    nombre: '',
    apellido: '',
    telefono: '',
    email: '',
    estado: 'activo',
  })
  const queryClient = useQueryClient()

  // Obtener propietarios
  const { data: propietarios, isLoading, refetch } = useQuery({
    queryKey: ['admin-propietarios'],
    queryFn: () => propietarioAPI.getAll(),
    staleTime: 0,
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  })

  // Eliminar propietario
  const deleteMutation = useMutation({
    mutationFn: (id: string) => propietarioAPI.delete(id),
    onSuccess: () => {
      toast.success('Propietario eliminado correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-propietarios'] })
      setDeleteId(null)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al eliminar el propietario'
      toast.error(message)
    },
  })

  // Actualizar propietario
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => propietarioAPI.update(id, data),
    onSuccess: () => {
      toast.success('Propietario actualizado correctamente')
      queryClient.invalidateQueries({ queryKey: ['admin-propietarios'] })
      setEditPropietario(null)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al actualizar el propietario'
      toast.error(message)
    },
  })

  // Filtrar propietarios
  const filteredPropietarios = propietarios?.filter((prop: Propietario) => {
    const searchLower = search.toLowerCase()
    return (
      prop.nombre?.toLowerCase().includes(searchLower) ||
      prop.email?.toLowerCase().includes(searchLower) ||
      prop.telefono?.toLowerCase().includes(searchLower)
    )
  })

  // Manejar edición
  const handleEditClick = (prop: Propietario) => {
    const nameParts = prop.nombre?.split(' ') || ['', '']
    setEditForm({
      nombre: nameParts[0] || '',
      apellido: nameParts.slice(1).join(' ') || '',
      telefono: prop.telefono || '',
      email: prop.email || '',
      estado: prop.estado || 'activo',
    })
    setEditPropietario(prop)
  }

  const handleSaveEdit = () => {
    if (editPropietario) {
      updateMutation.mutate({
        id: editPropietario.usuario_id,
        data: {
          nombre: editForm.nombre,
          apellido: editForm.apellido,
          telefono: editForm.telefono,
          estado: editForm.estado,
        },
      })
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
          <h1 className="text-2xl font-bold tracking-tight">Propietarios</h1>
          <p className="text-muted-foreground">
            Gestión de dueños de vehículos y flotas
          </p>
        </div>
        <Link href="/admin/propietarios/nuevo">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Propietario
          </Button>
        </Link>
      </div>

      {/* Tabla */}
      <Card>
        <CardHeader>
          <CardTitle className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <span>Listado de Propietarios</span>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre, email o teléfono..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 w-full sm:w-80"
              />
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-3 font-medium">Propietario</th>
                  <th className="pb-3 font-medium">Contacto</th>
                  <th className="pb-3 font-medium">Vehículos</th>
                  <th className="pb-3 font-medium">Contratos</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Registro</th>
                  <th className="pb-3 font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredPropietarios?.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-muted-foreground">
                      No hay propietarios registrados
                    </td>
                  </tr>
                ) : (
                  filteredPropietarios?.map((prop: Propietario) => (
                    <tr key={prop.id} className="border-b hover:bg-muted/50">
                      <td className="py-3">
                        <div className="font-medium">{prop.nombre || 'N/A'}</div>
                        <div className="text-xs text-muted-foreground">
                          ID: {prop.usuario_id?.slice(0, 8)}...
                        </div>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-1 text-xs">
                          <Mail className="h-3 w-3" />
                          {prop.email || 'N/A'}
                        </div>
                        <div className="flex items-center gap-1 text-xs mt-1">
                          <Phone className="h-3 w-3" />
                          {prop.telefono || 'N/A'}
                        </div>
                      </td>
                      <td className="py-3">
                        <Link href={`/dashboard-propietario/vehiculos?propietario=${prop.usuario_id}`}>
                          <Button variant="ghost" size="sm" className="gap-1">
                            <Building2 className="h-4 w-4" />
                            {prop.total_vehiculos || 0}
                          </Button>
                        </Link>
                      </td>
                      <td className="py-3">
                        <Badge variant="outline" className="gap-1">
                          <Users className="h-3 w-3" />
                          {prop.total_contratos || 0}
                        </Badge>
                      </td>
                      <td className="py-3">
                        <Badge className={prop.estado === 'activo' ? 'bg-green-500' : 'bg-gray-500'}>
                          {prop.estado === 'activo' ? 'Activo' : 'Inactivo'}
                        </Badge>
                      </td>
                      <td className="py-3 text-xs">
                        {prop.fecha_registro ? new Date(prop.fecha_registro).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Ver detalles"
                            onClick={() => setViewPropietario(prop)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Editar"
                            onClick={() => handleEditClick(prop)}
                          >
                            <Edit className="h-4 w-4 text-blue-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Eliminar"
                            onClick={() => setDeleteId(prop.usuario_id)}
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

      {/* Diálogo de Visualización */}
      <Dialog open={!!viewPropietario} onOpenChange={() => setViewPropietario(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Detalle del Propietario</DialogTitle>
          </DialogHeader>
          {viewPropietario && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Nombre</Label>
                  <p className="font-medium">{viewPropietario.nombre}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Email</Label>
                  <p className="font-medium">{viewPropietario.email}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Teléfono</Label>
                  <p className="font-medium">{viewPropietario.telefono || 'N/A'}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Estado</Label>
                  <Badge className={viewPropietario.estado === 'activo' ? 'bg-green-500' : 'bg-gray-500'}>
                    {viewPropietario.estado === 'activo' ? 'Activo' : 'Inactivo'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Total Vehículos</Label>
                  <p className="font-medium">{viewPropietario.total_vehiculos || 0}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Total Contratos</Label>
                  <p className="font-medium">{viewPropietario.total_contratos || 0}</p>
                </div>
              </div>

              {viewPropietario.vehiculos && viewPropietario.vehiculos.length > 0 && (
                <div>
                  <Label className="text-muted-foreground">Vehículos</Label>
                  <div className="mt-2 space-y-1">
                    {viewPropietario.vehiculos.map((v) => (
                      <div key={v.id} className="flex items-center gap-2 text-sm">
                        <Badge variant="outline">{v.patente}</Badge>
                        <span>{v.marca} {v.modelo}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewPropietario(null)}>
              Cerrar
            </Button>
            {viewPropietario && (
              <Link href={`/dashboard-propietario/vehiculos?propietario=${viewPropietario.usuario_id}`}>
                <Button>Ver Vehículos</Button>
              </Link>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Diálogo de Edición */}
      <Dialog open={!!editPropietario} onOpenChange={() => setEditPropietario(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Propietario</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-nombre">Nombre</Label>
              <Input
                id="edit-nombre"
                value={editForm.nombre}
                onChange={(e) => setEditForm({ ...editForm, nombre: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-apellido">Apellido</Label>
              <Input
                id="edit-apellido"
                value={editForm.apellido}
                onChange={(e) => setEditForm({ ...editForm, apellido: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-telefono">Teléfono</Label>
              <Input
                id="edit-telefono"
                value={editForm.telefono}
                onChange={(e) => setEditForm({ ...editForm, telefono: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email</Label>
              <Input
                id="edit-email"
                value={editForm.email}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground">El email no se puede cambiar</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-estado">Estado</Label>
              <Select
                value={editForm.estado}
                onValueChange={(value) => setEditForm({ ...editForm, estado: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="activo">Activo</SelectItem>
                  <SelectItem value="inactivo">Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditPropietario(null)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveEdit} disabled={updateMutation.isPending}>
              {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Guardar Cambios
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Diálogo de Confirmación de Eliminación */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar propietario?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. El propietario será eliminado permanentemente.
              Se eliminarán también todos sus vehículos y contratos asociados.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && deleteMutation.mutate(deleteId)}
              className="bg-red-500 hover:bg-red-600"
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Eliminar'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}