'use client'

import { useEffect, useRef } from 'react'
import { Loader2 } from 'lucide-react'

interface MapViewProps {
  origen: { lat: number; lng: number; direccion: string }
  destino: { lat: number; lng: number; direccion: string }
}

export function RouteMap({ origen, destino }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const leafletLoaded = useRef(false)

  useEffect(() => {
    if (!origen?.lat || !origen?.lng || !destino?.lat || !destino?.lng) {
      return
    }

    const initMap = async () => {
      const L = await import('leaflet')
      
      if (leafletLoaded.current) return
      leafletLoaded.current = true

      // Crear mapa
      const map = L.map(mapRef.current!).setView([origen.lat, origen.lng], 13)

      // Tile layer (mapa base)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
      }).addTo(map)

      // Icono personalizado
      const greenIcon = L.divIcon({
        className: 'custom-div-icon',
        html: '<div style="background-color:#22c55e; width:12px; height:12px; border-radius:50%; border:2px solid white;"></div>',
        iconSize: [12, 12],
        popupAnchor: [0, -6]
      })

      const redIcon = L.divIcon({
        className: 'custom-div-icon',
        html: '<div style="background-color:#ef4444; width:12px; height:12px; border-radius:50%; border:2px solid white;"></div>',
        iconSize: [12, 12],
        popupAnchor: [0, -6]
      })

      // Marcadores
      L.marker([origen.lat, origen.lng], { icon: greenIcon })
        .addTo(map)
        .bindPopup(`<b>Origen</b><br/>${origen.direccion}`)

      L.marker([destino.lat, destino.lng], { icon: redIcon })
        .addTo(map)
        .bindPopup(`<b>Destino</b><br/>${destino.direccion}`)

      // Dibujar línea entre puntos
      L.polyline([[origen.lat, origen.lng], [destino.lat, destino.lng]], {
        color: '#3b82f6',
        weight: 4,
        opacity: 0.7
      }).addTo(map)

      // Ajustar vista para mostrar ambos puntos
      const bounds = L.latLngBounds(
        [origen.lat, origen.lng],
        [destino.lat, destino.lng]
      )
      map.fitBounds(bounds, { padding: [50, 50] })
    }

    initMap()

    return () => {
      if (leafletLoaded.current && mapRef.current) {
        leafletLoaded.current = false
      }
    }
  }, [origen, destino])

  if (!origen?.lat || !origen?.lng || !destino?.lat || !destino?.lng) {
    return (
      <div className="flex h-[400px] items-center justify-center rounded-lg border bg-muted/50">
        <p className="text-muted-foreground">No hay coordenadas disponibles para mostrar la ruta</p>
      </div>
    )
  }

  return <div ref={mapRef} className="h-[400px] w-full rounded-lg overflow-hidden bg-muted/20" />
}