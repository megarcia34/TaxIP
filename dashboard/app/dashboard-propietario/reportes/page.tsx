'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, Download, Loader2, Calendar, BarChart3, FileSpreadsheet } from 'lucide-react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function PropietarioReportesPage() {
  const [loading, setLoading] = useState(false)
  const [periodo, setPeriodo] = useState('mes')
  const [formato, setFormato] = useState('csv')
  const [fechaDesde, setFechaDesde] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [fechaHasta, setFechaHasta] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [anio, setAnio] = useState(new Date().getFullYear())

  const exportarGastos = async (formato: 'csv' | 'excel') => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (fechaDesde) params.append('desde', fechaDesde)
      if (fechaHasta) params.append('hasta', fechaHasta)
      
      const url = `/api/propietario/reportes/gastos/${formato}?${params.toString()}`
      
      const response = await apiClient.get(url, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { 
        type: formato === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `gastos_${new Date().toISOString().split('T')[0]}.${formato === 'csv' ? 'csv' : 'xlsx'}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      
      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const exportarMantenimientos = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/api/propietario/reportes/mantenimientos/csv', {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { type: 'text/csv' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `mantenimientos_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      
      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const exportarRentabilidad = async (formato: 'csv' | 'json') => {
    setLoading(true)
    try {
      const response = await apiClient.get(
        `/api/propietario/reportes/rentabilidad?formato=${formato}&periodo=${periodo}`,
        { responseType: formato === 'csv' ? 'blob' : 'json' }
      )
      
      if (formato === 'csv') {
        const blob = new Blob([response.data], { type: 'text/csv' })
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `rentabilidad_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        a.remove()
      } else {
        const data = response.data
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `rentabilidad_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        a.remove()
      }
      
      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const exportarReporteAnual = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get(`/api/propietario/reportes/anual?anio=${anio}`)
      
      const data = response.data
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `reporte_anual_${anio}.json`
      document.body.appendChild(a)
      a.click()
      a.remove()
      
      toast.success('Reporte descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reportes</h1>
        <p className="text-muted-foreground">
          Exporta reportes y estadísticas de tu flota
        </p>
      </div>

      {/* Reporte de Gastos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Reporte de Gastos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Fecha Desde</Label>
              <Input
                type="date"
                value={fechaDesde}
                onChange={(e) => setFechaDesde(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Fecha Hasta</Label>
              <Input
                type="date"
                value={fechaHasta}
                onChange={(e) => setFechaHasta(e.target.value)}
              />
            </div>
            <div className="flex items-end gap-2">
              <Button 
                onClick={() => exportarGastos('csv')} 
                disabled={loading}
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button 
                onClick={() => exportarGastos('excel')} 
                disabled={loading}
                variant="outline"
                className="flex-1"
              >
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Excel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reporte de Mantenimientos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Reporte de Mantenimientos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-2">
            <Button 
              onClick={exportarMantenimientos} 
              disabled={loading}
            >
              <Download className="h-4 w-4 mr-2" />
              Exportar CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Reporte de Rentabilidad */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Reporte de Rentabilidad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Período</Label>
              <Tabs value={periodo} onValueChange={setPeriodo}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="dia">Día</TabsTrigger>
                  <TabsTrigger value="mes">Mes</TabsTrigger>
                  <TabsTrigger value="ano">Año</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            <div className="space-y-2">
              <Label>Formato</Label>
              <Select value={formato} onValueChange={setFormato}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button 
                onClick={() => exportarRentabilidad(formato as 'csv' | 'json')} 
                disabled={loading}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reporte Anual */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            Reporte Anual Consolidado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Año</Label>
              <Input
                type="number"
                value={anio}
                onChange={(e) => setAnio(Number(e.target.value))}
                min={2020}
                max={new Date().getFullYear()}
              />
            </div>
            <div className="flex items-end">
              <Button 
                onClick={exportarReporteAnual} 
                disabled={loading}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar Reporte
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="flex justify-center items-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="ml-2">Generando reporte...</span>
        </div>
      )}
    </div>
  )
}