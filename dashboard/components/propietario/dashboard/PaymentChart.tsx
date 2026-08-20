// components/propietario/dashboard/PaymentChart.tsx

'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface PaymentChartProps {
  data?: Array<{
    dia: string
    efectivo: number
    qr: number
    debito: number
  }>
  loading?: boolean
}

export function PaymentChart({ data, loading = false }: PaymentChartProps) {
  const colors = {
    efectivo: '#f59e0b',
    qr: '#06b6d4',
    debito: '#3b82f6',
  }

  const hasData = data && data.length > 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          Distribución de Medios de Pago
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px]">
          {loading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : hasData ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" />
                <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />

                <Tooltip 
                  formatter={(value: any) => {
                    if (value === undefined || value === null || value === 0) return '$0'
                     return `$${value.toLocaleString()}`
           }} 
                />
                <Legend />
                <Bar dataKey="efectivo" name="💰 Efectivo" fill={colors.efectivo} stackId="a" />
                <Bar dataKey="qr" name="📱 QR" fill={colors.qr} stackId="a" />
                <Bar dataKey="debito" name="💳 Débito" fill={colors.debito} stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
              No hay datos de pagos disponibles
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}