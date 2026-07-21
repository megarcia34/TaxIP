'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Car } from 'lucide-react'

interface Marca {
  id: string
  nombre: string
}

interface Modelo {
  id: string
  nombre: string
}

interface Props {
  data: any
  updateData: (data: any) => void
}

export default function RegistroVehiculo({ data, updateData }: Props) {
  const [modelos, setModelos] = useState<Modelo[]>([])

  const { data: marcas } = useQuery({
    queryKey: ['marcas'],
    queryFn: async () => {
      const response = await apiClient.get('/api/catalogo/marcas')
      return response.data
    },
  })

  useEffect(() => {
    if (data.marca_id) {
      const fetchModelos = async () => {
        const response = await apiClient.get(`/api/catalogo/modelos/${data.marca_id}`)
        setModelos(response.data)
      }
      fetchModelos()
    } else {
      setModelos([])
    }
  }, [data.marca_id])

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Checkbox
          id="registrar_vehiculo"
          checked={data.registrar_vehiculo}
          onCheckedChange={(checked) => updateData({ registrar_vehiculo: checked })}
        />
        <Label htmlFor="registrar_vehiculo" className="font-normal cursor-pointer">
          Registrar vehículo ahora (opcional)
        </Label>
      </div>

      {data.registrar_vehiculo && (
        <Card>
          <CardContent className="p-4 space-y-4">
            <div className="flex items-center gap-2 text-primary">
              <Car className="h-4 w-4" />
              <span className="font-medium">Datos del Vehículo</span>
            </div>
            
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="patente">Patente *</Label>
                <Input
                  id="patente"
                  placeholder="ABC123"
                  value={data.patente}
                  onChange={(e) => updateData({ patente: e.target.value.toUpperCase() })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Select
                  value={data.marca_id}
                  onValueChange={(value) => updateData({ marca_id: value, modelo_id: '' })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccione marca" />
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
                  value={data.modelo_id}
                  onValueChange={(value) => updateData({ modelo_id: value })}
                  disabled={!data.marca_id}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccione modelo" />
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
                  value={data.anio}
                  onChange={(e) => updateData({ anio: e.target.value })}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-muted/50">
        <CardContent className="p-4 text-sm text-muted-foreground">
          <p>💡 Puedes registrar más vehículos más tarde desde el panel de propietario.</p>
        </CardContent>
      </Card>
    </div>
  )
}