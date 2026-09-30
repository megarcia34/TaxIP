import { useState } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Keyboard,
} from 'react-native';
import { COLORS } from '@/constants/colors';
import { COMBUSTIBLES, COMBUSTIBLE_LABELS } from '@/types/turno.types';
import type { Combustible } from '@/types/turno.types';

interface ModalCheckInProps {
  visible: boolean;
  onClose: () => void;
  onIniciar: (kmInicial: number, combustible: Combustible) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  // Opcional: mostrar info del vehículo
  patente?: string;
}

export function ModalCheckIn({
  visible,
  onClose,
  onIniciar,
  isLoading = false,
  error = null,
  patente,
}: ModalCheckInProps) {
  const [kmInicial, setKmInicial] = useState('');
  const [combustible, setCombustible] = useState<Combustible>('LLENO');

  const isFormValid = kmInicial.length > 0 && parseFloat(kmInicial) > 0;

  const handleIniciar = async () => {
    if (!isFormValid) return;
    Keyboard.dismiss();
    await onIniciar(parseFloat(kmInicial), combustible);
  };

  const handleClose = () => {
    Keyboard.dismiss();
    setKmInicial('');
    setCombustible('LLENO');
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={handleClose}
      statusBarTranslucent={true}
    >
      <KeyboardAvoidingView
        style={styles.overlay}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <TouchableOpacity
          style={styles.backdrop}
          activeOpacity={1}
          onPress={handleClose}
        />

        <View style={styles.container}>
          <ScrollView
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <Text style={styles.titulo}>✅ Listo para iniciar</Text>
            <Text style={styles.subtitulo}>
              {patente
                ? `Vehículo: ${patente}`
                : 'Completá el check-in para iniciar el turno'}
            </Text>

            {/* Km inicial */}
            <View style={styles.inputWrapper}>
              <Text style={styles.inputLabel}>KILOMETRAJE INICIAL</Text>
              <TextInput
                style={styles.input}
                value={kmInicial}
                onChangeText={setKmInicial}
                placeholder="Ej: 15234"
                placeholderTextColor="rgba(255, 255, 255, 0.4)"
                keyboardType="numeric"
                editable={!isLoading}
              />
            </View>

            {/* Combustible */}
            <View style={styles.inputWrapper}>
              <Text style={styles.inputLabel}>COMBUSTIBLE</Text>
              <View style={styles.combustibleRow}>
                {COMBUSTIBLES.map((nivel) => (
                  <TouchableOpacity
                    key={nivel}
                    style={[
                      styles.combustibleChip,
                      combustible === nivel && styles.combustibleChipActive,
                    ]}
                    onPress={() => setCombustible(nivel)}
                    disabled={isLoading}
                  >
                    <Text
                      style={[
                        styles.combustibleText,
                        combustible === nivel && styles.combustibleTextActive,
                      ]}
                    >
                      {COMBUSTIBLE_LABELS[nivel]}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorTexto}>⚠️ {error}</Text>
              </View>
            )}

            <View style={styles.botonesRow}>
              <TouchableOpacity
                style={[styles.boton, styles.botonCancelar]}
                onPress={handleClose}
                disabled={isLoading}
              >
                <Text style={styles.botonCancelarTexto}>CANCELAR</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.boton,
                  styles.botonIniciar,
                  (!isFormValid || isLoading) && styles.botonDisabled,
                ]}
                onPress={handleIniciar}
                disabled={!isFormValid || isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color={COLORS.textPrimary} size="small" />
                ) : (
                  <Text style={styles.botonIniciarTexto}>INICIAR TURNO</Text>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
  },
  backdrop: {
    flex: 1,
  },
  container: {
    backgroundColor: '#1A3A52',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 32,
    maxHeight: '80%',
    elevation: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  titulo: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitulo: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.7,
    textAlign: 'center',
    marginBottom: 24,
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
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.35)',
  },
  combustibleRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8,
  },
  combustibleChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  combustibleChipActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  combustibleText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
  },
  combustibleTextActive: {
    color: COLORS.textDark,
  },
  errorContainer: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  errorTexto: {
    color: COLORS.error,
    fontSize: 13,
    textAlign: 'center',
  },
  botonesRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  boton: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  botonCancelar: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  botonCancelarTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
    letterSpacing: 1,
  },
  botonIniciar: {
    backgroundColor: COLORS.success,
  },
  botonIniciarTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  botonDisabled: {
    opacity: 0.4,
  },
});