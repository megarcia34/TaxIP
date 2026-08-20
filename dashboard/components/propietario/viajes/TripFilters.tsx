'use client'

import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { CalendarIcon, Filter, X } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { useVehiculos } from '@/hooks/useVehiculos'

interface TripFiltersProps {
  filters: {
    vehiculoId: string
    choferId: string
    fechaDesde: string
    fechaHasta: string
    estado: string
    metodoPago: string
    fuente: string
    search: string
  }
  onFiltersChange: (filters: any) => void
  choferes?: Array<{ id: string; nombre: string; apellido: string }>
}

export function TripFilters({ filters, onFiltersChange, choferes = [] }: TripFiltersProps) {
  const { data: vehiculos } = useVehiculos()
  const [dateOpen, setDateOpen] = useState(false)
  const [tempFechaDesde, setTempFechaDesde] = useState<Date | undefined>()
  const [tempFechaHasta, setTempFechaHasta] = useState<Date | undefined>()

  useEffect(() => {
    if (filters.fechaDesde) setTempFechaDesde(new Date(filters.fechaDesde))
    if (filters.fechaHasta) setTempFechaHasta(new Date(filters.fechaHasta))
  }, [filters.fechaDesde, filters.fechaHasta])

  const handleFilterChange = (key: string, value: string) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  const handleDateApply = () => {
    onFiltersChange({
      ...filters,
      fechaDesde: tempFechaDesde ? format(tempFechaDesde, 'yyyy-MM-dd') : '',
      fechaHasta: tempFechaHasta ? format(tempFechaHasta, 'yyyy-MM-dd') : '',
    })
    setDateOpen(false)
  }

  const handleClearFilters = () => {
    onFiltersChange({
      vehiculoId: '',
      choferId: '',
      fechaDesde: '',
      fechaHasta: '',
      estado: '',
      metodoPago: '',
      fuente: '',
      search: '',
    })
  }

  const hasFilters = Object.values(filters).some((v) => v !== '')

  return (
    <div className="space-y-4">
      {/* Búsqueda y filtros rápidos */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[200px]">
          <Input
            placeholder="Buscar por pasajero, dirección, ID..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full"
          />
        </div>

        <Popover open={dateOpen} onOpenChange={setDateOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2">
              <CalendarIcon className="h-4 w-4" />
              {filters.fechaDesde || filters.fechaHasta ? (
                <>
                  {filters.fechaDesde && format(new Date(filters.fechaDesde), 'dd/MM/yyyy')}
                  {filters.fechaDesde && filters.fechaHasta && ' - '}
                  {filters.fechaHasta && format(new Date(filters.fechaHasta), 'dd/MM/yyyy')}
                </>
              ) : (
                'Fechas'
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-4" align="start">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Desde</Label>
                  <Calendar
                    mode="single"
                    selected={tempFechaDesde}
                    onSelect={setTempFechaDesde}                    
                    locale={es}
                  />
                </div>
                <div>
                  <Label>Hasta</Label>
                  <Calendar
                    mode="single"
                    selected={tempFechaHasta}
                    onSelect={setTempFechaHasta}
                    locale={es}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => {
                  setTempFechaDesde(undefined)
                  setTempFechaHasta(undefined)
                }}>
                  Limpiar
                </Button>
                <Button size="sm" onClick={handleDateApply}>Aplicar</Button>
              </div>
            </div>
          </PopoverContent>
        </Popover>

        <Select value={filters.estado} onValueChange={(v) => handleFilterChange('estado', v)}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Estado" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todos</SelectItem>
            <SelectItem value="pendiente">Pendiente</SelectItem>
            <SelectItem value="aceptado">Aceptado</SelectItem>
            <SelectItem value="en_curso">En curso</SelectItem>
            <SelectItem value="finalizado">Finalizado</SelectItem>
            <SelectItem value="cancelado">Cancelado</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filters.metodoPago} onValueChange={(v) => handleFilterChange('metodoPago', v)}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Pago" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todos</SelectItem>
            <SelectItem value="efectivo">💰 Efectivo</SelectItem>
            <SelectItem value="qr">📱 QR</SelectItem>
            <SelectItem value="debito">💳 Débito</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filters.fuente} onValueChange={(v) => handleFilterChange('fuente', v)}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Fuente" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todas</SelectItem>
            <SelectItem value="app">📱 App</SelectItem>
            <SelectItem value="taximetro">⚙️ Taxímetro</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filters.vehiculoId} onValueChange={(v) => handleFilterChange('vehiculoId', v)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Vehículo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todos</SelectItem>
            {vehiculos?.map((v) => (
              <SelectItem key={v.id} value={v.id}>{v.patente}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filters.choferId} onValueChange={(v) => handleFilterChange('choferId', v)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Chofer" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todos</SelectItem>
            {choferes.map((c) => (
              <SelectItem key={c.id} value={c.id}>{c.nombre} {c.apellido}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={handleClearFilters} className="gap-1">
            <X className="h-4 w-4" /> Limpiar
          </Button>
        )}
      </div>
    </div>
  )
}