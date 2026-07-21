'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, FileText, Calendar } from 'lucide-react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DocumentoVencimiento {
  id: string
  tipo_documento: string
  numero: string
  fecha_vencimiento: string
  patente: string
  dias_restantes: number
}

export default function AlertasVencimiento() {
  const [documentos, setDocumentos] = useState<DocumentoVencimiento[]>([])
  const [loading, setLoading] = useState(true)

  const cargarAlertas = async () => {
    const token = localStorage.getItem('prop_token')
    if (!token) return

    try {
      const res = await fetch(`${API_URL}/api/propietario/documentos/vencimientos?dias_previos=30`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setDocumentos(data)
      }
    } catch (error) {
      console.error('Error cargando alertas:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarAlertas()
  }, [])

  if (loading) return null
  if (documentos.length === 0) return null

  const getTipoLabel = (tipo: string) => {
    const tipos: Record<string, string> = {
      'SEGURO': 'Seguro',
      'ITV': 'ITV',
      'PATENTE': 'Patente',
      'LICENCIA_CHOFER': 'Licencia de chofer',
      'CEDULA_VERDE': 'Cédula verde'
    }
    return tipos[tipo] || tipo
  }

  return (
    <Card className="border-red-200 bg-red-50/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2 text-red-800">
          <AlertTriangle className="h-5 w-5" />
          Documentos por vencer ({documentos.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {documentos.map((doc) => (
            <div key={doc.id} className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium">{getTipoLabel(doc.tipo_documento)}</p>
                  <p className="text-sm text-muted-foreground">{doc.patente} - N° {doc.numero}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-red-600">
                  {doc.dias_restantes} días
                </p>
                <p className="text-xs text-muted-foreground">
                  Vence: {new Date(doc.fecha_vencimiento).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}