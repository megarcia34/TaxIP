'use client'

import { useState, useEffect } from 'react'
import { useRouter, } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, MapPin, Navigation, DollarSign, Clock } from 'lucide-react'
import { toast } from 'sonner'
import Script from 'next/script'

declare global {
  interface Window {
    google: any
    initAutocomplete: () => void
  }
}

export default function ReservarPage() {
  const router = useRouter()
      // ✅ Reemplazo de useSearchParams() por window.location
    const [origenId, setOrigenId] = useState<string | null>(null)

    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        setOrigenId(params.get('origenId'))
    }, [])
    
  const [isLoading, setIsLoading] = useState(false)
  const [calculandoTarifa, setCalculandoTarifa] = useState(false)
  const [cargandoUbicacion, setCargandoUbicacion] = useState(false)
  const [tarifaEstimada, setTarifaEstimada] = useState<number | null>(null)
  const [distancia, setDistancia] = useState<string | null>(null)
  const [tiempo, setTiempo] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    origen: '',
    origen_lat: null as number | null,
    origen_lng: null as number | null,
    destino: '',
    destino_lat: null as number | null,
    destino_lng: null as number | null,
    metodo_pago: 'efectivo',
  })

  // ============================================
  // ✅ FUNCIÓN PARA OBTENER UBICACIÓN POR ID (QR)
  // ============================================
  const fetchUbicacionPorId = async (id: string) => {
    setCargandoUbicacion(true)
    try {
      // 🔥 Consume el nuevo endpoint público
      const response = await fetch(`/api/empresa/public/${id}`)
      
      if (!response.ok) {
        throw new Error('Empresa no encontrada')
      }
      
      const data = await response.json()
      
      // Precargar el formulario con los datos de la empresa
      setFormData(prev => ({
        ...prev,
        origen: data.direccion || data.nombre,
        origen_lat: data.latitud,
        origen_lng: data.longitud,
      }))
      
      toast.success(`Origen precargado: ${data.nombre}`)
    } catch (error) {
      console.error('Error al obtener ubicación:', error)
      toast.error('No se pudo cargar la ubicación del QR')
      
      // Fallback: usar geolocalización del navegador
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setFormData(prev => ({
              ...prev,
              origen_lat: position.coords.latitude,
              origen_lng: position.coords.longitude,
              origen: 'Tu ubicación actual (fallback)',
            }))
            reverseGeocode(position.coords.latitude, position.coords.longitude)
          },
          () => toast.error('No se pudo obtener ubicación automática')
        )
      }
    } finally {
      setCargandoUbicacion(false)
    }
  }

  // ============================================
  // REVERSE GEOCODING
  // ============================================
  const reverseGeocode = async (lat: number, lng: number) => {
    try {
      const response = await fetch(`/api/public/geocode?lat=${lat}&lng=${lng}`)
      const data = await response.json()
      if (data.direccion) {
        setFormData(prev => ({ ...prev, origen: data.direccion }))
      }
    } catch (error) {
      console.error('Error al obtener dirección:', error)
    }
  }

  // ============================================
  // DETECCIÓN DE ORIGEN (QR o Geolocalización)
  // ============================================
