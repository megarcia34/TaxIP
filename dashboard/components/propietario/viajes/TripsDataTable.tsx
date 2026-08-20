'use client'

import { useState, useMemo } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
import { TripStatusBadge } from './TripStatusBadge'
import { TripSourceBadge } from './TripSourceBadge'
import { Eye, MapPin, Columns } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

// ============================================
// TIPO DEFINIDO LOCALMENTE
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
  aceptado_en?: string;
  iniciado_en?: string;
  finalizado_en?: string;
  distancia_metros?: number;
  tiempo_estimado_segundos?: number;
  metodo_pago?: string;
  turno_id?: string;
  facturado?: boolean;
  transaccion_id?: string;
  comision_pasarela?: number;
  neto_propietario?: number;
  liquidacion_estado?: 'BORRADOR' | 'CALCULADA' | 'PENDIENTE_APROBACION' | 'APROBADA' | 'PAGADA';
}

// ============================================
// PROPS
// ============================================

interface TripsDataTableProps {
  data: ViajePropietario[]
  total?: number
  pageSize?: number
  pageIndex?: number
  onPageChange?: (page: number) => void
  onViewTrip?: (trip: ViajePropietario) => void
  onViewRoute?: (trip: ViajePropietario) => void
  isLoading?: boolean
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export function TripsDataTable({
  data,
  total,
  pageSize = 10,
  pageIndex = 0,
  onPageChange,
  onViewTrip,
  onViewRoute,
  isLoading,
}: TripsDataTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(pageIndex + 1)

  // Column visibility
  const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>({
    id: true,
    fecha: true,
    vehiculo: true,
    chofer: true,
    pasajero: true,
    origen: true,
    destino: true,
    monto: true,
    estado: true,
    fuente: true,
    acciones: true,
  })

  // Filter data locally
  const filteredData = useMemo(() => {
    if (!searchTerm) return data
    const term = searchTerm.toLowerCase()
    return data.filter((trip) =>
      trip.id.toLowerCase().includes(term) ||
      trip.vehiculo_patente?.toLowerCase().includes(term) ||
      `${trip.chofer_nombre} ${trip.chofer_apellido}`.toLowerCase().includes(term) ||
      trip.pasajero_nombre?.toLowerCase().includes(term) ||
      trip.direccion_origen.toLowerCase().includes(term) ||
      trip.direccion_destino.toLowerCase().includes(term)
    )
  }, [data, searchTerm])

  // Pagination
  const totalItems = total || filteredData.length
  const totalPages = Math.ceil(totalItems / pageSize)
  const currentPageNum = onPageChange ? pageIndex + 1 : currentPage

  const handlePageChange = (page: number) => {
    if (onPageChange) {
      onPageChange(page - 1) // Convert to 0-based for API
    } else {
      setCurrentPage(page)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p className="text-lg">No hay viajes para mostrar</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2 w-full sm:w-auto">
          <Input
            placeholder="Buscar viaje..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
        </div>
        <div className="flex gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <Columns className="h-4 w-4" />
                Columnas
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="max-h-64 overflow-y-auto">
              {Object.entries(columnVisibility).map(([key, value]) => (
                <DropdownMenuCheckboxItem
                  key={key}
                  checked={value}
                  onCheckedChange={(checked) =>
                    setColumnVisibility((prev) => ({ ...prev, [key]: !!checked }))
                  }
                >
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {columnVisibility.id && <TableHead className="min-w-[80px]">ID</TableHead>}
              {columnVisibility.fecha && <TableHead className="min-w-[120px]">Fecha</TableHead>}
              {columnVisibility.vehiculo && <TableHead className="min-w-[100px]">Vehículo</TableHead>}
              {columnVisibility.chofer && <TableHead className="min-w-[120px]">Chofer</TableHead>}
              {columnVisibility.pasajero && <TableHead className="min-w-[100px]">Pasajero</TableHead>}
              {columnVisibility.origen && <TableHead className="min-w-[150px]">Origen</TableHead>}
              {columnVisibility.destino && <TableHead className="min-w-[150px]">Destino</TableHead>}
              {columnVisibility.monto && <TableHead className="min-w-[80px] text-right">Monto</TableHead>}
              {columnVisibility.estado && <TableHead className="min-w-[100px]">Estado</TableHead>}
              {columnVisibility.fuente && <TableHead className="min-w-[80px]">Fuente</TableHead>}
              {columnVisibility.acciones && <TableHead className="min-w-[100px] text-right">Acciones</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((trip) => (
              <TableRow key={trip.id}>
                {columnVisibility.id && (
                  <TableCell className="font-mono text-xs">{trip.id.slice(0, 8)}</TableCell>
                )}
                {columnVisibility.fecha && (
                  <TableCell className="text-xs">
                    {format(new Date(trip.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                  </TableCell>
                )}
                {columnVisibility.vehiculo && (
                  <TableCell className="text-sm">
                    {trip.vehiculo_patente || trip.patente || 'N/A'}
                  </TableCell>
                )}
                {columnVisibility.chofer && (
                  <TableCell className="text-sm">
                    {trip.chofer_nombre} {trip.chofer_apellido}
                  </TableCell>
                )}
                {columnVisibility.pasajero && (
                  <TableCell className="text-sm">
                    {trip.pasajero_nombre || '-'}
                  </TableCell>
                )}
                {columnVisibility.origen && (
                  <TableCell className="text-sm max-w-[150px] truncate" title={trip.direccion_origen}>
                    {trip.direccion_origen}
                  </TableCell>
                )}
                {columnVisibility.destino && (
                  <TableCell className="text-sm max-w-[150px] truncate" title={trip.direccion_destino}>
                    {trip.direccion_destino}
                  </TableCell>
                )}
                {columnVisibility.monto && (
                  <TableCell className="text-right font-mono text-sm">
                    ${trip.precio_final?.toFixed(2) || '0.00'}
                  </TableCell>
                )}
                {columnVisibility.estado && (
                  <TableCell>
                    <TripStatusBadge estado={trip.estado} size="sm" />
                  </TableCell>
                )}
                {columnVisibility.fuente && (
                  <TableCell>
                    {trip.fuente && <TripSourceBadge fuente={trip.fuente} />}
                  </TableCell>
                )}
                {columnVisibility.acciones && (
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      {onViewRoute && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => onViewRoute(trip)}
                          title="Ver ruta"
                        >
                          <MapPin className="h-4 w-4" />
                        </Button>
                      )}
                      {onViewTrip && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => onViewTrip(trip)}
                          title="Ver detalles"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Mostrando {((currentPageNum - 1) * pageSize) + 1} - {Math.min(currentPageNum * pageSize, totalItems)} de {totalItems} viajes
          </div>
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => handlePageChange(Math.max(1, currentPageNum - 1))}
                  className={currentPageNum === 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                />
              </PaginationItem>
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                let pageNum
                if (totalPages <= 5) {
                  pageNum = i + 1
                } else if (currentPageNum <= 3) {
                  pageNum = i + 1
                } else if (currentPageNum >= totalPages - 2) {
                  pageNum = totalPages - 4 + i
                } else {
                  pageNum = currentPageNum - 2 + i
                }
                return (
                  <PaginationItem key={pageNum}>
                    <PaginationLink
                      isActive={pageNum === currentPageNum}
                      onClick={() => handlePageChange(pageNum)}
                    >
                      {pageNum}
                    </PaginationLink>
                  </PaginationItem>
                )
              })}
              <PaginationItem>
                <PaginationNext
                  onClick={() => handlePageChange(Math.min(totalPages, currentPageNum + 1))}
                  className={currentPageNum === totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  )
}