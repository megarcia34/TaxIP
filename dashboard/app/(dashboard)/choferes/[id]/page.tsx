'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, MapPin, Search, Navigation } from 'lucide-react'
import { toast } from 'sonner'

interface Ubicacion {
  lat: number
  lng: number
  direccion: string
}

// ✅ Definir ubicaciones predefinidas (si existen)
const UBICACIONES_PREDEFINIDAS: Record<string, Ubicacion> = {
  // Ejemplo:
  // HOTEL_1: { lat: -34.6037, lng: -58.3816, direccion: 'Hotel Ejemplo 1' },
  // OFICINA_1: { lat: -34.6037, lng: -58.3816, direccion: 'Oficina Ejemplo' },
}

export default function ReservarPage() {
  const searchParams = useSearchParams()
  const origenId = searchParams.get('origenId')
  
  const [origen, setOrigen] = useState('')
  const [destino, setDestino] = useState('')
  const [origenCoords, setOrigenCoords] = useState<{ lat: number; lng: number } | null>(null)
  const [loading, setLoading] = useState(false)
  const [precioEstimado, setPrecioEstimado] = useState<number | null>(null)

  // ✅ Función para obtener ubicación por ID (vía API)
  const fetchUbicacionPorId = async (id: string) => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/api/ubicaciones/${id}`)
      const data = response.data
      if (data.latitud && data.longitud) {
        setOrigenCoords({ lat: data.latitud, lng: data.longitud })
        setOrigen(data.direccion || data.nombre || '')
      } else {
        toast.error('No se pudo obtener la ubicación')
      }
    } catch (error) {
      console.error('Error al obtener ubicación:', error)
      toast.error('Error al cargar la ubicación')
    } finally {
      setLoading(false)
    }
  }

  // ✅ Función para obtener ubicación por ID desde mapa predefinido
  const fetchUbicacionPredefinida = (id: string) => {
    const ubicacion = UBICACIONES_PREDEFINIDAS[id]
    if (ubicacion) {
      setOrigenCoords({ lat: ubicacion.lat, lng: ubicacion.lng })
      setOrigen(ubicacion.direccion)
    } else {
      toast.error('Ubicación no encontrada')
    }
  }

  // ✅ Manejar geolocalización del navegador
  const fetchGeolocalizacion = () => {
    if (navigator.geolocation) {
      setLoading(true)
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setOrigenCoords({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          })
          setLoading(false)
        },
        (error) => {
          console.error('Error de geolocalización:', error)
          toast.error('No se pudo obtener tu ubicación')
          setLoading(false)
        }
      )
    } else {
      toast.error('Tu navegador no soporta geolocalización')
    }
  }

  // ✅ Cargar origen según el parámetro
  useEffect(() => {
    if (origenId) {
      // Si el ID está en el mapa predefinido, usarlo directamente
      if (UBICACIONES_PREDEFINIDAS[origenId]) {
        fetchUbicacionPredefinida(origenId)
      } else {
        // Si no, intentar con la API
        fetchUbicacionPorId(origenId)
      }
    } else {
      // Si no hay ID, usar geolocalización automática
      fetchGeolocalizacion()
    }
  }, [origenId])

  const calcularPrecio = async () => {
    if (!origen || !destino) {
      toast.error('Completa origen y destino')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.post('/api/reservas/estimar-precio', {
        origen: origenCoords || undefined,
        direccion_origen: origen,
        direccion_destino: destino,
      })
      setPrecioEstimado(response.data.precio_estimado)
      toast.success('Precio calculado correctamente')
    } catch (error) {
      console.error('Error al calcular precio:', error)
      toast.error('Error al calcular el precio')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    // Lógica para crear la reserva
  }

  return (
    <div className="container max-w-2xl py-10">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Solicitar Taxi</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Origen</Label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <MapPin className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Dirección de origen"
                    value={origen}
                    onChange={(e) => setOrigen(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={fetchGeolocalizacion}
                  disabled={loading}
                >
                  <Navigation className="h-4 w-4" />
                </Button>
              </div>
              {origenCoords && (
                <p className="text-xs text-muted-foreground">
                  📍 Coordenadas: {origenCoords.lat.toFixed(6)}, {origenCoords.lng.toFixed(6)}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Destino</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Dirección de destino"
                  value={destino}
                  onChange={(e) => setDestino(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={calcularPrecio}
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                Calcular Precio
              </Button>
              <Button className="flex-1" onClick={handleSubmit}>
                Solicitar Taxi
              </Button>
            </div>

            {precioEstimado !== null && (
              <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg text-center">
                <p className="text-sm text-muted-foreground">Precio estimado</p>
                <p className="text-2xl font-bold text-green-600">${precioEstimado}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}