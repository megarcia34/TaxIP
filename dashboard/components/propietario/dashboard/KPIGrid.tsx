// components/propietario/dashboard/KPIGrid.tsx

'use client'

import { KPICard } from './KPICard'
import { DollarSign, Car, Clock, Wifi } from 'lucide-react'

interface KPIGridProps {
  data?: {
    neto_hoy: number
    total_viajes_hoy: number
    saldo_semana: number
    flota_activa: number
    flota_total: number
    detalle_neto?: Array<{ vehiculo_id: string; patente: string; valor: number }>
    detalle_viajes?: Array<{ vehiculo_id: string; patente: string; viajes: number }>
    detalle_saldo?: Array<{ vehiculo_id: string; patente: string; valor: number }>
    detalle_flota?: Array<{ vehiculo_id: string; patente: string; estado: string; chofer_nombre: string }>
  }
  loading?: boolean
}

export function KPIGrid({ data, loading = false }: KPIGridProps) {
  // Si no hay datos, mostrar valores por defecto
  const netoHoy = data?.neto_hoy ?? 0
  const totalViajes = data?.total_viajes_hoy ?? 0
  const saldoSemana = data?.saldo_semana ?? 0
  const flotaActiva = data?.flota_activa ?? 0

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <KPICard
        title="Neto Propietario (Hoy)"
        value={netoHoy}
        icon={<DollarSign className="h-4 w-4" />}
        detailData={data?.detalle_neto}
        detailTitle="Neto por vehículo (Hoy)"
        detailValueLabel="Neto"
        loading={loading}
      />

      <KPICard
        title="Total Viajes (Hoy)"
        value={totalViajes}
        icon={<Car className="h-4 w-4" />}
        detailData={data?.detalle_viajes?.map((d) => ({ ...d, valor: d.viajes }))}
        detailTitle="Viajes por vehículo (Hoy)"
        detailValueLabel="Viajes"
        detailSecondaryLabel=""
        loading={loading}
      />

      <KPICard
        title="Saldo a Liquidar (Semana)"
        value={saldoSemana}
        icon={<Clock className="h-4 w-4" />}
        detailData={data?.detalle_saldo}
        detailTitle="Saldo por vehículo (Semana)"
        detailValueLabel="Saldo"
        loading={loading}
      />

      <KPICard
        title="Estado de Flota"
        value={flotaActiva}
        icon={<Wifi className="h-4 w-4" />}
        detailData={data?.detalle_flota?.map((d) => ({
          vehiculo_id: d.vehiculo_id,
          patente: d.patente,
          valor: d.estado === 'ocupado' ? 1 : d.estado === 'libre' ? 0 : -1,
        }))}
        detailTitle="Estado de vehículos"
        detailValueLabel="Estado"
        detailSecondaryLabel=""
        loading={loading}
      />
    </div>
  )
}