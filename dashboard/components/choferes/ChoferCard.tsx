'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Star, Car, User, Eye, Edit2, MoreHorizontal, Phone, Mail } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface ChoferCardProps {
  chofer: {
    id: string
    nombre: string
    apellido: string
    email: string
    telefono: string
    estado_laboral: string
    estado_aprobacion: string
    calificacion_promedio: number
    total_viajes: number
    vehiculo?: {
      patente: string
      marca: string
      modelo: string
    }
    foto_perfil_url?: string
    propietario?: string
  }
  onAssignVehicle?: (id: string) => void
  onChangeStatus?: (id: string) => void
}

export function ChoferCard({ chofer, onAssignVehicle, onChangeStatus }: ChoferCardProps) {
  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'libre': return 'bg-green-100 text-green-800 border-green-200'
      case 'ocupado': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'inactivo': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getEstadoLabel = (estado: string) => {
    switch (estado) {
      case 'libre': return '🟢 Libre'
      case 'ocupado': return '🟡 Ocupado'
      case 'inactivo': return '🔴 Inactivo'
      default: return estado
    }
  }

  const getAprobacionBadge = (estado: string) => {
    switch (estado) {
      case 'aprobado': return <Badge className="bg-green-500">Aprobado</Badge>
      case 'pendiente': return <Badge className="bg-yellow-500">Pendiente</Badge>
      case 'rechazado': return <Badge className="bg-red-500">Rechazado</Badge>
      default: return null
    }
  }

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <CardContent className="p-0">
        <div className="p-4">
          <div className="flex items-start gap-4">
            {/* Avatar */}
            <div className="flex-shrink-0">
              {chofer.foto_perfil_url ? (
                <img
                  src={chofer.foto_perfil_url}
                  alt={chofer.nombre}
                  className="w-14 h-14 rounded-full object-cover border-2 border-muted"
                />
              ) : (
                <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-7 w-7 text-primary" />
                </div>
              )}
            </div>

            {/* Info principal */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-base truncate">
                  {chofer.nombre} {chofer.apellido}
                </h3>
                {getAprobacionBadge(chofer.estado_aprobacion)}
              </div>
              
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="h-3 w-3" />
                <span className="truncate">{chofer.email}</span>
              </div>
              
              {chofer.telefono && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone className="h-3 w-3" />
                  <span>{chofer.telefono}</span>
                </div>
              )}
            </div>

            {/* Estado */}
            <div className="flex-shrink-0">
              <Badge className={cn('border', getEstadoColor(chofer.estado_laboral))}>
                {getEstadoLabel(chofer.estado_laboral)}
              </Badge>
            </div>
          </div>

          {/* Detalles */}
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              <span className="font-medium">{chofer.calificacion_promedio?.toFixed(1) || 'N/A'}</span>
              <span className="text-xs">({chofer.total_viajes || 0} viajes)</span>
            </div>
            {chofer.vehiculo && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Car className="h-4 w-4" />
                <span>{chofer.vehiculo.patente}</span>
                <span className="text-xs">({chofer.vehiculo.marca} {chofer.vehiculo.modelo})</span>
              </div>
            )}
            {!chofer.vehiculo && (
              <div className="text-xs text-red-500">⚠️ Sin vehículo asignado</div>
            )}
            {chofer.propietario && (
              <div className="text-xs text-muted-foreground col-span-2">
                Propietario: {chofer.propietario}
              </div>
            )}
          </div>

          {/* Acciones */}
          <div className="mt-3 pt-3 border-t flex items-center justify-between">
            <div className="flex gap-1">
              <Button asChild variant="ghost" size="sm">
                <Link href={`/choferes/${chofer.id}`}>
                  <Eye className="h-4 w-4 mr-1" />
                  Ver
                </Link>
              </Button>
              <Button asChild variant="ghost" size="sm">
                <Link href={`/choferes/${chofer.id}/editar`}>
                  <Edit2 className="h-4 w-4 mr-1" />
                  Editar
                </Link>
              </Button>
            </div>
            <div className="flex gap-1">
              {!chofer.vehiculo && onAssignVehicle && (
                <Button variant="outline" size="sm" onClick={() => onAssignVehicle(chofer.id)}>
                  Asignar vehículo
                </Button>
              )}
              {onChangeStatus && (
                <Button variant="outline" size="sm" onClick={() => onChangeStatus(chofer.id)}>
                  {chofer.estado_laboral === 'inactivo' ? 'Activar' : 'Desactivar'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}