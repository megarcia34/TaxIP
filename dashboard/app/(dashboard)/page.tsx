'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { KpiCards } from '@/components/dashboard/KpiCards'
import { MapSimple } from '@/components/dashboard/MapSimple'
import { SolicitudesActivas } from '@/components/dashboard/SolicitudesActivas'
import { ChoferesOnline } from '@/components/dashboard/ChoferesOnline'
import { ViajesChart } from '@/components/dashboard/ViajesChart'
import { RankingChoferes } from '@/components/dashboard/RankingChoferes'
import { AlertasNegocio } from '@/components/dashboard/AlertasNegocio'

export default function DashboardPage() {
  const pathname = usePathname()
  const [mapKey, setMapKey] = useState(0)

  useEffect(() => {
    setMapKey(prev => prev + 1)
  }, [pathname])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Bienvenido de vuelta. Aquí está el resumen de tu flota en tiempo real.
        </p>
      </div>

      {/* KPIs */}
      <KpiCards />

      {/* Fila 1: Mapa + Solicitudes */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2" style={{ minHeight: '500px' }}>
          <div className="rounded-lg border bg-card overflow-hidden" style={{ height: '500px', minHeight: '500px' }}>
            <MapSimple key={`map-${mapKey}`} />
          </div>
        </div>
        <div>
          <SolicitudesActivas />
        </div>
      </div>

      {/* Fila 2: Gráfico + Ranking */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ViajesChart />
        <RankingChoferes />
      </div>

      {/* Fila 3: Choferes Online + Alertas */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ChoferesOnline />
        <AlertasNegocio />
      </div>
    </div>
  )
}