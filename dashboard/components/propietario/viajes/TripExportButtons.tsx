'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Download, FileSpreadsheet, Loader2 } from 'lucide-react'
import { format } from 'date-fns'

// ============================================
// TIPOS
// ============================================

type EstadoViaje = "pendiente" | "aceptado" | "en_curso" | "cancelado" | "finalizado" | "programada";
type FuenteViaje = "app" | "taximetro";

interface ViajePropietario {
  id: string;
  vehiculo_id: string;
  patente: string;
  vehiculo_patente?: string;
  vehiculo_marca?: string;
  vehiculo_modelo?: string;
  chofer_id: string;
  chofer_nombre: string;
  chofer_apellido: string;
  pasajero_nombre?: string;
  direccion_origen: string;
  direccion_destino: string;
  precio_final: number;
  estado: EstadoViaje;
  fuente?: FuenteViaje;
  created_at: string;
  finalizado_at?: string;
  distancia_metros?: number;
  metodo_pago?: string;
  facturado?: boolean;
  comision_pasarela?: number;
  neto_propietario?: number;
}

interface TripExportButtonsProps {
  data: ViajePropietario[]
  filename?: string
  disabled?: boolean
}

// ============================================
// HELPERS
// ============================================

function escapeCSV(value: string | number | undefined | null): string {
  if (value === undefined || value === null) return ''
  const str = String(value)
  // Escapar comillas y envolver si contiene separadores
  if (str.includes(';') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

// ============================================
// COMPONENTE
// ============================================

export function TripExportButtons({ data, filename = 'viajes', disabled }: TripExportButtonsProps) {
  const [isExporting, setIsExporting] = useState(false)

  const exportToCSV = () => {
    if (data.length === 0) return
    setIsExporting(true)

    try {
      const headers = [
        'ID',
        'Fecha',
        'Vehículo',
        'Chofer',
        'Pasajero',
        'Origen',
        'Destino',
        'Monto',
        'Estado',
        'Fuente',
        'Método de Pago',
        'Distancia (km)',
        'Comisión Pasarela',
        'Neto Propietario',
        'Facturado',
      ]

      const rows = data.map((trip) => [
        trip.id,
        format(new Date(trip.created_at), 'dd/MM/yyyy HH:mm'),
        trip.vehiculo_patente || trip.patente || '',
        `${trip.chofer_nombre} ${trip.chofer_apellido}`.trim(),
        trip.pasajero_nombre || '',
        trip.direccion_origen,
        trip.direccion_destino,
        trip.precio_final?.toFixed(2) ?? '0.00',
        trip.estado,
        trip.fuente || '',
        trip.metodo_pago || '',
        trip.distancia_metros ? (trip.distancia_metros / 1000).toFixed(2) : '',
        trip.comision_pasarela?.toFixed(2) ?? '',
        trip.neto_propietario?.toFixed(2) ?? '',
        trip.facturado ? 'Sí' : 'No',
      ])

      // BOM (\uFEFF) para que Excel respete los acentos en UTF-8
      // Separador ";" para Excel en configuración regional en español
      const csvContent = '\uFEFF' + [
        headers.join(';'),
        ...rows.map((row) => row.map(escapeCSV).join(';')),
      ].join('\r\n')

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${filename}_${format(new Date(), 'yyyyMMdd_HHmm')}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        className="gap-2"
        onClick={exportToCSV}
        disabled={disabled || isExporting || data.length === 0}
      >
        {isExporting ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <FileSpreadsheet className="h-4 w-4" />
        )}
        Exportar CSV
      </Button>
    </div>
  )
}