'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Search, Filter, X, RefreshCw } from 'lucide-react'

interface FiltrosChoferesProps {
  onFilterChange: (filtros: any) => void
  loading?: boolean
}

export function ChoferesFiltros({ onFilterChange, loading }: FiltrosChoferesProps) {
  const [filtros, setFiltros] = useState({
    search: '',
    propietario: '',
    estadoLaboral: '',
    calificacionMin: 0,
    aprobacion: '',
  })
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleChange = (key: string, value: any) => {
    const nuevosFiltros = { ...filtros, [key]: value }
    setFiltros(nuevosFiltros)
    onFilterChange(nuevosFiltros)
  }

  const handleReset = () => {
    const resetFiltros = {
      search: '',
      propietario: '',
      estadoLaboral: '',
      calificacionMin: 0,
      aprobacion: '',
    }
    setFiltros(resetFiltros)
    onFilterChange(resetFiltros)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => setShowAdvanced(!showAdvanced)}>
              {showAdvanced ? 'Simplificar' : 'Avanzado'}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleReset} disabled={loading}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Resetear
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Búsqueda rápida */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nombre, email, patente, documento..."
            value={filtros.search}
            onChange={(e) => handleChange('search', e.target.value)}
            className="pl-9"
            disabled={loading}
          />
          {filtros.search && (
            <button
              onClick={() => handleChange('search', '')}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
            </button>
          )}
        </div>

        {/* Filtros básicos */}
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-1">
            <Label htmlFor="estado-laboral">Estado Laboral</Label>
            <Select
              value={filtros.estadoLaboral}
              onValueChange={(value) => handleChange('estadoLaboral', value)}
              disabled={loading}
            >
              <SelectTrigger id="estado-laboral">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="libre">🟢 Libre</SelectItem>
                <SelectItem value="ocupado">🟡 Ocupado</SelectItem>
                <SelectItem value="inactivo">🔴 Inactivo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="aprobacion">Estado Aprobación</Label>
            <Select
              value={filtros.aprobacion}
              onValueChange={(value) => handleChange('aprobacion', value)}
              disabled={loading}
            >
              <SelectTrigger id="aprobacion">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="pendiente">⏳ Pendiente</SelectItem>
                <SelectItem value="aprobado">✅ Aprobado</SelectItem>
                <SelectItem value="rechazado">❌ Rechazado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="propietario">Propietario</Label>
            <Select
              value={filtros.propietario}
              onValueChange={(value) => handleChange('propietario', value)}
              disabled={loading}
            >
              <SelectTrigger id="propietario">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="1">Propietario 1</SelectItem>
                <SelectItem value="2">Propietario 2</SelectItem>
                <SelectItem value="3">Propietario 3</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Filtros avanzados */}
        {showAdvanced && (
          <div className="space-y-4 pt-4 border-t">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Calificación Mínima</Label>
                <span className="text-sm font-medium">{filtros.calificacionMin} ⭐</span>
              </div>
              <Slider
                value={[filtros.calificacionMin]}
                onValueChange={([value]) => handleChange('calificacionMin', value)}
                max={5}
                step={0.5}
                disabled={loading}
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <Label>Fecha de Registro</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input type="date" disabled={loading} placeholder="Desde" />
                  <Input type="date" disabled={loading} placeholder="Hasta" />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Total Viajes</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Input type="number" placeholder="Mín" disabled={loading} />
                  <Input type="number" placeholder="Máx" disabled={loading} />
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}