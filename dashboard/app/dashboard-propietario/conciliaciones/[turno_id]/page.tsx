'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  ArrowLeft, Check, X, Loader2, AlertCircle, CheckCircle2,
  DollarSign, Wallet, Receipt, Car, Globe, Smartphone, Building2, Monitor
} from 'lucide-react'
import { toast } from 'sonner'
import { conciliacionesAPI, ConciliacionDetalle } from '@/lib/api/conciliaciones'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

// ============================================
// HELPERS VISUALES
// ============================================
const formatCurrency = (v: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(v)

const getOrigenIcon = (tipo: string) => {
  switch (tipo) {
    case 'via_publica': return <Car className="h-4 w-4 text-muted-foreground" />
    case 'plataforma': return <Globe className="h-4 w-4 text-blue-500" />
    case 'qr_comercio': return <Smartphone className="h-4 w-4 text-purple-500" />
    case 'corporativo': return <Building2 className="h-4 w-4 text-orange-500" />
    case 'despacho_manual': return <Monitor className="h-4 w-4 text-green-500" />
    default: return <Globe className="h-4 w-4 text-muted-foreground" />
  }
}

const getOrigenLabel = (tipo: string) => {
  switch (tipo) {
    case 'via_publica': return 'Calle'
    case 'plataforma': return 'App/Landing'
    case 'qr_comercio': return 'Código QR'
    case 'corporativo': return 'Corporativo'
    case 'despacho_manual': return 'Operativo'
    default: return tipo
  }
}

const getMetodoPagoLabel = (m: string) => {
  switch (m) {
    case 'efectivo': return 'Efectivo'
    case 'tarjeta_debito': return 'Tarjeta Débito'
    case 'tarjeta_credito': return 'Tarjeta Crédito'
    case 'qr': return 'QR'
    case 'transferencia': return 'Transferencia'
    default: return m
  }
}

export default function ConciliacionDetallePage() {
  const params = useParams()
  const router = useRouter()
  const turnoId = params.turno_id as string

  const [detalle, setDetalle] = useState<ConciliacionDetalle | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Modal rechazo
  const [rechazoModal, setRechazoModal] = useState<{ gastoId: string } | null>(null)
  const [motivoRechazo, setMotivoRechazo] = useState('')

  // Modal cierre
  const [cierreModal, setCierreModal] = useState(false)
  const [observaciones, setObservaciones] = useState('')

  const cargar = async () => {
    setLoading(true)
    try {
      const data = await conciliacionesAPI.detalle(turnoId)
      setDetalle(data)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Error al cargar detalle')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (turnoId) cargar()
  }, [turnoId])

  const handleAprobar = async (gastoId: string) => {
    setActionLoading(gastoId)
    try {
      await conciliacionesAPI.aprobarGasto(turnoId, gastoId)
      toast.success('Gasto aprobado')
      await cargar()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al aprobar')
    } finally {
      setActionLoading(null)
    }
  }

  const handleRechazar = async () => {
    if (!rechazoModal || !motivoRechazo.trim()) return
    setActionLoading(rechazoModal.gastoId)
    try {
      await conciliacionesAPI.rechazarGasto(turnoId, rechazoModal.gastoId, motivoRechazo)
      toast.success('Gasto rechazado')
      setRechazoModal(null)
      setMotivoRechazo('')
      await cargar()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al rechazar')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCerrar = async () => {
    setActionLoading('cerrar')
    try {
      await conciliacionesAPI.cerrar(turnoId, observaciones)
      toast.success('Conciliación cerrada y liquidación generada')
      setCierreModal(false)
      router.push('/dashboard-propietario/conciliaciones')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al cerrar')
    } finally {
      setActionLoading(null)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!detalle) return null

  const gastosPendientes = detalle.gastos.filter(g => g.estado_aprobacion === 'pendiente').length
  const desglose = (detalle as any).desglose_viajes || [] // Fallback si el backend aún no lo manda

  return (
    <div className="space-y-6 pb-10">
      {/* HEADER */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Volver
        </Button>
        <div>
          <h1 className="text-2xl font-bold">
            Conciliar Turno · {detalle.vehiculo_patente}
          </h1>
          <p className="text-muted-foreground">
            {detalle.chofer_nombre} · {detalle.tipo_contrato}
          </p>
        </div>
      </div>

      {/* 1. TARJETAS SUPERIORES MEJORADAS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" /> Recaudación Total
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatCurrency(detalle.recaudacion_total)}</p>
            <p className="text-xs text-muted-foreground">
              Viajes {formatCurrency(detalle.recaudacion_viajes)} + Manual {formatCurrency(detalle.recaudacion_manual)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Wallet className="h-3 w-3" /> Efectivo en Mano
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatCurrency(detalle.efectivo_en_mano)}</p>
            <p className="text-xs text-muted-foreground">
              Calculado (viajes + manual)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Receipt className="h-3 w-3" /> Gastos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">
              {formatCurrency(detalle.gastos_total)}
            </p>
            <p className="text-xs text-muted-foreground">{detalle.gastos.length} gasto(s)</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              {detalle.diferencia_efectivo === 0 ? (
                <CheckCircle2 className="h-3 w-3 text-green-600" />
              ) : (
                <AlertCircle className="h-3 w-3 text-red-500" />
              )}
              Diferencia Efectivo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${
              detalle.diferencia_efectivo === 0 ? 'text-green-600' : 'text-red-500'
            }`}>
              {formatCurrency(detalle.diferencia_efectivo)}
            </p>
            <p className="text-xs text-muted-foreground">
              {detalle.diferencia_efectivo === 0 ? 'Caja cuadrada' : 'Revisar diferencia'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 2. ESTADO DE CUENTA */}
      <Card>
        <CardHeader>
          <CardTitle>Estado de Cuenta del Turno</CardTitle>
          <CardDescription>
            Operación matemática de ingresos, gastos y liquidación final.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[220px]">Concepto</TableHead>
                <TableHead>Detalle</TableHead>
                <TableHead className="text-right">Ingresos</TableHead>
                <TableHead className="text-right">Egresos</TableHead>
                <TableHead className="text-right">Saldo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Recaudación Viajes</TableCell>
                <TableCell className="text-muted-foreground">
                  {desglose.reduce((acc: number, v: any) => acc + v.cantidad, 0) || '-'} viajes finalizados
                </TableCell>
                <TableCell className="text-right text-green-600 font-medium">
                  {formatCurrency(detalle.recaudacion_viajes)}
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Gastos Declarados</TableCell>
                <TableCell className="text-muted-foreground">
                  {detalle.gastos.length} gasto(s) declarado(s)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right text-red-500 font-medium">
                  {formatCurrency(detalle.gastos_total)}
                </TableCell>
                <TableCell className="text-right">—</TableCell>
              </TableRow>

              <TableRow className="bg-muted/50 font-semibold">
                <TableCell colSpan={2}>Subtotal Operativo</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.recaudacion_viajes)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.gastos_total)}
                </TableCell>
                <TableCell className="text-right text-lg">
                  {formatCurrency(detalle.recaudacion_viajes - detalle.gastos_total)}
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Efectivo Calculado</TableCell>
                <TableCell className="text-muted-foreground">
                  Viajes efectivo + Manual
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.efectivo_en_mano)}
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Diferencia de Caja</TableCell>
                <TableCell className="text-muted-foreground">
                  Calculado - Declarado
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className={`text-right font-bold ${
                  detalle.diferencia_efectivo === 0 ? 'text-green-600' : 'text-red-500'
                }`}>
                  {formatCurrency(detalle.diferencia_efectivo)}
                </TableCell>
              </TableRow>

              <TableRow className="bg-primary/5">
                <TableCell colSpan={5} className="font-bold text-primary py-3">
                  Resultado de la Liquidación (Contrato {detalle.tipo_contrato})
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">A favor del Propietario</TableCell>
                <TableCell className="text-muted-foreground">
                  (Recaudación - Gastos)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right font-bold text-primary">
                  {formatCurrency(detalle.recaudacion_total - detalle.gastos_total)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">A favor del Chofer</TableCell>
                <TableCell className="text-muted-foreground">
                  (Comisión / Salario)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right font-bold">
                  $0.00
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 3. DESGLOSE DE VIAJES (Si el backend lo devuelve) */}
      {desglose.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Resumen de Operación (Viajes)</CardTitle>
            <CardDescription>
              Desglose de los viajes por canal y método de pago.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Canal</TableHead>
                  <TableHead>Método de Pago</TableHead>
                  <TableHead className="text-right">Cantidad</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {desglose.map((item: any, idx: number) => (
                  <TableRow key={idx}>
                    <TableCell className="flex items-center gap-2">
                      {getOrigenIcon(item.origen_tipo)}
                      <span>{getOrigenLabel(item.origen_tipo)}</span>
                    </TableCell>
                    <TableCell>{getMetodoPagoLabel(item.metodo_pago)}</TableCell>
                    <TableCell className="text-right">{item.cantidad}</TableCell>
                    <TableCell className="text-right font-medium">
                      {formatCurrency(item.total)}
                    </TableCell>
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-semibold">
                  <TableCell colSpan={2}>TOTAL</TableCell>
                  <TableCell className="text-right">
                    {desglose.reduce((acc: number, v: any) => acc + v.cantidad, 0)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(detalle.recaudacion_viajes)}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* 4. GASTOS DECLARADOS */}
      <Card>
        <CardHeader>
          <CardTitle>Gastos Declarados ({detalle.gastos.length})</CardTitle>
          <CardDescription>
            Aprobá o rechazá los gastos declarados por el chofer.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {detalle.gastos.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Sin gastos</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead className="text-right">Monto</TableHead>
                  <TableHead className="text-center">Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detalle.gastos.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-medium">{g.tipo_gasto}</TableCell>
                    <TableCell className="text-muted-foreground">{g.descripcion || '-'}</TableCell>
                    <TableCell className="text-right font-semibold">${g.monto.toLocaleString()}</TableCell>
                    <TableCell className="text-center">
                      <Badge
                        variant={g.estado_aprobacion === 'rechazado' ? 'destructive' : 'outline'}
                        className={
                          g.estado_aprobacion === 'aprobado'
                          ? 'bg-green-100 text-green-700 border-green-300'
                          : g.estado_aprobacion === 'pendiente'
                          ? 'bg-yellow-100 text-yellow-700 border-yellow-300'
                          : ''
                        }
                      >
                        {g.estado_aprobacion}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {g.estado_aprobacion === 'pendiente' && (
                        <div className="flex gap-2 justify-end">
                          <Button size="sm" variant="outline" onClick={() => handleAprobar(g.id)} disabled={actionLoading === g.id}>
                            {actionLoading === g.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4 text-green-600" />}
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setRechazoModal({ gastoId: g.id })} disabled={actionLoading === g.id}>
                            <X className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* 5. DIFERENCIAS REGISTRADAS */}
      {detalle.diferencias.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Diferencias Registradas</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Concepto</TableHead>
                  <TableHead className="text-right">Monto</TableHead>
                  <TableHead className="text-center">Estado</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detalle.diferencias.map((d) => (
                  <TableRow key={d.id}>
                    <TableCell>
                      <Badge variant={d.tipo === 'DEUDA_CHOFER' ? 'destructive' : 'secondary'}>
                        {d.tipo}
                      </Badge>
                    </TableCell>
                    <TableCell>{d.concepto}</TableCell>
                    <TableCell className="text-right font-semibold">${d.monto.toLocaleString()}</TableCell>
                    <TableCell className="text-center">
                      <Badge
                        variant="outline"
                        className={
                          d.estado === 'SALDADA'
                          ? 'bg-green-100 text-green-700 border-green-300'
                          : 'bg-yellow-100 text-yellow-700 border-yellow-300'
                        }
                      >
                        {d.estado}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* 6. CIERRE */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-center">
            <div>
              {gastosPendientes > 0 ? (
                <p className="text-sm text-orange-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Quedan {gastosPendientes} gasto(s) pendientes de aprobar. Al cerrar, se aprobarán automáticamente.
                </p>
              ) : (
                <p className="text-sm text-green-600 flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  Listo para cerrar la conciliación y generar la liquidación.
                </p>
              )}
            </div>
            <Button
              onClick={() => setCierreModal(true)}
              disabled={!detalle.puede_cerrar && gastosPendientes === 0}
            >
              Cerrar Conciliación
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* MODALES (Sin cambios) */}
      <Dialog open={!!rechazoModal} onOpenChange={(o) => !o && setRechazoModal(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rechazar Gasto</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Label>Motivo del rechazo</Label>
            <Input
              value={motivoRechazo}
              onChange={(e) => setMotivoRechazo(e.target.value)}
              placeholder="Ej: Comprobante ilegible"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRechazoModal(null)}>Cancelar</Button>
            <Button variant="destructive" onClick={handleRechazar} disabled={!motivoRechazo.trim()}>
              Rechazar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={cierreModal} onOpenChange={setCierreModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Cierre de Conciliación</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p className="text-sm text-muted-foreground">
              Al cerrar, se generará la liquidación final del turno. 
              {detalle.diferencia_efectivo !== 0 && (
                <span className="block mt-2 font-semibold text-orange-600">
                  Se registrará una deuda por la diferencia de efectivo de ${Math.abs(detalle.diferencia_efectivo).toLocaleString()}.
                </span>
              )}
            </p>
            <Label>Observaciones (opcional)</Label>
            <Input
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              placeholder="Observaciones..."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCierreModal(false)}>Cancelar</Button>
            <Button onClick={handleCerrar} disabled={actionLoading === 'cerrar'}>
              {actionLoading === 'cerrar' && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Confirmar Cierre
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}