'use client'

import { Badge } from '@/components/ui/badge'
import { Smartphone, Gauge } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TripSourceBadgeProps {
  fuente: 'app' | 'taximetro'
  className?: string
}

export function TripSourceBadge({ fuente, className }: TripSourceBadgeProps) {
  const config = {
    app: {
      color: 'bg-green-500 hover:bg-green-600',
      icon: Smartphone,
      label: 'App',
    },
    taximetro: {
      color: 'bg-amber-500 hover:bg-amber-600',
      icon: Gauge,
      label: 'Taxímetro',
    },
  }

  const { color, icon: Icon, label } = config[fuente]

  return (
    <Badge className={cn(color, 'text-white text-xs', className)}>
      <span className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {label}
      </span>
    </Badge>
  )
}