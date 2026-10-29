import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Location from 'expo-location'; // ✅ Importamos Location
import { COLORS } from '@/constants/colors';
import { ScreenHeader } from '@/components/common/ScreenHeader';
import { useViajeStore } from '@/stores/viaje.store';
import { viajeService } from '@/services/viaje.service';
import { websocketService } from '@/services/websocket.service';
import type { ViajeSolicitado } from '@/types/viaje.types';

export default function GestionViajesScreen() {
  const navigation = useNavigation<any>();
  const insets = useSafeAreaInsets();
  
  const viajesDisponibles = useViajeStore((s) => s.viajesDisponibles);
  const agregarViajeDisponible = useViajeStore((s) => s.agregarViajeDisponible);
  const quitarViajeDisponible = useViajeStore((s) => s.quitarViajeDisponible);
  const setViajeActivo = useViajeStore((s) => s.setViajeActivo);

  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [cargandoDisponibles, setCargandoDisponibles] = useState(false);

  // ============================================
  // CARGAR VIAJES DISPONIBLES AL ABRIR LA PANTALLA
  // ============================================
  useEffect(() => {
    const cargarViajesDisponibles = async () => {
      setCargandoDisponibles(true);
      try {
        // 1. Pedir permiso de ubicación
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== 'granted') {
          console.warn('[GestionViajes] Permiso de ubicación denegado');
          return;
        }

        // 2. Obtener ubicación actual
        const location = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });

        // 3. Consultar al backend
        const data = await viajeService.obtenerViajesDisponibles(
          location.coords.latitude,
          location.coords.longitude,
          5000 // 5 km
        );

        // 4. Agregar al store (sin duplicar los que ya llegaron por WS)
        data.viajes.forEach((v) => {
          if (!viajesDisponibles.some((existente) => existente.id === v.id)) {
            // Adaptamos el payload del backend a ViajeSolicitado
            const viajeAdaptado: ViajeSolicitado = {
              id: v.id,
              control_base_id: '',
              pasajero_id: '',
              chofer_id: null,
              chofer_vehiculo_id: null,
              vehiculo_id: null,
              turno_id: null,
              origen_lat: v.origen_lat,
              origen_lng: v.origen_lng,
              destino_lat: v.destino_lat,
              destino_lng: v.destino_lng,
              direccion_origen: v.direccion_origen,
              direccion_destino: v.direccion_destino,
              estado: 'publicado',
              precio_estimado: v.precio_estimado,
              precio_final: null,
              moneda: 'ARS',
              tiempo_estimado_segundos: v.tiempo_estimado_segundos,
              distancia_metros: v.distancia_metros,
              url_seguimiento: null,
              codigo_compartido: null,
              solicitado_en: v.solicitado_en,
              aceptado_en: null,
              iniciado_en: null,
              finalizado_en: null,
              cancelado_en: null,
              cancelado_por: null,
              motivo_cancelacion: null,
              fecha_programada: null,
              reserva_procesada: false,
              comercio_id: null,
              empresa_id: null,
              nombre_pasajero: v.nombre_pasajero,
              notas: null,
              facturado: false,
              origen_tipo: null,
              metodo_pago: null,
            };
            agregarViajeDisponible(viajeAdaptado);
          }
        });
      } catch (error: any) {
        console.warn('[GestionViajes] Error cargando viajes:', error?.message);
      } finally {
        setCargandoDisponibles(false);
      }
    };

    cargarViajesDisponibles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Solo al montar la pantalla

  // ============================================
  // WEBSOCKET: ESCUCHAR NUEVOS VIAJES Y VIAJES TOMADOS
  // ============================================
  useEffect(() => {
    const manejarMensaje = (mensaje: any) => {
      // 1. Llega un nuevo viaje publicado
      if (mensaje.type === 'nuevo_viaje') {
        const viaje = mensaje.data as ViajeSolicitado;
        agregarViajeDisponible(viaje);
      }
      // 2. Otro chofer aceptó el viaje -> quitarlo de mi lista
      if (mensaje.type === 'viaje_tomado') {
        const viajeId = mensaje.data?.viaje_id || mensaje.data?.id;
        if (viajeId) {
          quitarViajeDisponible(viajeId);
        }
      }
    };

    websocketService.onMensaje(manejarMensaje);
  }, [agregarViajeDisponible, quitarViajeDisponible]);

  // ============================================
  // ACEPTAR VIAJE
  // ============================================
  const handleAceptar = async (viaje: ViajeSolicitado) => {
    setLoadingId(viaje.id);
    try {
      await viajeService.aceptarViaje(viaje.id);
      
      // Quitar de la lista de disponibles
      quitarViajeDisponible(viaje.id);
      
      // Setear como activo y navegar
      setViajeActivo({
        id: viaje.id,
        estado: 'aceptado',
        origen: viaje.origen_lat && viaje.origen_lng ? { lat: viaje.origen_lat, lng: viaje.origen_lng } : null,
        destino: viaje.destino_lat && viaje.destino_lng ? { lat: viaje.destino_lat, lng: viaje.destino_lng } : null,
        direccion_origen: viaje.direccion_origen,
        direccion_destino: viaje.direccion_destino,
        pasajero_id: viaje.pasajero_id ?? '',
        pasajero_nombre: viaje.pasajero_nombre || 'Pasajero',
        precio_estimado: viaje.precio_estimado,
        precio_final: viaje.precio_final,
        moneda: viaje.moneda || 'ARS',
        tiempo_estimado_segundos: viaje.tiempo_estimado_segundos,
        distancia_metros: viaje.distancia_metros,
        solicitado_en: viaje.solicitado_en,
        aceptado_en: new Date().toISOString(),
        iniciado_en: null,
        origen_tipo: viaje.origen_tipo || 'app',
        metodo_pago: viaje.metodo_pago || 'efectivo',
      });

      navigation.navigate('ViajeDetalle', { id: viaje.id });

    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'No se pudo aceptar el viaje');
    } finally {
      setLoadingId(null);
    }
  };

  // ============================================
  // RECHAZAR VIAJE
  // ============================================
  const handleRechazar = async (viaje: ViajeSolicitado) => {
    setLoadingId(viaje.id);
    try {
      await viajeService.rechazarViaje(viaje.id);
      quitarViajeDisponible(viaje.id);
    } catch (e: any) {
      Alert.alert('Error', 'No se pudo rechazar el viaje');
    } finally {
      setLoadingId(null);
    }
  };

  // ============================================
  // RENDER
  // ============================================
  const renderViaje = ({ item }: { item: ViajeSolicitado }) => {
    const isLoading = loadingId === item.id;
    
    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardPrecio}>
            {item.precio_estimado ? `$${item.precio_estimado}` : 'A calcular'}
          </Text>
          <Text style={styles.cardDistancia}>
            {item.distancia_metros ? `${(item.distancia_metros / 1000).toFixed(1)} km` : '—'}
          </Text>
        </View>
        
        <Text style={styles.cardDireccion}>📍 {item.direccion_origen}</Text>
        <Text style={styles.cardDireccion}>🏁 {item.direccion_destino || 'Destino no especificado'}</Text>
        
        <View style={styles.botonesContainer}>
          <TouchableOpacity 
            style={[styles.btnAceptar, isLoading && { opacity: 0.5 }]} 
            onPress={() => handleAceptar(item)}
            disabled={isLoading}
          >
            {isLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>ACEPTAR</Text>}
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.btnRechazar, isLoading && { opacity: 0.5 }]} 
            onPress={() => handleRechazar(item)}
            disabled={isLoading}
          >
            <Text style={styles.btnText}>RECHAZAR</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={styles.container}>
      <View style={[styles.content, { paddingHorizontal: 20 }]}>
        <ScreenHeader 
          titulo="VIAJES DISPONIBLES" 
          textoIzquierda="← HOME" 
          onIzquierda={() => navigation.navigate('Home')} 
          conSafeArea={false} 
          style={{ paddingTop: insets.top + 12 }} 
        />

        {cargandoDisponibles && viajesDisponibles.length === 0 && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color={COLORS.primary} size="large" />
            <Text style={styles.loadingText}>Buscando viajes en tu zona...</Text>
          </View>
        )}

        <FlatList
          data={viajesDisponibles}
          keyExtractor={(item) => item.id}
          renderItem={renderViaje}
          contentContainerStyle={{ paddingBottom: 32 }}
          ListEmptyComponent={
            !cargandoDisponibles ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>🛰️</Text>
                <Text style={styles.emptyText}>Esperando viajes...</Text>
                <Text style={styles.emptySubtext}>Los viajes aparecerán acá automáticamente</Text>
              </View>
            ) : null
          }
        />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1 },
  loadingContainer: { alignItems: 'center', justifyContent: 'center', paddingTop: 60 },
  loadingText: { color: COLORS.textSecondary, marginTop: 12 },
  emptyContainer: { alignItems: 'center', justifyContent: 'center', paddingTop: 60 },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyText: { color: COLORS.textPrimary, fontSize: 18, fontWeight: 'bold' },
  emptySubtext: { color: COLORS.textSecondary, fontSize: 14, marginTop: 4, textAlign: 'center' },
  
  card: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  cardPrecio: { color: COLORS.primary, fontSize: 20, fontWeight: 'bold' },
  cardDistancia: { color: COLORS.textSecondary, fontSize: 14 },
  cardDireccion: { color: COLORS.textPrimary, fontSize: 14, marginBottom: 6 },
  
  botonesContainer: { flexDirection: 'row', gap: 10, marginTop: 16 },
  btnAceptar: { flex: 1, backgroundColor: '#4CAF50', padding: 14, borderRadius: 8, alignItems: 'center' },
  btnRechazar: { flex: 1, backgroundColor: '#FF6B6B', padding: 14, borderRadius: 8, alignItems: 'center' },
  btnText: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
});