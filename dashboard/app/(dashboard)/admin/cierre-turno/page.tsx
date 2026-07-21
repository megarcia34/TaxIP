'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { RefreshCw, CheckCircle, XCircle, Clock, AlertCircle, Printer, Download, Calendar } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

interface TurnoData {
  activo: boolean
  mensaje?: string
  turno?: {
    id: string
    fecha_inicio: string
    viajes_gestionados: number
    facturado_total: number
  }
  kpis?: {
    total_viajes: number
    completados: number
    cancelados: number
    total_facturado: number
    promedio_viaje: number
  }
  viajes?: Array<{
    id: string
    pasajero: string
    origen: string
    destino: string
    estado: string
    precio: number
    created_at: string
  }>
}

export default function CierreTurnoPage() {
  const { status } = useSession()
  const { toast } = useToast()
  const router = useRouter()
  const [data, setData] = useState<TurnoData | null>(null)
  const [loading, setLoading] = useState(true)
  const [cerrando, setCerrando] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/tenant/cierre-turno')
      if (!res.ok) throw new Error('Error al cargar datos del turno')
      const result = await res.json()
      setData(result)
    } catch (error) {
      console.error('Error:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los datos del turno',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchData()
      const interval = setInterval(fetchData, 30000)
      return () => clearInterval(interval)
    }
  }, [status])

  const handleCerrarTurno = async () => {
    try {
      setCerrando(true)
      const res = await fetch('/api/tenant/cierre-turno', { method: 'POST' })
      if (!res.ok) throw new Error('Error al cerrar turno')
      
      toast({
        title: '✅ Turno cerrado',
        description: 'El turno ha sido cerrado correctamente',
      })
      
      // Recargar datos
      await fetchData()
      router.refresh()
    } catch (error) {
      console.error('Error:', error)
      toast({
        title: 'Error',
        description: 'No se pudo cerrar el turno',
        variant: 'destructive',
      })
    } finally {
      setCerrando(false)
    }
  }

  const getEstadoBadge = (estado: string) => {
    const estados: Record<string, { label: string; className: string }> = {
      pendiente: { label: 'Pendiente', className: 'bg-yellow-100 text-yellow-800' },
      aceptado: { label: 'Aceptado', className: 'bg-blue-100 text-blue-800' },
      en_curso: { label: 'En Curso', className: 'bg-purple-100 text-purple-800' },
      completado: { label: 'Completado', className: 'bg-green-100 text-green-800' },
      cancelado: { label: 'Cancelado', className: 'bg-red-100 text-red-800' },
    }
    const info = estados[estado] || estados.pendiente
    return <Badge className={info.className}>{info.label}</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!data?.activo) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Cierre de Turno</h1>
          <p className="text-muted-foreground">
            Resumen y cierre del turno actual
          </p>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <div className="text-6xl">⏰</div>
            <p className="text-lg font-medium">No hay turno activo</p>
            <p className="text-sm text-muted-foreground">
              Inicia un turno desde el módulo operativo para comenzar
            </p>
            <Button onClick={() => router.push('/operativo')}>
              Ir a Operativo
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { turno, kpis, viajes } = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Cierre de Turno</h1>
          <p className="text-muted-foreground">
            Resumen y cierre del turno actual
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
          <Button variant="outline" size="sm">
            <Printer className="h-4 w-4 mr-2" />
            Imprimir
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar PDF
          </Button>
        </div>
      </div>

      {/* Info del Turno */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Inicio del Turno</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>
                {turno?.fecha_inicio ? new Date(turno.fecha_inicio).toLocaleString() : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Viajes Gestionados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis?.total_viajes || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Facturado Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${(kpis?.total_facturado || 0).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-xl font-bold">{kpis?.completados || 0}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Cancelados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" />
              <span className="text-xl font-bold">{kpis?.cancelados || 0}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Promedio por Viaje</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">
              ${(kpis?.promedio_viaje || 0).toFixed(2)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eficiencia</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">
              {kpis?.total_viajes 
                ? Math.round((kpis.completados / kpis.total_viajes) * 100) 
                : 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Viajes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Viajes del Turno</span>
            <Badge variant="secondary">{viajes?.length || 0}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Pasajero</TableHead>
                  <TableHead>Origen</TableHead>
                  <TableHead>Destino</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Precio</TableHead>
                  <TableHead>Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {viajes?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      No hay viajes en este turno
                    </TableCell>
                  </TableRow>
                ) : (
                  viajes?.map((viaje) => (
                    <TableRow key={viaje.id}>
                      <TableCell>{viaje.pasajero}</TableCell>
                      <TableCell className="max-w-[100px] truncate">{viaje.origen}</TableCell>
                      <TableCell className="max-w-[100px] truncate">{viaje.destino}</TableCell>
                      <TableCell>{getEstadoBadge(viaje.estado)}</TableCell>
                      <TableCell className="text-right font-medium">
                        ${viaje.precio.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-xs">
                        {new Date(viaje.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Botón Cerrar Turno */}
      <div className="flex justify-end">
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button 
              size="lg" 
              className="bg-red-600 hover:bg-red-700 text-white"
              disabled={cerrando}
            >
              {cerrando ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2" />
                  Cerrando...
                </>
              ) : (
                <>
                  <Clock className="h-4 w-4 mr-2" />
                  Cerrar Turno
                </>
              )}
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
              <AlertDialogDescription>
                Esta acción cerrará el turno actual. No podrás agregar más viajes a este turno.
                <br />
                <br />
                <strong>Resumen del turno:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Viajes: {kpis?.total_viajes || 0}</li>
                  <li>Completados: {kpis?.completados || 0}</li>
                  <li>Cancelados: {kpis?.cancelados || 0}</li>
                  <li>Facturado: ${(kpis?.total_facturado || 0).toLocaleString()}</li>
                </ul>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction onClick={handleCerrarTurno} className="bg-red-600 hover:bg-red-700">
                Sí, cerrar turno
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  )
}