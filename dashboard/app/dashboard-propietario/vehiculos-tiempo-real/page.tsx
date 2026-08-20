'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { Loader2, RefreshCw, MapPin, Car, Wifi, WifiOff } from 'lucide-react'
import { propietarioAPI, propietarioVehiculosAPI } from '@/lib/api'
import { MapaPropietario } from '@/components/propietario/MapaPropietario'

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

export default function VehiculosTiempoRealPage() {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [ubicaciones, setUbicaciones] = useState<Record<string, Ubicacion>>({})
  const [loading, setLoading] = useState(true)
  const [loadingUbicaciones, setLoadingUbicaciones] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const cargarVehiculos = async () => {
    setLoading(true)
    try {
      const data = await propietarioAPI.getVehiculos()
      setVehiculos(data || [])
      
      if (data && data.length > 0) {
        await cargarUbicaciones(data.map((v: Vehiculo) => v.id))
      }
    } catch (error) {
      console.error('Error cargando vehículos:', error)
      toast.error('Error al cargar vehículos')
    } finally {
      setLoading(false)
    }
  }

  const cargarUbicaciones = async (vehiculoIds: string[]) => {
    setLoadingUbicaciones(true)
    try {
      const nuevasUbicaciones: Record<string, Ubicacion> = {}
      
      for (const id of vehiculoIds) {
        try {
          const ubicacion = await propietarioVehiculosAPI.getUbicacion(id)
          nuevasUbicaciones[id] = ubicacion
        } catch (error) {
          // Vehículo sin GPS
          nuevasUbicaciones[id] = {
            vehiculo_id: id,
            ubicacion: {
              latitud: 0,
              longitud: 0,
              ultima_actualizacion: new Date().toISOString()
            },
            conductor: { email: '', nombre: 'Sin datos' },
            estado: { laboral: 'desconocido', calificacion_promedio: 0 },
            viaje_actual: null
          }
        }
      }
      
      setUbicaciones(nuevasUbicaciones)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error cargando ubicaciones:', error)
      toast.error('Error al cargar ubicaciones')
    } finally {
      setLoadingUbicaciones(false)
    }
  }

  const refrescarUbicaciones = async () => {
    if (vehiculos.length === 0) return
    await cargarUbicaciones(vehiculos.map((v) => v.id))
    toast.success('Ubicaciones actualizadas')
  }

  useEffect(() => {
    cargarVehiculos()
    
    // Refrescar cada 30 segundos
    const interval = setInterval(() => {
      if (vehiculos.length > 0) {
        cargarUbicaciones(vehiculos.map((v) => v.id))
      }
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string, className: string }> = {
      'libre': { label: 'Disponible', className: 'bg-green-100 text-green-800' },
      'ocupado': { label: 'Ocupado', className: 'bg-red-100 text-red-800' },
      'en_viaje': { label: 'En viaje', className: 'bg-yellow-100 text-yellow-800' },
      'fuera_servicio': { label: 'Fuera de servicio', className: 'bg-gray-100 text-gray-800' },
      'desconocido': { label: 'Sin datos', className: 'bg-gray-100 text-gray-800' },
    }
    const info = estados[estado] || { label: estado, className: 'bg-gray-100 text-gray-800' }
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const vehiculosConGps = vehiculos.filter(v => {
    const u = ubicaciones[v.id]
    return u && u.ubicacion.latitud !== 0 && u.ubicacion.longitud !== 0
  })

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-muted-foreground">Cargando vehículos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <MapPin className="h-6 w-6 text-primary" />
            Vehículos en Tiempo Real
          </h1>
          <p className="text-muted-foreground">
            Ubicación GPS de tus vehículos
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="text-xs text-muted-foreground">
              Última actualización: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <Button onClick={refrescarUbicaciones} disabled={loadingUbicaciones} variant="outline">
            <RefreshCw className={`h-4 w-4 mr-2 ${loadingUbicaciones ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>
      </div>

      {/* Mapa */}
      <Card>
        <CardContent className="p-4">
          <MapaPropietario 
            vehiculos={vehiculos} 
            ubicaciones={ubicaciones} 
            loading={loadingUbicaciones}
          />
        </CardContent>
      </Card>

      {/* Lista rápida de vehículos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehiculos.map((vehiculo) => {
          const ubicacion = ubicaciones[vehiculo.id]
          const tieneGps = ubicacion && ubicacion.ubicacion.latitud !== 0 && ubicacion.ubicacion.longitud !== 0

          return (
            <Card key={vehiculo.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-4">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <Car className="h-4 w-4 text-muted-foreground" />
                    <span className="font-bold">{vehiculo.patente}</span>
                  </div>
                  {getEstadoBadge(ubicacion?.estado?.laboral || 'desconocido')}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})
                </p>
                <div className="flex items-center gap-2 mt-2 text-xs">
                  {tieneGps ? (
                    <>
                      <Wifi className="h-3 w-3 text-green-600" />
                      <span className="text-green-600">GPS activo</span>
                      <span className="text-muted-foreground">
                        {ubicacion.ubicacion.latitud.toFixed(4)}, {ubicacion.ubicacion.longitud.toFixed(4)}
                      </span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="h-3 w-3 text-muted-foreground" />
                      <span className="text-muted-foreground">Sin GPS</span>
                    </>
                  )}
                </div>
                {ubicacion?.conductor?.nombre && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Conductor: {ubicacion.conductor.nombre}
                  </p>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Resumen */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{vehiculos.length}</p>
              <p className="text-sm text-muted-foreground">Total Vehículos</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {Object.values(ubicaciones).filter(u => u.estado?.laboral === 'libre').length}
              </p>
              <p className="text-sm text-muted-foreground">Disponibles</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-600">
                {Object.values(ubicaciones).filter(u => u.estado?.laboral === 'en_viaje' || u.estado?.laboral === 'ocupado').length}
              </p>
              <p className="text-sm text-muted-foreground">En viaje</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {vehiculosConGps.length}
              </p>
              <p className="text-sm text-muted-foreground">Con GPS</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}