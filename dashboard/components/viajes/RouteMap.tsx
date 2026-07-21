'use client'

import { useEffect, useRef, useState } from 'react'
import { Loader2 } from 'lucide-react'

interface RouteMapProps {
  origen: { lat: number; lng: number; direccion: string }
  destino: { lat: number; lng: number; direccion: string }
}

export function RouteMap({ origen, destino }: RouteMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

  useEffect(() => {
    if (!apiKey) {
      setError('API key de Google Maps no configurada')
      setIsLoading(false)
      return
    }

    if (!origen?.lat || !origen?.lng || !destino?.lat || !destino?.lng) {
      setError('No hay coordenadas disponibles para mostrar la ruta')
      setIsLoading(false)
      return
    }

    // Cargar el script de Google Maps
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&libraries=places`
    script.async = true
    script.defer = true

    window.initMap = () => {
      try {
        const map = new google.maps.Map(mapRef.current!, {
          center: { lat: origen.lat, lng: origen.lng },
          zoom: 13,
        })

        // Marcadores
        new google.maps.Marker({
          position: { lat: origen.lat, lng: origen.lng },
          map: map,
          label: 'O',
          title: origen.direccion,
        })

        new google.maps.Marker({
          position: { lat: destino.lat, lng: destino.lng },
          map: map,
          label: 'D',
          title: destino.direccion,
        })

        // Dibujar ruta
        const directionsService = new google.maps.DirectionsService()
        const directionsRenderer = new google.maps.DirectionsRenderer()

        directionsRenderer.setMap(map)

        directionsService.route(
          {
            origin: { lat: origen.lat, lng: origen.lng },
            destination: { lat: destino.lat, lng: destino.lng },
            travelMode: google.maps.TravelMode.DRIVING,
          },
          (result, status) => {
            if (status === 'OK' && result) {
              directionsRenderer.setDirections(result)
            }
            setIsLoading(false)
          }
        )
      } catch (err) {
        console.error('Error al cargar el mapa:', err)
        setError('Error al cargar el mapa')
        setIsLoading(false)
      }
    }

    document.head.appendChild(script)

    return () => {
      window.initMap = undefined as any
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [origen, destino, apiKey])

  if (error) {
    return (
      <div className="flex h-[400px] items-center justify-center rounded-lg border bg-muted/50">
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center rounded-lg border bg-muted/50">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return <div ref={mapRef} className="h-[400px] w-full rounded-lg overflow-hidden" />
}