'use client'

import { useState } from 'react'
import { NeumaticoCard } from './NeumaticoCard'
import { ResumenNeumaticos } from './ResumenNeumaticos'
import { AccionesNeumaticos } from './AccionesNeumaticos'
import { DetalleNeumaticoModal } from './DetalleNeumaticoModal'
import { Loader2, Car } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { NeumaticosActivosResponse } from '@/lib/api/neumaticos'

// ✅ Definir el tipo de posición permitida
type Posicion = 'DI' | 'DD' | 'TI' | 'TD'

// ✅ Array de posiciones válidas
const POSICIONES_VALIDAS: Posicion[] = ['DI', 'DD', 'TI', 'TD']

interface VistaNeumaticosProps {
  vehiculoId: string
  data: NeumaticosActivosResponse | null
  loading: boolean
  onRotar: (km: number) => Promise<void>
  onMedir: (neumaticoId: string, profundidad: number) => Promise<void>
  onDesmontar: (neumaticoId: string, motivo: string) => Promise<void>
  onRecargar: () => void
}

// ✅ Tipar los objetos con Posicion como clave
const posicionLabels: Record<Posicion, string> = {
  DI: 'Delantero Izquierdo',
  DD: 'Delantero Derecho',
  TI: 'Trasero Izquierdo',
  TD: 'Trasero Derecho',
}

const posicionOrden: Record<Posicion, number> = {
  DI: 0,
  DD: 1,
  TI: 2,
  TD: 3,
}

export function VistaNeumaticos({
  vehiculoId,
  data,
  loading,
  onRotar,
  onMedir,
  onDesmontar,
  onRecargar
}: VistaNeumaticosProps) {
  const [selectedNeumaticoId, setSelectedNeumaticoId] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // Verificar si hay neumáticos activos
  const tieneNeumaticos = data && data.neumaticos && 
    Object.values(data.neumaticos).some((n) => n !== null)

  if (!data || !data.neumaticos || !tieneNeumaticos) {
    return (
      <div className="text-center py-12 space-y-4">
        <Car className="h-12 w-12 mx-auto text-muted-foreground" />
        <div>
          <h3 className="text-lg font-medium">No hay neumáticos activos</h3>
          <p className="text-muted-foreground text-sm">
            Este vehículo no tiene neumáticos montados actualmente
          </p>
        </div>
        <Button variant="outline" onClick={onRecargar}>
          Actualizar
        </Button>
      </div>
    )
  }

  const neumaticos = data.neumaticos
  const resumen = data.resumen

  // ✅ Filtrar solo neumáticos no nulos usando POSICIONES_VALIDAS
  const posicionesConNeumaticos = POSICIONES_VALIDAS
    .filter((pos) => neumaticos[pos] !== null)
    .sort((a, b) => posicionOrden[a] - posicionOrden[b])

  // ✅ Posiciones vacías usando POSICIONES_VALIDAS
  const posicionesVacias = POSICIONES_VALIDAS
    .filter((pos) => neumaticos[pos] === null)

  const handleOpenDetalle = (id: string) => {
    setSelectedNeumaticoId(id)
    setModalOpen(true)
  }

  return (
    <div className="space-y-4">
      {/* Resumen */}
      <ResumenNeumaticos resumen={resumen} />

      {/* Grid de neumáticos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {posicionesConNeumaticos.map((pos) => (
          <div 
            key={pos} 
            onClick={() => neumaticos[pos] && handleOpenDetalle(neumaticos[pos].id)} 
            className="cursor-pointer"
          >
            <NeumaticoCard
              neumatico={neumaticos[pos]!}
              posicion={pos}
              posicionLabel={posicionLabels[pos] || pos}
            />
          </div>
        ))}
        
        {/* Mostrar posiciones vacías */}
        {posicionesVacias.map((pos) => (
          <div 
            key={pos} 
            className="border-2 border-dashed border-muted rounded-lg p-4 flex flex-col items-center justify-center min-h-[200px] text-muted-foreground"
          >
            <Car className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">{posicionLabels[pos] || pos}</p>
            <p className="text-xs">Sin neumático</p>
          </div>
        ))}
      </div>

      {/* Acciones */}
      <AccionesNeumaticos
        vehiculoId={vehiculoId}
        onRotar={onRotar}
        onRecargar={onRecargar}
      />

      {/* Modal de detalle */}
      {selectedNeumaticoId && (
        <DetalleNeumaticoModal
          open={modalOpen}
          onOpenChange={setModalOpen}
          neumaticoId={selectedNeumaticoId}
          onMedir={onMedir}
          onDesmontar={onDesmontar}
          onRecargar={onRecargar}
        />
      )}
    </div>
  )
}