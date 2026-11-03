'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Check, X, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'
import { conciliacionesAPI, ConciliacionDetalle } from '@/lib/api/conciliaciones'

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

  return (
    <div className="space-y-6">
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

      {/* Resumen financiero */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Recaudación</p>
            <p className="text-xl font-bold">${detalle.recaudacion_total.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Efectivo en mano</p>
            <p className="text-xl font-bold">${detalle.efectivo_en_mano.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Gastos</p>
            <p className="text-xl font-bold text-red-500">-${detalle.gastos_total.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Diferencia efectivo</p>
            <p className={`text-xl font-bold ${detalle.diferencia_efectivo < 0 ? 'text-red-600' : detalle.diferencia_efectivo > 0 ? 'text-orange-600' : 'text-green-600'}`}>
              ${detalle.diferencia_efectivo.toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gastos */}
      <Card>
        <CardHeader>
          <CardTitle>Gastos Declarados ({detalle.gastos.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {detalle.gastos.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Sin gastos</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Tipo</th>
                    <th className="text-left py-3">Descripción</th>
                    <th className="text-right py-3">Monto</th>
                    <th className="text-center py-3">Estado</th>
                    <th className="text-right py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {detalle.gastos.map((g) => (
                    <tr key={g.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 font-medium">{g.tipo_gasto}</td>
                      <td className="py-3 text-muted-foreground">{g.descripcion || '-'}</td>
                      <td className="py-3 text-right font-semibold">${g.monto.toLocaleString()}</td>
                      <td className="py-3 text-center">
                        <Badge
                          variant={
                            g.estado_aprobacion === 'rechazado' ? 'destructive' : 'outline'
                          }
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
                      </td>
                      <td className="py-3 text-right">
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
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Diferencias */}
      {detalle.diferencias.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Diferencias Registradas</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3">Tipo</th>
                  <th className="text-left py-3">Concepto</th>
                  <th className="text-right py-3">Monto</th>
                  <th className="text-center py-3">Estado</th>
                </tr>
              </thead>
              <tbody>
                {detalle.diferencias.map((d) => (
                  <tr key={d.id} className="border-b">
                    <td className="py-3">
                      <Badge variant={d.tipo === 'DEUDA_CHOFER' ? 'destructive' : 'secondary'}>
                        {d.tipo}
                      </Badge>
                    </td>
                    <td className="py-3">{d.concepto}</td>
                    <td className="py-3 text-right font-semibold">${d.monto.toLocaleString()}</td>
                    <td className="py-3 text-center">
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
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Cierre */}
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

      {/* Modal rechazo */}
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

      {/* Modal cierre */}
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