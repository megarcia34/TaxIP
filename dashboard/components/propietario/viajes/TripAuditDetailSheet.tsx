'use client'

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter } from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { TripStatusBadge } from './TripStatusBadge'
import { TripSourceBadge } from './TripSourceBadge'
import {
  Calendar,
  Clock,
  User,
  Car,
  MapPin,
  CreditCard,
  DollarSign,
  Phone,
  Mail,
  FileText,
  Printer,
} from 'lucide-react'
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
// CONFIGURACIÓN DE LIQUIDACIÓN
// ============================================

const liquidacionColors: Record<string, string> = {
  BORRADOR: 'bg-gray-500',
  CALCULADA: 'bg-blue-500',
  PENDIENTE_APROBACION: 'bg-yellow-500',
  APROBADA: 'bg-green-500',
  PAGADA: 'bg-green-700',
}

const liquidacionLabels: Record<string, string> = {
  BORRADOR: 'Borrador',
  CALCULADA: 'Calculada',
  PENDIENTE_APROBACION: 'Pendiente aprobación',
  APROBADA: 'Aprobada',
  PAGADA: 'Pagada',
}

// ============================================
// PROPS
// ============================================

interface TripAuditDetailSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  trip: ViajePropietario | null
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export function TripAuditDetailSheet({ open, onOpenChange, trip }: TripAuditDetailSheetProps) {
  if (!trip) return null

  const isLiquidated = trip.liquidacion_estado === 'APROBADA' || trip.liquidacion_estado === 'PAGADA'

  // Usar patente del vehículo (campo normalizado)
  const patente = trip.vehiculo_patente || trip.patente || 'N/A'
  const marca = trip.vehiculo_marca || ''
  const modelo = trip.vehiculo_modelo || ''

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-3 flex-wrap">
            Viaje #{trip.id.slice(0, 8)}
            <TripStatusBadge estado={trip.estado} size="sm" />
          </SheetTitle>
          <SheetDescription className="flex items-center gap-3 flex-wrap">
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {format(new Date(trip.created_at), "PPP 'a las' HH:mm", { locale: es })}
            </span>
            {trip.fuente && <TripSourceBadge fuente={trip.fuente} />}
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Información del vehículo y chofer */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2 rounded-lg border p-3">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Car className="h-4 w-4" /> Vehículo
              </p>
              <p className="font-medium">{patente}</p>
              <p className="text-sm text-muted-foreground">
                {marca} {modelo}
              </p>
            </div>
            <div className="space-y-2 rounded-lg border p-3">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <User className="h-4 w-4" /> Chofer
              </p>
              <p className="font-medium">{trip.chofer_nombre} {trip.chofer_apellido}</p>
              {trip.pasajero_nombre && (
                <p className="text-sm text-muted-foreground">
                  Pasajero: {trip.pasajero_nombre}
                </p>
              )}
            </div>
          </div>

          <Separator />

          {/* Recorrido */}
          <div className="space-y-2">
            <p className="text-sm font-medium flex items-center gap-1">
              <MapPin className="h-4 w-4" /> Recorrido
            </p>
            <div className="space-y-1 rounded-lg border p-3">
              <p className="text-sm">
                <span className="text-muted-foreground">Origen:</span> {trip.direccion_origen}
              </p>
              <p className="text-sm">
                <span className="text-muted-foreground">Destino:</span> {trip.direccion_destino}
              </p>
            </div>
          </div>

          <Separator />

          {/* Desglose financiero */}
          <div className="space-y-2">
            <p className="text-sm font-medium flex items-center gap-1">
              <DollarSign className="h-4 w-4" /> Desglose Financiero
            </p>
            <div className="rounded-lg border bg-muted/30 p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Monto Bruto</span>
                <span className="font-mono font-medium">
                  ${(trip.precio_final || 0).toFixed(2)}
                </span>
              </div>
              {trip.comision_pasarela !== undefined && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    Comisión Pasarela ({trip.metodo_pago || 'N/A'})
                  </span>
                  <span className="font-mono text-red-500">
                    -${trip.comision_pasarela.toFixed(2)}
                  </span>
                </div>
              )}
              {trip.neto_propietario !== undefined && (
                <>
                  <Separator />
                  <div className="flex justify-between font-bold">
                    <span>Neto Propietario</span>
                    <span className="text-green-600">
                      ${trip.neto_propietario.toFixed(2)}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          <Separator />

          {/* Transacción y liquidación */}
          <div className="grid grid-cols-2 gap-4">
            {trip.transaccion_id && (
              <div className="space-y-2 rounded-lg border p-3">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <CreditCard className="h-4 w-4" /> Transacción
                </p>
                <p className="text-sm font-mono break-all">{trip.transaccion_id}</p>
              </div>
            )}
            {trip.liquidacion_estado && (
              <div className="space-y-2 rounded-lg border p-3">
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <FileText className="h-4 w-4" /> Estado Liquidación
                </p>
                <Badge className={liquidacionColors[trip.liquidacion_estado] || 'bg-gray-500'}>
                  {liquidacionLabels[trip.liquidacion_estado] || trip.liquidacion_estado}
                </Badge>
                {isLiquidated && (
                  <p className="text-xs text-muted-foreground">
                    Este viaje ya fue liquidado y no puede modificarse
                  </p>
                )}
              </div>
            )}
          </div>

          <Separator />

          {/* Línea de tiempo */}
          <div className="space-y-2">
            <p className="text-sm font-medium flex items-center gap-1">
              <Clock className="h-4 w-4" /> Línea de Tiempo
            </p>
            <div className="space-y-2 rounded-lg border p-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Solicitado</span>
                <span>{format(new Date(trip.created_at), 'HH:mm')}</span>
              </div>
              {trip.aceptado_en && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Aceptado</span>
                  <span>{format(new Date(trip.aceptado_en), 'HH:mm')}</span>
                </div>
              )}
              {trip.iniciado_en && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Iniciado</span>
                  <span>{format(new Date(trip.iniciado_en), 'HH:mm')}</span>
                </div>
              )}
              {trip.finalizado_en && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Finalizado</span>
                  <span>{format(new Date(trip.finalizado_en), 'HH:mm')}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <SheetFooter className="mt-6 pt-4 border-t">
          <Button variant="outline" size="sm" className="gap-2" onClick={() => window.print()}>
            <Printer className="h-4 w-4" /> Imprimir
          </Button>
          <Button size="sm" onClick={() => onOpenChange(false)}>Cerrar</Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}