import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '@/constants/colors';
import { ProgressBar } from '@/components/registro/ProgressBar';
import { RegistroHeader } from '@/components/registro/RegistroHeader';
import { registroService } from '@/services/registro.service';
import { useRegistroStore } from '@/stores/registro.store';

export default function Paso1CuentaScreen() {
  const router = useRouter();
  const { setEmail: setEmailStore, setUserId } = useRegistroStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const isEmailValid = email.includes('@') && email.includes('.');
  const isPasswordValid = password.length >= 8;
  const isConfirmValid =
    password === confirmPassword && confirmPassword.length > 0;

  const isFormValid =
    isEmailValid && isPasswordValid && isConfirmValid && acceptTerms;

  const handleContinue = async () => {
    if (!isFormValid) return;

    setIsLoading(true);
    try {
      const response = await registroService.iniciarRegistro(
        email.trim(),
        password
      );

      // Guardar datos en el store temporal
      setEmailStore(email.trim());
      setUserId(response.user_id);

      // Detectar si es reanudación
      if (response.es_reanudacion) {
        Alert.alert(
          'Registro en curso',
          'Ya habías empezado tu registro. Te enviamos un nuevo código para continuar donde lo dejaste.',
          [
            {
              text: 'Continuar',
              onPress: () =>
                router.push('/(auth)/registro/paso2-validar-email' as any),
            },
          ]
        );
      } else {
        // Flujo normal: primera vez
        router.push('/(auth)/registro/paso2-validar-email' as any);
      }
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al crear la cuenta';
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
      <RegistroHeader title="Crear Cuenta" />
      <ProgressBar currentStep={1} />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <Text style={styles.subtitle}>Registrate como chofer TAXIP</Text>

          {/* Email */}
          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>EMAIL</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder="tu@email.com"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
            />
          </View>

          {/* Contraseña */}
          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>CONTRASEÑA</Text>
            <View style={styles.passwordRow}>
              <TextInput
                style={[styles.input, styles.passwordInput]}
                value={password}
                onChangeText={setPassword}
                placeholder="Mínimo 8 caracteres"
                placeholderTextColor="rgba(255, 255, 255, 0.4)"
                secureTextEntry={!showPassword}
                editable={!isLoading}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowPassword(!showPassword)}
              >
                <Text style={styles.eyeText}>{showPassword ? '🙈' : '👁'}</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Confirmar contraseña */}
          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>CONFIRMAR CONTRASEÑA</Text>
            <View style={styles.passwordRow}>
              <TextInput
                style={[styles.input, styles.passwordInput]}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                placeholder="Repetí la contraseña"
                placeholderTextColor="rgba(255, 255, 255, 0.4)"
                secureTextEntry={!showConfirmPassword}
                editable={!isLoading}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                <Text style={styles.eyeText}>
                  {showConfirmPassword ? '🙈' : '👁'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Términos y condiciones */}
          <TouchableOpacity
            style={styles.termsRow}
            onPress={() => setAcceptTerms(!acceptTerms)}
            disabled={isLoading}
          >
            <View
              style={[styles.checkbox, acceptTerms && styles.checkboxChecked]}
            >
              {acceptTerms && <Text style={styles.checkboxText}>✓</Text>}
            </View>
            <Text style={styles.termsText}>
              Acepto los Términos y Condiciones y la Política de Privacidad
            </Text>
          </TouchableOpacity>

          {/* Botón continuar */}
          <TouchableOpacity
            style={[
              styles.primaryButton,
              (!isFormValid || isLoading) && styles.primaryButtonDisabled,
            ]}
            onPress={handleContinue}
            disabled={!isFormValid || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={COLORS.textDark} />
            ) : (
              <Text style={styles.primaryButtonText}>CONTINUAR</Text>
            )}
          </TouchableOpacity>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerQuestion}>¿Ya tenés cuenta?</Text>
            <TouchableOpacity
              onPress={() => router.replace('/(auth)/login' as any)}
              disabled={isLoading}
            >
              <Text style={styles.footerLink}>INICIAR SESIÓN</Text>
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
  subtitle: {
    color: COLORS.textPrimary,
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 32,
    opacity: 0.9,
  },
  inputWrapper: {
    marginBottom: 24,
  },
  inputLabel: {
    color: COLORS.textPrimary,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.5,
    marginBottom: 6,
    opacity: 0.9,
  },
  input: {
    color: COLORS.textPrimary,
    fontSize: 16,
    paddingVertical: 10,
    paddingHorizontal: 0,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.35)',
  },
  passwordRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.35)',
  },
  passwordInput: {
    flex: 1,
    borderBottomWidth: 0,
  },
  eyeButton: {
    padding: 8,
    marginBottom: -10,
  },
  eyeText: {
    fontSize: 20,
  },
  termsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 32,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  checkboxText: {
    color: COLORS.textDark,
    fontSize: 14,
    fontWeight: 'bold',
  },
  termsText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    flex: 1,
    opacity: 0.9,
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
    marginTop: 32,
  },
  footerQuestion: {
    color: COLORS.textPrimary,
    fontSize: 14,
    marginBottom: 8,
    opacity: 0.9,
  },
  footerLink: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 1,
  },
});