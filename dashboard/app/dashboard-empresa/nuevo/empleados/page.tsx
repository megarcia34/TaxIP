'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Loader2,
  UserPlus,
  Mail,
  Phone
} from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface Empleado {
  id: string
  email: string
  nombre: string
  apellido: string
  telefono: string
  rol: string
  activo: boolean
  created_at: string
  viajes_realizados: number
  gasto_total: number
}

const formatFecha = (fecha: string | undefined | null) => {
  if (!fecha) return 'N/A'
  try {
    return format(new Date(fecha), "dd/MM/yyyy", { locale: es })
  } catch {
    return 'N/A'
  }
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

export default function EmpresaEmpleadosPage() {
  const [showCrear, setShowCrear] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    telefono: '',
    rol: 'recepcionista',
  })
  const queryClient = useQueryClient()

  const { data: empleados, isLoading } = useQuery<Empleado[]>({
    queryKey: ['empresa-empleados'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/empleados')
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/empresa/dashboard/empleados', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Empleado creado exitosamente')
      queryClient.invalidateQueries({ queryKey: ['empresa-empleados'] })
      setShowCrear(false)
      resetForm()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al crear el empleado'
      toast.error(message)
    },
  })

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      nombre: '',
      apellido: '',
      telefono: '',
      rol: 'recepcionista',
    })
  }

  const handleSubmit = () => {
    if (!formData.email || !formData.password || !formData.nombre || !formData.apellido) {
      toast.error('Los campos email, contraseña, nombre y apellido son requeridos')
      return
    }
    createMutation.mutate(formData)
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
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Empleados</h1>
          <p className="text-muted-foreground">
            Gestión de empleados de la empresa
          </p>
        </div>
        <Button onClick={() => { resetForm(); setShowCrear(true) }}>
          <UserPlus className="h-4 w-4 mr-2" />
          Agregar Empleado
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Listado de Empleados</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Rol</TableHead>
                <TableHead>Viajes</TableHead>
                <TableHead>Gasto</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Fecha</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {empleados?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    No hay empleados registrados
                  </TableCell>
                </TableRow>
              ) : (
                empleados?.map((emp) => (
                  <TableRow key={emp.id}>
                    <TableCell>{emp.nombre} {emp.apellido}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Mail className="h-3 w-3 text-muted-foreground" />
                        {emp.email}
                      </div>
                    </TableCell>
                    <TableCell>
                      {emp.telefono ? (
                        <div className="flex items-center gap-1">
                          <Phone className="h-3 w-3 text-muted-foreground" />
                          {emp.telefono}
                        </div>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{emp.rol}</Badge>
                    </TableCell>
                    <TableCell>{emp.viajes_realizados || 0}</TableCell>
                    <TableCell>{formatMoneda(emp.gasto_total)}</TableCell>
                    <TableCell>
                      <Badge className={emp.activo ? 'bg-green-500' : 'bg-red-500'}>
                        {emp.activo ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs">{formatFecha(emp.created_at)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Modal Crear Empleado */}
      <Dialog open={showCrear} onOpenChange={setShowCrear}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar Empleado</DialogTitle>
            <DialogDescription>
              Cree un nuevo empleado para la empresa
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Email *</Label>
              <Input
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="empleado@empresa.com"
              />
            </div>
            <div>
              <Label>Contraseña *</Label>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="••••••••"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Nombre *</Label>
                <Input
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  placeholder="Nombre"
                />
              </div>
              <div>
                <Label>Apellido *</Label>
                <Input
                  value={formData.apellido}
                  onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                  placeholder="Apellido"
                />
              </div>
            </div>
            <div>
              <Label>Teléfono</Label>
              <Input
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                placeholder="Teléfono de contacto"
              />
            </div>
            <div>
              <Label>Rol</Label>
              <Select
                value={formData.rol}
                onValueChange={(value) => setFormData({ ...formData, rol: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="recepcionista">Recepcionista</SelectItem>
                  <SelectItem value="admin_empresa">Administrador</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCrear(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={createMutation.isPending}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Crear Empleado
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}