import { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '@/constants/colors';
import { useAuthStore } from '@/stores/auth.store';
import { useTurnoStore } from '@/stores/turno.store';
import { BannerResultados } from '@/components/home/BannerResultados';
import { ModuloCard } from '@/components/home/ModuloCard';
import type { ResultadosResumen } from '@/components/home/BannerResultados';

export default function HomeScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user } = useAuthStore();

  // J12: fuente de verdad para habilitar/deshabilitar modulos operativos.
  const turnoActivo = useTurnoStore((s) => s.turnoActivo);
  const cargarTurnoActivo = useTurnoStore((s) => s.cargarTurnoActivo);

  // Datos del día anterior (mock por ahora, Fase 3 los traerá del backend)
  const [resultadosAyer, setResultadosAyer] = useState<ResultadosResumen | null>(
    null
  );
  const [isLoadingResultados, setIsLoadingResultados] = useState(false);

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
  // activo contra el backend. Sin bloquear la UI.
  useEffect(() => {
    if (turnoActivo == null) {
      cargarTurnoActivo();
    }
  }, [turnoActivo, cargarTurnoActivo]);

  const nombreCorto = user?.nombreCompleto?.split(' ')[0] || 'Chofer';

  const modulos = [
    {
      id: 'turnos',
      icono: '🔑',
      titulo: 'TURNOS',
      descripcion: 'Iniciar/cerrar turno',
      ruta: '/(app)/turnos' as const,
    },
    {
      id: 'viaje-calle',
      icono: '🚖',
      titulo: 'VIAJE DE CALLE',
      descripcion: turnoActivo
        ? 'Registrar pasajero en la via publica'
        : 'Inicia turno primero',
      ruta: '/(app)/viajes/calle' as const,
      disabled: turnoActivo == null,
    },
    {
      id: 'viajes',
      icono: '🚕',
      titulo: 'GESTIÓN DE VIAJES',
      descripcion: 'Recibir y gestionar viajes',
      ruta: '/(app)/viajes' as const,
      disabled: true,
    },
    {
      id: 'finanzas',
      icono: '💰',
      titulo: 'FINANZAS',
      descripcion: 'Ingresos, gastos y liquidación',
      ruta: '/(app)/finanzas' as const,
      disabled: true,
    },
    {
      id: 'historicos',
      icono: '📜',
      titulo: 'HISTÓRICOS',
      descripcion: 'Viajes y turnos cerrados',
      ruta: '/(app)/historicos' as const,
    },
    {
      id: 'perfil',
      icono: '👤',
      titulo: 'MI CUENTA',
      descripcion: 'Perfil, vehículo y documentos',
      ruta: '/(app)/perfil' as const,
    },
  ];

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      {/* Header */}
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.logo}>TAXIP</Text>
        <View style={styles.headerRight}>
          <TouchableOpacity style={styles.headerButton}>
            <Text style={styles.headerIcon}>🔔</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={() => router.push('/(app)/perfil' as any)}
          >
            <Text style={styles.headerIcon}>👤</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Contenido */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Saludo */}
        <Text style={styles.saludo}>¡Hola, {nombreCorto}!</Text>

        {/* Banner de resultados del día anterior */}
        <BannerResultados
          datos={resultadosAyer}
          isLoading={isLoadingResultados}
        />

        {/* Título de módulos */}
        <Text style={styles.seccionTitulo}>MÓDULOS</Text>

        {/* Lista de módulos */}
        {modulos.map((modulo) => (
          <ModuloCard
            key={modulo.id}
            icono={modulo.icono}
            titulo={modulo.titulo}
            descripcion={modulo.descripcion}
            onPress={() => router.push(modulo.ruta as any)}
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