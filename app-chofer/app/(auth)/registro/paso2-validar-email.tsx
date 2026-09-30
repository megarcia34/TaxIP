import { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '@/constants/colors';
import { ProgressBar } from '@/components/registro/ProgressBar';
import { RegistroHeader } from '@/components/registro/RegistroHeader';
import { OTPInput } from '@/components/registro/OTPInput';
import { registroService } from '@/services/registro.service';
import { useRegistroStore } from '@/stores/registro.store';
import AsyncStorage from '@react-native-async-storage/async-storage';

const RESEND_COOLDOWN = 60; // segundos

export default function Paso2ValidarEmailScreen() {
  const router = useRouter();
  const { email, setEmailVerificado } = useRegistroStore();

  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(RESEND_COOLDOWN);
  const [canResend, setCanResend] = useState(false);

  // Timer para el reenvío
  useEffect(() => {
    if (secondsLeft <= 0) {
      setCanResend(true);
      return;
    }

    const timer = setTimeout(() => {
      setSecondsLeft(secondsLeft - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [secondsLeft]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}`;
  };

  const handleVerify = async () => {
    if (code.length !== 6) {
      Alert.alert('Error', 'Ingresá los 6 dígitos del código');
      return;
    }

    setIsLoading(true);
    try {
      const response = await registroService.validarEmail(email, code);

      // Guardar el access_token para las siguientes llamadas
      await AsyncStorage.setItem('@taxip:auth_token', response.access_token);

setEmailVerificado(true);

      Alert.alert(
        'Email verificado',
        'Tu email fue verificado correctamente',
        [
          {
            text: 'Continuar',
            onPress: () =>
              router.push('/(auth)/registro/paso3-datos-personales' as any),
          },
        ]
      );
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Código inválido o expirado';
      Alert.alert('Error', mensaje);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = () => {
    // TODO: Implementar endpoint de reenvío en el backend
    setSecondsLeft(RESEND_COOLDOWN);
    setCanResend(false);
    Alert.alert(
      'Código reenviado',
      `Enviamos un nuevo código a ${email}`
    );
  };

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <RegistroHeader title="Validar Email" />
      <ProgressBar currentStep={2} />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Image
              source={require('@/assets/images/logo-taxip.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>

          {/* Instrucción */}
          <Text style={styles.title}>Ingresá el código</Text>
          <Text style={styles.subtitle}>
            Enviamos un código de 6 dígitos a{'\n'}
            <Text style={styles.emailText}>{email}</Text>
          </Text>

          {/* Input OTP */}
          <View style={styles.otpContainer}>
            <OTPInput
              length={6}
              onComplete={(fullCode) => {
                // Cuando se completa, podés auto-verificar o dejar que toque el botón
                setCode(fullCode);
              }}
              onChangeText={setCode}
              autoFocus
            />
          </View>

          {/* Reenviar código */}
          <View style={styles.resendContainer}>
            {canResend ? (
              <TouchableOpacity onPress={handleResend}>
                <Text style={styles.resendLink}>Reenviar código</Text>
              </TouchableOpacity>
            ) : (
              <Text style={styles.resendText}>
                Reenviar código en{' '}
                <Text style={styles.resendTimer}>{formatTime(secondsLeft)}</Text>
              </Text>
            )}
          </View>

          {/* Botón verificar */}
          <TouchableOpacity
            style={[
              styles.primaryButton,
              (code.length !== 6 || isLoading) && styles.primaryButtonDisabled,
            ]}
            onPress={handleVerify}
            disabled={code.length !== 6 || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={COLORS.textDark} />
            ) : (
              <Text style={styles.primaryButtonText}>VERIFICAR</Text>
            )}
          </TouchableOpacity>

          {/* Footer */}
          <View style={styles.footer}>
            <TouchableOpacity
              onPress={() => router.back()}
              disabled={isLoading}
            >
              <Text style={styles.footerLink}>← Volver al paso anterior</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  keyboardView: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 48,
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 24,
  },
  logo: {
    width: 180,
    height: 60,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    color: COLORS.textPrimary,
    fontSize: 14,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 32,
    lineHeight: 20,
  },
  emailText: {
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  otpContainer: {
    marginBottom: 24,
  },
  resendContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  resendText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    opacity: 0.7,
  },
  resendTimer: {
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  resendLink: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
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
  footer: {
    alignItems: 'center',
    marginTop: 24,
  },
  footerLink: {
    color: COLORS.textPrimary,
    fontSize: 14,
    opacity: 0.7,
  },
});