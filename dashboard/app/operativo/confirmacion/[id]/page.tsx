'use client';

// ============================================================
// 1. IMPORTS
// ============================================================
import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { apiClient } from '@/lib/api';

// ============================================================
// 2. UI Components
// ============================================================
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

// ============================================================
// 3. Iconos
// ============================================================
import {
  Loader2,
  MapPin,
  User,
  Car,
  Clock,
  DollarSign,
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertCircle,
  Phone,
  Calendar,
  Package,
  Users,
  Navigation,
  Copy,
  Check,
  Home,
} from 'lucide-react';

// ============================================================
// 4. Componentes Operativos
// ============================================================
import { PipelineEstados } from '@/components/operativo/PipelineEstados';

// ============================================================
// 5. Toast
// ============================================================
import { toast } from 'sonner';

// ============================================================
// 6. TIPOS
// ============================================================
interface ReservaDetalle {
  id: string;
  empresa_id: string;
  empleado_id: string;
  turno_id: string | null;
  pasajero_nombre: string | null;
  pasajero_telefono: string | null;
  direccion_origen: string;
  latitud_origen: number | null;
  longitud_origen: number | null;
  direccion_destino: string;
  latitud_destino: number | null;
  longitud_destino: number | null;
  paradas_intermedias: Array<{
    direccion: string;
    latitud: number | null;
    longitud: number | null;
    descripcion?: string;
  }>;
  tipo_vehiculo: string;
  nota_conductor: string | null;
  estado: string;
  es_programado: boolean;
  fecha_programada: string | null;
  distancia_estimada_km: number | null;
  tiempo_estimado_minutos: number | null;
  precio_estimado: number | null;
  precio_final: number | null;
  metodo_pago: string;
  centro_costo: string | null;
  cantidad_pasajeros: number;
  cantidad_equipaje: number;
  created_at: string;
  updated_at: string;
}

