'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { MapPicker } from '@/components/operativo/MapPicker'
import { MapPin, Loader2 } from 'lucide-react'
import api from '@/lib/api/client'

interface ModalVerRutaProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  origen?: { lat: number; lng: number; direccion: string } | null
  destino?: { lat: number; lng: number; direccion: string } | null
  codigo?: string
  viajeId?: string
}

export function ModalVerRuta({
  open,
  onOpenChange,
  origen,
  destino,
  codigo,
  viajeId,
}: ModalVerRutaProps) {
  const [gpsPoints, setGpsPoints] = useState<Array<{ lat: number; lng: number }>>([])
  const [loadingGps, setLoadingGps] = useState(false)

  useEffect(() => {
    if (open && viajeId) {
      setLoadingGps(true)
      api.get(`/api/viajes/${viajeId}/gps`)
        .then((res) => {
          const puntos = res.data?.puntos || []
          setGpsPoints(puntos.map((p: any) => ({ lat: p.lat, lng: p.lng })))
        })
        .catch((err) => {
          console.error('Error cargando GPS:', err)
          setGpsPoints([])
        })
        .finally(() => setLoadingGps(false))
    } else {
      setGpsPoints([])
    }
  }, [open, viajeId])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Ruta del viaje {codigo ? `#${codigo}` : ''}
            {loadingGps && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          {origen && destino ? (
            <MapPicker
              origin={origen ? { lat: origen.lat, lng: origen.lng, address: origen.direccion } : null}
              destination={destino ? { lat: destino.lat, lng: destino.lng, address: destino.direccion } : null}
              gpsPoints={gpsPoints}
              height="100%"
              draggable={false}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              No hay coordenadas disponibles para este viaje
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}