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

    // No hace falta limpiar porque el websocketService maneja un solo callback global
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

        <FlatList
          data={viajesDisponibles}
          keyExtractor={(item) => item.id}
          renderItem={renderViaje}
          contentContainerStyle={{ paddingBottom: 32 }}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyIcon}>🛰️</Text>
              <Text style={styles.emptyText}>Esperando viajes...</Text>
              <Text style={styles.emptySubtext}>Los viajes aparecerán acá automáticamente</Text>
            </View>
          }
        />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1 },
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