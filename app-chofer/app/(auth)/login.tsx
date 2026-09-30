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
  Image,
  Linking,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '@/constants/colors';
import { authService } from '@/services/auth.service';

export default function LoginScreen() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const isFormValid = email.includes('@') && password.length >= 6;

  const handleLogin = async () => {
    if (!isFormValid) return;

    setIsLoading(true);
    try {
      await authService.login(email.trim(), password);

      // El servicio ya seteó la sesión en el store con setSession().
      router.replace('/(app)/home' as any);
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al iniciar sesión';
      Alert.alert('Error', mensaje);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegistrarme = () => {
    router.push('/(auth)/registro/paso1-cuenta' as any);
  };

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
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
              accessibilityLabel="Logo de TAXIP"
            />
            <Text style={styles.tagline}>Experimente el nuevo servicio</Text>
          </View>

          {/* Formulario */}
          <View style={styles.formContainer}>
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
                  placeholder="••••••••"
                  placeholderTextColor="rgba(255, 255, 255, 0.4)"
                  secureTextEntry={!showPassword}
                  editable={!isLoading}
                />
                <TouchableOpacity
                  style={styles.eyeButton}
                  onPress={() => setShowPassword(!showPassword)}
                  accessibilityLabel={
                    showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'
                  }
                >
                  <Text style={styles.eyeText}>
                    {showPassword ? '🙈' : '👁'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Olvidaste contraseña */}
            <TouchableOpacity
              style={styles.forgotButton}
              onPress={() => router.push('/(auth)/recuperar-password' as any)}
            >
              <Text style={styles.forgotText}>¿Olvidaste tu contraseña?</Text>
            </TouchableOpacity>

            {/* Botón principal */}
            <TouchableOpacity
              style={[
                styles.primaryButton,
                (!isFormValid || isLoading) && styles.primaryButtonDisabled,
              ]}
              onPress={handleLogin}
              disabled={!isFormValid || isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={COLORS.textDark} />
              ) : (
                <Text style={styles.primaryButtonText}>INICIAR SESIÓN</Text>
              )}
            </TouchableOpacity>

            {/* Divider */}
            <View style={styles.dividerRow}>
              <View style={styles.dividerLine} />
            </View>

            {/* Footer: ¿Sos nuevo? */}
            <View style={styles.footer}>
              <Text style={styles.footerQuestion}>¿Sos nuevo en TAXIP?</Text>
              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={handleRegistrarme}
                disabled={isLoading}
              >
                <Text style={styles.secondaryButtonText}>
                  REGISTRARME COMO CHOFER
                </Text>
              </TouchableOpacity>
            </View>
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
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingVertical: 48,
  },

  // Logo
  logoContainer: {
    alignItems: 'center',
    marginBottom: 48,
  },
  logo: {
    width: 240,
    height: 80,
    marginBottom: 12,
  },
  tagline: {
    color: COLORS.textPrimary,
    fontSize: 14,
    letterSpacing: 0.5,
    opacity: 0.85,
  },

  // Formulario
  formContainer: {
    width: '100%',
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

  // Olvidaste contraseña
  forgotButton: {
    alignSelf: 'flex-end',
    marginBottom: 32,
    marginTop: -8,
  },
  forgotText: {
    color: COLORS.primary,
    fontSize: 14,
  },

  // Botón principal
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

  // Divider
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },

  // Footer
  footer: {
    alignItems: 'center',
  },
  footerQuestion: {
    color: COLORS.textPrimary,
    fontSize: 14,
    marginBottom: 16,
    opacity: 0.9,
  },
  secondaryButton: {
    borderWidth: 1.5,
    borderColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  secondaryButtonText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 1,
  },
});