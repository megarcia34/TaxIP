'use client';

// ============================================================
// 1. IMPORTS - React y Next
// ============================================================
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

// ============================================================
// 2. UI Components (Shadcn/ui)
// ============================================================
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

// ============================================================
// 3. Iconos
// ============================================================
import { Loader2, MapPin, Navigation, Clock, Car, Users, AlertCircle, Trash2, AlertTriangle } from 'lucide-react';

// ============================================================
// 4. Libs y Utils
// ============================================================
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

// ============================================================
// 5. Componentes Operativos
// ============================================================
import { AddressAutocomplete, MapPicker, WaypointList } from '@/components/operativo';

// ============================================================
// 6. TIPOS
// ============================================================
interface Ubicacion {
  lat: number;
  lng: number;
  address: string;
}

interface Parada extends Ubicacion {}

// ============================================================
// 7. COMPONENTE PRINCIPAL
// ============================================================
export default function NuevaSolicitudPage() {
  const router = useRouter();

  // ============================================================
  // 7.1. ESTADOS - Carga y Turno
  // ============================================================
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [turnoActivo, setTurnoActivo] = useState<boolean | null>(null);
  const [turnoId, setTurnoId] = useState<string | null>(null);
  const [empresaId, setEmpresaId] = useState<string | null>(null);
  const [controlBaseId, setControlBaseId] = useState<string | null>(null);

  // ============================================================
  // 7.2. ESTADOS - Formulario
  // ============================================================
  const [origen, setOrigen] = useState<Ubicacion | null>(null);
  const [destino, setDestino] = useState<Ubicacion | null>(null);
  const [paradas, setParadas] = useState<Parada[]>([]);
  const [pasajeroNombre, setPasajeroNombre] = useState('');
  const [pasajeroTelefono, setPasajeroTelefono] = useState('');
  const [cantidadPasajeros, setCantidadPasajeros] = useState(1);
  const [cantidadEquipaje, setCantidadEquipaje] = useState(0);
  const [tipoVehiculo, setTipoVehiculo] = useState('standard');
  const [metodoPago, setMetodoPago] = useState('efectivo');
  const [notaConductor, setNotaConductor] = useState('');
  const [centroCosto, setCentroCosto] = useState('');

  // ============================================================
  // 7.3. ESTADOS - Cotización
  // ============================================================
  const [precioEstimado, setPrecioEstimado] = useState<number | null>(null);
  const [distanciaKm, setDistanciaKm] = useState<number | null>(null);
  const [tiempoMinutos, setTiempoMinutos] = useState<number | null>(null);
  const [calculandoPrecio, setCalculandoPrecio] = useState(false);

  // ============================================================
  // 7.4. ESTADOS - Mapa (CORREGIDO: San Miguel de Tucumán)
  // ============================================================
  const [mapCenter, setMapCenter] = useState({ lat: -26.829964, lng: -65.204332 });

  // ============================================================
  // 8. QUERY - Choferes disponibles (para empleados)
  // ============================================================
  const {
    data: choferesData,
    isLoading: isLoadingChoferes,
  } = useQuery({
    queryKey: ['choferes-disponibles', controlBaseId],
    queryFn: async () => {
      if (!controlBaseId) return { choferes: [] };
      try {
        // ✅ Endpoint para empleados (solo visualización)
        const response = await apiClient.get(
          `/api/control-base/choferes-disponibles?control_base_id=${controlBaseId}`
        );
        // El endpoint devuelve un array directamente
        return response.data;
      } catch (error) {
        console.warn('⚠️ Error al obtener choferes:', error);
        return [];
      }
    },
    enabled: !!controlBaseId,
    refetchInterval: 30000,
    staleTime: 25000,
    retry: 1,
  });

  // ============================================================
  // 9. Cálculo de estadísticas de choferes
  // ============================================================
  const choferes = Array.isArray(choferesData) ? choferesData : [];
  const disponibles = choferes.length;
  const hayPocosChoferes = disponibles > 0 && disponibles <= 2;

  // ============================================================
  // 10. FUNCIÓN - Limpiar formulario
  // ============================================================
  const limpiarFormulario = () => {
    setOrigen(null);
    setDestino(null);
    setParadas([]);
    setPasajeroNombre('');
    setPasajeroTelefono('');
    setCantidadPasajeros(1);
    setCantidadEquipaje(0);
    setTipoVehiculo('standard');
    setMetodoPago('efectivo');
    setNotaConductor('');
    setCentroCosto('');
    setPrecioEstimado(null);
    setDistanciaKm(null);
    setTiempoMinutos(null);
    setMapCenter({ lat: -26.829964, lng: -65.204332 });
    toast.info('🧹 Formulario limpiado');
  };

  // ============================================================
  // 11. EFECTOS - Inicialización
  // ============================================================
  useEffect(() => {
    const inicializar = async () => {
      try {
        console.log('🔍 [inicializar] Iniciando carga de datos...');

        const sessionRes = await fetch('/api/auth/session');
        const session = await sessionRes.json();

        if (session?.user) {
          setEmpresaId(session.user.empresa_id || null);
          setControlBaseId(session.user.control_base_id || null);
        }

        const turnoResp = await apiClient.get('/api/turnos/estado');
        if (turnoResp.data.activo) {
          setTurnoActivo(true);
          setTurnoId(turnoResp.data.turno_id || null);
        } else {
          setTurnoActivo(false);
        }

        const defaultOrigin = {
          address: 'Av. Independencia 1234, San Miguel de Tucumán, Tucumán, Argentina',
          lat: -26.829964,
          lng: -65.204332,
        };

        try {
          const empresaResp = await apiClient.get('/api/empresa/ubicacion');
          if (empresaResp.data && empresaResp.data.direccion) {
            setOrigen({
              address: empresaResp.data.direccion,
              lat: empresaResp.data.latitud || defaultOrigin.lat,
              lng: empresaResp.data.longitud || defaultOrigin.lng,
            });
            if (empresaResp.data.latitud && empresaResp.data.longitud) {
              setMapCenter({
                lat: empresaResp.data.latitud,
                lng: empresaResp.data.longitud,
              });
            }
          } else {
            setOrigen(defaultOrigin);
            setMapCenter({ lat: defaultOrigin.lat, lng: defaultOrigin.lng });
          }
        } catch (error) {
          console.warn('⚠️ Usando origen por defecto:', error);
          setOrigen(defaultOrigin);
          setMapCenter({ lat: defaultOrigin.lat, lng: defaultOrigin.lng });
        }
      } catch (error) {
        console.error('❌ Error al inicializar:', error);
        toast.error('Error al cargar datos iniciales');
      }
    };
    inicializar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ============================================================
  // 12. FUNCIONES - Geocodificación y Arrastre
  // ============================================================
  const geocodeLatLng = useCallback(async (lat: number, lng: number): Promise<string> => {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&language=es`
      );
      const data = await response.json();
      if (data.results && data.results.length > 0) {
        return data.results[0].formatted_address;
      }
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    } catch {
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
  }, []);

  const handleOriginDragEnd = useCallback(
    async (lat: number, lng: number) => {
      const address = await geocodeLatLng(lat, lng);
      setOrigen({ lat, lng, address });
      setMapCenter({ lat, lng });
    },
    [geocodeLatLng]
  );

  const handleDestinationDragEnd = useCallback(
    async (lat: number, lng: number) => {
      const address = await geocodeLatLng(lat, lng);
      setDestino({ lat, lng, address });
    },
    [geocodeLatLng]
  );

  const handleWaypointDragEnd = useCallback(
    async (index: number, lat: number, lng: number) => {
      const address = await geocodeLatLng(lat, lng);
      setParadas((prev) => {
        const newParadas = [...prev];
        newParadas[index] = { ...newParadas[index], lat, lng, address };
        return newParadas;
      });
    },
    [geocodeLatLng]
  );

  // ============================================================
  // 13. FUNCIONES - Envío
  // ============================================================
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!turnoActivo) {
      toast.error('No tienes un turno activo. Realiza el check-in primero.');
      return;
    }

    if (!origen || !origen.address.trim()) {
      toast.error('❌ Selecciona un origen válido. Escribe una dirección y selecciona una sugerencia.');
      return;
    }

    if (!destino || !destino.address.trim()) {
      toast.error('❌ Selecciona un destino válido. Escribe una dirección y selecciona una sugerencia.');
      return;
    }

    if (!pasajeroNombre.trim()) {
      toast.error('Ingresa el nombre del pasajero.');
      return;
    }

    if (!empresaId) {
      toast.error('No se detectó la empresa. Reingresa a la aplicación.');
      return;
    }

    if (!isLoadingChoferes && disponibles === 0) {
      toast.error('❌ No hay choferes disponibles en este momento. Intenta más tarde.');
      return;
    }

    if (!isLoadingChoferes && hayPocosChoferes) {
      toast.warning(
        `⚠️ Solo ${disponibles} chofer${disponibles !== 1 ? 'es' : ''} disponible${disponibles !== 1 ? 's' : ''}. El tiempo de espera puede ser mayor.`
      );
    }

    setIsSubmitting(true);

    try {
      const payload = {
        empresa_id: empresaId,
        pasajero_nombre: pasajeroNombre.trim(),
        pasajero_telefono: pasajeroTelefono.trim() || null,
        direccion_origen: origen.address,
        latitud_origen: origen.lat,
        longitud_origen: origen.lng,
        direccion_destino: destino.address,
        latitud_destino: destino.lat,
        longitud_destino: destino.lng,
        paradas_intermedias: paradas
          .filter((p) => p.address.trim() && p.lat && p.lng)
          .map((p) => ({
            direccion: p.address,
            latitud: p.lat,
            longitud: p.lng,
          })),
        tipo_vehiculo: tipoVehiculo,
        cantidad_pasajeros: cantidadPasajeros,
        cantidad_equipaje: cantidadEquipaje,
        metodo_pago: metodoPago,
        nota_conductor: notaConductor.trim() || null,
        centro_costo: centroCosto.trim() || null,
        es_programado: false,
        fecha_programada: null,
      };

      const response = await apiClient.post('/api/reservas', payload);
      toast.success('✅ Viaje creado correctamente');
      router.push(`/operativo/confirmacion/${response.data.id}`);
    } catch (error: any) {
      console.error('❌ Error al crear reserva:', error);
      const detail = error?.response?.data?.detail;
      let mensaje = 'Error al crear la solicitud';
      if (typeof detail === 'string') mensaje = detail;
      else if (Array.isArray(detail)) {
        mensaje = detail
          .map((err: any) => {
            const campo = err.loc ? err.loc.slice(1).join('.') : 'campo';
            return `${campo}: ${err.msg}`;
          })
          .join(', ');
      } else if (detail?.msg) mensaje = detail.msg;
      toast.error(mensaje);
    } finally {
      setIsSubmitting(false);
    }
  };




// ============================================================
// 14. EFECTO - Estimación de precio con debounce
// ============================================================
useEffect(() => {
  if (!origen || !destino) {
    setPrecioEstimado(null);
    setDistanciaKm(null);
    setTiempoMinutos(null);
    return;
  }

  const timer = setTimeout(async () => {
    setCalculandoPrecio(true);
    try {
      const payload = {
        direccion_origen: origen.address,
        direccion_destino: destino.address,
        paradas_intermedias: paradas
          .filter((p) => p.address.trim() && p.lat && p.lng)
          .map((p) => ({
            direccion: p.address,
            latitud: p.lat,
            longitud: p.lng,
          })),
        tipo_vehiculo: tipoVehiculo,
      };

      const response = await apiClient.post('/api/reservas/estimar-precio', payload);
      const data = response.data;

      setPrecioEstimado(data.precio_estimado);
      setDistanciaKm(data.distancia_km);
      setTiempoMinutos(data.tiempo_minutos);

      if (data.latitud_origen && data.longitud_origen) {
        setMapCenter({ lat: data.latitud_origen, lng: data.longitud_origen });
      } else if (origen.lat && origen.lng) {
        setMapCenter({ lat: origen.lat, lng: origen.lng });
      }
    } catch (error) {
      console.warn('⚠️ Error al estimar precio:', error);
      // ✅ CORRECCIÓN: No mostrar valor fijo incorrecto
      setPrecioEstimado(null);
      setDistanciaKm(null);
      setTiempoMinutos(null);
    } finally {
      setCalculandoPrecio(false);
    }
  }, 500);

  return () => clearTimeout(timer);
}, [origen, destino, paradas, tipoVehiculo]);




  // ============================================================
  // 15. RENDERIZADO CONDICIONAL
  // ============================================================
  if (turnoActivo === false) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Alert variant="destructive" className="max-w-lg">
          <AlertCircle className="h-5 w-5" />
          <AlertDescription className="ml-2">
            <p className="font-semibold">Turno inactivo</p>
            <p className="text-sm">
              Para crear una nueva solicitud, primero debes iniciar tu turno desde el{' '}
              <Button variant="link" className="px-0 h-auto" onClick={() => router.push('/operativo')}>
                Dashboard Operativo
              </Button>.
            </p>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (turnoActivo === null) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // ============================================================
  // 16. RENDERIZADO PRINCIPAL
  // ============================================================
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Car className="h-6 w-6" />
            Nueva Solicitud
          </h1>
          <p className="text-muted-foreground">
            Completa los datos para despachar un taxi. El origen se tomará desde la ubicación de la empresa.
          </p>
        </div>
        <Badge className="bg-green-100 text-green-800 border-green-200">Turno activo</Badge>
      </div>

      {/* Grid principal - 50/50 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* COLUMNA IZQUIERDA - Formulario */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Datos del Viaje</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Origen */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-green-500" />
                    Origen *
                  </Label>
                  <AddressAutocomplete
                    value={origen?.address || ''}
                    onChange={(address) => {
                      setOrigen((prev) => {
                        if (!prev) return { address, lat: 0, lng: 0 };
                        return { ...prev, address };
                      });
                    }}
                    onSelect={(address, lat, lng) => {
                      setOrigen({ address, lat, lng });
                      setMapCenter({ lat, lng });
                    }}
                    placeholder="Dirección de recogida"
                    initialLat={origen?.lat || null}
                    initialLng={origen?.lng || null}
                    label="Origen *"
                    required
                  />
                </div>

                {/* Paradas intermedias */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Paradas intermedias (opcional)</Label>
                  <WaypointList
                    waypoints={paradas}
                    onChange={setParadas}
                    maxWaypoints={5}
                    disabled={!turnoActivo}
                  />
                </div>

                {/* Destino */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Navigation className="h-4 w-4 text-red-500" />
                    Destino *
                  </Label>
                  <AddressAutocomplete
                    value={destino?.address || ''}
                    onChange={(address) => {
                      setDestino((prev) => {
                        if (!prev) return { address, lat: 0, lng: 0 };
                        return { ...prev, address };
                      });
                    }}
                    onSelect={(address, lat, lng) => {
                      setDestino({ address, lat, lng });
                    }}
                    placeholder="¿A dónde vas?"
                    label="Destino *"
                    required
                  />
                </div>

                {/* Pasajero y teléfono */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      Pasajero *
                    </Label>
                    <Input
                      placeholder="Nombre completo"
                      value={pasajeroNombre}
                      onChange={(e) => setPasajeroNombre(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Teléfono del pasajero</Label>
                    <Input
                      placeholder="Teléfono (opcional)"
                      value={pasajeroTelefono}
                      onChange={(e) => setPasajeroTelefono(e.target.value)}
                    />
                  </div>
                </div>

                {/* Pasajeros y equipaje */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Pasajeros</Label>
                    <Select
                      value={String(cantidadPasajeros)}
                      onValueChange={(v) => setCantidadPasajeros(Number(v))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Cantidad" />
                      </SelectTrigger>
                      <SelectContent>
                        {[1, 2, 3, 4].map((n) => (
                          <SelectItem key={n} value={String(n)}>
                            {n}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Equipaje (medianas)</Label>
                    <Select
                      value={String(cantidadEquipaje)}
                      onValueChange={(v) => setCantidadEquipaje(Number(v))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Cantidad" />
                      </SelectTrigger>
                      <SelectContent>
                        {[0, 1, 2, 3, 4].map((n) => (
                          <SelectItem key={n} value={String(n)}>
                            {n}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Tipo de vehículo y método de pago */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Car className="h-4 w-4" />
                      Tipo de Vehículo
                    </Label>
                    <Select value={tipoVehiculo} onValueChange={setTipoVehiculo}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard">Standard (4 pasajeros)</SelectItem>
                        <SelectItem value="premium">Premium</SelectItem>
                        <SelectItem value="van">Van (6 pasajeros)</SelectItem>
                        <SelectItem value="minivan">Minivan (7 pasajeros)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Método de Pago</Label>
                    <Select value={metodoPago} onValueChange={setMetodoPago}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="efectivo">Efectivo</SelectItem>
                        <SelectItem value="qr">QR / Transferencia</SelectItem>
                        <SelectItem value="transferencia">Transferencia Bancaria</SelectItem>
                        <SelectItem value="cuenta_corriente">Cuenta Corriente</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Centro de costo */}
                <div className="space-y-2">
                  <Label>Centro de costo / Referencia</Label>
                  <Input
                    placeholder="Ej: Habitación 304, Paciente Pérez"
                    value={centroCosto}
                    onChange={(e) => setCentroCosto(e.target.value)}
                  />
                </div>

                {/* Nota para el conductor */}
                <div className="space-y-2">
                  <Label>Nota para el conductor</Label>
                  <Input
                    placeholder="Necesidades especiales, equipaje, etc."
                    value={notaConductor}
                    onChange={(e) => setNotaConductor(e.target.value)}
                  />
                </div>

                {/* Botones */}
                <div className="flex flex-col sm:flex-row gap-3 pt-2">
                  <Button
                    type="submit"
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                    disabled={
                      isSubmitting ||
                      !turnoActivo ||
                      (!isLoadingChoferes && disponibles === 0)
                    }
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Despachando...
                      </>
                    ) : (
                      <>
                        Despachar Taxi
                        {precioEstimado !== null && (
                          <span className="ml-2 font-mono">| ${precioEstimado.toFixed(0)}</span>
                        )}
                      </>
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={limpiarFormulario}
                    disabled={isSubmitting}
                    className="flex items-center gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    Limpiar
                  </Button>
                </div>

                {/* Mensaje si no hay choferes disponibles */}
                {!isLoadingChoferes && disponibles === 0 && (
                  <Alert variant="destructive" className="mt-2">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      No hay choferes disponibles en este momento. Intenta más tarde.
                    </AlertDescription>
                  </Alert>
                )}

                {/* Mensaje si hay pocos choferes */}
                {!isLoadingChoferes && hayPocosChoferes && (
                  <Alert className="mt-2 border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <AlertDescription className="text-yellow-800 dark:text-yellow-400">
                      Solo {disponibles} chofer{disponibles !== 1 ? 'es' : ''} disponible{disponibles !== 1 ? 's' : ''}. 
                      El tiempo de espera puede ser mayor.
                    </AlertDescription>
                  </Alert>
                )}
              </form>
            </CardContent>
          </Card>
        </div>

        {/* COLUMNA DERECHA - Mapa, Cotización y Choferes */}
        <div className="space-y-6">
          {/* Mapa */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Ubicación en el mapa</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <MapPicker
                origin={origen}
                destination={destino}
                waypoints={paradas}
                onOriginDragEnd={handleOriginDragEnd}
                onDestinationDragEnd={handleDestinationDragEnd}
                onWaypointDragEnd={handleWaypointDragEnd}
                height="400px"
                center={mapCenter}
                zoom={14}
                draggable={true}
              />
            </CardContent>
          </Card>

          {/* Cotización */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Tarifa Estimada
              </CardTitle>
            </CardHeader>
            <CardContent>
              {calculandoPrecio ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : precioEstimado !== null ? (
                <div className="space-y-3">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">${precioEstimado.toFixed(0)}</p>
                    <p className="text-xs text-muted-foreground">Precio estimado</p>
                  </div>
                  <div className="flex justify-between text-sm">
                    <div className="flex items-center gap-1">
                      <Navigation className="h-3 w-3" />
                      <span>{distanciaKm?.toFixed(1) || '--'} km</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{tiempoMinutos || '--'} min</span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground text-sm py-4">
                  Completa origen y destino para ver la tarifa
                </p>
              )}
            </CardContent>
          </Card>

          {/* Choferes disponibles */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Car className="h-4 w-4" />
                Coches Libres
                {isLoadingChoferes ? (
                  <Loader2 className="h-3 w-3 animate-spin ml-1" />
                ) : (
                  <Badge
                    variant="secondary"
                    className={`ml-1 text-xs ${
                      disponibles === 0
                        ? 'bg-red-100 text-red-800 border-red-200'
                        : 'bg-green-100 text-green-800 border-green-200'
                    }`}
                  >
                    {disponibles}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingChoferes ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : choferes.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-sm text-muted-foreground">No hay choferes disponibles</p>
                </div>
              ) : (
                <>
                  <div className="text-center py-2">
                    <p
                      className={`text-2xl font-bold ${
                        disponibles === 0 ? 'text-red-600' : 'text-green-600'
                      }`}
                    >
                      {disponibles}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Chofer{disponibles !== 1 ? 'es' : ''} disponible{disponibles !== 1 ? 's' : ''} en la zona
                    </p>
                    {disponibles === 0 && (
                      <p className="text-xs text-red-500 mt-1 font-medium">
                        ⚠️ Sin coches disponibles
                      </p>
                    )}
                  </div>
                  <div className="space-y-2 text-sm max-h-[180px] overflow-y-auto pr-1">
                    {choferes.map((chofer: any, index: number) => {
                      const estadoColor =
                        chofer.estado_laboral === 'libre'
                          ? 'bg-green-100 text-green-800 border-green-200'
                          : chofer.estado_laboral === 'ocupado'
                          ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                          : 'bg-gray-100 text-gray-500 border-gray-200';

                      const estadoLabel =
                        chofer.estado_laboral === 'libre'
                          ? 'Libre'
                          : chofer.estado_laboral === 'ocupado'
                          ? 'Ocupado'
                          : 'Fuera de servicio';

                      return (
                        <div
                          key={chofer.id || index}
                          className="flex justify-between items-center border-b last:border-0 py-1.5"
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            <div
                              className={`h-2 w-2 rounded-full flex-shrink-0 ${
                                chofer.estado_laboral === 'libre'
                                  ? 'bg-green-500'
                                  : chofer.estado_laboral === 'ocupado'
                                  ? 'bg-yellow-500'
                                  : 'bg-gray-400'
                              }`}
                            />
                            <span className="truncate">{chofer.nombre || 'Sin nombre'}</span>
                            {chofer.vehiculo?.patente && (
                              <span className="text-xs text-muted-foreground font-mono">
                                {chofer.vehiculo.patente}
                              </span>
                            )}
                          </div>
                          <Badge className={`${estadoColor} shadow-none flex-shrink-0 ml-2`}>
                            {estadoLabel}
                          </Badge>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}