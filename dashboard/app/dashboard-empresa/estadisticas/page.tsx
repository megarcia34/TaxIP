'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, TrendingUp, TrendingDown, MapPin, DollarSign, Car } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

interface EstadisticaMensual {
  mes: string
  fecha: string
  total_viajes: number
  viajes_completados: number
  viajes_cancelados: number
  gasto_total: number
  promedio_gasto: number
}

interface TopDestino {
  destino: string
  total_viajes: number
  gasto_total: number
  promedio_gasto: number
}

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

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

export default function EmpresaEstadisticasPage() {
  const { data: mensual, isLoading: mensualLoading } = useQuery<EstadisticaMensual[]>({
    queryKey: ['empresa-estadisticas-mensual'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/estadisticas/mensual?meses=6')
      return response.data
    },
  })

  const { data: topDestinos, isLoading: topLoading } = useQuery<TopDestino[]>({
    queryKey: ['empresa-top-destinos'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/estadisticas/top-destinos?limit=10')
      return response.data
    },
  })

  const { data: cuenta, isLoading: cuentaLoading } = useQuery<CuentaCorriente>({
    queryKey: ['empresa-cuenta-corriente'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/cuenta-corriente')
      return response.data
    },
  })

  if (mensualLoading || topLoading || cuentaLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Estadísticas</h1>
        <p className="text-muted-foreground">
          Análisis detallado de viajes, gastos y tendencias
        </p>
      </div>

      {/* Cuenta Corriente Resumen */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Límite de Crédito</p>
            <p className="text-xl font-bold">{formatMoneda(cuenta?.limite_credito)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Saldo Disponible</p>
            <p className={`text-xl font-bold ${(cuenta?.saldo_disponible || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatMoneda(cuenta?.saldo_disponible)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Deuda Total</p>
            <p className="text-xl font-bold text-red-600">{formatMoneda(cuenta?.deuda_total)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Facturas Pendientes</p>
            <p className="text-xl font-bold text-yellow-600">{cuenta?.facturas_pendientes || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Estadísticas Mensuales */}
      <Card>
        <CardHeader>
          <CardTitle>Evolución Mensual</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mensual?.map((stat) => (
              <div key={stat.mes} className="flex items-center justify-between border-b py-3">
                <div>
                  <p className="font-medium">{stat.mes}</p>
                  <div className="flex gap-3 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Car className="h-3 w-3" />
                      {stat.total_viajes} viajes
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3 text-green-500" />
                      {stat.viajes_completados} completados
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingDown className="h-3 w-3 text-red-500" />
                      {stat.viajes_cancelados} cancelados
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatMoneda(stat.gasto_total)}</p>
                  <p className="text-xs text-muted-foreground">
                    Promedio: {formatMoneda(stat.promedio_gasto)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top Destinos */}
      <Card>
        <CardHeader>
          <CardTitle>Top Destinos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topDestinos?.map((destino, idx) => (
              <div key={destino.destino} className="flex items-center justify-between border-b py-3">
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="w-8 h-8 rounded-full flex items-center justify-center">
                    {idx + 1}
                  </Badge>
                  <div>
                    <p className="font-medium flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      {destino.destino}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {destino.total_viajes} viajes • Promedio: {formatMoneda(destino.promedio_gasto)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatMoneda(destino.gasto_total)}</p>
                </div>
              </div>
            ))}
            {topDestinos?.length === 0 && (
              <p className="text-center text-muted-foreground">No hay datos de destinos</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}