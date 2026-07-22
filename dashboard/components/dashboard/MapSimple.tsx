'use client'
import { useEffect, useRef, useState, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { controlBaseAPI } from '@/lib/api'

// Coordenadas de San Miguel de Tucumán
const CENTER = { lat: -26.830458141771548, lng: -65.20383899799425 }

interface ChoferOnline {
  id: string
  usuario_id: string
  nombre: string
  latitud: number | null
  longitud: number | null
  estado: string
  calificacion: number
  patente: string
  modelo: string
  total_viajes: number
  foto_perfil_url?: string | null
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

export function MapSimple() {
  console.log('🗺️ [MapSimple] Componente renderizado')
  
  // ✅ CORRECCIÓN: Agregar | null al tipo genérico
  const mapContainer = useRef<HTMLDivElement | null>(null)
  const map = useRef<google.maps.Map | null>(null)
  const markers = useRef<google.maps.Marker[]>([])
  const infoWindows = useRef<google.maps.InfoWindow[]>([])
  
  const { status } = useSession()
  const [choferes, setChoferes] = useState<ChoferOnline[]>([])
  const [loading, setLoading] = useState(true)
  const [containerReady, setContainerReady] = useState(false)
  const [scriptReady, setScriptReady] = useState(false)

  // Cargar Google Maps
  useEffect(() => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
    if (!apiKey) {
      console.error('❌ Google Maps API Key no configurada')
      return
    }
    loadGoogleMaps(apiKey).then(() => {
      console.log('✅ Google Maps API cargada')
      setScriptReady(true)
    })
  }, [])

  // Obtener choferes online
  useEffect(() => {
    if (status !== 'authenticated') return

    const fetchChoferes = async () => {
      try {
        const data = await controlBaseAPI.getChoferesOnline()
        console.log('📍 Choferes obtenidos:', data.length)
        setChoferes(data || [])
      } catch (error) {
        console.error('Error fetching choferes online:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchChoferes()
    const interval = setInterval(fetchChoferes, 10000)
    return () => clearInterval(interval)
  }, [status])

  const setMapContainerRef = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      console.log('🗺️ Contenedor del mapa montado en el DOM')
      node.style.height = '500px'
      node.style.width = '100%'
      node.style.minHeight = '500px'
      node.style.display = 'block'
      node.style.backgroundColor = '#e8e8e8'
      mapContainer.current = node
      setContainerReady(true)
    } else {
      console.log('🗺️ Contenedor del mapa desmontado')
      mapContainer.current = null
      setContainerReady(false)
    }
  }, [])

  // Inicializar mapa
  useEffect(() => {
    if (!containerReady) {
      console.log('⏳ Esperando contenedor del mapa...')
      return
    }
    if (!scriptReady) {
      console.log('⏳ Esperando Google Maps...')
      return
    }
    if (!mapContainer.current) {
      console.log('⚠️ mapContainer.current es null')
      return
    }
    if (map.current) {
      console.log('⚠️ El mapa ya está inicializado')
      return
    }

    console.log('🗺️ Inicializando mapa de Google Maps...')
    console.log('🗺️ Contenedor:', mapContainer.current)

    try {
      map.current = new google.maps.Map(mapContainer.current, {
        center: CENTER,
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
      console.log('✅ Mapa inicializado correctamente')
    } catch (error) {
      console.error('❌ Error al crear el mapa:', error)
    }

    return () => {
      map.current = null
    }
  }, [containerReady, scriptReady])

  // Actualizar marcadores
  useEffect(() => {
    if (!map.current || !containerReady || !scriptReady) return

    const mapInstance = map.current

    console.log(`📍 Actualizando ${choferes.length} choferes...`)

    // Cerrar y eliminar InfoWindows viejos
    infoWindows.current.forEach(iw => iw.close())
    infoWindows.current = []

    // Eliminar marcadores viejos
    markers.current.forEach(marker => marker.setMap(null))
    markers.current = []

    // Agregar nuevos marcadores
    let count = 0
    choferes.forEach((chofer) => {
      if (!chofer.latitud || !chofer.longitud) return
      count++

      const position = {
        lat: Number(chofer.latitud),
        lng: Number(chofer.longitud),
      }

      const isLibre = chofer.estado === 'libre'
      const color = isLibre ? '#22c55e' : '#eab308'

      // Marcador con círculo de color + ícono de auto
      const marker = new google.maps.Marker({
        position,
        map: mapInstance,
        title: chofer.nombre,
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

      // Foto de perfil o avatar
      const profileImage = chofer.foto_perfil_url 
        ? `<img src="${chofer.foto_perfil_url}" alt="${chofer.nombre}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; border: 2px solid #e5e7eb; flex-shrink: 0;" />`
        : `<div style="width: 48px; height: 48px; border-radius: 50%; background: #e5e7eb; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0;">👤</div>`

      // Badge de estado
      const estadoBadge = isLibre
        ? '<span style="background: #dcfce7; color: #166534; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 500;">🟢 Libre</span>'
        : '<span style="background: #fef9c3; color: #854d0e; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 500;">🟡 Ocupado</span>'

      const htmlContent = `
        <div style="padding: 8px; min-width: 220px; max-width: 280px; font-family: system-ui, -apple-system, sans-serif;">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
            ${profileImage}
            <div>
              <div style="font-weight: 600; font-size: 15px; color: #111827;">${chofer.nombre}</div>
              <div style="font-size: 12px; color: #6b7280; display: flex; align-items: center; gap: 4px;">
                ⭐ ${chofer.calificacion.toFixed(1)}
                <span style="color: #9ca3af;">·</span>
                ${chofer.total_viajes || 0} viajes
              </div>
            </div>
          </div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            ${estadoBadge}
            <span style="background: #f3f4f6; padding: 2px 10px; border-radius: 9999px; font-size: 11px; color: #374151;">🚗 ${chofer.patente || 'Sin vehículo'}</span>
          </div>
          ${chofer.modelo ? `<div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">📐 ${chofer.modelo}</div>` : ''}
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #f3f4f6; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 10px; color: #9ca3af;">ID: ${chofer.id.slice(0, 8)}</span>
            <span style="font-size: 10px; color: #9ca3af;">${isLibre ? '🟢 Disponible' : '🟡 En viaje'}</span>
          </div>
        </div>
      `

      const infoWindow = new google.maps.InfoWindow({
        content: htmlContent,
        maxWidth: 300,
      })

      marker.addListener('click', () => {
        // Cerrar todos los InfoWindows abiertos
        infoWindows.current.forEach(iw => iw.close())
        infoWindows.current = []
        infoWindow.open(mapInstance, marker)
        infoWindows.current.push(infoWindow)
      })

      markers.current.push(marker)
    })

    console.log(`✅ ${count} marcadores agregados al mapa`)
  }, [choferes, containerReady, scriptReady])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-muted/20" style={{ minHeight: '500px' }}>
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto" />
          <p className="mt-2 text-sm text-muted-foreground">Cargando choferes...</p>
        </div>
      </div>
    )
  }

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
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#22c55e' }} />
            <span>Libre</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#eab308' }} />
            <span>Ocupado</span>
          </div>
          <div className="text-muted-foreground">
            {choferes.filter(c => c.estado === 'libre').length} libres / {choferes.length} total
          </div>
        </div>
      </div>
    </div>
  )
}