useEffect(() => {
  // ✅ Obtener parámetros de la URL usando window.location
  const params = new URLSearchParams(window.location.search)
  
  // ✅ Leer todos los parámetros
  const origenParam = params.get('origen')
  const latParam = params.get('lat')
  const lngParam = params.get('lng')
  const direccionParam = params.get('direccion')
  
  // ✅ PRIORIDAD 1: QR con origenId (UUID de empresa)
  if (origenId) {
    fetchUbicacionPorId(origenId)
    return
  }
  
  // ✅ PRIORIDAD 2: Coordenadas directas (fallback)
  if (latParam && lngParam) {
    setFormData(prev => ({
      ...prev,
      origen: direccionParam || 'Ubicación del QR',
      origen_lat: parseFloat(latParam),
      origen_lng: parseFloat(lngParam),
    }))
    return
  }
  
  // ✅ PRIORIDAD 3: Geolocalización del navegador
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setFormData(prev => ({
          ...prev,
          origen_lat: latitude,
          origen_lng: longitude,
          origen: 'Tu ubicación actual',
        }))
        reverseGeocode(latitude, longitude)
      },
      (error) => {
        console.error('Error de geolocalización:', error)
      }
    )
  }
}, [origenId])  // ✅ Dependencia: solo origenId

  // ============================================
  // CALCULAR TARIFA
  // ============================================
  const calcularTarifa = async () => {
    if (!formData.origen_lat || !formData.origen_lng || !formData.destino_lat || !formData.destino_lng) {
      toast.error('Completa el origen y destino')
      return
    }
    
    setCalculandoTarifa(true)
    try {
      const response = await fetch('/api/public/viajes/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origen_lat: formData.origen_lat,
          origen_lng: formData.origen_lng,
          destino_lat: formData.destino_lat,
          destino_lng: formData.destino_lng,
        }),
      })
      
      const data = await response.json()
      if (data.success) {
        setTarifaEstimada(data.tarifa)
        setDistancia(data.distancia)
        setTiempo(data.tiempo)
      }
    } catch (error) {
      console.error('Error al calcular tarifa:', error)
    } finally {
      setCalculandoTarifa(false)
    }
  }
  
  // ============================================
  // MANEJAR CAMBIO DE DESTINO
  // ============================================
  const handleDestinoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setFormData(prev => ({ ...prev, destino: value }))
    
    // Aquí se integraría Google Places Autocomplete
  }
  
  // ============================================
  // ENVIAR SOLICITUD
  // ============================================
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.origen_lat || !formData.origen_lng) {
      toast.error('No se pudo determinar tu ubicación de origen')
      return
    }
    
    if (!formData.destino_lat || !formData.destino_lng) {
      toast.error('Selecciona un destino válido')
      return
    }
    
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/public/viajes/solicitar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          direccion_origen: formData.origen,
          origen_lat: formData.origen_lat,
          origen_lng: formData.origen_lng,
          direccion_destino: formData.destino,
          destino_lat: formData.destino_lat,
          destino_lng: formData.destino_lng,
          metodo_pago: formData.metodo_pago,
          precio_estimado: tarifaEstimada,
        }),
      })
      
      const data = await response.json()
      
      if (response.ok) {
        toast.success('¡Taxi solicitado! Buscando el vehículo más cercano...')
        router.push(`/reservar/confirmacion/${data.viaje_id}`)
      } else {
        toast.error(data.detail || 'Error al solicitar el taxi')
      }
    } catch (error) {
      toast.error('Error al conectar con el servidor')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="container max-w-4xl py-8">
      <div className="grid gap-8 md:grid-cols-2">
        {/* Formulario */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Solicitar Taxi</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-green-500" />
                    Origen
                  </Label>
                  <Input
                    value={formData.origen}
                    disabled
                    className="bg-muted"
                  />
                  {cargandoUbicacion && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Cargando ubicación...
                    </div>
                  )}
                  {formData.origen_lat && formData.origen_lng && !cargandoUbicacion && (
                    <p className="text-xs text-muted-foreground">
                      📍 Ubicación detectada automáticamente
                    </p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Navigation className="h-4 w-4 text-red-500" />
                    Destino *
                  </Label>
                  <Input
                    placeholder="¿A dónde vas?"
                    value={formData.destino}
                    onChange={handleDestinoChange}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Método de Pago</Label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                    value={formData.metodo_pago}
                    onChange={(e) => setFormData({ ...formData, metodo_pago: e.target.value })}
                  >
                    <option value="efectivo">Efectivo</option>
                    <option value="tarjeta">Tarjeta</option>
                    <option value="app">App Wallet</option>
                  </select>
                </div>
                
                <Button type="submit" className="w-full" disabled={isLoading || cargandoUbicacion}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Buscando el taxi más cercano...
                    </>
                  ) : cargandoUbicacion ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Cargando ubicación...
                    </>
                  ) : (
                    'Solicitar Taxi'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
        
        {/* Tarjeta de tarifa estimada */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Tarifa Estimada</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!formData.destino_lat ? (
                <p className="text-center text-muted-foreground py-8">
                  Ingresa tu destino para ver la tarifa
                </p>
              ) : calculandoTarifa ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : tarifaEstimada ? (
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">
                      ${tarifaEstimada}
                    </p>
                    <p className="text-sm text-muted-foreground">Precio estimado</p>
                  </div>
                  <div className="flex justify-between text-sm">
                    <div className="flex items-center gap-1">
                      <Navigation className="h-4 w-4" />
                      <span>{distancia || 'Calculando...'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{tiempo || 'Calculando...'}</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={calcularTarifa}
                    disabled={calculandoTarifa}
                  >
                    Recalcular
                  </Button>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={calcularTarifa}
                  disabled={calculandoTarifa}
                >
                  Calcular tarifa
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}