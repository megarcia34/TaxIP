import { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Keyboard,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';
import { COLORS } from '@/constants/colors';
import { viajeService } from '@/services/viaje.service';
import { useViajeStore } from '@/stores/viaje.store';
import { ScreenHeader } from '@/components/common/ScreenHeader';
import {
  formatearMoneda,
  formatearDistancia,
  formatearDuracion,
} from '@/utils/formato';
import type { Coordenada } from '@/types/ubicacion.types';
import type {
  DestinoSeleccionado,
  MetodoPagoCalle,
  SolicitarViajeCalleRequest,
  ViajeSolicitado,
  CalcularCostoResponse,
} from '@/types/viaje.types';

// ============================================================
// CONFIGURACIÓN GOOGLE PLACES
// ============================================================
const PLACES_RADIUS_METROS = 30000; // 30 km

// ============================================================
// MÉTODOS DE PAGO
// ============================================================
const METODOS_PAGO: { id: MetodoPagoCalle; label: string }[] = [
  { id: 'efectivo', label: 'Efectivo' },
  { id: 'billetera', label: 'Billetera' },
  { id: 'tarjeta_debito', label: 'Débito' },
];

// ============================================================
// DEBOUNCE
// ============================================================
const DEBOUNCE_MS = 500;

export default function ViajeCalleScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const setViajeActivo = useViajeStore((s) => s.setViajeActivo);

  // Estado local
  const [origen, setOrigen] = useState<Coordenada | null>(null);
  const [origenLoading, setOrigenLoading] = useState(true);
  const [origenError, setOrigenError] = useState<string | null>(null);
  const [direccionOrigen, setDireccionOrigen] = useState<string | null>(null);
  const [destino, setDestino] = useState<DestinoSeleccionado | null>(null);
  const [metodoPago, setMetodoPago] = useState<MetodoPagoCalle>('efectivo');
  const [creando, setCreando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Costo tentativo
  const [calculando, setCalculando] = useState(false);
  const [costoTentativo, setCostoTentativo] =
    useState<CalcularCostoResponse | null>(null);

  // Mapa estático
  const [mapaUrl, setMapaUrl] = useState<string | null>(null);
  const [mapaLoading, setMapaLoading] = useState(false);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const placesRef = useRef<any>(null);

  // ============================================
  // OBTENER UBICACIÓN ACTUAL
  // ============================================
  const obtenerUbicacion = useCallback(async () => {
    setOrigenLoading(true);
    setOrigenError(null);
    setDireccionOrigen(null);
    try {
      const permiso = await Location.requestForegroundPermissionsAsync();
      if (permiso.status !== 'granted') {
        setOrigenError('Permiso denegado');
        setOrigen(null);
        return;
      }

      const pos = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      const coords = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      };
      setOrigen(coords);

      // Reverse geocoding del origen (G25) — no bloqueante.
      try {
        const geo = await viajeService.reverseGeocode(coords.lat, coords.lng);
        setDireccionOrigen(geo.direccion);
      } catch (geoErr) {
        console.warn('[Viaje de calle] Reverse geocode falló:', geoErr);
        setDireccionOrigen(null);
      }
    } catch (e: any) {
      setOrigenError(e?.message || 'Error al obtener ubicación');
      setOrigen(null);
    } finally {
      setOrigenLoading(false);
    }
  }, []);

  useEffect(() => {
    obtenerUbicacion();
  }, [obtenerUbicacion]);

  // ============================================
  // CALCULAR COSTO TENTATIVO (con debounce)
  // ============================================
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }

    if (!origen || !destino) {
      setCostoTentativo(null);
      setCalculando(false);
      return;
    }

    setCalculando(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const response = await viajeService.calcularCosto({
          origen_latitud: origen.lat,
          origen_longitud: origen.lng,
          destino_latitud: destino.lat,
          destino_longitud: destino.lng,
        });

        setCostoTentativo(response);
      } catch (e) {
        console.warn('[Viaje de calle] Error calculando costo:', e);
        setCostoTentativo(null);
      } finally {
        setCalculando(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
    };
  }, [origen, destino]);

  // ============================================
  // CARGAR MAPA ESTÁTICO (Static Maps)
  // Se dispara cuando hay origen + destino.
  // Se limpia cuando se limpia el destino.
  // ============================================
  useEffect(() => {
    if (!origen || !destino) {
      setMapaUrl(null);
      setMapaLoading(false);
      return;
    }

    let montado = true;
    setMapaLoading(true);

    (async () => {
      try {
        const { url } = await viajeService.obtenerUrlMapa({
          origen_lat: origen.lat,
          origen_lng: origen.lng,
          destino_lat: destino.lat,
          destino_lng: destino.lng,
        });
        if (!montado) return;
        setMapaUrl(url);
      } catch (e: any) {
        console.warn('[Viaje de calle] Error cargando mapa:', e?.message);
        if (!montado) return;
        setMapaUrl(null);
      } finally {
        if (montado) setMapaLoading(false);
      }
    })();

    return () => {
      montado = false;
    };
  }, [origen, destino]);

  // ============================================
  // HANDLER DE SELECCIÓN DE PLACES
  // ============================================
  const handlePlaceSelected = (data: any, details: any | null = null) => {
    if (!details) {
      console.warn('[Viaje de calle] Places sin detalles:', data);
      return;
    }

    const lat = details.geometry?.location?.lat;
    const lng = details.geometry?.location?.lng;
    if (lat == null || lng == null) {
      console.warn('[Viaje de calle] Places sin coordenadas:', details);
      return;
    }

    setDestino({
      direccion: data.description || details.formatted_address || '',
      lat,
      lng,
      place_id: data.place_id || details.place_id || '',
    });
  };

  const handleClearDestino = () => {
    setDestino(null);
    setCostoTentativo(null);
    setMapaUrl(null);
    placesRef.current?.setAddressText('');
  };

  // ============================================
  // VALIDACIÓN
  // ============================================
  const formValido =
    origen !== null && destino !== null && !creando;

  // ============================================
  // CREAR VIAJE
  // ============================================
  const handleIniciarViaje = async () => {
    if (!formValido || !origen || !destino) return;
    Keyboard.dismiss();
    setError(null);
    setCreando(true);

    try {
      const request: SolicitarViajeCalleRequest = {
        origen_lat: origen.lat,
        origen_lng: origen.lng,
        // El backend pisa este campo con reverse geocoding (G25).
        direccion_origen: direccionOrigen ?? 'Ubicación GPS del chofer',
        destino_lat: destino.lat,
        destino_lng: destino.lng,
        direccion_destino: destino.direccion,
        metodo_pago: metodoPago,
      };

      const viaje: ViajeSolicitado = await viajeService.solicitarViajeCalle(
        request
      );

      setViajeActivo({
        id: viaje.id,
        estado: viaje.estado,
        origen:
          viaje.origen_lat != null && viaje.origen_lng != null
            ? { lat: viaje.origen_lat, lng: viaje.origen_lng }
            : null,
        destino:
          viaje.destino_lat != null && viaje.destino_lng != null
            ? { lat: viaje.destino_lat, lng: viaje.destino_lng }
            : null,
        direccion_origen: viaje.direccion_origen,
        direccion_destino: viaje.direccion_destino,
        pasajero_id: viaje.pasajero_id ?? '',
        pasajero_nombre: viaje.pasajero_nombre ?? 'Pasajero anónimo',
        precio_estimado: viaje.precio_estimado,
        precio_final: viaje.precio_final,
        moneda: viaje.moneda,
        tiempo_estimado_segundos: viaje.tiempo_estimado_segundos,
        distancia_metros: viaje.distancia_metros,
        solicitado_en: viaje.solicitado_en,
        aceptado_en: viaje.aceptado_en,
        iniciado_en: viaje.iniciado_en,
        origen_tipo: viaje.origen_tipo ?? null,
        metodo_pago: viaje.metodo_pago ?? null,
      });

      router.replace(`/(app)/viajes/${viaje.id}` as any);
    } catch (e: any) {
      const mensaje =
        e?.response?.data?.detail ||
        e?.message ||
        'Error al registrar el viaje';
      setError(mensaje);
    } finally {
      setCreando(false);
    }
  };

  // ============================================
  // RENDER
  // ============================================
  const apiKey = process.env.EXPO_PUBLIC_GOOGLE_MAPS_API_KEY ?? '';
  const origenDisponible = origen !== null;
  const inputDestinoDeshabilitado = !origenDisponible || creando;

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingTop: insets.top + 8 },
        ]}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <ScreenHeader
          titulo="VIAJE DE CALLE"
          textoIzquierda="HOME"
          onIzquierda={() => router.replace('/(app)/home' as any)}
          conSafeArea={false}
        />

        {/* Origen inline */}
        <View style={styles.origenRow}>
          <Text style={styles.origenIcono}>📍</Text>
          {origenLoading ? (
            <>
              <ActivityIndicator
                color={COLORS.primary}
                size="small"
                style={{ marginRight: 8 }}
              />
              <Text style={styles.origenTexto}>Obteniendo ubicación...</Text>
            </>
          ) : origen ? (
            <>
              <Text style={styles.origenTexto} numberOfLines={1}>
                {direccionOrigen ??
                  `${origen.lat.toFixed(5)}, ${origen.lng.toFixed(5)}`}
              </Text>
              <TouchableOpacity
                style={styles.origenBoton}
                onPress={obtenerUbicacion}
                disabled={creando}
              >
                <Text style={styles.origenBotonTexto}>↻</Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              <Text style={[styles.origenTexto, { color: COLORS.error }]}>
                {origenError || 'Sin ubicación'}
              </Text>
              <TouchableOpacity
                style={styles.origenBoton}
                onPress={obtenerUbicacion}
                disabled={creando}
              >
                <Text style={styles.origenBotonTexto}>↻</Text>
              </TouchableOpacity>
            </>
          )}
        </View>

        {/* Destino */}
        <Text style={styles.label}>¿A DÓNDE VAMOS?</Text>

        {!origenDisponible ? (
          <View style={styles.destinoDeshabilitado}>
            <Text style={styles.destinoDeshabilitadoTexto}>
              Esperando ubicación...
            </Text>
          </View>
        ) : (
          <View style={styles.placesWrapper}>
            <GooglePlacesAutocomplete
              ref={placesRef}
              placeholder="Ej: Catamarca 375 o Ruta 9, Termas"
              minLength={3}
              fetchDetails
              onPress={handlePlaceSelected}
              query={{
                key: apiKey,
                language: 'es',
                components: 'country:ar',
                location: `${origen!.lat},${origen!.lng}`,
                radius: PLACES_RADIUS_METROS,
              }}
              enablePoweredByContainer={false}
              nearbyPlacesAPI="GooglePlacesSearch"
              debounce={300}
              styles={{
                container: {
                  flex: 0,
                },
                textInputContainer: {
                  backgroundColor: 'transparent',
                  borderTopWidth: 0,
                  borderBottomWidth: 0,
                },
                textInput: {
                  color: COLORS.textPrimary,
                  fontSize: 18,
                  fontWeight: '500',
                  paddingVertical: 8,
                  paddingHorizontal: 2,
                  backgroundColor: 'transparent',
                  borderBottomWidth: 2,
                  borderBottomColor: COLORS.primary,
                  marginBottom: 0,
                  height: 44,
                },
                listView: {
                  backgroundColor: COLORS.backgroundMedium,
                  borderRadius: 10,
                  marginTop: 4,
                  borderWidth: 1,
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  zIndex: 1000,
                  elevation: 5,
                },
                row: {
                  backgroundColor: 'transparent',
                  paddingVertical: 12,
                  paddingHorizontal: 14,
                },
                description: {
                  color: COLORS.textPrimary,
                  fontSize: 14,
                },
                separator: {
                  height: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                },
                poweredContainer: {
                  display: 'none',
                },
              }}
              textInputProps={{
                editable: !inputDestinoDeshabilitado,
                placeholderTextColor: 'rgba(255, 255, 255, 0.4)',
                autoCapitalize: 'words',
                autoCorrect: false,
              }}
            />
          </View>
        )}

        {/* Destino seleccionado (chip para limpiar) */}
        {destino && (
          <View style={styles.destinoSeleccionado}>
            <Text style={styles.destinoSeleccionadoTexto} numberOfLines={2}>
              🏁 {destino.direccion}
            </Text>
            <TouchableOpacity
              style={styles.destinoSeleccionadoBoton}
              onPress={handleClearDestino}
              disabled={creando}
            >
              <Text style={styles.destinoSeleccionadoBotonTexto}>✕</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Mapa estático */}
        {origen && destino && (
          <View style={styles.mapaWrapper}>
            {mapaLoading ? (
              <View style={styles.mapaLoading}>
                <ActivityIndicator color={COLORS.primary} size="small" />
                <Text style={styles.mapaLoadingTexto}>Cargando mapa...</Text>
              </View>
            ) : mapaUrl ? (
              <Image
                source={{ uri: mapaUrl }}
                style={styles.mapaImagen}
                resizeMode="cover"
              />
            ) : (
              <Image
                source={require('@/assets/images/mapa-placeholder.png')}
                style={styles.mapaImagen}
                resizeMode="cover"
              />
            )}
          </View>
        )}

        {/* Costo tentativo */}
        {(calculando || costoTentativo) && (
          <View style={styles.costoWrapper}>
            <Text style={styles.costoLabel}>COSTO TENTATIVO</Text>
            {calculando ? (
              <View style={styles.costoCalculando}>
                <ActivityIndicator color={COLORS.primary} size="small" />
                <Text style={styles.costoCalculandoTexto}>Calculando...</Text>
              </View>
            ) : costoTentativo ? (
              <>
                <Text style={styles.costoPrecio}>
                  {formatearMoneda(costoTentativo.precio_estimado)}
                </Text>
                <Text style={styles.costoDetalle}>
                  {formatearDistancia(costoTentativo.distancia_metros)}
                  {'  ·  '}
                  {formatearDuracion(costoTentativo.tiempo_estimado_segundos)}
                </Text>
              </>
            ) : null}
          </View>
        )}

        {/* Método de pago */}
        <Text style={styles.label}>MÉTODO DE PAGO</Text>
        <View style={styles.metodosRow}>
          {METODOS_PAGO.map((m) => (
            <TouchableOpacity
              key={m.id}
              style={[
                styles.metodoChip,
                metodoPago === m.id && styles.metodoChipActive,
              ]}
              onPress={() => setMetodoPago(m.id)}
              disabled={creando}
            >
              <Text
                style={[
                  styles.metodoChipTexto,
                  metodoPago === m.id && styles.metodoChipTextoActive,
                ]}
              >
                {m.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Error */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorTexto}>⚠️ {error}</Text>
          </View>
        )}

        {/* Botón */}
        <TouchableOpacity
          style={[styles.botonIniciar, !formValido && styles.botonDisabled]}
          onPress={handleIniciarViaje}
          disabled={!formValido}
        >
          {creando ? (
            <ActivityIndicator color={COLORS.textDark} size="small" />
          ) : (
            <Text style={styles.botonIniciarTexto}>INICIAR VIAJE</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </LinearGradient>
  );
}

// ============================================================
// ESTILOS
// ============================================================
const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },

  // Origen inline
  origenRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 16,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 10,
  },
  origenIcono: {
    fontSize: 16,
    marginRight: 8,
  },
  origenTexto: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  origenBoton: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 16,
    backgroundColor: 'rgba(249, 200, 14, 0.15)',
  },
  origenBotonTexto: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: 'bold',
  },

  // Labels
  label: {
    color: COLORS.textPrimary,
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1.5,
    marginBottom: 6,
    opacity: 0.6,
  },

  // Places wrapper
  placesWrapper: {
    zIndex: 1000,
    marginBottom: 8,
  },

  // Destino deshabilitado (sin origen)
  destinoDeshabilitado: {
    paddingVertical: 12,
    paddingHorizontal: 2,
    borderBottomWidth: 2,
    borderBottomColor: 'rgba(255, 255, 255, 0.2)',
    marginBottom: 14,
  },
  destinoDeshabilitadoTexto: {
    color: 'rgba(255, 255, 255, 0.4)',
    fontSize: 16,
    fontWeight: '500',
  },

  // Destino seleccionado (chip)
  destinoSeleccionado: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(249, 200, 14, 0.12)',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 12,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: 'rgba(249, 200, 14, 0.3)',
  },
  destinoSeleccionadoTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
    marginRight: 8,
  },
  destinoSeleccionadoBoton: {
    width: 28,
    height: 28,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 14,
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
  },
  destinoSeleccionadoBotonTexto: {
    color: COLORS.error,
    fontSize: 14,
    fontWeight: 'bold',
  },

  // Mapa
  mapaWrapper: {
    marginBottom: 14,
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  mapaImagen: {
    width: '100%',
    height: 140,
  },
  mapaLoading: {
    height: 140,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
  },
  mapaLoadingTexto: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.7,
  },

  // Costo tentativo
  costoWrapper: {
    backgroundColor: 'rgba(249, 200, 14, 0.1)',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: 'rgba(249, 200, 14, 0.2)',
    alignItems: 'center',
  },
  costoLabel: {
    color: COLORS.textPrimary,
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.6,
    marginBottom: 4,
  },
  costoPrecio: {
    color: COLORS.textPrimary,
    fontSize: 26,
    fontWeight: 'bold',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  costoDetalle: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.75,
    fontWeight: '500',
  },
  costoCalculando: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 6,
  },
  costoCalculandoTexto: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.8,
  },

  // Métodos de pago
  metodosRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  metodoChip: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
  },
  metodoChipActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  metodoChipTexto: {
    color: COLORS.textPrimary,
    fontSize: 12,
    fontWeight: '600',
  },
  metodoChipTextoActive: {
    color: COLORS.textDark,
  },

  // Error
  errorContainer: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  errorTexto: {
    color: COLORS.error,
    fontSize: 12,
    textAlign: 'center',
  },

  // Botón
  botonIniciar: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  botonIniciarTexto: {
    color: COLORS.textDark,
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 1.5,
  },
  botonDisabled: {
    opacity: 0.4,
  },
});