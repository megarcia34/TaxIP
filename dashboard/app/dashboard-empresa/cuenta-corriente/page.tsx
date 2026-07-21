'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Loader2,
  Wallet,
  CreditCard,
  DollarSign,
  TrendingUp,
  Clock,
  FileText,
  Plus,
  Download,
  History,
  CheckCircle,
  XCircle,
  AlertCircle,
  Calendar,
} from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface CuentaCorriente {
  empresa_id: string
  empresa_nombre: string
  limite_credito: number
  saldo_disponible: number
  deuda_total: number
  total_pagado: number
  viajes_pendientes: number
  facturas_pendientes: number
}

interface Pago {
  id: string
  monto: number
  metodo_pago: string
  referencia: string
  estado: string
  comprobante_url: string
  observaciones: string
  fecha_pago: string
  confirmado_en: string
  factura: {
    periodo: string
    total: number
  } | null
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

const formatFecha = (fecha: string | undefined | null) => {
  if (!fecha) return 'N/A'
  try {
    return format(new Date(fecha), "dd/MM/yyyy HH:mm", { locale: es })
  } catch {
    return 'N/A'
  }
}

const getEstadoColor = (estado: string) => {
  const colores: Record<string, string> = {
    pendiente: 'bg-yellow-500',
    confirmado: 'bg-green-500',
    rechazado: 'bg-red-500',
    cancelado: 'bg-gray-500',
  }
  return colores[estado] || 'bg-gray-500'
}

const getEstadoLabel = (estado: string) => {
  const labels: Record<string, string> = {
    pendiente: 'Pendiente',
    confirmado: 'Confirmado',
    rechazado: 'Rechazado',
    cancelado: 'Cancelado',
  }
  return labels[estado] || estado
}

const getMetodoPagoLabel = (metodo: string) => {
  const labels: Record<string, string> = {
    transferencia: 'Transferencia',
    efectivo: 'Efectivo',
    tarjeta: 'Tarjeta',
    deposito: 'Depósito',
    otros: 'Otros',
  }
  return labels[metodo] || metodo
}

export default function EmpresaCuentaCorrientePage() {
  const [showPagoModal, setShowPagoModal] = useState(false)
  const [monto, setMonto] = useState('')
  const [metodoPago, setMetodoPago] = useState('transferencia')
  const [referencia, setReferencia] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [activeTab, setActiveTab] = useState('resumen')
  const queryClient = useQueryClient()

  // ========== QUERIES ==========
  const { data: cuenta, isLoading: isLoadingCuenta } = useQuery<CuentaCorriente>({
    queryKey: ['empresa-cuenta-corriente'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/cuenta-corriente')
      return response.data
    },
  })

  const { data: historialPagos, isLoading: isLoadingHistorial } = useQuery<Pago[]>({
    queryKey: ['empresa-historial-pagos'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/cuenta-corriente/historial-pagos?limit=50')
      return response.data
    },
    enabled: activeTab === 'historial',
  })

  // ========== MUTATIONS ==========
  const pagoMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/empresa/dashboard/cuenta-corriente/pagar', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Pago registrado correctamente. Pendiente de confirmación.')
      queryClient.invalidateQueries({ queryKey: ['empresa-cuenta-corriente'] })
      queryClient.invalidateQueries({ queryKey: ['empresa-historial-pagos'] })
      setShowPagoModal(false)
      resetForm()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Error al registrar el pago'
      toast.error(message)
    },
  })

  // ========== FUNCIONES ==========
  const resetForm = () => {
    setMonto('')
    setMetodoPago('transferencia')
    setReferencia('')
    setObservaciones('')
  }

  const handleSubmitPago = () => {
    if (!monto || parseFloat(monto) <= 0) {
      toast.error('Ingrese un monto válido')
      return
    }

    if (parseFloat(monto) > (cuenta?.deuda_total || 0)) {
      toast.error(`El monto (${formatMoneda(parseFloat(monto))}) supera la deuda total (${formatMoneda(cuenta?.deuda_total)})`)
      return
    }

    pagoMutation.mutate({
      monto: parseFloat(monto),
      metodo_pago: metodoPago,
      referencia: referencia || undefined,
      observaciones: observaciones || undefined,
    })
  }

  if (isLoadingCuenta) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Wallet className="h-6 w-6" />
            Cuenta Corriente
          </h1>
          <p className="text-muted-foreground">
            Estado y gestión de la cuenta corriente de la empresa
          </p>
        </div>
        <Button onClick={() => setShowPagoModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Realizar Pago
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="resumen">Resumen</TabsTrigger>
          <TabsTrigger value="historial" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Historial de Pagos
          </TabsTrigger>
        </TabsList>

        {/* TAB 1: RESUMEN */}
        <TabsContent value="resumen" className="space-y-6">
          {/* KPIs */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Límite de Crédito</p>
                    <p className="text-2xl font-bold">{formatMoneda(cuenta?.limite_credito)}</p>
                  </div>
                  <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                    <CreditCard className="h-5 w-5 text-blue-600 dark:text-blue-300" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Saldo Disponible</p>
                    <p className={`text-2xl font-bold ${(cuenta?.saldo_disponible || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatMoneda(cuenta?.saldo_disponible)}
                    </p>
                  </div>
                  <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
                    <Wallet className="h-5 w-5 text-green-600 dark:text-green-300" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Deuda Total</p>
                    <p className="text-2xl font-bold text-red-600">{formatMoneda(cuenta?.deuda_total)}</p>
                  </div>
                  <div className="rounded-full bg-red-100 p-3 dark:bg-red-900">
                    <DollarSign className="h-5 w-5 text-red-600 dark:text-red-300" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Pagado</p>
                    <p className="text-2xl font-bold">{formatMoneda(cuenta?.total_pagado)}</p>
                  </div>
                  <div className="rounded-full bg-purple-100 p-3 dark:bg-purple-900">
                    <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-300" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detalles */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Viajes Pendientes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-orange-100 p-3 dark:bg-orange-900">
                    <Clock className="h-5 w-5 text-orange-600 dark:text-orange-300" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold">{cuenta?.viajes_pendientes || 0}</p>
                    <p className="text-sm text-muted-foreground">Viajes en curso o pendientes</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Facturas Pendientes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
                    <FileText className="h-5 w-5 text-yellow-600 dark:text-yellow-300" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold">{cuenta?.facturas_pendientes || 0}</p>
                    <p className="text-sm text-muted-foreground">Facturas por pagar</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumen de cuenta */}
          <Card>
            <CardHeader>
              <CardTitle>Resumen de Cuenta</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between border-b py-2">
                  <span className="text-muted-foreground">Empresa</span>
                  <span className="font-medium">{cuenta?.empresa_nombre}</span>
                </div>
                <div className="flex justify-between border-b py-2">
                  <span className="text-muted-foreground">Límite de Crédito</span>
                  <span className="font-medium">{formatMoneda(cuenta?.limite_credito)}</span>
                </div>
                <div className="flex justify-between border-b py-2">
                  <span className="text-muted-foreground">Saldo Disponible</span>
                  <span className={`font-medium ${(cuenta?.saldo_disponible || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatMoneda(cuenta?.saldo_disponible)}
                  </span>
                </div>
                <div className="flex justify-between border-b py-2">
                  <span className="text-muted-foreground">Deuda Total</span>
                  <span className="font-medium text-red-600">{formatMoneda(cuenta?.deuda_total)}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-muted-foreground">Total Pagado</span>
                  <span className="font-medium text-green-600">{formatMoneda(cuenta?.total_pagado)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 2: HISTORIAL DE PAGOS */}
        <TabsContent value="historial">
          {isLoadingHistorial ? (
            <div className="flex h-[300px] items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Historial de Pagos</CardTitle>
              </CardHeader>
              <CardContent>
                {historialPagos?.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <p>No hay pagos registrados</p>
                  </div>
                ) : (
                  <div className="relative overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3">Fecha</th>
                          <th className="text-left py-3">Monto</th>
                          <th className="text-left py-3">Método</th>
                          <th className="text-left py-3">Referencia</th>
                          <th className="text-left py-3">Estado</th>
                          <th className="text-left py-3">Factura</th>
                        </tr>
                      </thead>
                      <tbody>
                        {historialPagos?.map((pago) => (
                          <tr key={pago.id} className="border-b hover:bg-muted/50">
                            <td className="py-3 text-xs">{formatFecha(pago.fecha_pago)}</td>
                            <td className="py-3 font-medium">{formatMoneda(pago.monto)}</td>
                            <td className="py-3">{getMetodoPagoLabel(pago.metodo_pago)}</td>
                            <td className="py-3">{pago.referencia || 'N/A'}</td>
                            <td className="py-3">
                              <Badge className={getEstadoColor(pago.estado)}>
                                {getEstadoLabel(pago.estado)}
                              </Badge>
                            </td>
                            <td className="py-3">
                              {pago.factura ? pago.factura.periodo : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* ========== MODAL REALIZAR PAGO ========== */}
      <Dialog open={showPagoModal} onOpenChange={setShowPagoModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              Realizar Pago
            </DialogTitle>
            <DialogDescription>
              Registre un pago a cuenta corriente. El pago quedará pendiente de confirmación.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label>Deuda Total</Label>
                <p className="text-lg font-bold text-red-600">{formatMoneda(cuenta?.deuda_total)}</p>
                <p className="text-xs text-muted-foreground">Monto máximo a pagar</p>
              </div>
              <div className="col-span-2">
                <Label>Monto a Pagar *</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max={cuenta?.deuda_total}
                  value={monto}
                  onChange={(e) => setMonto(e.target.value)}
                  placeholder="0.00"
                />
              </div>
              <div className="col-span-2">
                <Label>Método de Pago *</Label>
                <Select value={metodoPago} onValueChange={setMetodoPago}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="transferencia">Transferencia</SelectItem>
                    <SelectItem value="efectivo">Efectivo</SelectItem>
                    <SelectItem value="tarjeta">Tarjeta</SelectItem>
                    <SelectItem value="deposito">Depósito</SelectItem>
                    <SelectItem value="otros">Otros</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="col-span-2">
                <Label>Referencia (N° de comprobante)</Label>
                <Input
                  value={referencia}
                  onChange={(e) => setReferencia(e.target.value)}
                  placeholder="Número de transferencia o comprobante"
                />
              </div>
              <div className="col-span-2">
                <Label>Observaciones</Label>
                <Input
                  value={observaciones}
                  onChange={(e) => setObservaciones(e.target.value)}
                  placeholder="Observaciones adicionales"
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPagoModal(false)}>
              Cancelar
            </Button>
            <Button
              onClick={handleSubmitPago}
              disabled={pagoMutation.isPending || !monto || parseFloat(monto) <= 0}
              className="bg-green-600 hover:bg-green-700"
            >
              {pagoMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Registrar Pago
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}