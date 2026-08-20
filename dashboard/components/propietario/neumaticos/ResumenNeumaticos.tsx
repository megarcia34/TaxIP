'use client'

import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle, AlertTriangle, XCircle, Circle } from 'lucide-react'

// ✅ Interfaz actualizada para coincidir con la API
interface ResumenNeumaticosProps {
  resumen: {
    total_neumaticos: number
    estado_verde: number
    estado_amarillo: number
    estado_rojo: number
  }
}

export function ResumenNeumaticos({ resumen }: ResumenNeumaticosProps) {
  const { total_neumaticos, estado_verde, estado_amarillo, estado_rojo } = resumen
  
  if (total_neumaticos === 0) {
    return (
      <Card>
        <CardContent className="py-4 text-center text-muted-foreground">
          No hay neumáticos registrados
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* Total */}
      <Card className="border-gray-200 bg-gray-50/50">
        <CardContent className="py-3 text-center">
          <div className="flex items-center justify-center gap-2">
            <Circle className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Total</span>
          </div>
          <p className="text-2xl font-bold text-gray-700">{total_neumaticos}</p>
        </CardContent>
      </Card>

      {/* Verde - Bueno */}
      <Card className="border-green-200 bg-green-50/50">
        <CardContent className="py-3 text-center">
          <div className="flex items-center justify-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-green-700">Bueno</span>
          </div>
          <p className="text-2xl font-bold text-green-700">{estado_verde}</p>
        </CardContent>
      </Card>
      
      {/* Amarillo - Atención */}
      <Card className="border-yellow-200 bg-yellow-50/50">
        <CardContent className="py-3 text-center">
          <div className="flex items-center justify-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-700">Atención</span>
          </div>
          <p className="text-2xl font-bold text-yellow-700">{estado_amarillo}</p>
        </CardContent>
      </Card>
      
      {/* Rojo - Crítico */}
      <Card className="border-red-200 bg-red-50/50">
        <CardContent className="py-3 text-center">
          <div className="flex items-center justify-center gap-2">
            <XCircle className="h-4 w-4 text-red-600" />
            <span className="text-sm font-medium text-red-700">Crítico</span>
          </div>
          <p className="text-2xl font-bold text-red-700">{estado_rojo}</p>
        </CardContent>
      </Card>
    </div>
  )
}