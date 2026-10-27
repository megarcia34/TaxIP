import { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import { COLORS } from '@/constants/colors';
import { useAuthStore } from '@/stores/auth.store';
import { useTurnoStore } from '@/stores/turno.store';
import { useViajeStore } from '@/stores/viaje.store';
import { viajeService } from '@/services/viaje.service';
import { websocketService } from '@/services/websocket.service';
import { BannerResultados } from '@/components/home/BannerResultados';
import { ModuloCard } from '@/components/home/ModuloCard';
import type { ResultadosResumen } from '@/components/home/BannerResultados';

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuthStore();

  const turnoActivo = useTurnoStore((s) => s.turnoActivo);
  const cargarTurnoActivo = useTurnoStore((s) => s.cargarTurnoActivo);
  const setViajeActivo = useViajeStore((s) => s.setViajeActivo);

  const hayTurnoActivo = turnoActivo != null;

  const [resultadosAyer, setResultadosAyer] = useState<ResultadosResumen | null>(null);
  const [isLoadingResultados, setIsLoadingResultados] = useState(false);

  // ============================================
  // CONECTAR WEBSOCKET AL MONTAR
  // ============================================
  useEffect(() => {
    if (user?.id && token) {
      console.log('[WS] Conectando WebSocket desde Home...');
      websocketService.conectar(user.id, token);
    }
  }, [user?.id, token]);

  // Mock: simular carga de datos del backend
  useEffect(() => {
    setIsLoadingResultados(true);
    setTimeout(() => {
      setResultadosAyer({
        fecha: new Date(Date.now() - 86400000).toISOString().split('T')[0],
        viajes: 12,
        recaudado: 4500,
        kmRecorridos: 120,
        duracionMinutos: 510,
        viajeMasCaro: 800,
        viajeMasBajo: 200,
        promedioViaje: 375,
      });
      setIsLoadingResultados(false);
    }, 800);
  }, []);

  // J12: al montar, si el store persistido esta vacio, verificar el turno
  useEffect(() => {
    if (!hayTurnoActivo) {
      cargarTurnoActivo();
    }
  }, [hayTurnoActivo, cargarTurnoActivo]);

  // J15: verificar viaje activo
  useEffect(() => {
    const verificarViajeActivo = async () => {
      try {
        const viaje = await viajeService.obtenerViajeActivo();
        if (viaje) {
          setViajeActivo({
            id: viaje.id,
            estado: viaje.estado,
            origen: viaje.origen_lat && viaje.origen_lng
              ? { lat: viaje.origen_lat, lng: viaje.origen_lng }
              : null,
            destino: viaje.destino_lat && viaje.destino_lng
              ? { lat: viaje.destino_lat, lng: viaje.destino_lng }
              : null,
            direccion_origen: viaje.direccion_origen,
            direccion_destino: viaje.direccion_destino,
            pasajero_id: viaje.pasajero_id ?? '',
            pasajero_nombre: 'Pasajero anónimo',
            precio_estimado: viaje.precio_estimado,
            precio_final: viaje.precio_final,
            moneda: viaje.moneda,
            tiempo_estimado_segundos: viaje.tiempo_estimado_segundos,
            distancia_metros: viaje.distancia_metros,
            solicitado_en: viaje.solicitado_en,
            aceptado_en: viaje.aceptado_en,
            iniciado_en: viaje.iniciado_en,
            origen_tipo: 'via_publica',
            metodo_pago: viaje.metodo_pago,
          });
          navigation.navigate('ViajeDetalle', { id: viaje.id });
        }
      } catch (error) {
        // Si no hay viaje activo, no hacer nada
      }
    };

    verificarViajeActivo();
  }, [navigation, setViajeActivo]);

  // ============================================
  // GPS: ENVIAR UBICACIÓN CADA 15 SEGUNDOS
  // ============================================
  useEffect(() => {
    if (!hayTurnoActivo) {
      console.log('[GPS] ❌ No hay turno activo');
      return;
    }

    console.log('[GPS] ✅ Turno activo detectado, iniciando GPS...');

    let interval: ReturnType<typeof setInterval> | null = null;

    const iniciarGPS = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      console.log('[GPS] Permiso:', status);

      if (status !== 'granted') {
        console.log('[GPS] ❌ Permiso denegado');
        return;
      }

      const enviarUbicacion = async () => {
        try {
          const location = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Balanced,
          });
          console.log('[GPS] 📍', location.coords.latitude, location.coords.longitude);

          if (!websocketService.estaConectado()) {
            console.log('[GPS] ⏳ WS desconectado, esperando reconexión...');
            return;
          }

          websocketService.enviar({
            type: 'location_update',
            data: {
              lat: location.coords.latitude,
              lng: location.coords.longitude,
            },
          });
          console.log('[GPS] ✅ Ubicación enviada');
        } catch (error) {
          console.log('[GPS] ❌ Error:', error);
        }
      };

      await enviarUbicacion();
      // CAMBIO: 15 segundos en lugar de 30
      interval = setInterval(enviarUbicacion, 15000);
    };

    iniciarGPS();

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [hayTurnoActivo]);

  const nombreCorto = user?.nombreCompleto?.split(' ')[0] || 'Chofer';

  const modulos = [
    {
      id: 'turnos',
      icono: '🔑',
      titulo: 'TURNOS',
      descripcion: 'Iniciar/cerrar turno',
      screenName: 'Turnos',
    },
    {
      id: 'viaje-calle',
      icono: '🚖',
      titulo: 'VIAJE DE CALLE',
      descripcion: hayTurnoActivo
        ? 'Registrar pasajero en la via publica'
        : 'Inicia turno primero',
      screenName: 'ViajeCalle',
      disabled: !hayTurnoActivo,
    },
    {
      id: 'viajes',
      icono: '🚕',
      titulo: 'GESTION DE VIAJES',
      descripcion: 'Recibir y gestionar viajes',
      screenName: 'GestionViajes',
      disabled: !hayTurnoActivo,
    },
    {
      id: 'finanzas',
      icono: '💰',
      titulo: 'FINANZAS',
      descripcion: 'Ingresos, gastos y liquidacion',
      screenName: 'Finanzas',
      disabled: false,
    },
    {
      id: 'historicos',
      icono: '📜',
      titulo: 'HISTORICOS',
      descripcion: 'Viajes y turnos cerrados',
      screenName: 'Turnos',
    },
  ];

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.logo}>TAXIP</Text>
        <View style={styles.headerRight}>
          <TouchableOpacity style={styles.headerButton}>
            <Text style={styles.headerIcon}>🔔</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={() => navigation.navigate('Perfil')}
          >
            <Text style={styles.headerIcon}>👤</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.saludo}>¡Hola, {nombreCorto}!</Text>

        <BannerResultados
          datos={resultadosAyer}
          isLoading={isLoadingResultados}
        />

        <Text style={styles.seccionTitulo}>MODULOS</Text>

        {modulos.map((modulo) => (
          <ModuloCard
            key={modulo.id}
            icono={modulo.icono}
            titulo={modulo.titulo}
            descripcion={modulo.descripcion}
            onPress={() => navigation.navigate(modulo.screenName)}
            disabled={modulo.disabled}
          />
        ))}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  logo: {
    color: COLORS.primary,
    fontSize: 28,
    fontWeight: '900',
    letterSpacing: 2,
  },
  headerRight: {
    flexDirection: 'row',
  },
  headerButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerIcon: {
    fontSize: 22,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 32,
  },
  saludo: {
    color: COLORS.textPrimary,
    fontSize: 22,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 20,
  },
  seccionTitulo: {
    color: COLORS.textPrimary,
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.6,
    marginTop: 8,
    marginBottom: 12,
  },
});