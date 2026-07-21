'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, MapPin, Crosshair, Building2, Phone, Mail } from 'lucide-react'
import { toast } from 'sonner'

declare global {
  interface Window {
    google: any
    initMap: () => void
  }
}

export default function RegistroComercioPage() {
  const router = useRouter()
  const mapRef = useRef<HTMLDivElement>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number; address: string } | null>(null)
  
  const [formData, setFormData] = useState({
    nombre: '',
    rubro: '',
    direccion: '',
    latitud: '',
    longitud: '',
    email_contacto: '',
    telefono: '',
  })

  // Cargar Google Maps
  useEffect(() => {
    if (!window.google) {
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places&callback=initMap`
      script.async = true
      script.defer = true
      
      window.initMap = () => {
        if (mapRef.current) {
          const map = new window.google.maps.Map(mapRef.current, {
            center: { lat: -34.6037, lng: -58.3816 },
            zoom: 13,
          })
          
          const marker = new window.google.maps.Marker({
            position: { lat: -34.6037, lng: -58.3816 },
            map: map,
            draggable: true,
          })
          
          map.addListener('click', (e: any) => {
            const lat = e.latLng.lat()
            const lng = e.latLng.lng()
            marker.setPosition({ lat, lng })
            updateLocation(lat, lng)
          })
          
          marker.addListener('dragend', (e: any) => {
            const lat = e.latLng.lat()
            const lng = e.latLng.lng()
            updateLocation(lat, lng)
          })
          
          setMapLoaded(true)
        }
      }
      
      document.head.appendChild(script)
    }
  }, [])

  const updateLocation = async (lat: number, lng: number) => {
    setFormData(prev => ({
      ...prev,
      latitud: lat.toString(),
      longitud: lng.toString(),
    }))
    
    if (window.google) {
      const geocoder = new window.google.maps.Geocoder()
      geocoder.geocode({ location: { lat, lng } }, (results: any, status: any) => {
        if (status === 'OK' && results[0]) {
          const address = results[0].formatted_address
          setSelectedLocation({ lat, lng, address })
          setFormData(prev => ({ ...prev, direccion: address }))
        }
      })
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          updateLocation(latitude, longitude)
        },
        () => toast.error('No se pudo obtener tu ubicación')
      )
    } else {
      toast.error('Geolocalización no soportada')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.nombre || !formData.direccion || !formData.latitud || !formData.longitud) {
      toast.error('Complete los campos obligatorios')
      return
    }
    
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/comercio/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: formData.nombre,
          rubro: formData.rubro,
          direccion: formData.direccion,
          latitud: parseFloat(formData.latitud),
          longitud: parseFloat(formData.longitud),
          email_contacto: formData.email_contacto,
          telefono: formData.telefono,
        }),
      })
      
      const data = await response.json()
      
      if (response.ok) {
        router.push(`/qr/exito/${data.id}`)
      } else {
        toast.error(data.detail || 'Error al registrar el comercio')
      }
    } catch (error) {
      toast.error('Error al conectar con el servidor')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container max-w-5xl py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Generá tu código QR</h1>
        <p className="text-muted-foreground mt-2">
          Registrá tu negocio y obtené un código QR para que tus clientes soliciten taxis desde tu ubicación
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Formulario */}
        <Card>
          <CardHeader>
            <CardTitle>Datos del negocio</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Nombre del negocio *
                </Label>
                <Input
                  placeholder="Ej: Restaurant El Tucumano"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label>Rubro</Label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={formData.rubro}
                  onChange={(e) => setFormData({ ...formData, rubro: e.target.value })}
                >
                  <option value="">Seleccionar rubro</option>
                  <option value="restaurante">Restaurante / Bar</option>
                  <option value="hotel">Hotel / Hospedaje</option>
                  <option value="comercio">Comercio / Tienda</option>
                  <option value="oficina">Oficina / Empresa</option>
                  <option value="turismo">Punto turístico</option>
                  <option value="evento">Salón de eventos</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Teléfono
                </Label>
                <Input
                  placeholder="3811234567"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email de contacto
                </Label>
                <Input
                  type="email"
                  placeholder="contacto@negocio.com"
                  value={formData.email_contacto}
                  onChange={(e) => setFormData({ ...formData, email_contacto: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Dirección *
                </Label>
                <Input
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                  placeholder="Selecciona una ubicación en el mapa"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Latitud *</Label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={formData.latitud}
                    onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Longitud *</Label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={formData.longitud}
                    onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generando QR...
                  </>
                ) : (
                  'Generar código QR'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Mapa */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Ubicación en el mapa</CardTitle>
            <Button type="button" size="sm" variant="outline" onClick={getCurrentLocation}>
              <Crosshair className="h-4 w-4 mr-2" />
              Mi ubicación
            </Button>
          </CardHeader>
          <CardContent>
            {!mapLoaded ? (
              <div className="flex h-[350px] items-center justify-center rounded-lg border bg-muted/50">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                <div ref={mapRef} className="h-[350px] rounded-lg border" />
                {selectedLocation && (
                  <div className="mt-4 p-3 rounded-lg bg-green-50 text-sm">
                    <p className="font-medium text-green-800">✓ Ubicación seleccionada</p>
                    <p className="text-xs text-green-700 mt-1 break-all">{selectedLocation.address}</p>
                  </div>
                )}
                <p className="text-xs text-muted-foreground mt-3">
                  💡 Haz clic en el mapa o arrastra el marcador para seleccionar la ubicación exacta
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}