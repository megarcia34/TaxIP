import { useState, useEffect } from 'react';
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
import { Selector, SelectorOption } from '@/components/ui/Selector';
import { catalogoService } from '@/services/catalogo.service';
import { registroService } from '@/services/registro.service';
import { useRegistroStore } from '@/stores/registro.store';
import type { Prestadora, Ciudad } from '@/types/catalogo.types';

export default function Paso3DatosScreen() {
  const router = useRouter();
  const { setEmailVerificado } = useRegistroStore();

  // Datos del formulario
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [dni, setDni] = useState('');
  const [telefono, setTelefono] = useState('');
  const [direccion, setDireccion] = useState('');
  const [codigoPostal, setCodigoPostal] = useState('');

  // Selectores
  const [prestadoraSeleccionada, setPrestadoraSeleccionada] =
    useState<SelectorOption | null>(null);
  const [ciudadSeleccionada, setCiudadSeleccionada] =
    useState<SelectorOption | null>(null);

  // Catálogos
  const [prestadoras, setPrestadoras] = useState<SelectorOption[]>([]);
  const [ciudades, setCiudades] = useState<SelectorOption[]>([]);
  const [loadingPrestadoras, setLoadingPrestadoras] = useState(true);
  const [loadingCiudades, setLoadingCiudades] = useState(true);

  const [isLoading, setIsLoading] = useState(false);

  // Cargar catálogos al montar
  useEffect(() => {
    cargarCatalogos();
  }, []);

  const cargarCatalogos = async () => {
    try {
      const prestadorasData = await catalogoService.getPrestadoras();
      const prestadorasOptions: SelectorOption[] = prestadorasData.map(
        (p: Prestadora) => ({
          id: p.id,
          label: p.nombre,
          subtitle: p.codigo_pais,
        })
      );
      setPrestadoras(prestadorasOptions);
    } catch (error) {
      console.warn('Error cargando prestadoras:', error);
      Alert.alert(
        'Aviso',
        'No se pudieron cargar las prestadoras. Intentá de nuevo.'
      );
    } finally {
      setLoadingPrestadoras(false);
    }

    try {
      const ciudadesData = await catalogoService.getCiudades();
      const ciudadesOptions: SelectorOption[] = ciudadesData.map(
        (c: Ciudad) => ({
          id: c.id,
          label: c.nombre,
          subtitle: c.tenant_nombre,
        })
      );
      setCiudades(ciudadesOptions);
    } catch (error) {
      console.warn('Error cargando ciudades:', error);
    } finally {
      setLoadingCiudades(false);
    }
  };

  // Validaciones
  const isNombreValid = nombre.trim().length >= 2;
  const isApellidoValid = apellido.trim().length >= 2;
  const isDniValid = /^\d{7,8}[A-Z]?$/i.test(dni.trim());
  const isTelefonoValid = /^\+?[1-9]\d{9,14}$/.test(
    telefono.replace(/\s|-/g, '')
  );
  const isDireccionValid = direccion.trim().length >= 5;
  const isCodigoPostalValid = /^[A-Za-z0-9\s-]{4,10}$/.test(
    codigoPostal.trim()
  );

  const isFormValid =
    isNombreValid &&
    isApellidoValid &&
    isDniValid &&
    isTelefonoValid &&
    isDireccionValid &&
    isCodigoPostalValid &&
    prestadoraSeleccionada !== null &&
    ciudadSeleccionada !== null;

  const handleContinue = async () => {
    if (!isFormValid) return;

    if (!prestadoraSeleccionada || !ciudadSeleccionada) return;

    setIsLoading(true);
    try {
      // 1. Verificar DNI en el tenant de la ciudad elegida
      const { existe, estado_aprobacion, bloqueante } =
        await registroService.verificarDni(
          dni.trim(),
          ciudadSeleccionada.id
        );

      // Solo bloqueamos si el registro existente está aprobado o en revisión
      if (existe && bloqueante) {
        setIsLoading(false);
        Alert.alert(
          'DNI ya registrado',
          estado_aprobacion === 'en_revision'
            ? 'Ya hay un registro en revisión con este DNI. Esperá la aprobación.'
            : estado_aprobacion === 'aprobado'
            ? 'Ya existe un chofer aprobado con este DNI en esta ciudad.'
            : 'Ya existe un registro con este DNI en esta ciudad.'
        );
        return;
      }

      // Si existe pero NO es bloqueante (pendiente o rechazado),
      // permitimos continuar y reemplazamos los datos

      // 2. Guardar datos personales
      await registroService.actualizarDatos({
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        dni: dni.trim(),
        telefono: telefono.replace(/\s|-/g, ''),
        prestadora_id: prestadoraSeleccionada.id,
        direccion: direccion.trim(),
        ciudad_id: ciudadSeleccionada.id,
        codigo_postal: codigoPostal.trim(),
      });

      // 3. Navegar al Paso 4
      router.push('/(auth)/registro/paso4-documentos' as any);
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al guardar los datos';
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
      <RegistroHeader title="Datos Personales" />
      <ProgressBar currentStep={3} />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Sección: Datos personales */}
          <Text style={styles.sectionTitle}>Datos Personales</Text>

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>NOMBRE</Text>
            <TextInput
              style={styles.input}
              value={nombre}
              onChangeText={setNombre}
              placeholder="Juan"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              autoCapitalize="words"
              editable={!isLoading}
            />
          </View>

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>APELLIDO</Text>
            <TextInput
              style={styles.input}
              value={apellido}
              onChangeText={setApellido}
              placeholder="Pérez"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              autoCapitalize="words"
              editable={!isLoading}
            />
          </View>

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>DNI</Text>
            <TextInput
              style={styles.input}
              value={dni}
              onChangeText={setDni}
              placeholder="12345678"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              keyboardType="numeric"
              maxLength={9}
              editable={!isLoading}
            />
          </View>

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>TELÉFONO</Text>
            <TextInput
              style={styles.input}
              value={telefono}
              onChangeText={setTelefono}
              placeholder="+54 9 381 123-4567"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              keyboardType="phone-pad"
              editable={!isLoading}
            />
          </View>

          {/* Sección: Contacto */}
          <Text style={[styles.sectionTitle, styles.sectionTitleSpacing]}>
            Contacto
          </Text>

          <Selector
            label="PRESTADORA"
            placeholder="Seleccionar prestadora"
            value={prestadoraSeleccionada}
            options={prestadoras}
            onSelect={setPrestadoraSeleccionada}
            isLoading={loadingPrestadoras}
            disabled={isLoading}
          />

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>DIRECCIÓN</Text>
            <TextInput
              style={styles.input}
              value={direccion}
              onChangeText={setDireccion}
              placeholder="Av. Siempre Viva 123"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              autoCapitalize="words"
              editable={!isLoading}
            />
          </View>

          <Selector
            label="CIUDAD"
            placeholder="Seleccionar ciudad"
            value={ciudadSeleccionada}
            options={ciudades}
            onSelect={setCiudadSeleccionada}
            isLoading={loadingCiudades}
            disabled={isLoading}
          />

          <View style={styles.inputWrapper}>
            <Text style={styles.inputLabel}>CÓDIGO POSTAL</Text>
            <TextInput
              style={styles.input}
              value={codigoPostal}
              onChangeText={setCodigoPostal}
              placeholder="4000"
              placeholderTextColor="rgba(255, 255, 255, 0.4)"
              keyboardType="default"
              maxLength={10}
              editable={!isLoading}
            />
          </View>

          {/* Botón */}
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
    paddingTop: 16,
    paddingBottom: 48,
  },
  sectionTitle: {
    color: COLORS.textPrimary,
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 20,
    opacity: 0.95,
  },
  sectionTitleSpacing: {
    marginTop: 16,
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
  primaryButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    marginTop: 16,
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
});