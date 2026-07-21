'use client'

import { useState, useEffect } from 'react'
import { useRouter, } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, Plus, Eye, Edit, Trash2, Car, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number
  numero_licencia: string
  chofer_asignado: string | null
  estado_laboral: string
}

export default function PropietarioVehiculosPage() {
  const router = useRouter()
      // ✅ Reemplazo de useSearchParams() por window.location
    const [propietario_id, setPropietario_id] = useState<string | null>(null)

    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        setPropietario_id(params.get('propietario_id'))
    }, [])
    
  const { user } = useAuth()
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const isAdmin = user?.rol === 'admin'
  const propietarioId = propietario_id

  const cargarVehiculos = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(res.data)
    } catch (error: any) {
      console.error('Error al cargar vehículos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar vehículos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      cargarVehiculos()
    }
  }, [user, propietarioId])

  const eliminarVehiculo = async (id: string) => {
    try {
      await apiClient.delete(`/api/propietario/vehiculos/${id}`)
      toast.success('Vehículo eliminado correctamente')
      cargarVehiculos()
    } catch (error: any) {
      console.error('Error al eliminar vehículo:', error)
      toast.error(error?.response?.data?.detail || 'Error al eliminar vehículo')
    } finally {
      setDeleteId(null)
    }
  }

  // ✅ CORREGIDO: Usa className en lugar de variant para Badge
  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string, className: string }> = {
      'libre': {
        label: 'Disponible',
        className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-200'
      },
      'ocupado': {
        label: 'Ocupado',
        className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-200'
      },
      'en_viaje': {
        label: 'En viaje',
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200'
      },
      'fuera_servicio': {
        label: 'Fuera de servicio',
        className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200'
      }
    }
    const info = estados[estado] || {
      label: estado || 'Desconocido',
      className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-200'
    }
    return <Badge className={info.className}>{info.label}</Badge>
  }

  const filteredVehiculos = vehiculos.filter(v => 
    v.patente?.toLowerCase().includes(search.toLowerCase()) ||
    v.marca?.toLowerCase().includes(search.toLowerCase()) ||
    v.modelo?.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Vehículos</h1>
          <p className="text-muted-foreground">
            Gestión de vehículos de la flota
          </p>
        </div>
        <Link href={`/dashboard-propietario/vehiculos/crear${isAdmin && propietarioId ? `?propietario_id=${propietarioId}` : ''}`}>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Vehículo
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Listado de Vehículos</CardTitle>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por patente, marca o modelo..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredVehiculos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Car className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay vehículos registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Patente</th>
                    <th className="text-left py-3">Marca / Modelo</th>
                    <th className="text-left py-3">Año</th>
                    <th className="text-left py-3">Chofer</th>
                    <th className="text-left py-3">Estado</th>
                    <th className="text-left py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredVehiculos.map((v) => (
                    <tr key={v.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 font-medium">{v.patente}</td>
                      <td className="py-3">{v.marca} {v.modelo}</td>
                      <td className="py-3">{v.anio || '-'}</td>
                      <td className="py-3">{v.chofer_asignado || 'Sin asignar'}</td>
                      <td className="py-3">{getEstadoBadge(v.estado_laboral)}</td>
                      <td className="py-3">
                        <div className="flex gap-1">
                          <Link href={`/dashboard-propietario/vehiculos/${v.id}${isAdmin && propietarioId ? `?propietario_id=${propietarioId}` : ''}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link href={`/dashboard-propietario/vehiculos/${v.id}/editar${isAdmin && propietarioId ? `?propietario_id=${propietarioId}` : ''}`}>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteId(v.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar vehículo?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. El vehículo será eliminado permanentemente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && eliminarVehiculo(deleteId)}
              className="bg-red-500 hover:bg-red-600"
            >
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}