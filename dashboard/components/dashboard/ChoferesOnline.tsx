'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { controlBaseAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { MapPin, Star } from 'lucide-react'

interface ChoferOnline {
  id: string
  nombre: string
  patente: string
  latitud: number
  longitud: number
  estado: 'libre' | 'ocupado'
  calificacion: number
  foto?: string
}

export function ChoferesOnline() {
  const { status } = useSession()

  const { data: choferes } = useQuery({
    queryKey: ['choferes-online'],
    queryFn: controlBaseAPI.getChoferesOnline,
    refetchInterval: 15000,
    enabled: status === 'authenticated', // ⬅️ NO ejecutar hasta tener sesión
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 401) return false
      return failureCount < 3
    },
  })

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Choferes Online</span>
          <Badge variant="secondary" className="bg-green-500 text-white">
            {choferes?.length || 0} activos
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="max-h-[400px] overflow-y-auto space-y-3">
        {choferes?.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No hay choferes online
          </p>
        ) : (
          choferes?.map((chofer: ChoferOnline) => (
            <div
              key={chofer.id}
              className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 transition-colors"
            >
              <Avatar>
                <AvatarImage src={chofer.foto} />
                <AvatarFallback className="bg-primary/10 text-primary">
                  {getInitials(chofer.nombre)}
                </AvatarFallback>
              </Avatar>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium truncate">{chofer.nombre}</p>
                  <Badge
                    variant="outline"
                    className={chofer.estado === 'libre' ? 'text-green-500' : 'text-orange-500'}
                  >
                    {chofer.estado === 'libre' ? 'Libre' : 'Ocupado'}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{chofer.patente}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center gap-0.5">
                    <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                    <span className="text-xs">{chofer.calificacion.toFixed(1)}</span>
                  </div>
                  <div className="flex items-center gap-0.5 text-xs text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    <span>En movimiento</span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}