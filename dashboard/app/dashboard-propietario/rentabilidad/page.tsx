'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Loader2, TrendingUp, TrendingDown, DollarSign, Car, BarChart3 } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'

interface RentabilidadVehiculo {
  vehiculo_id: string
  patente: string
  ingresos: number
  gastos: number
  canones_recibidos: number
  total_ingresos: number
  ganancia_neta: number
  margen: number
}

interface RentabilidadData {
  periodo: string
  desde: string
  hasta: string
  vehiculos: RentabilidadVehiculo[]
  resumen_total: {
    total_ingresos: number
    total_gastos: number
    total_ganancia_neta: number
    promedio_margen: number
  }
}

export default function PropietarioRentabilidadPage() {
  const router = useRouter()
  const { user } = useAuth()
  
  // ✅ Estado para propietario_id (leído desde la URL)
  const [propietarioId, setPropietarioId] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])
  
  const [data, setData] = useState<RentabilidadData | null>(null)
  const [loading, setLoading] = useState(true)
  const [periodo, setPeriodo] = useState('mes')

  const isAdmin = user?.rol === 'admin'
  // ✅ Usar el estado 'propietarioId' en lugar de searchParams
  // const propietarioId = searchParams?.get('propietario_id')  // ← ELIMINAR

  const cargarRentabilidad = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/api/propietario/rentabilidad?periodo=${periodo}`)
      setData(res.data)
    } catch (error: any) {
      console.error('Error al cargar rentabilidad:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar rentabilidad')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      cargarRentabilidad()
    }
  }, [user, propietarioId, periodo])

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

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
            Análisis financiero de tu flota
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

      {/* Resumen KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <p className="text-xs text-muted-foreground">Total Ingresos</p>
            </div>
            <p className="text-xl font-bold text-green-600">{formatCurrency(resumen_total.total_ingresos)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <p className="text-xs text-muted-foreground">Total Gastos</p>
            </div>
            <p className="text-xl font-bold text-red-600">{formatCurrency(resumen_total.total_gastos)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-primary" />
              <p className="text-xs text-muted-foreground">Ganancia Neta</p>
            </div>
            <p className={`text-xl font-bold ${resumen_total.total_ganancia_neta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(resumen_total.total_ganancia_neta)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-blue-600" />
              <p className="text-xs text-muted-foreground">Margen Promedio</p>
            </div>
            <p className="text-xl font-bold">{resumen_total.promedio_margen}%</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabla de rentabilidad por vehículo */}
      <Card>
        <CardHeader>
          <CardTitle>Rentabilidad por Vehículo</CardTitle>
          <p className="text-sm text-muted-foreground">
            Período: {new Date(data.desde).toLocaleDateString()} - {new Date(data.hasta).toLocaleDateString()}
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
                    <th className="text-left py-3">Ingresos</th>
                    <th className="text-left py-3">Gastos</th>
                    <th className="text-left py-3">Canones</th>
                    <th className="text-left py-3">Total Ingresos</th>
                    <th className="text-left py-3">Ganancia Neta</th>
                    <th className="text-left py-3">Margen</th>
                  </tr>
                </thead>
                <tbody>
                  {vehiculos.map((v) => (
                    <tr key={v.vehiculo_id} className="border-b hover:bg-muted/50">
                      <td className="py-3 font-medium">{v.patente}</td>
                      <td className="py-3">{formatCurrency(v.ingresos)}</td>
                      <td className="py-3 text-red-600">{formatCurrency(v.gastos)}</td>
                      <td className="py-3">{formatCurrency(v.canones_recibidos)}</td>
                      <td className="py-3 font-semibold">{formatCurrency(v.total_ingresos)}</td>
                      <td className={`py-3 font-bold ${v.ganancia_neta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(v.ganancia_neta)}
                      </td>
                      <td className="py-3">
                        <Badge variant={v.margen >= 20 ? 'default' : 'destructive'}>
                          {v.margen}%
                        </Badge>
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