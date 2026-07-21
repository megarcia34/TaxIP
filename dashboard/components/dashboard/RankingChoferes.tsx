'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Star, User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChoferRanking {
  id: string
  nombre: string
  apellido: string
  calificacion: number
  total_viajes: number
  estado_laboral: string
  foto_perfil_url: string | null
}

export function RankingChoferes() {
  const [data, setData] = useState<ChoferRanking[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/tenant/dashboard/ranking')
        const json = await res.json()
        setData(json)
      } catch (error) {
        console.error('Error fetching ranking:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>🏆 Ranking de Choferes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>🏆 Ranking de Choferes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No hay datos de choferes disponibles
          </div>
        </CardContent>
      </Card>
    )
  }

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'libre':
        return 'bg-green-500'
      case 'ocupado':
        return 'bg-yellow-500'
      case 'inactivo':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getEstadoText = (estado: string) => {
    switch (estado) {
      case 'libre':
        return 'Libre'
      case 'ocupado':
        return 'Ocupado'
      case 'inactivo':
        return 'Inactivo'
      default:
        return estado
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>🏆 Ranking de Choferes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((chofer, index) => (
            <div
              key={chofer.id}
              className={cn(
                'flex items-center gap-4 p-3 rounded-lg transition-colors',
                index === 0 ? 'bg-yellow-50 dark:bg-yellow-950/20' :
                index === 1 ? 'bg-gray-50 dark:bg-gray-800/50' :
                index === 2 ? 'bg-amber-50 dark:bg-amber-950/20' :
                'hover:bg-muted'
              )}
            >
              {/* Posición */}
              <div className="flex-shrink-0 w-8 text-center font-bold text-sm">
                {index === 0 && '🥇'}
                {index === 1 && '🥈'}
                {index === 2 && '🥉'}
                {index > 2 && `#${index + 1}`}
              </div>

              {/* Avatar */}
              <div className="flex-shrink-0">
                {chofer.foto_perfil_url ? (
                  <img
                    src={chofer.foto_perfil_url}
                    alt={`${chofer.nombre} ${chofer.apellido}`}
                    className="h-10 w-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">
                  {chofer.nombre} {chofer.apellido}
                </p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>{chofer.total_viajes} viajes</span>
                  <span>•</span>
                  <Badge className={cn('text-xs', getEstadoColor(chofer.estado_laboral))}>
                    {getEstadoText(chofer.estado_laboral)}
                  </Badge>
                </div>
              </div>

              {/* Calificación */}
              <div className="flex-shrink-0 flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="font-bold">{chofer.calificacion.toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}