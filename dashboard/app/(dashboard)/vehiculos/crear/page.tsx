'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface Marca {
  id: string
  nombre: string
}

interface Modelo {
  id: string
  nombre: string
}

export default function CrearVehiculoPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    marca_id: '',
    modelo_id: '',
    patente: '',
    numero_licencia: '',
    anio: '',
  })
  const [modelos, setModelos] = useState<Modelo[]>([])

  const { data: marcas, isLoading: marcasLoading } = useQuery({
    queryKey: ['marcas'],
    queryFn: async () => {
      const response = await apiClient.get('/api/catalogo/marcas')
      return response.data
    },
  })

  useEffect(() => {
    if (formData.marca_id) {
      const fetchModelos = async () => {
        const response = await apiClient.get(`/api/catalogo/modelos/${formData.marca_id}`)
        setModelos(response.data)
      }
      fetchModelos()
    } else {
      setModelos([])
    }
  }, [formData.marca_id])

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const marca = marcas?.find((m: Marca) => m.id === data.marca_id)
      const modelo = modelos?.find((m: Modelo) => m.id === data.modelo_id)
      
      const response = await apiClient.post('/api/vehiculos/crear', {
        patente: data.patente.toUpperCase(),
        marca: marca?.nombre,
        modelo: modelo?.nombre,
        anio: parseInt(data.anio) || null,
        numero_licencia: data.numero_licencia.toUpperCase(),
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('Vehículo creado correctamente')
      router.push('/vehiculos')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al crear el vehículo'
      toast.error(message)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.marca_id || !formData.modelo_id || !formData.patente || !formData.numero_licencia) {
      toast.error('Complete los campos obligatorios')
      return
    }

    createMutation.mutate(formData)
  }

  if (marcasLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Nuevo Vehículo</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Información del Vehículo</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="patente">Patente *</Label>
                <Input
                  id="patente"
                  placeholder="ABC123"
                  value={formData.patente}
                  onChange={(e) => setFormData({ ...formData, patente: e.target.value.toUpperCase() })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_licencia">Número de Licencia *</Label>
                <Input
                  id="numero_licencia"
                  placeholder="LIC-12345"
                  value={formData.numero_licencia}
                  onChange={(e) => setFormData({ ...formData, numero_licencia: e.target.value.toUpperCase() })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Select
                  value={formData.marca_id}
                  onValueChange={(value) => setFormData({ ...formData, marca_id: value, modelo_id: '' })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccione una marca" />
                  </SelectTrigger>
                  <SelectContent>
                    {marcas?.map((marca: Marca) => (
                      <SelectItem key={marca.id} value={marca.id}>
                        {marca.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Select
                  value={formData.modelo_id}
                  onValueChange={(value) => setFormData({ ...formData, modelo_id: value })}
                  disabled={!formData.marca_id}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccione un modelo" />
                  </SelectTrigger>
                  <SelectContent>
                    {modelos?.map((modelo: Modelo) => (
                      <SelectItem key={modelo.id} value={modelo.id}>
                        {modelo.nombre}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="anio">Año</Label>
                <Input
                  id="anio"
                  type="number"
                  placeholder="2020"
                  value={formData.anio}
                  onChange={(e) => setFormData({ ...formData, anio: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-4">
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancelar
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Crear Vehículo
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}