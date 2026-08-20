'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

interface ChartData {
  dia: string
  viajes: number
  facturado: number
}

export function ViajesChart() {
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/tenant/dashboard/charts')
        const json = await res.json()
        
        // ✅ VERIFICAR que sea un array
        const datos = Array.isArray(json) ? json : json?.viajes || []
        setData(datos)
        
        console.log('Datos recibidos:', datos)  // ← Depuración
      } catch (error) {
        console.error('Error fetching chart data:', error)
        setData([])  // ← Si falla, array vacío
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Formatear fechas para mostrar día de la semana
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('es-AR', { weekday: 'short' })
    } catch {
      return dateStr
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Viajes Últimos 7 Días</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        </CardContent>
      </Card>
    )
  }

  // ✅ Verificar que data sea un array
  const chartData = Array.isArray(data) && data.length > 0
    ? data.map(item => ({
        ...item,
        dia: formatDate(item.dia),
      }))
    : []

  if (chartData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Viajes Últimos 7 Días</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No hay datos disponibles
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Viajes Últimos 7 Días</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="dia" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="viajes" fill="#3b82f6" name="Viajes" />
              <Bar yAxisId="right" dataKey="facturado" fill="#22c55e" name="Facturación ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}