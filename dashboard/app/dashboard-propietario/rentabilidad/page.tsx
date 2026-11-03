'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Loader2, TrendingUp, TrendingDown, DollarSign, Car, BarChart3, Percent, Wallet } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'

interface RentabilidadVehiculo {
  vehiculo_id: string
  patente: string
  turnos_conciliados: number
  ingresos: number
  gastos_turno: number
  gastos_vehiculo: number
  comision_chofer: number
  utilidad_neta: number
  margen: number
  roi: number
}

interface RentabilidadData {
  periodo: string
  desde: string
  hasta: string
  vehiculos: RentabilidadVehiculo[]
  resumen_total: {
    total_turnos: number
    total_ingresos: number
    total_gastos_turno: number
    total_gastos_vehiculo: number
    total_gastos: number
    total_comision_chofer: number
    total_utilidad_neta: number
    promedio_margen: number
  }
}

const fmtMoney = (n: number | undefined | null) => {
  if (n === undefined || n === null) return '$0'
  return `$${n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

export default function PropietarioRentabilidadPage() {
  const { user } = useAuth()
  const [propietarioId, setPropietarioId] = useState<string | null>(null)
  const [data, setData] = useState<RentabilidadData | null>(null)
  const [loading, setLoading] = useState(true)
  const [periodo, setPeriodo] = useState('mes')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])

  const cargarRentabilidad = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/api/propietario/rentabilidad?periodo=${periodo}`)
      setData(res.data)
    } catch (error: any) {
      console.error('Error al cargar rentabilidad:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar rentabilidad')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) cargarRentabilidad()
  }, [user, propietarioId, periodo])

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-muted-foreground">No hay datos disponibles</p>
      </div>
    )
  }

  const { resumen_total, vehiculos } = data

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Rentabilidad</h1>
          <p className="text-muted-foreground">
            Análisis financiero de tu flota (post-conciliación)
          </p>
        </div>
        <Tabs value={periodo} onValueChange={setPeriodo} className="w-[240px]">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="dia">Día</TabsTrigger>
            <TabsTrigger value="mes">Mes</TabsTrigger>
            <TabsTrigger value="ano">Año</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <p className="text-xs text-muted-foreground">Ingresos (post-conciliación)</p>
            </div>
            <p className="text-xl font-bold text-green-600">{fmtMoney(resumen_total?.total_ingresos)}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {resumen_total?.total_turnos ?? 0} turnos conciliados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Wallet className="h-4 w-4 text-red-600" />
              <p className="text-xs text-muted-foreground">Gastos Totales</p>
            </div>
            <p className="text-xl font-bold text-red-600">{fmtMoney(resumen_total?.total_gastos)}</p>
            <p className="text-xs text-muted-foreground mt-1">
              Turno {fmtMoney(resumen_total?.total_gastos_turno)} + Vehículo {fmtMoney(resumen_total?.total_gastos_vehiculo)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-primary" />
              <p className="text-xs text-muted-foreground">Utilidad Neta</p>
            </div>
            <p className={`text-xl font-bold ${(resumen_total?.total_utilidad_neta ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {fmtMoney(resumen_total?.total_utilidad_neta)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Percent className="h-4 w-4 text-blue-600" />
              <p className="text-xs text-muted-foreground">Margen Promedio</p>
            </div>
            <p className="text-xl font-bold">{(resumen_total?.promedio_margen ?? 0).toFixed(1)}%</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Rentabilidad por Vehículo</CardTitle>
          <p className="text-sm text-muted-foreground">
            Período: {new Date(data.desde).toLocaleDateString('es-AR')} - {new Date(data.hasta).toLocaleDateString('es-AR')}
          </p>
        </CardHeader>
        <CardContent>
          {vehiculos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Car className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay vehículos con datos en este período</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Vehículo</th>
                    <th className="text-center py-3">Turnos</th>
                    <th className="text-right py-3">Ingresos</th>
                    <th className="text-right py-3">Gastos Turno</th>
                    <th className="text-right py-3">Gastos Vehículo</th>
                    <th className="text-right py-3">Comisión Chofer</th>
                    <th className="text-right py-3">Utilidad Neta</th>
                    <th className="text-center py-3">Margen</th>
                    <th className="text-center py-3">ROI</th>
                  </tr>
                </thead>
                <tbody>
                  {vehiculos.map((v) => (
                    <tr key={v.vehiculo_id} className="border-b hover:bg-muted/50">
                      <td className="py-3 font-medium">{v.patente}</td>
                      <td className="py-3 text-center">{v.turnos_conciliados}</td>
                      <td className="py-3 text-right text-green-600 font-semibold">
                        {fmtMoney(v.ingresos)}
                      </td>
                      <td className="py-3 text-right text-red-600">{fmtMoney(v.gastos_turno)}</td>
                      <td className="py-3 text-right text-red-600">{fmtMoney(v.gastos_vehiculo)}</td>
                      <td className="py-3 text-right text-muted-foreground">{fmtMoney(v.comision_chofer)}</td>
                      <td className={`py-3 text-right font-bold ${v.utilidad_neta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {fmtMoney(v.utilidad_neta)}
                      </td>

                     <td className="py-3 text-center">
                         <Badge variant={(v.margen ?? 0) >= 30 ? 'default' : (v.margen ?? 0) >= 0 ? 'secondary' : 'destructive'}>
                           {(v.margen ?? 0).toFixed(1)}%
                         </Badge>
                     </td>
                    <td className="py-3 text-center text-muted-foreground">
                        {(v.roi ?? 0).toFixed(1)}%
                    </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}