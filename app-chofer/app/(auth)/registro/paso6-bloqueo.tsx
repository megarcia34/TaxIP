import { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { COLORS } from '@/constants/colors';
import { STORAGE_KEYS } from '@/constants/config';
import { splashService } from '@/services/splash.service';
import type { SplashEstado } from '@/types/splash.types';

const POLLING_INTERVAL = 30000; // 30 segundos

export default function Paso6BloqueoScreen() {
  const router = useRouter();

  const [estado, setEstado] = useState<SplashEstado | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const consultarEstado = useCallback(async () => {
    try {
      const resultado = await splashService.obtenerEstadoExpediente();
      setEstado(resultado);
      setError(null);

      // Si el estado cambió, navegar
      if (resultado.estado_aprobacion === 'aprobado') {
        // Verificar si tiene vehículo
        if (resultado.tiene_vehiculo && resultado.tiene_contrato_activo) {
          router.replace('/(app)/home' as any);
        } else {
          // Aprobado pero sin vehículo → mostrar mensaje
          Alert.alert(
            '¡Felicitaciones!',
            'Tu registro fue aprobado. Un propietario te asignará un vehículo pronto. Podés cerrar la app.',
            [
              {
                text: 'Entendido',
                onPress: () => {
                  // Nos quedamos en la pantalla con el mensaje
                },
              },
            ]
          );
        }
      }
    } catch (err: any) {
      console.warn('Error al consultar estado:', err);
      setError(
        err?.response?.data?.detail ||
          'No pudimos verificar tu estado. Reintentando...'
      );
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // Polling cada 30 segundos
  useEffect(() => {
    consultarEstado();

    const interval = setInterval(consultarEstado, POLLING_INTERVAL);

    return () => clearInterval(interval);
  }, [consultarEstado]);

  const handleLogout = () => {
    Alert.alert(
      'Cerrar sesión',
      '¿Estás seguro que querés cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar sesión',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.multiRemove([
              STORAGE_KEYS.AUTH_TOKEN,
              STORAGE_KEYS.REFRESH_TOKEN,
              STORAGE_KEYS.USER,
            ]);
            router.replace('/(auth)/login' as any);
          },
        },
      ]
    );
  };

  const handleReintentar = () => {
    setIsLoading(true);
    consultarEstado();
  };

  // Determinar el estado a mostrar
  const estadoAprobacion = estado?.estado_aprobacion || 'en_revision';
  const progreso = estado?.progreso;

  const esRechazado = estadoAprobacion === 'rechazado';
  const esAprobado = estadoAprobacion === 'aprobado';

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Icono según estado */}
        <View style={styles.iconContainer}>
          <View
            style={[
              styles.iconCircle,
              esRechazado && styles.iconCircleError,
              esAprobado && styles.iconCircleSuccess,
            ]}
          >
            <Text style={styles.iconText}>
              {esRechazado ? '❌' : esAprobado ? '✅' : '⏰'}
            </Text>
          </View>
        </View>

        {/* Título */}
        <Text style={styles.title}>
          {esRechazado
            ? 'Expediente Rechazado'
            : esAprobado
            ? '¡Aprobado!'
            : 'En Revisión'}
        </Text>

        {/* Mensaje */}
        <Text style={styles.message}>
          {esRechazado
            ? estado?.motivo_bloqueo ||
              'Tu expediente fue rechazado. Contactá al administrador para más información.'
            : esAprobado
            ? estado?.tiene_vehiculo && estado?.tiene_contrato_activo
              ? 'Tu registro fue aprobado. Ya podés comenzar a trabajar.'
              : 'Tu registro fue aprobado. Estamos esperando que un propietario te asigne un vehículo.'
            : 'Tu expediente está siendo evaluado por la administración'}
        </Text>

        {/* Lista de verificación */}
        <View style={styles.checklistContainer}>
          <ChecklistItem
            label="Email verificado"
            checked={true}
          />
          <ChecklistItem
            label="Datos personales"
            checked={progreso?.datos_personales || false}
          />
          <ChecklistItem
            label="Documentación"
            checked={progreso?.documentos_basicos || false}
          />
          <ChecklistItem
            label="Selfie"
            checked={progreso?.selfie || false}
          />
        </View>

        {/* Estado de espera */}
        {!esRechazado && !esAprobado && (
          <View style={styles.waitingContainer}>
            <ActivityIndicator size="small" color={COLORS.primary} />
            <Text style={styles.waitingText}>
              Esperando aprobación...
            </Text>
          </View>
        )}

        {/* Error de red */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={handleReintentar}
            >
              <Text style={styles.retryButtonText}>REINTENTAR</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Footer */}
        <Text style={styles.footerText}>
          {esRechazado
            ? 'Corregí la información y volvé a enviar tu expediente'
            : esAprobado
            ? 'Ya podés cerrar la app'
            : 'Te notificaremos cuando tu expediente sea aprobado'}
        </Text>

        {/* Botón cerrar sesión */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Text style={styles.logoutButtonText}>CERRAR SESIÓN</Text>
        </TouchableOpacity>
      </ScrollView>
    </LinearGradient>
  );
}

// Componente de item de la lista
function ChecklistItem({ label, checked }: { label: string; checked: boolean }) {
  return (
    <View style={styles.checklistItem}>
      <Text
        style={[
          styles.checklistIcon,
          checked ? styles.checklistIconChecked : styles.checklistIconPending,
        ]}
      >
        {checked ? '✓' : '○'}
      </Text>
      <Text style={styles.checklistLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 48,
    paddingBottom: 48,
    alignItems: 'center',
  },
  iconContainer: {
    marginBottom: 24,
  },
  iconCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(249, 200, 14, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: COLORS.primary,
  },
  iconCircleError: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderColor: COLORS.error,
  },
  iconCircleSuccess: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderColor: COLORS.success,
  },
  iconText: {
    fontSize: 48,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 26,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 12,
  },
  message: {
    color: COLORS.textPrimary,
    fontSize: 14,
    textAlign: 'center',
    opacity: 0.85,
    marginBottom: 32,
    lineHeight: 20,
    paddingHorizontal: 8,
  },
  checklistContainer: {
    width: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  checklistItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
  },
  checklistIcon: {
    fontSize: 18,
    marginRight: 12,
    fontWeight: 'bold',
  },
  checklistIconChecked: {
    color: COLORS.success,
  },
  checklistIconPending: {
    color: 'rgba(255, 255, 255, 0.3)',
  },
  checklistLabel: {
    color: COLORS.textPrimary,
    fontSize: 14,
    flex: 1,
  },
  waitingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  waitingText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    marginLeft: 8,
    opacity: 0.8,
  },
  errorContainer: {
    width: '100%',
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    alignItems: 'center',
  },
  errorText: {
    color: COLORS.error,
    fontSize: 13,
    textAlign: 'center',
    marginBottom: 12,
  },
  retryButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 6,
  },
  retryButtonText: {
    color: COLORS.textDark,
    fontSize: 13,
    fontWeight: 'bold',
  },
  footerText: {
    color: COLORS.textPrimary,
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.7,
    marginBottom: 24,
    fontStyle: 'italic',
  },
  logoutButton: {
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 32,
  },
  logoutButtonText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 1,
  },
});