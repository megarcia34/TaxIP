'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, MapPin, Building2, Phone, Mail } from 'lucide-react'
import { toast } from 'sonner'
import Script from 'next/script'
import { useEffect } from 'react'

declare global {
  interface Window {
    google: any
    initMap: () => void
  }
}

export default function RegistroComercioPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number; address: string } | null>(null)
  
  const [formData, setFormData] = useState({
    nombre: '',
    rubro: '',
    direccion: '',
    email_contacto: '',
    telefono: '',
  })

  // Cargar mapa de Google
  useEffect(() => {
    const loadGoogleMaps = () => {
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places&callback=initMap`
      script.async = true
      script.defer = true
      
      window.initMap = () => {
        setMapLoaded(true)
      }
      
      document.head.appendChild(script)
    }
    
    loadGoogleMaps()
  }, [])

  // Configurar autocompletado de dirección
  useEffect(() => {
    if (mapLoaded && window.google) {
      const input = document.getElementById('direccion') as HTMLInputElement
      const autocomplete = new window.google.maps.places.Autocomplete(input)
      
      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace()
        if (place.geometry) {
          setSelectedLocation({
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
            address: place.formatted_address
          })
          setFormData(prev => ({ ...prev, direccion: place.formatted_address }))
        }
      })
    }
  }, [mapLoaded])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.nombre) {
      toast.error('Ingrese el nombre del establecimiento')
      return
    }
    
    if (!selectedLocation) {
      toast.error('Seleccione una ubicación en el mapa')
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
          direccion: selectedLocation.address,
          latitud: selectedLocation.lat,
          longitud: selectedLocation.lng,
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
    <div className="container max-w-4xl py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Generá tu código QR</h1>
        <p className="text-muted-foreground mt-2">
          Registrá tu negocio y obtené un código QR para que tus clientes soliciten taxis desde tu ubicación
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
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
                  <option value="otro">Otro</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Dirección *
                </Label>
                <Input
                  id="direccion"
                  placeholder="Comenzá a escribir la dirección..."
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Seleccioná la dirección del cuadro de sugerencias
                </p>
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
                  <Phone className="h-4 w-4" />
                  Teléfono de contacto
                </Label>
                <Input
                  placeholder="3811234567"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
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
          <CardHeader>
            <CardTitle>Ubicación en el mapa</CardTitle>
          </CardHeader>
          <CardContent>
            {!mapLoaded ? (
              <div className="flex h-[300px] items-center justify-center rounded-lg border bg-muted/50">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="space-y-4">
                <div 
                  id="map" 
                  className="h-[300px] rounded-lg border"
                />
                {selectedLocation && (
                  <div className="rounded-lg bg-green-50 p-3 text-sm text-green-800">
                    <p className="font-medium">✓ Ubicación seleccionada</p>
                    <p className="text-xs mt-1">{selectedLocation.address}</p>
                    <p className="text-xs mt-1">
                      Coordenadas: {selectedLocation.lat.toFixed(6)}, {selectedLocation.lng.toFixed(6)}
                    </p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}