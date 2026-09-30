import { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '@/constants/colors';
import { viajeService } from '@/services/viaje.service';
import { useViajeStore } from '@/stores/viaje.store';
import { ScreenHeader } from '@/components/common/ScreenHeader';
import { ModalCancelarViaje } from '@/components/viaje/ModalCancelarViaje';
import {
  formatearMoneda,
  formatearDistancia,
  formatearDuracion,
  formatearHora,
} from '@/utils/formato';
import type { ViajeActivo, ViajeSolicitado, FinalizarViajeResponse} from '@/types/viaje.types';

// ============================================================
// TRADUCCIONES DE VALORES DEL BACKEND
// ============================================================
const ESTADO_LABELS: Record<string, string> = {
  pendiente: 'Pendiente',
  publicado: 'Publicado',
  programada: 'Programada',
  aceptado: 'Aceptado',
  en_curso: 'En curso',
  finalizado: 'Finalizado',
  cancelado: 'Cancelado',
  pagado: 'Pagado',
  expirado: 'Expirado',
};

const METODO_PAGO_LABELS: Record<string, string> = {
  efectivo: 'Efectivo',
  billetera: 'Billetera',
  tarjeta_credito: 'Tarjeta crédito',
  tarjeta_debito: 'Tarjeta débito',
};

function traducirEstado(estado: string | null | undefined): string {
  if (!estado) return '—';
  return ESTADO_LABELS[estado] ?? estado;
}

function traducirMetodoPago(metodo: string | null | undefined): string {
  if (!metodo) return '—';
  return METODO_PAGO_LABELS[metodo] ?? metodo;
}

export default function ViajeEnCursoScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const viajeActivoStore = useViajeStore((s) => s.viajeActivo);
  const setViajeActivo = useViajeStore((s) => s.setViajeActivo);

  const [viaje, setViaje] = useState<ViajeActivo | null>(viajeActivoStore);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalCancelarVisible, setModalCancelarVisible] = useState(false);
  const [cancelando, setCancelando] = useState(false);
  const [cancelarError, setCancelarError] = useState<string | null>(null);

  // Mapa estático
  const [mapaUrl, setMapaUrl] = useState<string | null>(null);
  const [mapaLoading, setMapaLoading] = useState(false);

  // ============================================
  // SI EL STORE ESTÁ VACÍO, TRAER DEL BACKEND
  // ============================================
  useEffect(() => {
    if (viaje || !id) return;

    let montado = true;
    (async () => {
      setLoading(true);
      try {
        const data: ViajeSolicitado = await viajeService.obtenerEstado(id);
        if (!montado) return;

        const adaptado: ViajeActivo = {
          id: data.id,
          estado: data.estado,
          origen:
            data.origen_lat != null && data.origen_lng != null
              ? { lat: data.origen_lat, lng: data.origen_lng }
              : null,
          destino:
            data.destino_lat != null && data.destino_lng != null
              ? { lat: data.destino_lat, lng: data.destino_lng }
              : null,
          direccion_origen: data.direccion_origen,
          direccion_destino: data.direccion_destino,
          pasajero_id: data.pasajero_id ?? '',
          pasajero_nombre: data.pasajero_nombre ?? 'Pasajero anónimo',
          precio_estimado: data.precio_estimado,
          precio_final: data.precio_final,
          moneda: data.moneda,
          tiempo_estimado_segundos: data.tiempo_estimado_segundos,
          distancia_metros: data.distancia_metros,
          solicitado_en: data.solicitado_en,
          aceptado_en: data.aceptado_en,
          iniciado_en: data.iniciado_en,
          origen_tipo: data.origen_tipo ?? null,
          metodo_pago: data.metodo_pago ?? null,
        };

        setViaje(adaptado);
        setViajeActivo(adaptado);
      } catch (e: any) {
        if (!montado) return;
        setError(
          e?.response?.data?.detail ||
            e?.message ||
            'No se pudo cargar el viaje'
        );
      } finally {
        if (montado) setLoading(false);
      }
    })();

    return () => {
      montado = false;
    };
  }, [id, viaje, setViajeActivo]);

  // ============================================
  // CARGAR MAPA ESTÁTICO
  // ============================================
  useEffect(() => {
    if (!viaje) return;
    if (!viaje.origen || !viaje.destino) return;
    if (mapaUrl) return; // ya cargado, no re-fetch

    let montado = true;
    (async () => {
      setMapaLoading(true);
      try {
        const { url } = await viajeService.obtenerUrlMapa({
          origen_lat: viaje.origen!.lat,
          origen_lng: viaje.origen!.lng,
          destino_lat: viaje.destino!.lat,
          destino_lng: viaje.destino!.lng,
        });
        if (!montado) return;
        setMapaUrl(url);
      } catch (e: any) {
        // Fallback: se usa la imagen mock
        console.warn('[Viaje en curso] Error cargando mapa:', e?.message);
      } finally {
        if (montado) setMapaLoading(false);
      }
    })();

    return () => {
      montado = false;
    };
  }, [viaje, mapaUrl]);

  // ============================================
  // FINALIZAR VIAJE
  // ============================================
  const handleFinalizar = () => {
    Alert.alert(
      '¿Llegaste al destino?',
      'Se finalizará el viaje y quedarás libre para otro.',
      [
        { text: 'Todavía no', style: 'cancel' },
        {
          text: 'Sí, llegué',
          onPress: () => confirmarFinalizar(),
        },
      ]
    );
  };

    const confirmarFinalizar = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const resultado: FinalizarViajeResponse = await viajeService.finalizarViaje(id);

      // Limpiar el store antes de navegar
      setViajeActivo(null);

      // Armar el mensaje del alert
      const montoFormateado = formatearMoneda(resultado.precio_final);
      const esFallback = resultado.precio_calculado_con === 'fallback_estimado';

      const mensaje = esFallback
        ? `Monto: ${montoFormateado} ${resultado.moneda}\n\n⚠️ El precio se calculó por fallback (usando el estimado). Avisá al administrador.`
        : `Monto: ${montoFormateado} ${resultado.moneda}\n\nCalculado con el motor de tarifas.`;

      Alert.alert(
        'Viaje finalizado',
        mensaje,
        [
          {
            text: 'OK',
            onPress: () => router.replace('/(app)/viajes/calle' as any),
          },
        ],
        { cancelable: false }
      );
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          e?.message ||
          'Error al finalizar el viaje'
      );
      setLoading(false);
    }
  };

  // ============================================
  // CANCELAR VIAJE
  // ============================================
  const handleAbrirCancelar = () => {
    setCancelarError(null);
    setModalCancelarVisible(true);
  };

  const handleConfirmarCancelar = async (motivo: string) => {
    if (!id) return;
    setCancelando(true);
    setCancelarError(null);
    try {
      await viajeService.cancelarViaje(id, motivo);
      setModalCancelarVisible(false);
      setViajeActivo(null);
      router.replace('/(app)/viajes/calle' as any);
    } catch (e: any) {
      setCancelarError(
        e?.response?.data?.detail ||
          e?.message ||
          'Error al cancelar el viaje'
      );
    } finally {
      setCancelando(false);
    }
  };

  // ============================================
  // RENDER
  // ============================================
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
      >
        <ScreenHeader
          titulo="VIAJE EN CURSO"
          conSafeArea={false}
        />

        {/* Estado de carga */}
        {loading && !viaje && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color={COLORS.primary} size="large" />
            <Text style={styles.loadingTexto}>Cargando viaje...</Text>
          </View>
        )}

        {/* Sin viaje */}
        {!loading && !viaje && (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcono}>🚖</Text>
            <Text style={styles.emptyTitulo}>No hay viaje activo</Text>
            <Text style={styles.emptyTexto}>
              {error || `No se encontró el viaje con id ${id}`}
            </Text>
          </View>
        )}

        {/* Con viaje */}
        {viaje && (
          <>
            {/* Mapa estático */}
            <View style={styles.mapaWrapper}>
              {mapaLoading ? (
                <View style={styles.mapaLoading}>
                  <ActivityIndicator color={COLORS.primary} size="small" />
                  <Text style={styles.mapaLoadingTexto}>
                    Cargando mapa...
                  </Text>
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

            {/* Direcciones */}
            <View style={styles.bloque}>
              <View style={styles.direccionItem}>
                <Text style={styles.direccionIconoOrigen}>📍</Text>
                <View style={styles.direccionTextoWrapper}>
                  <Text style={styles.direccionLabel}>ORIGEN</Text>
                  <Text style={styles.direccionTexto} numberOfLines={2}>
                    {viaje.direccion_origen || '—'}
                  </Text>
                </View>
              </View>

              <View style={styles.direccionSeparador} />

              <View style={styles.direccionItem}>
                <Text style={styles.direccionIconoDestino}>🏁</Text>
                <View style={styles.direccionTextoWrapper}>
                  <Text style={styles.direccionLabel}>DESTINO</Text>
                  <Text style={styles.direccionTexto} numberOfLines={2}>
                    {viaje.direccion_destino || '—'}
                  </Text>
                </View>
              </View>
            </View>

            {/* Info destacada */}
            <View style={styles.infoDestacada}>
              <View style={styles.infoDestacadaItem}>
                <Text style={styles.infoDestacadaValor}>
                  {formatearDistancia(viaje.distancia_metros)}
                </Text>
                <Text style={styles.infoDestacadaLabel}>DISTANCIA</Text>
              </View>
              <View style={styles.infoDestacadaDivider} />
              <View style={styles.infoDestacadaItem}>
                <Text style={styles.infoDestacadaValor}>
                  {formatearDuracion(viaje.tiempo_estimado_segundos)}
                </Text>
                <Text style={styles.infoDestacadaLabel}>TIEMPO</Text>
              </View>
              <View style={styles.infoDestacadaDivider} />
              <View style={styles.infoDestacadaItem}>
                <Text style={styles.infoDestacadaValor}>
                  {viaje.precio_estimado != null
                    ? formatearMoneda(viaje.precio_estimado)
                    : '—'}
                </Text>
                <Text style={styles.infoDestacadaLabel}>PRECIO</Text>
              </View>
            </View>

            {/* Info secundaria */}
            <View style={styles.infoSecundaria}>
              <View style={styles.infoRow}>
                <Text style={styles.infoRowIcono}>💵</Text>
                <Text style={styles.infoRowLabel}>Pago</Text>
                <Text style={styles.infoRowValor}>
                  {traducirMetodoPago(viaje.metodo_pago)}
                </Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoRowIcono}>🕐</Text>
                <Text style={styles.infoRowLabel}>Iniciado</Text>
                <Text style={styles.infoRowValor}>
                  {formatearHora(viaje.iniciado_en || viaje.solicitado_en)}
                </Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoRowIcono}>✅</Text>
                <Text style={styles.infoRowLabel}>Estado</Text>
                <Text style={styles.infoRowValor}>
                  {traducirEstado(viaje.estado)}
                </Text>
              </View>
            </View>

            {/* Error */}
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorTexto}>⚠️ {error}</Text>
              </View>
            )}

            {/* Botones */}
            <TouchableOpacity
              style={[styles.botonPrincipal, loading && styles.botonDisabled]}
              onPress={handleFinalizar}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color={COLORS.textPrimary} size="small" />
              ) : (
                <Text style={styles.botonPrincipalTexto}>
                  ✓ LLEGUÉ AL DESTINO
                </Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.botonSecundario, loading && styles.botonDisabled]}
              onPress={handleAbrirCancelar}
              disabled={loading}
            >
              <Text style={styles.botonSecundarioTexto}>✕ CANCELAR VIAJE</Text>
            </TouchableOpacity>
          </>
        )}
      </ScrollView>

      <ModalCancelarViaje
        visible={modalCancelarVisible}
        onClose={() => {
          setModalCancelarVisible(false);
          setCancelarError(null);
        }}
        onConfirmar={handleConfirmarCancelar}
        isLoading={cancelando}
        error={cancelarError}
      />
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 24,
  },

  // Loading / empty
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    opacity: 0.7,
    marginTop: 12,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcono: {
    fontSize: 56,
    marginBottom: 12,
  },
  emptyTitulo: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  emptyTexto: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.6,
    textAlign: 'center',
    paddingHorizontal: 20,
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

  // Direcciones
  bloque: {
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    marginBottom: 14,
  },
  direccionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  direccionIconoOrigen: {
    fontSize: 18,
    marginRight: 10,
    marginTop: 1,
  },
  direccionIconoDestino: {
    fontSize: 18,
    marginRight: 10,
    marginTop: 1,
  },
  direccionTextoWrapper: {
    flex: 1,
  },
  direccionLabel: {
    color: COLORS.textPrimary,
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.5,
    marginBottom: 3,
  },
  direccionTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 18,
  },
  direccionSeparador: {
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    marginVertical: 12,
    marginLeft: 28,
  },

  // Info destacada
  infoDestacada: {
    flexDirection: 'row',
    backgroundColor: 'rgba(249, 200, 14, 0.1)',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: 'rgba(249, 200, 14, 0.2)',
    marginBottom: 14,
  },
  infoDestacadaItem: {
    flex: 1,
    alignItems: 'center',
  },
  infoDestacadaValor: {
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 0.3,
    marginBottom: 3,
  },
  infoDestacadaLabel: {
    color: COLORS.textPrimary,
    fontSize: 9,
    opacity: 0.6,
    letterSpacing: 1,
    fontWeight: '600',
  },
  infoDestacadaDivider: {
    width: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    marginHorizontal: 4,
  },

  // Info secundaria
  infoSecundaria: {
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 16,
    marginBottom: 18,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 7,
  },
  infoRowIcono: {
    fontSize: 14,
    width: 22,
  },
  infoRowLabel: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.6,
    flex: 1,
    marginLeft: 4,
  },
  infoRowValor: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
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

  // Botones
  botonPrincipal: {
    backgroundColor: COLORS.success,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    minHeight: 54,
  },
  botonPrincipalTexto: {
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 1.5,
  },
  botonSecundario: {
    backgroundColor: 'rgba(239, 68, 68, 0.12)',
    borderWidth: 1,
    borderColor: COLORS.error,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
  },
  botonSecundarioTexto: {
    color: COLORS.error,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1.5,
  },
  botonDisabled: {
    opacity: 0.4,
  },
});