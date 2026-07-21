'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Loader2, FileText, Download, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface Factura {
  id: string
  periodo: string
  total: number
  descuento: number
  total_final: number
  estado: string
  pdf_url: string
  created_at: string
  pagada_at: string
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

const getEstadoColor = (estado: string) => {
  const estados: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    pagada: 'bg-green-500',
    vencida: 'bg-red-500',
    cancelada: 'bg-gray-500',
  }
  return estados[estado] || 'bg-gray-500'
}

const getEstadoIcon = (estado: string) => {
  const icons: Record<string, any> = {
    pendiente: <Clock className="h-4 w-4" />,
    pagada: <CheckCircle className="h-4 w-4" />,
    vencida: <AlertCircle className="h-4 w-4" />,
    cancelada: <AlertCircle className="h-4 w-4" />,
  }
  return icons[estado] || <Clock className="h-4 w-4" />
}

export default function EmpresaFacturacionPage() {
  const { data: facturas, isLoading } = useQuery<Factura[]>({
    queryKey: ['empresa-facturas'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/facturas')
      return response.data
    },
  })

  // Resumen de facturas
  const totalPendiente = facturas?.filter(f => f.estado === 'pendiente').reduce((sum, f) => sum + f.total_final, 0) || 0
  const totalPagado = facturas?.filter(f => f.estado === 'pagada').reduce((sum, f) => sum + f.total_final, 0) || 0
  const totalVencido = facturas?.filter(f => f.estado === 'vencida').reduce((sum, f) => sum + f.total_final, 0) || 0

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Facturación</h1>
        <p className="text-muted-foreground">
          Historial de facturas y estado de cuenta
        </p>
      </div>

      {/* Resumen */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pendientes</p>
                <p className="text-2xl font-bold text-yellow-600">{formatMoneda(totalPendiente)}</p>
              </div>
              <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
                <Clock className="h-5 w-5 text-yellow-600 dark:text-yellow-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pagadas</p>
                <p className="text-2xl font-bold text-green-600">{formatMoneda(totalPagado)}</p>
              </div>
              <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-300" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Vencidas</p>
                <p className="text-2xl font-bold text-red-600">{formatMoneda(totalVencido)}</p>
              </div>
              <div className="rounded-full bg-red-100 p-3 dark:bg-red-900">
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-300" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Listado de facturas */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Historial de Facturas</CardTitle>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Descargar todas
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Período</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Descuento</TableHead>
                <TableHead>Total Final</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>PDF</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {facturas?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    No hay facturas disponibles
                  </TableCell>
                </TableRow>
              ) : (
                facturas?.map((factura) => (
                  <TableRow key={factura.id}>
                    <TableCell className="font-medium">{factura.periodo}</TableCell>
                    <TableCell>{formatMoneda(factura.total)}</TableCell>
                    <TableCell>{formatMoneda(factura.descuento)}</TableCell>
                    <TableCell className="font-bold">{formatMoneda(factura.total_final)}</TableCell>
                    <TableCell>
                      <Badge className={getEstadoColor(factura.estado)}>
                        <span className="flex items-center gap-1">
                          {getEstadoIcon(factura.estado)}
                          {factura.estado}
                        </span>
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs">
                      {format(new Date(factura.created_at), "dd/MM/yyyy", { locale: es })}
                    </TableCell>
                    <TableCell>
                      {factura.pdf_url ? (
                        <Button variant="ghost" size="sm" asChild>
                          <a href={factura.pdf_url} target="_blank" rel="noopener noreferrer">
                            <FileText className="h-4 w-4" />
                          </a>
                        </Button>
                      ) : (
                        <span className="text-muted-foreground">N/A</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}