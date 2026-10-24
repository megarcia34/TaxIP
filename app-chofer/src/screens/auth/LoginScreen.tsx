import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native'; // 👈 Importante
import { COLORS } from '@/constants/colors';
import { useAuthStore } from '@/stores/auth.store';
import { authService } from '@/services/auth.service';

export default function LoginScreen() {
  const navigation = useNavigation<any>(); // 👈 Importante
  const setSession = useAuthStore((s) => s.setSession);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Atención', 'Por favor, completá todos los campos.');
      return;
    }

    setIsLoading(true);
    try {
      const respuesta = await authService.login(email, password);

      // El servicio ya seteó la sesión en el store con setSession().
      // Ahora navegamos al Home.
      navigation.replace('Home');
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

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.logoContainer}>
            <Text style={styles.logo}>TAXIP</Text>
            <Text style={styles.subtitle}>Experimente el nuevo servicio</Text>
          </View>

          <View style={styles.formContainer}>
            <Text style={styles.label}>EMAIL</Text>
            <TextInput
              style={styles.input}
              placeholder="tu@email.com"
              placeholderTextColor="rgba(255,255,255,0.4)"
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
            />

            <Text style={styles.label}>CONTRASEÑA</Text>
            <TextInput
              style={styles.input}
              placeholder="********"
              placeholderTextColor="rgba(255,255,255,0.4)"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <TouchableOpacity style={styles.forgotPassword}>
              <Text style={styles.forgotPasswordText}>¿Olvidaste tu contraseña?</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.button}
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={COLORS.textDark} />
              ) : (
                <Text style={styles.buttonText}>INICIAR SESIÓN</Text>
              )}
            </TouchableOpacity>

            <View style={styles.divider} />

            <Text style={styles.registerText}>¿Sos nuevo en TAXIP?</Text>
            <TouchableOpacity style={styles.registerButton}>
              <Text style={styles.registerButtonText}>REGISTRARME COMO CHOFER</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: { flexGrow: 1, justifyContent: 'center', padding: 20 },
  logoContainer: { alignItems: 'center', marginBottom: 40 },
  logo: { color: COLORS.primary, fontSize: 48, fontWeight: '900', letterSpacing: 4 },
  subtitle: { color: COLORS.textPrimary, fontSize: 14, marginTop: 8, opacity: 0.8 },
  formContainer: { width: '100%' },
  label: { color: COLORS.textPrimary, fontSize: 12, fontWeight: '700', letterSpacing: 1.5, marginBottom: 8 },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.2)',
    borderRadius: 4,
    padding: 12,
    color: COLORS.textPrimary,
    fontSize: 16,
    marginBottom: 20,
  },
  forgotPassword: { alignItems: 'flex-end', marginBottom: 20 },
  forgotPasswordText: { color: COLORS.primary, fontSize: 12 },
  button: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: { color: COLORS.textDark, fontSize: 16, fontWeight: 'bold' },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.1)', marginVertical: 20 },
  registerText: { color: COLORS.textPrimary, textAlign: 'center', marginBottom: 12, opacity: 0.8 },
  registerButton: { borderWidth: 1, borderColor: COLORS.primary, borderRadius: 8, paddingVertical: 16, alignItems: 'center' },
  registerButtonText: { color: COLORS.primary, fontSize: 14, fontWeight: 'bold' },
});