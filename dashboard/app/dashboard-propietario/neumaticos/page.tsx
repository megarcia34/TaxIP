'use client'

import { useEffect, useState } from 'react'
import { useVehiculos } from '@/hooks/useVehiculo'
import { useNeumaticos } from '@/hooks/useNeumaticos'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2, Car } from 'lucide-react'
import { VistaNeumaticos } from '@/components/propietario/neumaticos/VistaNeumaticos'
import { SugerenciasNeumaticos } from '@/components/propietario/neumaticos/SugerenciasNeumaticos'
import { toast } from 'sonner'

export default function NeumaticosPage() {
  const { vehiculos, loading: loadingVehiculos, recargar: recargarVehiculos } = useVehiculos()
  const { 
    activos, 
    loading, 
    configuracion,
    rotar,
    medir,
    desmontar,
    recargar: recargarNeumaticos
  } = useNeumaticos()
  
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState<string | null>(null)

  // Seleccionar primer vehículo por defecto
  useEffect(() => {
    if (vehiculos.length > 0 && !vehiculoSeleccionado) {
      setVehiculoSeleccionado(vehiculos[0].id)
    }
  }, [vehiculos])

  // Recargar neumáticos cuando cambia el vehículo
  useEffect(() => {
    if (vehiculoSeleccionado) {
      recargarNeumaticos(vehiculoSeleccionado)
    }
  }, [vehiculoSeleccionado])

  const handleRotar = async (km: number) => {
    if (!vehiculoSeleccionado) return
    await rotar(vehiculoSeleccionado, km)
    await recargarNeumaticos(vehiculoSeleccionado)
  }

  const handleMedir = async (neumaticoId: string, profundidad: number) => {
    await medir(neumaticoId, profundidad)
    if (vehiculoSeleccionado) {
      await recargarNeumaticos(vehiculoSeleccionado)
    }
  }

  const handleDesmontar = async (neumaticoId: string, motivo: string) => {
    if (!vehiculoSeleccionado) return
    // Obtener km actual del vehículo (simplificado, debería venir de un estado)
    const kmActual = 30000 // TODO: Obtener del vehículo
    await desmontar(neumaticoId, kmActual, motivo)
    await recargarNeumaticos(vehiculoSeleccionado)
  }

  if (loadingVehiculos) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (vehiculos.length === 0) {
    return (
      <div className="text-center py-12">
        <Car className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">No hay vehículos</h3>
        <p className="text-muted-foreground">
          Registra un vehículo para comenzar a gestionar neumáticos
        </p>
        <Button className="mt-4" onClick={() => window.location.href = '/dashboard-propietario/vehiculos/crear'}>
          Registrar Vehículo
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Control de Neumáticos</h1>
          <p className="text-muted-foreground">
            Gestión y seguimiento de neumáticos por vehículo
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => {
              if (vehiculoSeleccionado) {
                recargarNeumaticos(vehiculoSeleccionado)
                toast.info('Datos actualizados')
              }
            }}
            disabled={loading}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Actualizar'}
          </Button>
        </div>
      </div>

      {/* Selector de vehículo */}
      <div className="flex flex-wrap gap-2">
        {vehiculos.map((v) => (
          <button
            key={v.id}
            onClick={() => setVehiculoSeleccionado(v.id)}
            className={`px-4 py-2 rounded-lg border transition-colors text-sm ${
              vehiculoSeleccionado === v.id
                ? 'bg-primary text-primary-foreground border-primary'
                : 'hover:bg-muted'
            }`}
          >
            {v.patente} - {v.marca} {v.modelo}
          </button>
        ))}
      </div>

      {/* Vista de neumáticos */}
      <Tabs defaultValue="activos">
        <TabsList>
          <TabsTrigger value="activos">Neumáticos Activos</TabsTrigger>
          <TabsTrigger value="sugerencias">Sugerencias</TabsTrigger>
          <TabsTrigger value="historial">Historial</TabsTrigger>
        </TabsList>

        <TabsContent value="activos" className="mt-4">
          <VistaNeumaticos
            vehiculoId={vehiculoSeleccionado || ''}
            data={activos}
            loading={loading}
            onRotar={handleRotar}
            onMedir={handleMedir}
            onDesmontar={handleDesmontar}
            onRecargar={() => {
              if (vehiculoSeleccionado) {
                recargarNeumaticos(vehiculoSeleccionado)
              }
            }}
          />
        </TabsContent>

        <TabsContent value="sugerencias" className="mt-4">
          <SugerenciasNeumaticos vehiculoId={vehiculoSeleccionado || ''} />
        </TabsContent>

        <TabsContent value="historial" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Neumáticos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-sm">
                Próximamente: historial completo de neumáticos del vehículo
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}