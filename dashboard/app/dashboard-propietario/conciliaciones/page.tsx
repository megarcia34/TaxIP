'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Search, AlertCircle, CheckCircle2, Clock, Loader2, DollarSign
} from 'lucide-react'
import { toast } from 'sonner'
import {
  conciliacionesAPI,
  ConciliacionPendienteItem,
  ConciliacionHistorialItem,
} from '@/lib/api/conciliaciones'

type Tab = 'pendientes' | 'historial'

export default function ConciliacionesPage() {
  const [tab, setTab] = useState<Tab>('pendientes')
  const [turnos, setTurnos] = useState<ConciliacionPendienteItem[]>([])
  const [historial, setHistorial] = useState<ConciliacionHistorialItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const cargarPendientes = async () => {
    setLoading(true)
    try {
      const data = await conciliacionesAPI.listar()
      setTurnos(data.turnos)
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al cargar conciliaciones')
    } finally {
      setLoading(false)
    }
  }

  const cargarHistorial = async () => {
    setLoading(true)
    try {
      const data = await conciliacionesAPI.historial()
      setHistorial(data.conciliaciones)
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al cargar historial')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (tab === 'pendientes') cargarPendientes()
    else cargarHistorial()
  }, [tab])

  const filteredPendientes = turnos.filter(t =>
    t.vehiculo_patente.toLowerCase().includes(search.toLowerCase()) ||
    t.chofer_nombre.toLowerCase().includes(search.toLowerCase())
  )
  const filteredHistorial = historial.filter(h =>
    h.vehiculo_patente.toLowerCase().includes(search.toLowerCase()) ||
    h.chofer_nombre.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Conciliaciones</h1>
          <p className="text-muted-foreground">
            Gestión de cierres de turnos y liquidaciones
          </p>
        </div>
        <Button variant="outline" onClick={tab === 'pendientes' ? cargarPendientes : cargarHistorial}>
          Actualizar
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setTab('pendientes')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === 'pendientes'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Pendientes ({turnos.length})
        </button>
        <button
          onClick={() => setTab('historial')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === 'historial'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Historial ({historial.length})
        </button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>{tab === 'pendientes' ? 'Turnos Pendientes' : 'Conciliaciones Cerradas'}</CardTitle>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por patente o chofer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : tab === 'pendientes' ? (
            filteredPendientes.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle2 className="h-12 w-12 mx-auto mb-3 text-green-500/50" />
                <p>No hay conciliaciones pendientes</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3">Vehículo</th>
                      <th className="text-left py-3">Chofer</th>
                      <th className="text-left py-3">Contrato</th>
                      <th className="text-right py-3">Recaudación</th>
                      <th className="text-right py-3">Gastos</th>
                      <th className="text-right py-3">Diferencia</th>
                      <th className="text-center py-3">Días</th>
                      <th className="text-right py-3">Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPendientes.map((t) => (
                      <tr key={t.turno_id} className="border-b hover:bg-muted/50">
                        <td className="py-3 font-medium">{t.vehiculo_patente}</td>
                        <td className="py-3">{t.chofer_nombre}</td>
                        <td className="py-3"><Badge variant="outline">{t.tipo_contrato}</Badge></td>
                        <td className="py-3 text-right font-semibold">${t.recaudacion_declarada.toLocaleString()}</td>
                        <td className="py-3 text-right text-red-500">-${t.gastos_declarados.toLocaleString()}</td>
                        <td className={`py-3 text-right font-semibold ${t.diferencia < 0 ? 'text-red-600' : t.diferencia > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                          ${t.diferencia.toLocaleString()}
                        </td>
                        <td className="py-3 text-center">
                          <Badge variant={t.dias_restantes <= 2 ? 'destructive' : 'secondary'}>
                            {t.dias_restantes}d
                          </Badge>
                        </td>
                        <td className="py-3 text-right">
                          <Link href={`/dashboard-propietario/conciliaciones/${t.turno_id}`}>
                            <Button size="sm">Conciliar</Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            filteredHistorial.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
                <p>No hay conciliaciones cerradas</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3">Vehículo</th>
                      <th className="text-left py-3">Chofer</th>
                      <th className="text-left py-3">Conciliado</th>
                      <th className="text-right py-3">Recaudación</th>
                      <th className="text-right py-3">Chofer</th>
                      <th className="text-right py-3">Propietario</th>
                      <th className="text-right py-3">Deuda Pendiente</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredHistorial.map((h) => (
                      <tr key={h.turno_id} className="border-b hover:bg-muted/50">
                        <td className="py-3 font-medium">{h.vehiculo_patente}</td>
                        <td className="py-3">{h.chofer_nombre}</td>
                        <td className="py-3 text-muted-foreground">
                          {h.conciliado_en ? new Date(h.conciliado_en).toLocaleString('es-AR') : '-'}
                        </td>
                        <td className="py-3 text-right font-semibold">${h.recaudacion_total.toLocaleString()}</td>
                        <td className="py-3 text-right text-green-600">${h.total_chofer.toLocaleString()}</td>
                        <td className="py-3 text-right">${h.total_propietario.toLocaleString()}</td>
                        <td className={`py-3 text-right font-semibold ${h.deuda_pendiente > 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
                          {h.deuda_pendiente > 0 ? `$${h.deuda_pendiente.toLocaleString()}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
        </CardContent>
      </Card>
    </div>
  )
}