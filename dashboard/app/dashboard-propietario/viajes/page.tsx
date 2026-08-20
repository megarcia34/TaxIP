'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { TripsDataTable } from '@/components/propietario/viajes/TripsDataTable'
import { TripFilters } from '@/components/propietario/viajes/TripFilters'
import { TripExportButtons } from '@/components/propietario/viajes/TripExportButtons'
import { useViajesData } from '@/hooks/propietario'

export default function ViajesPage() {
  const [filters, setFilters] = useState({
    vehiculoId: '',
    choferId: '',
    fechaDesde: '',
    fechaHasta: '',
    estado: '',
    metodoPago: '',
    fuente: '',
    search: '',
    page: 1,
    pageSize: 10,
  })

  const { data, isLoading } = useViajesData(filters)

  // Lista de choferes mock (esto vendrá del backend)
  const choferes = [
    { id: 'c1', nombre: 'Juan', apellido: 'Pérez' },
    { id: 'c2', nombre: 'María', apellido: 'López' },
  ]

  const handlePageChange = (page: number) => {
    setFilters({ ...filters, page })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Viajes</h1>
          <p className="text-muted-foreground">
            Historial completo de viajes de tu flota
          </p>
        </div>
        <TripExportButtons data={(data as any)?.viajes || []} />
      </div>

      <Card>
        <CardHeader>
          <TripFilters
            filters={filters}
            onFiltersChange={(newFilters) => setFilters({ ...newFilters, page: 1 })}
            choferes={choferes}
          />
        </CardHeader>
        <CardContent>
          <TripsDataTable
            data={(data as any)?.viajes || []}
            total={(data as any)?.total || 0}
            pageSize={filters.pageSize}
            pageIndex={filters.page - 1}
            onPageChange={handlePageChange}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>
    </div>
  )
}