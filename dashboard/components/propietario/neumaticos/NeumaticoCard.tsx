'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Car, AlertTriangle } from 'lucide-react'
// ✅ Importar desde @/lib/api/neumaticos
import { NeumaticoActivo } from '@/lib/api/neumaticos'

// ✅ Definir el tipo de posición permitida
type Posicion = 'DI' | 'DD' | 'TI' | 'TD'

interface NeumaticoCardProps {
  neumatico: NeumaticoActivo
  posicion: Posicion | string
  posicionLabel: string
}

// ✅ Mapeo de colores con tipos más específicos
const colorMap: Record<string, {
  bg: string
  border: string
  text: string
  progress: string
}> = {
  VERDE: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-700',
    progress: 'bg-green-500',
  },
  AMARILLO: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-700',
    progress: 'bg-yellow-500',
  },
  ROJO: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-700',
    progress: 'bg-red-500',
  },
}

export function NeumaticoCard({ neumatico, posicion, posicionLabel }: NeumaticoCardProps) {
  const colors = colorMap[neumatico.estado_color] || colorMap.VERDE
  const kmDisplay = neumatico.km_recorridos < 0 ? 0 : neumatico.km_recorridos
  const profundidadDisplay = neumatico.ultima_profundidad_mm ?? '--'
  const esCritico = neumatico.estado_color === 'ROJO'

  // Calcular porcentaje de desgaste (basado en vida útil de 50,000 km)
  const porcentajeDesgaste = neumatico.km_recorridos < 0 
    ? 0 
    : Math.min(Math.round((neumatico.km_recorridos / 50000) * 100), 100)

  return (
    <Card className={`border-2 ${colors.border} ${colors.bg}`}>
      <CardContent className="pt-4">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs text-muted-foreground">{posicionLabel}</p>
            <p className="font-bold text-sm">{neumatico.marca}</p>
            {neumatico.modelo_dibujo && (
              <p className="text-xs text-muted-foreground">{neumatico.modelo_dibujo}</p>
            )}
          </div>
          <Badge className={`${esCritico ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
            {esCritico ? 'CRÍTICO' : neumatico.estado_color}
          </Badge>
        </div>

        <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
          <span className="text-muted-foreground">Medida:</span>
          <span className="font-medium">{neumatico.medida || '--'}</span>
          <span className="text-muted-foreground">Km montaje:</span>
          <span className="font-medium">{neumatico.km_montaje?.toLocaleString() || 0}</span>
          <span className="text-muted-foreground">Km recorridos:</span>
          <span className="font-medium">{kmDisplay.toLocaleString()}</span>
          <span className="text-muted-foreground">Profundidad:</span>
          <span className="font-medium">{typeof profundidadDisplay === 'number' ? `${profundidadDisplay} mm` : profundidadDisplay}</span>
        </div>

        <div className="mt-3">
          <div className="flex justify-between text-xs mb-1">
            <span>Desgaste estimado</span>
            <span className={colors.text}>
              {porcentajeDesgaste}%
            </span>
          </div>
          <Progress 
            value={porcentajeDesgaste} 
            className="h-2"
          />
        </div>

        {neumatico.sugerencia && (
          <div className="mt-2 p-2 bg-yellow-100 rounded text-xs text-yellow-700 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            {neumatico.sugerencia}
          </div>
        )}
      </CardContent>
    </Card>
  )
}