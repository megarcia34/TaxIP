'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, AlertCircle, Info, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import Link from 'next/link'

interface Alerta {
  id: string
  tipo: 'info' | 'warning' | 'danger' | 'success'
  titulo: string
  descripcion: string
  accion?: { texto: string; url: string }
}

const getIcono = (tipo: string) => {
  switch (tipo) {
    case 'danger': return <XCircle className="h-5 w-5 text-red-500" />
    case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-500" />
    case 'info': return <Info className="h-5 w-5 text-blue-500" />
    case 'success': return <CheckCircle className="h-5 w-5 text-green-500" />
    default: return <AlertCircle className="h-5 w-5 text-gray-500" />
  }
}

const getColor = (tipo: string) => {
  switch (tipo) {
    case 'danger': return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/20'
    case 'warning': return 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950/20'
    case 'info': return 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20'
    case 'success': return 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/20'
    default: return 'border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950/20'
  }
}

export function AlertasNegocio() {
  const { status } = useSession()
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAlertas = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/tenant/dashboard/alertas')
      if (!res.ok) throw new Error('Error al cargar alertas')
      const data = await res.json()
      setAlertas(data)
    } catch (error) {
      console.error('Error fetching alertas:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status === 'authenticated') {
      fetchAlertas()
      const interval = setInterval(fetchAlertas, 30000)
      return () => clearInterval(interval)
    }
  }, [status])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Alertas de Negocio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (alertas.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Alertas de Negocio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-2 py-4 text-muted-foreground">
            <div className="text-4xl">✅</div>
            <p className="text-sm font-medium">Todo en orden</p>
            <p className="text-xs">No hay alertas pendientes</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Alertas de Negocio
          <Badge variant="destructive">{alertas.length}</Badge>
        </CardTitle>
        <Button variant="ghost" size="icon" onClick={fetchAlertas} title="Actualizar">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-3 max-h-[400px] overflow-y-auto">
        {alertas.map((alerta) => (
          <div
            key={alerta.id}
            className={`rounded-lg border p-3 ${getColor(alerta.tipo)}`}
          >
            <div className="flex items-start gap-3">
              {getIcono(alerta.tipo)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{alerta.titulo}</p>
                <p className="text-sm text-muted-foreground">{alerta.descripcion}</p>
                {alerta.accion && (
                  <Link href={alerta.accion.url} className="inline-block mt-2">
                    <Button size="sm" variant="outline">
                      {alerta.accion.texto}
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

// Bell icon (agregar al inicio del archivo)
import { Bell } from 'lucide-react'