// ============================================================
// 7. COMPONENTE PRINCIPAL
// ============================================================
export default function ConfirmacionReservaPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [copied, setCopied] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const reservaId = params.id as string;

  // ============================================================
  // 7.1. QUERY - Obtener detalle de la reserva
  // ============================================================
  const { data: reserva, isLoading, error, refetch } = useQuery({
    queryKey: ['reserva-detalle', reservaId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/reservas/${reservaId}`);
      return response.data as ReservaDetalle;
    },
    enabled: !!reservaId,
    retry: false,
  });

  // ============================================================
  // 7.2. MUTATIONS
  // ============================================================
  const cancelarMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.patch(
        `/api/reservas/${reservaId}/estado?estado=cancelado`,
        {}
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success('✅ Reserva cancelada correctamente');
      queryClient.invalidateQueries({ queryKey: ['reserva-detalle', reservaId] });
      setShowCancelDialog(false);
      refetch();
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail;
      toast.error(detail || 'Error al cancelar la reserva');
    },
  });

  const avanzarEstadoMutation = useMutation({
    mutationFn: async (estado: string) => {
      const response = await apiClient.patch(
        `/api/reservas/${reservaId}/estado?estado=${estado}`,
        {}
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success('✅ Estado actualizado correctamente');
      queryClient.invalidateQueries({ queryKey: ['reserva-detalle', reservaId] });
      refetch();
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail;
      toast.error(detail || 'Error al actualizar el estado');
    },
  });

  // ============================================================
  // 7.3. FUNCIONES AUXILIARES
  // ============================================================
  const copyReservaId = () => {
    navigator.clipboard.writeText(reservaId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast.success('ID copiado al portapapeles');
  };

  const formatDate = (date: string | null) => {
    if (!date) return '—';
    return format(new Date(date), "dd 'de' MMMM 'de' yyyy, HH:mm", { locale: es });
  };

  const getEstadoConfig = (estado: string) => {
    const configs: Record<string, { label: string; variant: 'default' | 'destructive' | 'outline' | 'secondary'; icon: any }> =
      {
        reservado: { label: 'Reservado', variant: 'default', icon: Clock },
        despachado: { label: 'Despachado', variant: 'secondary', icon: Car },
        vehiculo_llego: { label: 'Vehículo llegó', variant: 'secondary', icon: CheckCircle },
        pasajero_a_bordo: { label: 'Pasajero a bordo', variant: 'secondary', icon: Users },
        completado: { label: 'Completado', variant: 'outline', icon: CheckCircle },
        cancelado: { label: 'Cancelado', variant: 'destructive', icon: XCircle },
      };
    return configs[estado] || { label: estado, variant: 'default', icon: AlertCircle };
  };

  const getMetodoPagoLabel = (metodo: string) => {
    const labels: Record<string, string> = {
      efectivo: 'Efectivo en el vehículo',
      qr: 'QR / Transferencia',
      transferencia: 'Transferencia bancaria',
      cuenta_corriente: 'Cuenta Corriente',
    };
    return labels[metodo] || metodo;
  };

  const getVehiculoLabel = (tipo: string) => {
    const labels: Record<string, string> = {
      standard: 'Standard (4 pasajeros)',
      premium: 'Premium',
      van: 'Van (6 pasajeros)',
      minivan: 'Minivan (7 pasajeros)',
    };
    return labels[tipo] || tipo;
  };

  // ============================================================
  // 7.4. RENDERIZADO - Loading
  // ============================================================
  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // ============================================================
  // 7.5. RENDERIZADO - Error
  // ============================================================
  if (error || !reserva) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] gap-4">
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-5 w-5" />
          <AlertDescription>
            No se pudo encontrar la reserva o hubo un error al cargarla.
          </AlertDescription>
        </Alert>
        <Button onClick={() => router.push('/operativo')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver al Dashboard
        </Button>
      </div>
    );
  }

  // ============================================================
  // 7.6. RENDERIZADO PRINCIPAL
  // ============================================================
  const estadoConfig = getEstadoConfig(reserva.estado);
  const EstadoIcon = estadoConfig.icon;
  const isCancelable = !['completado', 'cancelado'].includes(reserva.estado);
  const isCompletado = reserva.estado === 'completado';
  const isCancelado = reserva.estado === 'cancelado';

  return (
    <div className="space-y-6">
      {/* ============================================================
          HEADER
          ============================================================ */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/operativo')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <CheckCircle className="h-7 w-7 text-green-500" />
              Confirmación de Viaje
            </h1>
            <p className="text-sm text-muted-foreground">
              Tu viaje ha sido creado exitosamente
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={estadoConfig.variant as any} className="flex items-center gap-1.5 px-3 py-1.5 text-sm">
            <EstadoIcon className="h-3.5 w-3.5" />
            {estadoConfig.label}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={copyReservaId}
            className="flex items-center gap-1.5 text-xs"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-green-500" />
                ID: {reservaId.substring(0, 8)}
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                ID: {reservaId.substring(0, 8)}
              </>
            )}
          </Button>
        </div>
      </div>

      {/* ============================================================
          PIPELINE DE ESTADOS (más visible)
          ============================================================ */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Estado del Viaje
          </CardTitle>
        </CardHeader>
        <CardContent>
          <PipelineEstados estado={reserva.estado} />
        </CardContent>
      </Card>

      {/* ============================================================
          GRID PRINCIPAL (2/3 - 1/3)
          ============================================================ */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* COLUMNA IZQUIERDA (2/3) - Detalle del viaje */}
        <div className="lg:col-span-2 space-y-6">
          {/* --- Tarjeta de ruta --- */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Navigation className="h-4 w-4 text-primary" />
                Detalle del Recorrido
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Origen */}
              <div className="flex items-start gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-3 w-3 rounded-full bg-green-500 mt-1.5" />
                  <div className="w-0.5 h-full min-h-[24px] bg-gray-300" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground font-medium">Origen</p>
                  <p className="font-medium">{reserva.direccion_origen}</p>
                </div>
              </div>

              {/* Paradas intermedias */}
              {reserva.paradas_intermedias && reserva.paradas_intermedias.length > 0 && (
                <>
                  {reserva.paradas_intermedias.map((parada, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="flex flex-col items-center">
                        <div className="h-3 w-3 rounded-full bg-yellow-400 mt-1.5 flex items-center justify-center text-[8px] font-bold text-white">
                          {index + 1}
                        </div>
                        <div className="w-0.5 h-full min-h-[24px] bg-gray-300" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground font-medium">Parada {index + 1}</p>
                        <p className="font-medium">{parada.direccion}</p>
                      </div>
                    </div>
                  ))}
                </>
              )}

              {/* Destino */}
              <div className="flex items-start gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-3 w-3 rounded-full bg-red-500 mt-1.5" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground font-medium">Destino</p>
                  <p className="font-medium">{reserva.direccion_destino}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* --- Tarjeta de información del pasajero --- */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <User className="h-4 w-4" />
                Información del Pasajero
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground text-xs">Nombre</p>
                  <p className="font-medium">{reserva.pasajero_nombre || 'No especificado'}</p>
                </div>
                {reserva.pasajero_telefono && (
                  <div>
                    <p className="text-muted-foreground text-xs flex items-center gap-1">
                      <Phone className="h-3 w-3" /> Teléfono
                    </p>
                    <p className="font-medium">{reserva.pasajero_telefono}</p>
                  </div>
                )}
                <div>
                  <p className="text-muted-foreground text-xs flex items-center gap-1">
                    <Users className="h-3 w-3" /> Pasajeros
                  </p>
                  <p className="font-medium">{reserva.cantidad_pasajeros}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs flex items-center gap-1">
                    <Package className="h-3 w-3" /> Equipaje
                  </p>
                  <p className="font-medium">{reserva.cantidad_equipaje} mediano(s)</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs flex items-center gap-1">
                    <Car className="h-3 w-3" /> Vehículo
                  </p>
                  <p className="font-medium">{getVehiculoLabel(reserva.tipo_vehiculo)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs flex items-center gap-1">
                    <DollarSign className="h-3 w-3" /> Método de pago
                  </p>
                  <p className="font-medium">{getMetodoPagoLabel(reserva.metodo_pago)}</p>
                </div>
                {reserva.centro_costo && (
                  <div className="sm:col-span-2">
                    <p className="text-muted-foreground text-xs">Centro de costo</p>
                    <p className="font-medium">{reserva.centro_costo}</p>
                  </div>
                )}
                {reserva.nota_conductor && (
                  <div className="sm:col-span-2">
                    <p className="text-muted-foreground text-xs">Nota para el conductor</p>
                    <p className="font-medium text-sm">{reserva.nota_conductor}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* COLUMNA DERECHA (1/3) - Resumen y acciones */}
        <div className="space-y-6">
          {/* --- Tarjeta de precio --- */}
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Resumen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-center">
                <p className="text-3xl font-bold text-primary">
                  ${(reserva.precio_final || reserva.precio_estimado || 0).toFixed(0)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {reserva.precio_final ? 'Precio final' : 'Precio estimado'}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="bg-background rounded-md p-2 text-center">
                  <p className="text-muted-foreground text-xs">Distancia</p>
                  <p className="font-medium">{reserva.distancia_estimada_km?.toFixed(1) || '--'} km</p>
                </div>
                <div className="bg-background rounded-md p-2 text-center">
                  <p className="text-muted-foreground text-xs">Tiempo estimado</p>
                  <p className="font-medium">{reserva.tiempo_estimado_minutos || '--'} min</p>
                </div>
              </div>
              <div className="flex justify-between text-sm border-t pt-2">
                <span className="text-muted-foreground">Creado</span>
                <span>{formatDate(reserva.created_at)}</span>
              </div>
              {reserva.es_programado && reserva.fecha_programada && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3" /> Programado
                  </span>
                  <span>{formatDate(reserva.fecha_programada)}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* --- Tarjeta de acciones --- */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Acciones</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Botones de acción según estado */}
              {!isCancelado && !isCompletado && (
                <div className="space-y-2">
                  <p className="text-xs text-muted-foreground font-medium">Avanzar estado</p>
                  <div className="flex flex-wrap gap-2">
                    {reserva.estado === 'reservado' && (
                      <Button
                        size="sm"
                        onClick={() => avanzarEstadoMutation.mutate('despachado')}
                        disabled={avanzarEstadoMutation.isPending}
                      >
                        Despachar
                      </Button>
                    )}
                    {reserva.estado === 'despachado' && (
                      <Button
                        size="sm"
                        onClick={() => avanzarEstadoMutation.mutate('vehiculo_llego')}
                        disabled={avanzarEstadoMutation.isPending}
                      >
                        Vehículo llegó
                      </Button>
                    )}
                    {reserva.estado === 'vehiculo_llego' && (
                      <Button
                        size="sm"
                        onClick={() => avanzarEstadoMutation.mutate('pasajero_a_bordo')}
                        disabled={avanzarEstadoMutation.isPending}
                      >
                        Pasajero a bordo
                      </Button>
                    )}
                    {reserva.estado === 'pasajero_a_bordo' && (
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => avanzarEstadoMutation.mutate('completado')}
                        disabled={avanzarEstadoMutation.isPending}
                      >
                        Completar viaje
                      </Button>
                    )}
                  </div>
                </div>
              )}

              {/* Botón de cancelar */}
              {isCancelable && (
                <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" className="w-full">
                      <XCircle className="mr-2 h-4 w-4" />
                      Cancelar Reserva
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>¿Cancelar el viaje?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Esta acción no se puede deshacer. El viaje será cancelado y el pasajero
                        deberá realizar una nueva solicitud.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Volver</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={() => cancelarMutation.mutate()}
                        disabled={cancelarMutation.isPending}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        {cancelarMutation.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Cancelando...
                          </>
                        ) : (
                          'Sí, cancelar'
                        )}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}

              {isCancelado && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>Esta reserva fue cancelada</AlertDescription>
                </Alert>
              )}

              {isCompletado && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Viaje completado exitosamente
                  </AlertDescription>
                </Alert>
              )}

              {/* ✅ MEJORA: Botón "Volver al Dashboard" */}
              <Button
                variant="default"
                className="w-full"
                onClick={() => router.push('/operativo')}
              >
                <Home className="mr-2 h-4 w-4" />
                Volver al Dashboard
              </Button>
            </CardContent>
          </Card>

          {/* ETD - solo si no está completado o cancelado */}
          {!isCancelado && !isCompletado && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
                  <div>
                    <p className="text-sm font-medium">Conductor en camino</p>
                    <p className="text-xs text-muted-foreground">ETA estimado: 5-10 min</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}