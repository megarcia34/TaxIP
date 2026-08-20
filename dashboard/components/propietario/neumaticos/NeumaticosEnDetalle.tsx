'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2, RefreshCw, AlertCircle } from 'lucide-react'
import { GestionNeumaticos } from './GestionNeumaticos'
// ✅ Cambiar import de @/types a @/lib/api/neumaticos
import { NeumaticosActivosResponse } from '@/lib/api/neumaticos'

// ✅ Validación de UUID
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

interface NeumaticosEnDetalleProps {
  vehiculoId: string
  activos: NeumaticosActivosResponse | null
  loading: boolean
  onRecargar: () => void
}

export function NeumaticosEnDetalle({ vehiculoId, activos, loading, onRecargar }: NeumaticosEnDetalleProps) {
  // ✅ Validar que vehiculoId sea un UUID válido
  const isValidId = vehiculoId && UUID_REGEX.test(vehiculoId)

  const cantidadActivos = activos?.neumaticos 
    ? Object.values(activos.neumaticos).filter(n => n !== null).length 
    : 0

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // ✅ Si el ID no es válido, mostrar mensaje
  if (!isValidId) {
    return (
      <Card className="border-dashed border-yellow-200 bg-yellow-50/30">
        <CardContent className="py-8 text-center">
          <AlertCircle className="h-12 w-12 mx-auto text-yellow-500 mb-3" />
          <p className="text-yellow-700 font-medium">ID de vehículo inválido</p>
          <p className="text-yellow-600 text-sm mt-1">
            No se pueden cargar los neumáticos sin un vehículo válido.
          </p>
        </CardContent>
      </Card>
    )
  }

  // ✅ Si no hay neumáticos, mostrar mensaje amigable
  if (!activos) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium">
              Neumáticos del Vehículo
              <span className="text-sm font-normal text-muted-foreground ml-2">
                (0/4 montados)
              </span>
            </h3>
          </div>
          <Button variant="outline" size="sm" onClick={onRecargar}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Actualizar
          </Button>
        </div>
        <Card className="border-dashed border-yellow-200 bg-yellow-50/30">
          <CardContent className="py-8 text-center">
            <AlertCircle className="h-12 w-12 mx-auto text-yellow-500 mb-3" />
            <p className="text-yellow-700 font-medium">No hay neumáticos registrados</p>
            <p className="text-yellow-600 text-sm mt-1">
              Este vehículo no tiene neumáticos cargados.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ✅ Pasar solo los neumáticos (no todo el objeto) a GestionNeumaticos
  // activos.neumaticos es de tipo { DI?: NeumaticoActivo, DD?: NeumaticoActivo, ... }
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">
            Neumáticos del Vehículo
            <span className="text-sm font-normal text-muted-foreground ml-2">
              ({cantidadActivos}/4 montados)
            </span>
          </h3>
        </div>
        <Button variant="outline" size="sm" onClick={onRecargar}>
          <RefreshCw className="h-4 w-4 mr-1" />
          Actualizar
        </Button>
      </div>

      <GestionNeumaticos 
        vehiculoId={vehiculoId}
        activos={activos.neumaticos}
        onRecargar={onRecargar}
      />
    </div>
  )
}