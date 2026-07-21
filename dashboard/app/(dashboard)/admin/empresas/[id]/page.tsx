'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Building2, Mail, Phone, MapPin, Percent, Calendar, Users, Car, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface Empresa {
  id: string
  nombre: string
  tipo: string
  email_facturacion: string
  telefono: string
  direccion: string
  latitud: number
  longitud: number
  tarifa_preferencial: number
  activo: boolean
  created_at: string
}

interface Empleado {
  id: string
  nombre: string
  apellido: string
  email: string
  telefono: string
  rol: string
  activo: boolean
}

interface ViajeCorporativo {
  id: string
  estado: string
  destino: string
  nombre_pasajero: string
  precio: number
  creado_en: string
  chofer_nombre: string
  patente: string
}

export default function AdminEmpresaDetallePage() {
  const params = useParams()
  const router = useRouter()
  const empresaId = params.id as string

  const { data: empresa, isLoading: empresaLoading } = useQuery({
    queryKey: ['empresa', empresaId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/empresa/${empresaId}`)
      return response.data as Empresa
    },
  })

  const { data: empleados, isLoading: empleadosLoading } = useQuery({
    queryKey: ['empresa-empleados', empresaId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/empresa/${empresaId}/empleados`)
      return response.data as Empleado[]
    },
  })

  const { data: viajes, isLoading: viajesLoading } = useQuery({
    queryKey: ['empresa-viajes', empresaId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/empresa/${empresaId}/viajes`)
      return response.data as ViajeCorporativo[]
    },
  })

  const getTipoBadge = (tipo: string) => {
    const colores: Record<string, string> = {
      hotel: 'bg-blue-500',
      empresa: 'bg-green-500',
      institucion: 'bg-purple-500',
    }
    return colores[tipo] || 'bg-gray-500'
  }

  const getEstadoBadge = (estado: string) => {
    const colores: Record<string, string> = {
      pendiente: 'bg-yellow-500',
      aceptado: 'bg-blue-500',
      en_curso: 'bg-purple-500',
      finalizado: 'bg-green-500',
      cancelado: 'bg-red-500',
    }
    return colores[estado] || 'bg-gray-500'
  }

  if (empresaLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!empresa) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Empresa no encontrada</p>
        <Button className="mt-4" onClick={() => router.back()}>Volver</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{empresa.nombre}</h1>
          <Badge className={getTipoBadge(empresa.tipo)}>
            {empresa.tipo}
          </Badge>
          <Badge className={empresa.activo ? 'bg-green-500' : 'bg-red-500'}>
            {empresa.activo ? 'Activo' : 'Inactivo'}
          </Badge>
        </div>
        <Link href={`/admin/empresas/${empresa.id}/editar`}>
          <Button variant="outline">Editar</Button>
        </Link>
      </div>

      <Tabs defaultValue="info" className="space-y-4">
        <TabsList>
          <TabsTrigger value="info">Información</TabsTrigger>
          <TabsTrigger value="empleados">Empleados</TabsTrigger>
          <TabsTrigger value="viajes">Viajes</TabsTrigger>
        </TabsList>

        <TabsContent value="info">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Datos de la Empresa</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Nombre</p>
                    <p className="font-medium">{empresa.nombre}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Email Facturación</p>
                    <p className="font-medium">{empresa.email_facturacion}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Phone className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Teléfono</p>
                    <p className="font-medium">{empresa.telefono}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Dirección</p>
                    <p className="font-medium">{empresa.direccion}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Coordenadas: {empresa.latitud}, {empresa.longitud}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Percent className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Descuento Preferencial</p>
                    <p className="font-medium">{empresa.tarifa_preferencial}%</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Fecha de registro</p>
                    <p className="font-medium">
                      {new Date(empresa.created_at).toLocaleDateString('es-AR')}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Estadísticas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <p className="text-2xl font-bold">{empleados?.length || 0}</p>
                    <p className="text-xs text-muted-foreground">Empleados</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <p className="text-2xl font-bold">{viajes?.length || 0}</p>
                    <p className="text-xs text-muted-foreground">Viajes Totales</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="empleados">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Empleados / Recepcionistas</CardTitle>
              <Link href={`/admin/empresas/${empresa.id}/empleados/nuevo`}>
                <Button size="sm">
                  <Users className="h-4 w-4 mr-2" />
                  Agregar Empleado
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {empleadosLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : empleados?.length === 0 ? (
                <p className="text-center py-8 text-muted-foreground">No hay empleados registrados</p>
              ) : (
                <div className="space-y-3">
                  {empleados?.map((empleado) => (
                    <div key={empleado.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{empleado.nombre} {empleado.apellido}</p>
                        <p className="text-sm text-muted-foreground">{empleado.email}</p>
                        {empleado.telefono && (
                          <p className="text-xs text-muted-foreground">{empleado.telefono}</p>
                        )}
                      </div>
                      <Badge variant={empleado.activo ? 'default' : 'secondary'}>
                        {empleado.rol}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="viajes">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Viajes</CardTitle>
            </CardHeader>
            <CardContent>
              {viajesLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : viajes?.length === 0 ? (
                <p className="text-center py-8 text-muted-foreground">No hay viajes registrados</p>
              ) : (
                <div className="space-y-3">
                  {viajes?.map((viaje) => (
                    <div key={viaje.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Car className="h-4 w-4 text-muted-foreground" />
                          <p className="font-medium">{viaje.nombre_pasajero}</p>
                          <Badge className={getEstadoBadge(viaje.estado)}>
                            {viaje.estado}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{viaje.destino}</p>
                        {viaje.chofer_nombre && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Chofer: {viaje.chofer_nombre} - {viaje.patente}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">${viaje.precio}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(viaje.creado_en).toLocaleDateString('es-AR')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}