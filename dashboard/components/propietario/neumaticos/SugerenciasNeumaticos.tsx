'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loader2, AlertTriangle, CheckCircle, XCircle, Check } from 'lucide-react'
import { neumaticosAPI } from '@/lib/api'
import { toast } from 'sonner'
import { SugerenciaNeumatico } from '@/types'
import { Sugerencia } from '@/lib/api/neumaticos'

interface SugerenciasNeumaticosProps {
  vehiculoId: string
}

export function SugerenciasNeumaticos({ vehiculoId }: SugerenciasNeumaticosProps) {
  
const [sugerencias, setSugerencias] = useState<Sugerencia[]>([])
  const [loading, setLoading] = useState(true)
  const [accionando, setAccionando] = useState<string | null>(null)

  const cargarSugerencias = async () => {
    setLoading(true)
    try {
      const data = await neumaticosAPI.getSugerencias(vehiculoId, 'PENDIENTE')
         setSugerencias(data || []) 
    } catch (error) {
      console.error('Error cargando sugerencias:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAtender = async (id: string) => {
    setAccionando(id)
    try {
      await neumaticosAPI.atenderSugerencia(id)
      toast.success('Sugerencia atendida')
      await cargarSugerencias()
    } catch (error) {
      toast.error('Error al atender sugerencia')
    } finally {
      setAccionando(null)
    }
  }

  const handleDesestimar = async (id: string) => {
    setAccionando(id)
    try {
      await neumaticosAPI.desestimarSugerencia(id, 'No aplica')
      toast.success('Sugerencia desestimada')
      await cargarSugerencias()
    } catch (error) {
      toast.error('Error al desestimar sugerencia')
    } finally {
      setAccionando(null)
    }
  }

  useEffect(() => {
    if (vehiculoId) {
      cargarSugerencias()
    }
  }, [vehiculoId])

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (sugerencias.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
          <p>No hay sugerencias pendientes</p>
          <p className="text-sm">Todos los neumáticos están en buen estado</p>
        </CardContent>
      </Card>
    )
  }

  const colorMap = {
    ROJO: 'border-red-200 bg-red-50',
    AMARILLO: 'border-yellow-200 bg-yellow-50',
    VERDE: 'border-green-200 bg-green-50',
  }

  const badgeColorMap = {
    ROJO: 'bg-red-100 text-red-800',
    AMARILLO: 'bg-yellow-100 text-yellow-800',
    VERDE: 'bg-green-100 text-green-800',
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-500" />
          Sugerencias Pendientes ({sugerencias.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {sugerencias.map((sug) => (
          <div key={sug.id} className={`border p-3 rounded-lg ${colorMap[sug.color]}`}>
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge className={badgeColorMap[sug.color]}>
                    {sug.color}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {sug.tipo}
                  </Badge>
                  {sug.neumatico && (
                    <span className="text-xs font-medium">{sug.neumatico}</span>
                  )}
                  {sug.posicion && (
                    <span className="text-xs text-muted-foreground">Posición: {sug.posicion}</span>
                  )}
                </div>
                <p className="text-sm mt-1">{sug.mensaje}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                  <span>Km actual: {sug.km_actual.toLocaleString()}</span>
                  <span>Umbral: {sug.km_umbral.toLocaleString()}</span>
                  <span>Activa hace {sug.dias_activa} días</span>
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                <Button
                  size="sm"
                  variant="outline"
                  className="text-green-600"
                  onClick={() => handleAtender(sug.id)}
                  disabled={accionando === sug.id}
                >
                  <Check className="h-4 w-4 mr-1" />
                  Atender
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-muted-foreground"
                  onClick={() => handleDesestimar(sug.id)}
                  disabled={accionando === sug.id}
                >
                  Desestimar
                </Button>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}