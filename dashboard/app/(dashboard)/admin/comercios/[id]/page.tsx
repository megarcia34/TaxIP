'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Building2, MapPin, Phone, Mail, QrCode, Calendar, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface Comercio {
  id: string
  nombre: string
  rubro: string
  direccion: string
  latitud: number
  longitud: number
  codigo_qr: string
  email_contacto: string
  telefono: string
  activo: boolean
  created_at: string
  url_qr: string
}

export default function AdminComercioDetallePage() {
  const params = useParams()
  const router = useRouter()
  const comercioId = params.id as string

  const { data: comercio, isLoading } = useQuery({
    queryKey: ['comercio', comercioId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/comercio/${comercioId}`)
      return response.data as Comercio
    },
    enabled: !!comercioId,
  })

  const getRubroBadge = (rubro: string) => {
    const colores: Record<string, string> = {
      restaurante: 'bg-orange-500',
      hotel: 'bg-blue-500',
      comercio: 'bg-green-500',
      oficina: 'bg-purple-500',
      turismo: 'bg-cyan-500',
      evento: 'bg-pink-500',
    }
    return colores[rubro] || 'bg-gray-500'
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!comercio) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Comercio no encontrado</p>
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
          <h1 className="text-2xl font-bold tracking-tight">{comercio.nombre}</h1>
          <Badge className={comercio.activo ? 'bg-green-500' : 'bg-red-500'}>
            {comercio.activo ? 'Activo' : 'Inactivo'}
          </Badge>
        </div>
        <Link href={`/admin/comercios/${comercio.id}/editar`}>
          <Button variant="outline">Editar</Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Información General</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Nombre</p>
                <p className="font-medium">{comercio.nombre}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Rubro</p>
                <Badge className={getRubroBadge(comercio.rubro)}>
                  {comercio.rubro || 'No especificado'}
                </Badge>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Dirección</p>
                <p className="font-medium">{comercio.direccion}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Coordenadas: {comercio.latitud}, {comercio.longitud}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Phone className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Teléfono</p>
                <p className="font-medium">{comercio.telefono || 'No especificado'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{comercio.email_contacto || 'No especificado'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Fecha de registro</p>
                <p className="font-medium">
                  {new Date(comercio.created_at).toLocaleDateString('es-AR')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Código QR</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <QrCode className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Código</p>
                <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                  {comercio.codigo_qr}
                </code>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <QrCode className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">URL del QR</p>
                <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                  {comercio.url_qr}
                </code>
              </div>
            </div>
            <div className="flex justify-center p-4">
              <img 
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(comercio.url_qr)}`}
                alt="QR Code"
                className="border rounded-lg p-2 bg-white"
              />
            </div>
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => window.open(comercio.url_qr, '_blank')}
            >
              Ver página de reserva
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}