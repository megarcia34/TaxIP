'use client'

import { Check, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PipelineEstadosProps {
  estado: string
}

const ESTADOS = [
  { id: 'reservado', label: 'Reservado' },
  { id: 'despachado', label: 'Despachado' },
  { id: 'vehiculo_llego', label: 'Vehículo llegó' },
  { id: 'pasajero_a_bordo', label: 'Pasajero a bordo' },
  { id: 'completado', label: 'Completado' },
]

export function PipelineEstados({ estado }: PipelineEstadosProps) {
  const estadoIndex = ESTADOS.findIndex(e => e.id === estado)
  const isCancelado = estado === 'cancelado'

  if (isCancelado) {
    return (
      <div className="flex items-center justify-center py-2">
        <span className="text-sm font-medium text-destructive">Viaje cancelado</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-1 overflow-x-auto py-2">
      {ESTADOS.map((e, index) => {
        const isCompleted = index <= estadoIndex
        const isActive = index === estadoIndex
        const isLast = index === ESTADOS.length - 1

        return (
          <div key={e.id} className="flex items-center flex-shrink-0">
            <div className="flex items-center gap-1.5">
              <div
                className={cn(
                  'h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium transition-colors',
                  isCompleted && !isActive && 'bg-green-500 text-white',
                  isActive && 'bg-primary text-primary-foreground',
                  !isCompleted && !isActive && 'bg-muted text-muted-foreground'
                )}
              >
                {isCompleted && !isActive ? (
                  <Check className="h-3.5 w-3.5" />
                ) : isActive ? (
                  <Clock className="h-3.5 w-3.5 animate-pulse" />
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={cn(
                  'text-xs whitespace-nowrap',
                  isActive && 'font-medium text-primary',
                  isCompleted && 'text-muted-foreground',
                  !isCompleted && !isActive && 'text-muted-foreground/60'
                )}
              >
                {e.label}
              </span>
            </div>
            {!isLast && (
              <div
                className={cn(
                  'h-0.5 w-6 mx-1',
                  index < estadoIndex ? 'bg-green-500' : 'bg-muted'
                )}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}