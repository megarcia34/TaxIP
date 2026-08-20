'use client'

import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { Clock, CheckCircle, Loader2, XCircle, AlertCircle, Calendar } from 'lucide-react'

interface TripStatusBadgeProps {
  estado: 'pendiente' | 'aceptado' | 'en_curso' | 'finalizado' | 'cancelado' | 'programada'
  size?: 'sm' | 'default'
  className?: string
}

const estadoConfig = {
  pendiente: {
    color: 'bg-yellow-500 hover:bg-yellow-600',
    icon: Clock,
    label: 'Pendiente',
  },
  aceptado: {
    color: 'bg-blue-500 hover:bg-blue-600',
    icon: CheckCircle,
    label: 'Aceptado',
  },
  en_curso: {
    color: 'bg-purple-500 hover:bg-purple-600',
    icon: Loader2,
    label: 'En curso',
  },
  finalizado: {
    color: 'bg-green-500 hover:bg-green-600',
    icon: CheckCircle,
    label: 'Finalizado',
  },
  cancelado: {
    color: 'bg-red-500 hover:bg-red-600',
    icon: XCircle,
    label: 'Cancelado',
  },
  programada: {
    color: 'bg-orange-500 hover:bg-orange-600',
    icon: Calendar,
    label: 'Programada',
  },
}

export function TripStatusBadge({ estado, size = 'default', className }: TripStatusBadgeProps) {
  const config = estadoConfig[estado]
  const Icon = config.icon

  return (
    <Badge className={cn(config.color, 'text-white', className)}>
      <span className="flex items-center gap-1">
        <Icon className={cn('h-3 w-3', estado === 'en_curso' && 'animate-spin')} />
        {config.label}
      </span>
    </Badge>
  )
}