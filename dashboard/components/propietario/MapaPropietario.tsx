'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { propietarioVehiculosAPI } from '@/lib/api'

// Coordenadas de San Miguel de Tucumán
const CENTER = { lat: -26.830458141771548, lng: -65.20383899799425 }

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  estado_laboral: string
  chofer_asignado: string | null
}

interface Ubicacion {
  vehiculo_id: string
  ubicacion: {
    latitud: number
    longitud: number
    ultima_actualizacion: string
  }
  conductor: {
    email: string
    nombre: string
  }
  estado: {
    laboral: string
    calificacion_promedio: number
  }
  viaje_actual: {
    id: string
    origen: string
    destino: string
    inicio: string
  } | null
}

interface MapaPropietarioProps {
  vehiculos: Vehiculo[]
  ubicaciones: Record<string, Ubicacion>
  loading?: boolean
}

// Cargar Google Maps (solo una vez)
let googleMapsLoaded = false
let googleMapsLoading = false
let googleMapsCallbacks: (() => void)[] = []

const loadGoogleMaps = (apiKey: string): Promise<void> => {
  return new Promise((resolve) => {
    if (googleMapsLoaded) {
      resolve()
      return
    }
    if (googleMapsLoading) {
      googleMapsCallbacks.push(resolve)
      return
    }
    googleMapsLoading = true
    googleMapsCallbacks.push(resolve)

    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`
    script.async = true
    script.defer = true
    script.onload = () => {
      console.log('✅ Google Maps API cargada correctamente')
      googleMapsLoaded = true
      googleMapsLoading = false
      googleMapsCallbacks.forEach(cb => cb())
      googleMapsCallbacks = []
    }
    script.onerror = () => {
      console.error('❌ Error al cargar Google Maps API')
      googleMapsLoading = false
    }
    document.head.appendChild(script)
  })
}

export function MapaPropietario({ vehiculos, ubicaciones, loading = false }: MapaPropietarioProps) {
  const mapContainer = useRef<HTMLDivElement | null>(null)
  const map = useRef<google.maps.Map | null>(null)
  const markers = useRef<google.maps.Marker[]>([])
  const infoWindows = useRef<google.maps.InfoWindow[]>([])
  
  const [containerReady, setContainerReady] = useState(false)
  const [scriptReady, setScriptReady] = useState(false)
  const [bounds, setBounds] = useState<google.maps.LatLngBounds | null>(null)

  // Cargar Google Maps
  useEffect(() => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
    if (!apiKey) {
      console.error('❌ Google Maps API Key no configurada')
      return
    }
    loadGoogleMaps(apiKey).then(() => {
      console.log('✅ Google Maps API cargada para propietarios')
      setScriptReady(true)
    })
  }, [])

  const setMapContainerRef = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      node.style.height = '500px'
      node.style.width = '100%'
      node.style.minHeight = '500px'
      node.style.display = 'block'
      node.style.backgroundColor = '#e8e8e8'
      mapContainer.current = node
      setContainerReady(true)
    } else {
      mapContainer.current = null
      setContainerReady(false)
    }
  }, [])

  // Inicializar mapa
  useEffect(() => {
    if (!containerReady || !scriptReady || map.current) return

    try {
      // Calcular centro basado en vehículos con GPS
      let center = CENTER
      const vehiculosConGps = vehiculos.filter(v => {
        const u = ubicaciones[v.id]
        return u && u.ubicacion.latitud !== 0 && u.ubicacion.longitud !== 0
      })

      if (vehiculosConGps.length > 0) {
        const total = vehiculosConGps.length
        const lat = vehiculosConGps.reduce((sum, v) => sum + (ubicaciones[v.id]?.ubicacion.latitud || 0), 0) / total
        const lng = vehiculosConGps.reduce((sum, v) => sum + (ubicaciones[v.id]?.ubicacion.longitud || 0), 0) / total
        center = { lat, lng }
      }

      map.current = new google.maps.Map(mapContainer.current!, {
        center,
        zoom: 13,
        mapTypeId: 'roadmap',
        mapTypeControl: false,
        fullscreenControl: false,
        streetViewControl: false,
        zoomControl: true,
        zoomControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP,
        },
      })
      console.log('✅ Mapa de propietarios inicializado')
    } catch (error) {
      console.error('❌ Error al crear el mapa:', error)
    }

    return () => {
      map.current = null
    }
  }, [containerReady, scriptReady, vehiculos, ubicaciones])

  // Actualizar marcadores
  useEffect(() => {
    if (!map.current || !containerReady || !scriptReady) return

    const mapInstance = map.current

    // Cerrar InfoWindows viejos
    infoWindows.current.forEach(iw => iw.close())
    infoWindows.current = []

    // Eliminar marcadores viejos
    markers.current.forEach(marker => marker.setMap(null))
    markers.current = []

    // Filtrar vehículos con GPS
    const vehiculosConGps = vehiculos.filter(v => {
      const u = ubicaciones[v.id]
      return u && u.ubicacion.latitud !== 0 && u.ubicacion.longitud !== 0
    })

    if (vehiculosConGps.length === 0) {
      console.log('⚠️ No hay vehículos con GPS disponible')
      return
    }

    // Crear bounds para ajustar el zoom
    const newBounds = new google.maps.LatLngBounds()

    // Agregar nuevos marcadores
    vehiculosConGps.forEach((vehiculo) => {
      const ubicacion = ubicaciones[vehiculo.id]
      if (!ubicacion) return

      const position = {
        lat: ubicacion.ubicacion.latitud,
        lng: ubicacion.ubicacion.longitud,
      }

      newBounds.extend(position)

      const estado = ubicacion.estado?.laboral || 'desconocido'
      const color = estado === 'libre' ? '#22c55e' 
        : estado === 'en_viaje' ? '#eab308' 
        : estado === 'ocupado' ? '#ef4444' 
        : '#6b7280'

      // Crear marcador con animación
      const marker = new google.maps.Marker({
        position,
        map: mapInstance,
        title: vehiculo.patente,
        animation: google.maps.Animation.DROP,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          fillColor: color,
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 3,
          scale: 14,
        },
        label: {
          text: '🚗',
          color: '#ffffff',
          fontSize: '10px',
          fontWeight: 'bold',
        },
      })

      const estadoLabel = estado === 'libre' ? '🟢 Disponible' 
        : estado === 'en_viaje' ? '🟡 En viaje' 
        : estado === 'ocupado' ? '🔴 Ocupado' 
        : '⚪ Sin datos'

      // Última actualización
      const lastUpdate = ubicacion.ubicacion.ultima_actualizacion 
        ? new Date(ubicacion.ubicacion.ultima_actualizacion).toLocaleTimeString() 
        : 'N/A'

      const htmlContent = `
        <div style="padding: 8px; min-width: 220px; max-width: 280px; font-family: system-ui, -apple-system, sans-serif;">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
            <div style="width: 48px; height: 48px; border-radius: 50%; background: #e5e7eb; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0;">🚗</div>
            <div>
              <div style="font-weight: 600; font-size: 15px; color: #111827;">${vehiculo.patente}</div>
              <div style="font-size: 12px; color: #6b7280;">${vehiculo.marca} ${vehiculo.modelo} (${vehiculo.anio})</div>
            </div>
          </div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            <span style="background: ${color === '#22c55e' ? '#dcfce7' : color === '#eab308' ? '#fef9c3' : '#f3f4f6'}; color: ${color === '#22c55e' ? '#166534' : color === '#eab308' ? '#854d0e' : '#374151'}; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 500;">
              ${estadoLabel}
            </span>
          </div>
          ${ubicacion.conductor?.nombre ? `<div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">👤 ${ubicacion.conductor.nombre}</div>` : ''}
          ${ubicacion.viaje_actual ? `
            <div style="margin-top: 8px; padding: 8px; background: #fef9c3; border-radius: 8px; font-size: 12px;">
              <div style="font-weight: 500; color: #854d0e;">En viaje</div>
              <div style="color: #6b7280; font-size: 11px;">${ubicacion.viaje_actual.origen || 'N/A'} → ${ubicacion.viaje_actual.destino || 'N/A'}</div>
            </div>
          ` : ''}
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #f3f4f6; font-size: 10px; color: #9ca3af;">
            📍 ${ubicacion.ubicacion.latitud.toFixed(6)}, ${ubicacion.ubicacion.longitud.toFixed(6)}
            <br />🔄 Actualizado: ${lastUpdate}
          </div>
        </div>
      `

      const infoWindow = new google.maps.InfoWindow({
        content: htmlContent,
        maxWidth: 300,
      })

      marker.addListener('click', () => {
        infoWindows.current.forEach(iw => iw.close())
        infoWindows.current = []
        infoWindow.open(mapInstance, marker)
        infoWindows.current.push(infoWindow)
      })

      markers.current.push(marker)
    })

    // Ajustar zoom para mostrar todos los vehículos
    if (vehiculosConGps.length > 1 && newBounds) {
        mapInstance.fitBounds(newBounds, { padding: [50, 50, 50, 50] } as any)
    } else if (vehiculosConGps.length === 1) {
      mapInstance.setZoom(15)
    }

    console.log(`✅ ${vehiculosConGps.length} vehículos en el mapa`)
  }, [vehiculos, ubicaciones, containerReady, scriptReady])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-muted/20" style={{ minHeight: '500px' }}>
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto" />
          <p className="mt-2 text-sm text-muted-foreground">Cargando vehículos...</p>
        </div>
      </div>
    )
  }

  const vehiculosConGps = vehiculos.filter(v => {
    const u = ubicaciones[v.id]
    return u && u.ubicacion.latitud !== 0 && u.ubicacion.longitud !== 0
  })

  return (
    <div className="relative w-full h-full" style={{ minHeight: '500px', width: '100%' }}>
      <div
        ref={setMapContainerRef}
        className="w-full h-full"
        style={{
          height: '500px',
          width: '100%',
          minHeight: '500px',
          backgroundColor: '#e8e8e8',
          position: 'relative',
          display: 'block',
        }}
      />
      
      {/* Leyenda */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3 text-xs">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span>Disponible</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-yellow-500" />
            <span>En viaje</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500" />
            <span>Ocupado</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-gray-400" />
            <span>Sin datos</span>
          </div>
          <div className="text-muted-foreground ml-2 border-l pl-2">
            {vehiculosConGps.length} / {vehiculos.length} con GPS
          </div>
          {vehiculosConGps.length > 0 && (
            <div className="text-muted-foreground border-l pl-2">
              🟢 Actualizado: {new Date().toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Contador de vehículos en el mapa */}
      {vehiculosConGps.length > 0 && (
        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg px-3 py-2 text-sm font-medium">
          🚗 {vehiculosConGps.length} vehículos
        </div>
      )}
    </div>
  )
}