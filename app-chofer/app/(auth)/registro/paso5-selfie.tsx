import { useState } from 'react';
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
import { COLORS } from '@/constants/colors';
import { ProgressBar } from '@/components/registro/ProgressBar';
import { RegistroHeader } from '@/components/registro/RegistroHeader';
import { SelfieCapture } from '@/components/registro/SelfieCapture';
import { uploadToCloudinary } from '@/services/cloudinary.service';
import { registroService } from '@/services/registro.service';

export default function Paso5SelfieScreen() {
  const router = useRouter();

  const [selfieUri, setSelfieUri] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCapture = (uri: string) => {
    setSelfieUri(uri);
  };

  const handleRetake = () => {
    setSelfieUri(null);
  };

  const handleContinue = async () => {
    if (!selfieUri) return;

    setIsLoading(true);
    try {
      // 1. Subir la selfie a Cloudinary
      const fotoUrl = await uploadToCloudinary(selfieUri, 'selfies');

      // 2. Enviar la URL al backend
      await registroService.subirSelfie(fotoUrl);

      // 3. Navegar al Paso 6
      router.replace('/(auth)/registro/paso6-bloqueo' as any);
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al subir la selfie';
      Alert.alert('Error', mensaje);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <RegistroHeader title="Verificación de Identidad" />
      <ProgressBar currentStep={5} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>Selfie de Verificación</Text>
        <Text style={styles.subtitle}>
          Tomate una selfie para completar tu verificación. Asegurate de tener
          buena iluminación y que tu rostro esté completamente visible.
        </Text>

        <View style={styles.cameraWrapper}>
          <SelfieCapture
            onCapture={handleCapture}
            capturedUri={selfieUri}
            onRetake={handleRetake}
          />
        </View>

        <TouchableOpacity
          style={[
            styles.primaryButton,
            (!selfieUri || isLoading) && styles.primaryButtonDisabled,
          ]}
          onPress={handleContinue}
          disabled={!selfieUri || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={COLORS.textDark} />
          ) : (
            <Text style={styles.primaryButtonText}>CONTINUAR</Text>
          )}
        </TouchableOpacity>

        {!selfieUri && (
          <Text style={styles.helpText}>
            Tomate una selfie para poder continuar
          </Text>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 48,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    color: COLORS.textPrimary,
    fontSize: 13,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 24,
    lineHeight: 19,
  },
  cameraWrapper: {
    alignItems: 'center',
    marginBottom: 24,
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    marginTop: 8,
  },
  primaryButtonDisabled: {
    opacity: 0.4,
  },
  primaryButtonText: {
    color: COLORS.textDark,
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  helpText: {
    color: COLORS.textPrimary,
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.6,
    marginTop: 12,
    fontStyle: 'italic',
  },
});