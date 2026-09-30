import { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  Animated,
  Easing,
  AccessibilityInfo,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '@/constants/colors';
import { APP_VERSION } from '@/constants/config';
import { useAuthStore } from '@/stores/auth.store';
import { splashService } from '@/services/splash.service';
import type { EtapaActual } from '@/types/splash.types';

const MIN_SPLASH_TIME = 2500;

export default function SplashScreen() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  // Suscripción al store. `hasHydrated` se pone en true cuando
  // Zustand terminó de leer AsyncStorage. `token` es la fuente de verdad.
  const token = useAuthStore((s) => s.token);
  const hasHydrated = useAuthStore((s) => s._hasHydrated);

  const logoOpacity = useRef(new Animated.Value(0)).current;
  const logoScale = useRef(new Animated.Value(0.95)).current;
  const taglineOpacity = useRef(new Animated.Value(0)).current;
  const versionOpacity = useRef(new Animated.Value(0)).current;

  // Animación de entrada
  useEffect(() => {
    const runAnimation = async () => {
      const reduceMotion = await AccessibilityInfo.isReduceMotionEnabled();

      if (reduceMotion) {
        logoOpacity.setValue(1);
        logoScale.setValue(1);
        taglineOpacity.setValue(1);
        versionOpacity.setValue(1);
        return;
      }

      Animated.parallel([
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(logoScale, {
          toValue: 1,
          duration: 1000,
          easing: Easing.out(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(taglineOpacity, {
          toValue: 1,
          duration: 500,
          delay: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(versionOpacity, {
          toValue: 1,
          duration: 500,
          delay: 1500,
          useNativeDriver: true,
        }),
      ]).start();
    };

    runAnimation();
  }, [logoOpacity, logoScale, taglineOpacity, versionOpacity]);

  // Verificación de sesión y navegación.
  // Espera a que el store hidrate antes de decidir.
  useEffect(() => {
    if (!hasHydrated) return;

    const checkSession = async () => {
      const startTime = Date.now();

      try {
        // 1. ¿Hay token en el store?
        const hasToken = !!token;

        if (!hasToken) {
          await waitMinimum(startTime);
          router.replace('/(auth)/login');
          return;
        }

        // 2. Consultar estado al backend
        const estado = await splashService.obtenerEstado();

        await waitMinimum(startTime);

        // 3. Navegar según etapa
        navigateByEtapa(estado.etapa_actual);
      } catch (err: any) {
        await waitMinimum(startTime);

        // Si es 401, el interceptor ya limpia y redirige
        if (err?.response?.status === 401) {
          return;
        }

        // Error de red u otro
        setError(
          err?.response?.data?.detail ||
            'No pudimos verificar tu sesión. Verificá tu conexión.'
        );
        setCargando(false);
      }
    };

    checkSession();
  }, [hasHydrated, token, router]);

  const waitMinimum = async (startTime: number) => {
    const elapsed = Date.now() - startTime;
    const remaining = MIN_SPLASH_TIME - elapsed;
    if (remaining > 0) {
      await new Promise((resolve) => setTimeout(resolve, remaining));
    }
  };

  const navigateByEtapa = (etapa: EtapaActual) => {
    switch (etapa) {
      case 'registro':
      case 'datos':
      case 'documentos':
      case 'selfie':
        router.replace('/(auth)/registro/paso1-cuenta' as any);
        break;
      case 'revision':
        router.replace('/(auth)/registro/paso6-bloqueo' as any);
        break;
      case 'esperando_vehiculo':
      case 'contrato_pendiente':
      case 'listo':
        router.replace('/(app)/home' as any);
        break;
      case 'home':
        router.replace('/(app)/home' as any);
        break;
      default:
        router.replace('/(auth)/login');
    }
  };

  const handleRetry = () => {
    setError(null);
    setCargando(true);
    router.replace('/(auth)/splash');
  };

  // Pantalla de error
  if (error) {
    return (
      <LinearGradient
        colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
        style={styles.container}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
      >
        <View style={styles.errorContent}>
          <Text style={styles.errorIcon}>📶</Text>
          <Text style={styles.errorTitle}>Sin conexión</Text>
          <Text style={styles.errorMessage}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleRetry}>
            <Text style={styles.retryButtonText}>REINTENTAR</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <View style={styles.watermarkContainer} pointerEvents="none">
        <Image
          source={require('@/assets/images/isotipo-taxip.png')}
          style={styles.watermark}
          resizeMode="contain"
        />
      </View>

      <View style={styles.content}>
        <Animated.Image
          source={require('@/assets/images/logo-taxip.png')}
          style={[
            styles.logo,
            {
              opacity: logoOpacity,
              transform: [{ scale: logoScale }],
            },
          ]}
          resizeMode="contain"
          accessibilityLabel="Logo de TAXIP"
        />

        <Animated.Text style={[styles.tagline, { opacity: taglineOpacity }]}>
          Gestioná tu turno, recibí viajes
        </Animated.Text>
      </View>

      <Animated.Text style={[styles.version, { opacity: versionOpacity }]}>
        {APP_VERSION}
      </Animated.Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  watermarkContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  watermark: {
    width: 250,
    height: 250,
    opacity: 0.08,
  },
  content: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  logo: {
    width: 280,
    height: 100,
    marginBottom: 24,
  },
  tagline: {
    color: COLORS.textPrimary,
    fontSize: 16,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  version: {
    position: 'absolute',
    bottom: 40,
    color: COLORS.textSecondary,
    fontSize: 12,
    letterSpacing: 1,
  },
  errorContent: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  errorIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  errorTitle: {
    color: COLORS.textPrimary,
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  errorMessage: {
    color: COLORS.textSecondary,
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: COLORS.textDark,
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
});