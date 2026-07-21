'use client'

import { useState, useEffect } from 'react'
import { useRouter, } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

export default function NuevoVehiculoPage() {
  const router = useRouter()
      // ✅ Reemplazo de useSearchParams() por window.location
    const [propietario_id, setPropietario_id] = useState<string | null>(null)

    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        setPropietario_id(params.get('propietario_id'))
    }, [])
    
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)

  const isAdmin = user?.rol === 'admin'
  const propietarioId = propietario_id

  const [formData, setFormData] = useState({
    patente: '',
    marca: '',
    modelo: '',
    anio: '',
    numero_licencia: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await apiClient.post('/api/propietario/vehiculos', {
        patente: formData.patente.toUpperCase(),
        marca: formData.marca,
        modelo: formData.modelo,
        anio: formData.anio ? parseInt(formData.anio) : null,
        numero_licencia: formData.numero_licencia,
      })
      
      toast.success('Vehículo creado correctamente')
      
      const redirectPath = isAdmin && propietarioId 
        ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
        : '/dashboard-propietario/vehiculos'
      router.push(redirectPath)
    } catch (error: any) {
      console.error('Error creando vehículo:', error)
      toast.error(error.response?.data?.detail || 'Error al crear el vehículo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={
            isAdmin && propietarioId
              ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
              : '/dashboard-propietario/vehiculos'
          }
        >
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Nuevo Vehículo</h1>
          <p className="text-muted-foreground">
            Registra un nuevo vehículo en la flota
          </p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Datos del Vehículo</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="patente">Patente *</Label>
              <Input
                id="patente"
                required
                placeholder="ABC123"
                value={formData.patente}
                onChange={(e) => setFormData({ ...formData, patente: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input
                  id="marca"
                  required
                  placeholder="Toyota"
                  value={formData.marca}
                  onChange={(e) => setFormData({ ...formData, marca: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Input
                  id="modelo"
                  required
                  placeholder="Corolla"
                  value={formData.modelo}
                  onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anio">Año</Label>
                <Input
                  id="anio"
                  type="number"
                  placeholder="2024"
                  value={formData.anio}
                  onChange={(e) => setFormData({ ...formData, anio: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_licencia">Número de Licencia</Label>
                <Input
                  id="numero_licencia"
                  placeholder="LIC-123456"
                  value={formData.numero_licencia}
                  onChange={(e) =>
                    setFormData({ ...formData, numero_licencia: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <Link
                href={
                  isAdmin && propietarioId
                    ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
                    : '/dashboard-propietario/vehiculos'
                }
              >
                <Button type="button" variant="outline">
                  Cancelar
                </Button>
              </Link>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Crear Vehículo
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}