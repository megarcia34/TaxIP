'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2, CheckCircle, MapPin, Navigation, DollarSign } from 'lucide-react'
import Link from 'next/link'
import { apiClient } from '@/lib/api'

interface ViajeInfo {
  id: string
  estado: string
  direccion_origen: string
  direccion_destino: string
  precio_estimado: number
  chofer_nombre?: string
  chofer_telefono?: string
  patente?: string
}

export default function ConfirmacionPage() {
  const params = useParams()
  const router = useRouter()
  const viajeId = params.id as string
  const [viaje, setViaje] = useState<ViajeInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [asignado, setAsignado] = useState(false)
  
  useEffect(() => {
    const checkViajeStatus = async () => {
      try {
        const response = await apiClient.get(`/api/viajes/${viajeId}/estado`)
        const data = response.data
        setViaje(data)
        
        if (data.chofer_id && data.estado !== 'pendiente') {
          setAsignado(true)
        }
        
        setIsLoading(false)
      } catch (error) {
        console.error('Error:', error)
        setIsLoading(false)
      }
    }
    
    checkViajeStatus()
    
    // Actualizar cada 5 segundos
    const interval = setInterval(checkViajeStatus, 5000)
    return () => clearInterval(interval)
  }, [viajeId])
  
  if (isLoading) {
    return (
      <div className="container max-w-2xl py-8">
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </CardContent>
        </Card>
      </div>
    )
  }
  
  return (
    <div className="container max-w-2xl py-8">
      <Card>
        <CardHeader className="text-center">
          <div className="mx-auto mb-4">
            {asignado ? (
              <CheckCircle className="h-16 w-16 text-green-500" />
            ) : (
              <Loader2 className="h-16 w-16 animate-spin text-primary" />
            )}
          </div>
          <CardTitle className="text-xl">
            {asignado ? '¡Taxi asignado!' : 'Buscando el taxi más cercano...'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {viaje && (
            <>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-green-500" />
                  Origen
                </p>
                <p className="font-medium">{viaje.direccion_origen}</p>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <Navigation className="h-4 w-4 text-red-500" />
                  Destino
                </p>
                <p className="font-medium">{viaje.direccion_destino}</p>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-yellow-500" />
                  Precio estimado
                </p>
                <p className="font-medium text-lg">${viaje.precio_estimado}</p>
              </div>
              
              {asignado && viaje.chofer_nombre && (
                <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg space-y-2">
                  <p className="font-medium text-green-800 dark:text-green-300">
                    🚗 Conductor asignado
                  </p>
                  <p className="text-sm">
                    <strong>Nombre:</strong> {viaje.chofer_nombre}
                  </p>
                  {viaje.patente && (
                    <p className="text-sm">
                      <strong>Vehículo:</strong> {viaje.patente}
                    </p>
                  )}
                </div>
              )}
              
              <div className="flex gap-4">
                <Link href="/" className="flex-1">
                  <Button variant="outline" className="w-full">
                    Nueva solicitud
                  </Button>
                </Link>
                <Link href={`/reservar/tracking/${viajeId}`} className="flex-1">
                  <Button className="w-full">
                    Ver seguimiento
                  </Button>
                </Link>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}