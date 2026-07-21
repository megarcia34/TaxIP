'use client'

import { useEffect } from 'react'

export function GoogleMapsLoader() {
  useEffect(() => {
    // Si ya está cargado, no hacer nada
    if (window.google) return

    console.log('🔄 Cargando Google Maps API...')

    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places,geometry&language=es`
    script.async = true
    script.defer = true
    script.id = 'google-maps-script'

    script.onload = () => {
      console.log('✅ Google Maps API cargada correctamente')
    }

    script.onerror = () => {
      console.error('❌ Error al cargar Google Maps API')
    }

    document.head.appendChild(script)

    return () => {
      const scriptElement = document.getElementById('google-maps-script')
      if (scriptElement) {
        scriptElement.remove()
        console.log('🗑️ Script de Google Maps removido')
      }
    }
  }, [])

  return null
}