'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2, CircleDot, FileText } from 'lucide-react'
import { toast } from 'sonner'
import { useCreateVehiculo } from '@/hooks/useVehiculos'

export default function NuevoVehiculoPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [propietario_id, setPropietario_id] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietario_id(params.get('propietario_id'))
  }, [])

  const isAdmin = user?.rol === 'admin'
  const propietarioId = propietario_id

  const [formData, setFormData] = useState({
    patente: '',
    marca: '',
    modelo: '',
    anio: '',
    numero_licencia: '',
  })

  const createMutation = useCreateVehiculo()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.patente || !formData.marca || !formData.modelo) {
      toast.error('Completa todos los campos obligatorios')
      return
    }

    createMutation.mutate(
      {
        patente: formData.patente,
        marca: formData.marca,
        modelo: formData.modelo,
        anio: formData.anio ? parseInt(formData.anio) : null,
        numero_licencia: formData.numero_licencia || null,
      },
      {
        onSuccess: (data) => {
          const vehiculoId = data?.vehiculo_id || data?.id
          const patente = formData.patente.toUpperCase()

          if (vehiculoId) {
            // ✅ Mostrar toast con enlaces a neumáticos y documentos
            toast.success(
              `✅ Vehículo ${patente} creado correctamente`,
              {
                duration: 8000,
                description: (
                  <div className="mt-2 space-y-2">
                    <p className="text-sm text-muted-foreground">
                      Para que el vehículo quede operativo, debes completar:
                    </p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <Link
                        href={`/dashboard-propietario/vehiculos/${vehiculoId}?tab=neumaticos${isAdmin && propietarioId ? `&propietario_id=${propietarioId}` : ''}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors"
                        onClick={() => {
                          // Cerrar el toast al hacer clic
                          toast.dismiss()
                        }}
                      >
                        <CircleDot className="h-4 w-4" />
                        Montar Neumáticos
                      </Link>
                      <Link
                        href={`/dashboard-propietario/vehiculos/${vehiculoId}?tab=documentos${isAdmin && propietarioId ? `&propietario_id=${propietarioId}` : ''}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors"
                        onClick={() => {
                          toast.dismiss()
                        }}
                      >
                        <FileText className="h-4 w-4" />
                        Subir Documentos
                      </Link>
                    </div>
                  </div>
                ),
              }
            )

            // ✅ Redirigir al detalle
            router.push(`/dashboard-propietario/vehiculos/${vehiculoId}`)
          } else {
            const redirectPath =
              isAdmin && propietarioId
                ? `/dashboard-propietario/vehiculos?propietario_id=${propietarioId}`
                : '/dashboard-propietario/vehiculos'
            router.push(redirectPath)
          }
        },
      }
    )
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
          <Button variant="outline" size="icon" type="button">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Nuevo Vehículo</h1>
          <p className="text-muted-foreground">Registra un nuevo vehículo en la flota</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Datos del Vehículo</CardTitle>
          <p className="text-sm text-muted-foreground">Los campos con * son obligatorios</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="patente">Patente *</Label>
              <Input
                id="patente"
                required
                placeholder="Ej: ABC123"
                value={formData.patente}
                onChange={(e) => setFormData({ ...formData, patente: e.target.value.toUpperCase() })}
              />
              <p className="text-xs text-muted-foreground">
                La patente se guardará en mayúsculas automáticamente
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="marca">Marca *</Label>
                <Input
                  id="marca"
                  required
                  placeholder="Ej: Toyota"
                  value={formData.marca}
                  onChange={(e) => setFormData({ ...formData, marca: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo *</Label>
                <Input
                  id="modelo"
                  required
                  placeholder="Ej: Corolla"
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
                  placeholder="Ej: 2024"
                  min="1900"
                  max="2100"
                  value={formData.anio}
                  onChange={(e) => setFormData({ ...formData, anio: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_licencia">Número de Licencia</Label>
                <Input
                  id="numero_licencia"
                  placeholder="Ej: LIC-123456"
                  value={formData.numero_licencia}
                  onChange={(e) => setFormData({ ...formData, numero_licencia: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t">
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