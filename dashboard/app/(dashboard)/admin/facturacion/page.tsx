'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { RefreshCw, CheckCircle, XCircle, Clock, Download, Eye, Plus } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface Factura {
  id: string
  empresa_nombre: string
  periodo: string
  total: number
  descuento: number
  total_final: number
  estado: string
  created_at: string
  pagada_at: string | null
  estado_deuda: string
}

export default function FacturacionPage() {
  const { status } = useSession()
  const { toast } = useToast()
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)

  const fetchFacturas = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/tenant/facturacion')
      if (!res.ok) throw new Error('Error al cargar facturas')
      const data = await res.json()
      setFacturas(data)
    } catch (error) {
      console.error('Error:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar las facturas',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchFacturas()
    }
  }, [status])

  const actualizarEstado = async (facturaId: string, nuevoEstado: string) => {
    try {
      setUpdating(facturaId)
      const res = await fetch('/api/tenant/facturacion', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ factura_id: facturaId, estado: nuevoEstado }),
      })

      if (!res.ok) throw new Error('Error al actualizar')

      toast({
        title: 'Éxito',
        description: `Factura ${nuevoEstado === 'pagada' ? 'pagada' : 'actualizada'} correctamente`,
      })

      await fetchFacturas()
    } catch (error) {
      console.error('Error:', error)
      toast({
        title: 'Error',
        description: 'No se pudo actualizar la factura',
        variant: 'destructive',
      })
    } finally {
      setUpdating(null)
    }
  }

  const getEstadoBadge = (estado: string, estadoDeuda: string) => {
    if (estado === 'pagada') {
      return <Badge className="bg-green-500">Pagada</Badge>
    }
    if (estadoDeuda === 'vencida') {
      return <Badge className="bg-red-500">Vencida</Badge>
    }
    if (estadoDeuda === 'proximo_vencimiento') {
      return <Badge className="bg-yellow-500">Próximo vencimiento</Badge>
    }
    return <Badge variant="secondary">Pendiente</Badge>
  }

  const getTotalLabel = (estado: string, estadoDeuda: string) => {
    if (estado === 'pagada') return 'Pagado'
    if (estadoDeuda === 'vencida') return 'Vencido'
    if (estadoDeuda === 'proximo_vencimiento') return 'Por vencer'
    return 'Pendiente'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  const totalPendiente = facturas
    .filter(f => f.estado === 'pendiente')
    .reduce((sum, f) => sum + f.total_final, 0)

  const totalVencido = facturas
    .filter(f => f.estado === 'pendiente' && f.estado_deuda === 'vencida')
    .reduce((sum, f) => sum + f.total_final, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Facturación</h1>
          <p className="text-muted-foreground">
            Gestión de facturas de empresas corporativas
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchFacturas}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Nueva Factura
          </Button>
        </div>
      </div>

      {/* Resumen */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Pendiente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              ${totalPendiente.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Vencido</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ${totalVencido.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Facturado</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${facturas.reduce((sum, f) => sum + f.total_final, 0).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabla */}
      <Card>
        <CardHeader>
          <CardTitle>Listado de Facturas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Empresa</TableHead>
                  <TableHead>Período</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead className="text-right">Descuento</TableHead>
                  <TableHead className="text-right">Total Final</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {facturas.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      No hay facturas registradas
                    </TableCell>
                  </TableRow>
                ) : (
                  facturas.map((factura) => (
                    <TableRow key={factura.id}>
                      <TableCell className="font-medium">{factura.empresa_nombre}</TableCell>
                      <TableCell>{factura.periodo}</TableCell>
                      <TableCell className="text-right">${factura.total.toLocaleString()}</TableCell>
                      <TableCell className="text-right text-green-600">
                        -${factura.descuento.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right font-bold">
                        ${factura.total_final.toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {getEstadoBadge(factura.estado, factura.estado_deuda)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            title="Ver detalle"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            title="Descargar PDF"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          {factura.estado === 'pendiente' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => actualizarEstado(factura.id, 'pagada')}
                              disabled={updating === factura.id}
                            >
                              {updating === factura.id ? (
                                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                              ) : (
                                <CheckCircle className="h-4 w-4 mr-1" />
                              )}
                              Marcar pagada
                            </Button>
                          )}
                          {factura.estado === 'pagada' && (
                            <Badge className="bg-green-100 text-green-800">
                              {factura.pagada_at ? new Date(factura.pagada_at).toLocaleDateString() : ''}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}