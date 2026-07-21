'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Loader2, MapPin, Crosshair } from 'lucide-react'
import { toast } from 'sonner'

declare global {
  interface Window {
    google: any
    initMap: () => void
  }
}

export default function AdminNuevoComercioPage() {
  const router = useRouter()
  const mapRef = useRef<HTMLDivElement>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
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
          
          // Crear marcador
          const marker = new window.google.maps.Marker({
            position: { lat: -34.6037, lng: -58.3816 },
            map: map,
            draggable: true,
          })
          
          // Al hacer clic en el mapa
          map.addListener('click', (e: any) => {
            const lat = e.latLng.lat()
            const lng = e.latLng.lng()
            marker.setPosition({ lat, lng })
            updateLocation(lat, lng)
          })
          
          // Al arrastrar el marcador
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
    setSelectedLocation({ lat, lng, address: '' })
    
    // Obtener dirección desde coordenadas (reverse geocoding)
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
          // Centrar mapa en ubicación actual
          if (window.google && mapRef.current) {
            const map = new window.google.maps.Map(mapRef.current, {
              center: { lat: latitude, lng: longitude },
              zoom: 15,
            })
          }
        },
        (error) => {
          toast.error('No se pudo obtener tu ubicación')
        }
      )
    } else {
      toast.error('Geolocalización no soportada')
    }
  }

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.post('/api/comercio/registro', {
        nombre: data.nombre,
        rubro: data.rubro,
        direccion: data.direccion,
        latitud: parseFloat(data.latitud),
        longitud: parseFloat(data.longitud),
        email_contacto: data.email_contacto,
        telefono: data.telefono,
      })
      return response.data
    },
    onSuccess: () => {
      toast.success('Comercio registrado correctamente')
      router.push('/admin/comercios')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al registrar el comercio')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.nombre || !formData.direccion || !formData.latitud || !formData.longitud) {
      toast.error('Complete los campos obligatorios')
      return
    }
    createMutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Nuevo Comercio</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Formulario */}
        <Card>
          <CardHeader>
            <CardTitle>Datos del Comercio</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="nombre">Nombre del comercio *</Label>
                <Input
                  id="nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="rubro">Rubro</Label>
                <select
                  id="rubro"
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={formData.rubro}
                  onChange={(e) => setFormData({ ...formData, rubro: e.target.value })}
                >
                  <option value="">Seleccionar rubro</option>
                  <option value="restaurante">Restaurante / Bar</option>
                  <option value="hotel">Hotel / Hospedaje</option>
                  <option value="comercio">Comercio / Tienda</option>
                  <option value="oficina">Oficina / Empresa</option>
                  <option value="turismo">Punto turistico</option>
                  <option value="evento">Salon de eventos</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="telefono">Telefono</Label>
                <Input
                  id="telefono"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email_contacto">Email de contacto</Label>
                <Input
                  id="email_contacto"
                  type="email"
                  value={formData.email_contacto}
                  onChange={(e) => setFormData({ ...formData, email_contacto: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="direccion">Direccion *</Label>
                <Input
                  id="direccion"
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="latitud">Latitud *</Label>
                  <Input
                    id="latitud"
                    type="number"
                    step="0.000001"
                    value={formData.latitud}
                    onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="longitud">Longitud *</Label>
                  <Input
                    id="longitud"
                    type="number"
                    step="0.000001"
                    value={formData.longitud}
                    onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end gap-4">
                <Button type="button" variant="outline" onClick={() => router.back()}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Registrar Comercio
                </Button>
              </div>
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
              <div className="flex h-[400px] items-center justify-center rounded-lg border bg-muted/50">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                <div ref={mapRef} className="h-[350px] rounded-lg border" />
                {selectedLocation && (
                  <div className="mt-4 p-3 rounded-lg bg-green-50 text-sm">
                    <p className="font-medium text-green-800">✓ Ubicación seleccionada</p>
                    <p className="text-xs text-green-700 mt-1 break-all">{selectedLocation.address}</p>
                    <p className="text-xs text-green-700 mt-1">
                      Lat: {selectedLocation.lat.toFixed(6)}, Lng: {selectedLocation.lng.toFixed(6)}
                    </p>
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