'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'
import { 
  Play, 
  Square, 
  PlusCircle, 
  History, 
  AlertTriangle, 
  Loader2, 
  Clock, 
  ShieldCheck,
  Building
} from 'lucide-react'

interface EstadoTurno {
  activo: boolean
  message: string
  turno_id?: string
  fecha_inicio?: string
}

export default function DashboardOperativoPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [checkingTurno, setCheckingTurno] = useState(true)
  const [estadoTurno, setEstadoTurno] = useState<EstadoTurno>({ activo: false, message: 'Cargando...' })

  // Verificar el estado del turno al cargar la página
  const verificarEstadoTurno = async () => {
    setCheckingTurno(true)
    try {
      const response = await apiClient.get('/api/turnos/estado')
      setEstadoTurno(response.data)
    } catch (error) {
      console.error('❌ Error al obtener el estado del turno:', error)
      setEstadoTurno({ activo: false, message: 'No se pudo verificar el turno operativo' })
    } finally {
      setCheckingTurno(false)
    }
  }

  useEffect(() => {
    verificarEstadoTurno()
  }, [])

  // ============================================
  // FUNCIÓN AUXILIAR: FORMATEAR ERRORES FASTAPI
  // ============================================
  const extraerMensajeError = (error: any, fallback: string): string => {
    console.error("❌ Detalle del error capturado:", error)
    const detail = error?.response?.data?.detail
    
    if (typeof detail === 'string') {
      return detail
    } else if (Array.isArray(detail)) {
      // Mapea la estructura anidada de Pydantic v2 ({type, loc, msg, input}) a un String plano
      return detail.map((err: any) => {
        const campo = err.loc ? err.loc.slice(1).join('.') : 'campo'
        return `${campo}: ${err.msg}`
      }).join(', ')
    } else if (detail?.msg) {
      return detail.msg
    } else if (error?.message) {
      return error.message
    }
    return fallback
  }

  // ============================================
  // OPERACIÓN: INICIAR TURNO (CHECK-IN)
  // ============================================
  const handleCheckIn = async () => {
    setIsLoading(true)
    try {
      await apiClient.post('/api/turnos/checkin')
      toast.success('✅ Check-in exitoso. Tu turno de despacho ha comenzado.')
      await verificarEstadoTurno()
    } catch (error: any) {
      // ✅ CORREGIDO: Evita el crash transformando el objeto de validación a un String directo
      const mensaje = extraerMensajeError(error, 'Error al iniciar el turno de trabajo')
      toast.error(mensaje)
    } finally {
      setIsLoading(false)
    }
  }

  // ============================================
  // OPERACIÓN: FINALIZAR TURNO (CHECK-OUT)
  // ============================================
  const handleCheckOut = async () => {
    if (!confirm('¿Estás seguro de que deseas cerrar tu turno operativo actual?')) return
    setIsLoading(true)
    try {
      await apiClient.post('/api/turnos/checkout')
      toast.success('🔒 Turno cerrado correctamente. Que tengas un buen descanso.')
      await verificarEstadoTurno()
    } catch (error: any) {
      // ✅ CORREGIDO: Tratamiento preventivo para que React no rompa en el Check-Out
      const mensaje = extraerMensajeError(error, 'Error al finalizar el turno operativo')
      toast.error(mensaje)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Cabecera Principal */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Consola Operativa</h1>
          <p className="text-muted-foreground">Gestión de asistencia de personal y despacho de solicitudes corporativas.</p>
        </div>
        
        {/* Badge de Estado del Turno */}
        <div>
          {checkingTurno ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted px-3 py-1.5 rounded-full border">
              <Loader2 className="h-4 w-4 animate-spin" /> Verificando sesión...
            </div>
          ) : estadoTurno.activo ? (
            <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1.5 text-sm font-medium flex items-center gap-1.5 rounded-full shadow-none hover:bg-green-100">
              <ShieldCheck className="h-4 w-4 text-green-600" /> Turno Activo
            </Badge>
          ) : (
            <Badge variant="destructive" className="px-3 py-1.5 text-sm font-medium flex items-center gap-1.5 rounded-full shadow-none">
              <AlertTriangle className="h-4 w-4" /> Turno Inactivo
            </Badge>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Tarjeta de Control de Asistencia */}
        <Card className="md:col-span-1 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Asistencia & Turno
            </CardTitle>
            <CardDescription>
              Registra tu inicio de jornada para habilitar el despacho de viajes corporativos.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {checkingTurno ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : estadoTurno.activo ? (
              <div className="space-y-4">
                <div className="rounded-lg bg-green-50/50 p-4 border border-green-100 text-sm space-y-2">
                  <p className="text-green-800 font-medium">Información del turno:</p>
                  <p className="text-muted-foreground text-xs">
                    <span className="font-semibold">ID Turno:</span> {estadoTurno.turno_id}
                  </p>
                  {estadoTurno.fecha_inicio && (
                    <p className="text-muted-foreground text-xs">
                      <span className="font-semibold">Iniciado:</span> {new Date(estadoTurno.fecha_inicio).toLocaleString()}
                    </p>
                  )}
                </div>
                
                <Button 
                  variant="destructive" 
                  className="w-full" 
                  onClick={handleCheckOut}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Procesando...</>
                  ) : (
                    <><Square className="mr-2 h-4 w-4 fill-current" /> Cerrar Turno (Check-Out)</>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg bg-yellow-50/60 p-4 border border-yellow-100 text-sm text-yellow-800 flex items-start gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 shrink-0 mt-0.5" />
                  <p className="text-xs leading-relaxed">
                    Deberás marcar tu ingreso (Check-In) para poder registrar solicitudes. El sistema vinculará automáticamente tus despachos a la empresa asignada.
                  </p>
                </div>

                <Button 
                  className="w-full bg-primary hover:bg-primary/95" 
                  onClick={handleCheckIn}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Procesando...</>
                  ) : (
                    <><Play className="mr-2 h-4 w-4 fill-current" /> Iniciar Turno (Check-In)</>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tarjeta de Acciones Rápidas */}
        <Card className="md:col-span-2 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Building className="h-5 w-5 text-primary" />
              Gestión Operativa de Viajes
            </CardTitle>
            <CardDescription>
              Accesos rápidos a la plataforma de asignación y solicitudes de traslados corporativos.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              {/* Botón Nueva Solicitud */}
              <Button
                variant="outline"
                className="h-28 flex flex-col items-center justify-center gap-2 border-2 border-dashed hover:border-primary hover:text-primary transition-all rounded-xl bg-card"
                disabled={checkingTurno || !estadoTurno.activo}
                onClick={() => router.push('/operativo/nueva-solicitud')}
              >
                <PlusCircle className="h-6 w-6 text-muted-foreground group-hover:text-primary" />
                <div className="text-center">
                  <p className="font-semibold text-sm">Nueva Solicitud</p>
                  <p className="text-xs text-muted-foreground max-w-[180px] mt-0.5 font-normal">
                    Despachar un taxi para un paciente o empleado.
                  </p>
                </div>
              </Button>

              {/* Botón Historial */}
              <Button
                variant="outline"
                className="h-28 flex flex-col items-center justify-center gap-2 border-2 border-dashed hover:border-primary hover:text-primary transition-all rounded-xl bg-card"
                onClick={() => router.push('/operativo/historial')}
              >
                <History className="h-6 w-6 text-muted-foreground" />
                <div className="text-center">
                  <p className="font-semibold text-sm">Historial de Viajes</p>
                  <p className="text-xs text-muted-foreground max-w-[180px] mt-0.5 font-normal">
                    Revisar las reservas pasadas y estados de facturación.
                  </p>
                </div>
              </Button>
            </div>

            {/* Alerta si el turno está inactivo */}
            {!checkingTurno && !estadoTurno.activo && (
              <p className="text-center text-xs text-red-500 font-medium mt-4 bg-red-50 py-2 border border-red-100 rounded-lg">
                ⚠️ Recuerda iniciar turno para habilitar la creación de nuevas solicitudes.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}