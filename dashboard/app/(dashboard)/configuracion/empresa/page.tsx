'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { controlBaseAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, Save, Building2, Mail, Phone, MapPin } from 'lucide-react'
import { toast } from 'sonner'

interface DatosEmpresa {
  id: string
  nombre: string
  email: string
  telefono: string
  latitud?: number
  longitud?: number
  activo: boolean
}

export default function DatosEmpresaPage() {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
  })

  const { data: empresa, isLoading } = useQuery({
    queryKey: ['datos-empresa'],
    queryFn: controlBaseAPI.getDatosEmpresa,
  })

  useEffect(() => {
    if (empresa) {
      setFormData({
        nombre: empresa.nombre || '',
        email: empresa.email || '',
        telefono: empresa.telefono || '',
      })
    }
  }, [empresa])

  const updateMutation = useMutation({
    mutationFn: (data: any) => controlBaseAPI.actualizarEmpresa(data),
    onSuccess: () => {
      toast.success('Datos actualizados correctamente')
      queryClient.invalidateQueries({ queryKey: ['datos-empresa'] })
      setIsEditing(false)
    },
    onError: () => {
      toast.error('Error al actualizar los datos')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Información de la Empresa</CardTitle>
        {!isEditing && (
          <Button variant="outline" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {!isEditing ? (
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Nombre</p>
                <p className="font-medium">{empresa?.nombre || 'No especificado'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{empresa?.email || 'No especificado'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Phone className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Teléfono</p>
                <p className="font-medium">{empresa?.telefono || 'No especificado'}</p>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nombre">Nombre de la Empresa</Label>
              <Input
                id="nombre"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="telefono">Teléfono</Label>
              <Input
                id="telefono"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-4 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <Save className="h-4 w-4 mr-2" />
                Guardar Cambios
              </Button>
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  )
}