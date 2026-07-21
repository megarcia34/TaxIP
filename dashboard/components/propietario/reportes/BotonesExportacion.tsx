'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Download, FileSpreadsheet, FileText, File } from 'lucide-react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface BotonesExportacionProps {
  tipo: 'gastos' | 'mantenimientos' | 'contratos' | 'rentabilidad'
  vehiculo_id?: string
  desde?: string
  hasta?: string
  label?: string
}

export function BotonesExportacion({ tipo, vehiculo_id, desde, hasta, label = 'Exportar' }: BotonesExportacionProps) {
  const [loading, setLoading] = useState(false)

  const exportar = async (formato: string) => {
    setLoading(true)
    const token = localStorage.getItem('prop_token')
    
    let url = `${API_URL}/api/propietario/reportes/${tipo}/${formato}`
    const params = new URLSearchParams()
    
    if (vehiculo_id) params.append('vehiculo_id', vehiculo_id)
    if (desde) params.append('desde', desde)
    if (hasta) params.append('hasta', hasta)
    
    if (params.toString()) {
      url += `?${params.toString()}`
    }
    
    try {
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        const error = await response.json()
        toast.error(error.detail || 'Error al exportar')
        return
      }
      
      // Obtener nombre del archivo del header Content-Disposition
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `${tipo}_${new Date().toISOString().slice(0, 10)}.${formato === 'excel' ? 'xlsx' : formato}`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/)
        if (match) filename = match[1]
      }
      
      const blob = await response.blob()
      const urlBlob = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = urlBlob
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(urlBlob)
      
      toast.success('Archivo descargado correctamente')
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al exportar')
    } finally {
      setLoading(false)
    }
  }

  const getIcon = (formato: string) => {
    switch (formato) {
      case 'csv': return <File className="h-4 w-4 mr-2" />
      case 'excel': return <FileSpreadsheet className="h-4 w-4 mr-2" />
      case 'pdf': return <FileText className="h-4 w-4 mr-2" />
      default: return <Download className="h-4 w-4 mr-2" />
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={loading}>
          <Download className="h-4 w-4 mr-2" />
          {loading ? 'Exportando...' : label}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => exportar('csv')}>
          {getIcon('csv')} CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => exportar('excel')}>
          {getIcon('excel')} Excel
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}