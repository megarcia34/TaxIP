'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { controlBaseAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Trophy, 
  Star, 
  Car, 
  TrendingUp,
  Medal,
  Loader2,
  Users,
  Calendar
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface RankingChofer {
  posicion: number
  chofer_id: string
  nombre: string
  calificacion_promedio: number
  total_calificaciones: number
  total_viajes: number
  fecha_registro: string
  imagen_url: string
  vehiculo: string
  medalla: string
}

const getMedallaColor = (posicion: number) => {
  if (posicion === 1) return 'text-yellow-500'
  if (posicion === 2) return 'text-gray-400'
  if (posicion === 3) return 'text-amber-600'
  return 'text-muted-foreground'
}

const getMedallaBg = (posicion: number) => {
  if (posicion === 1) return 'bg-yellow-500/10 border-yellow-500/30'
  if (posicion === 2) return 'bg-gray-400/10 border-gray-400/30'
  if (posicion === 3) return 'bg-amber-600/10 border-amber-600/30'
  return 'bg-muted/50 border-muted'
}

// ============================================
// ✅ HELPER SEGURO PARA FORMATEAR FECHAS
// ============================================
const formatearFechaSeguro = (fecha: string | null | undefined) => {
  if (!fecha) return 'Fecha no disponible'
  try {
    const date = new Date(fecha)
    if (isNaN(date.getTime())) return 'Fecha inválida'
    return format(date, 'dd/MM/yyyy', { locale: es })
  } catch {
    return 'Fecha inválida'
  }
}

export default function RankingPage() {
  const [criterio, setCriterio] = useState<'calificacion' | 'viajes' | 'antiguedad'>('calificacion')
  const [limite, setLimite] = useState(20)

  const { data: ranking, isLoading } = useQuery({
    queryKey: ['ranking-choferes', criterio, limite],
    queryFn: () => controlBaseAPI.getRankingChoferes(limite, criterio),
    staleTime: 60000, // 1 minuto
  })

  const getCriterioLabel = () => {
    const labels = {
      calificacion: 'Mejor Calificación',
      viajes: 'Más Viajes',
      antiguedad: 'Mayor Antigüedad'
    }
    return labels[criterio]
  }

  const getCriterioIcon = () => {
    const icons = {
      calificacion: <Star className="h-5 w-5" />,
      viajes: <Car className="h-5 w-5" />,
      antiguedad: <Calendar className="h-5 w-5" />
    }
    return icons[criterio]
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Ranking de Choferes</h1>
        <p className="text-muted-foreground">
          Los mejores conductores de la flota según su desempeño
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Top {limite} - {getCriterioLabel()}
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant={criterio === 'calificacion' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCriterio('calificacion')}
              >
                <Star className="h-4 w-4 mr-1" />
                Calificación
              </Button>
              <Button
                variant={criterio === 'viajes' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCriterio('viajes')}
              >
                <Car className="h-4 w-4 mr-1" />
                Viajes
              </Button>
              <Button
                variant={criterio === 'antiguedad' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCriterio('antiguedad')}
              >
                <Calendar className="h-4 w-4 mr-1" />
                Antigüedad
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {ranking?.length === 0 ? (
              <div className="py-8 text-center text-muted-foreground">
                No hay suficientes datos para generar el ranking
              </div>
            ) : (
              ranking?.map((chofer: RankingChofer, index: number) => (
                <div
                  key={chofer.chofer_id}
                  className={`flex items-center gap-4 rounded-lg border p-4 transition-colors hover:bg-muted/50 ${getMedallaBg(chofer.posicion)}`}
                >
                  {/* Posición */}
                  <div className="flex w-12 flex-col items-center justify-center">
                    <span className={`text-2xl font-bold ${getMedallaColor(chofer.posicion)}`}>
                      {chofer.medalla}
                    </span>
                    <span className="text-xs text-muted-foreground">#{chofer.posicion}</span>
                  </div>

                  {/* Avatar */}
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={chofer.imagen_url} />
                    <AvatarFallback className="bg-primary/10 text-primary">
                      {chofer.nombre?.charAt(0) || '?'}
                    </AvatarFallback>
                  </Avatar>

                  {/* Información */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{chofer.nombre}</span>
                      {chofer.posicion <= 3 && (
                        <Badge variant="outline" className="text-xs">
                          {chofer.posicion === 1 ? '🏆' : chofer.posicion === 2 ? '🥈' : '🥉'}
                        </Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                        {chofer.calificacion_promedio?.toFixed(1)}
                        <span className="text-xs">
                          ({chofer.total_calificaciones} calificaciones)
                        </span>
                      </span>
                      <span className="flex items-center gap-1">
                        <Car className="h-3 w-3" />
                        {chofer.total_viajes} viajes
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {chofer.vehiculo || 'Sin vehículo'}
                      </span>
                      <span className="text-xs">
                        {/* ✅ CORREGIDO: usa el helper seguro */}
                        Desde {formatearFechaSeguro(chofer.fecha_registro)}
                      </span>
                    </div>
                  </div>

                  {/* Stats resumidos */}
                  <div className="hidden flex-col items-end sm:flex">
                    {criterio === 'calificacion' && (
                      <span className="text-lg font-bold text-green-600">
                        {chofer.calificacion_promedio?.toFixed(1)}
                      </span>
                    )}
                    {criterio === 'viajes' && (
                      <span className="text-lg font-bold text-blue-600">
                        {chofer.total_viajes}
                      </span>
                    )}
                    {criterio === 'antiguedad' && (
                      <span className="text-lg font-bold text-purple-600">
                        {formatearFechaSeguro(chofer.fecha_registro)}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}