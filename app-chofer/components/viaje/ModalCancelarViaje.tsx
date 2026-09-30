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
  Keyboard,
  ScrollView,
} from 'react-native';
import { COLORS } from '@/constants/colors';

interface ModalCancelarViajeProps {
  visible: boolean;
  onClose: () => void;
  onConfirmar: (motivo: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export function ModalCancelarViaje({
  visible,
  onClose,
  onConfirmar,
  isLoading = false,
  error = null,
}: ModalCancelarViajeProps) {
  const [motivo, setMotivo] = useState('');

  const isFormValid = motivo.trim().length >= 3;

  const handleConfirmar = async () => {
    if (!isFormValid) return;
    Keyboard.dismiss();
    await onConfirmar(motivo.trim());
  };

  const handleClose = () => {
    Keyboard.dismiss();
    setMotivo('');
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleClose}
      statusBarTranslucent
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
            <Text style={styles.titulo}>⚠️ Cancelar viaje</Text>
            <Text style={styles.subtitulo}>
              Indicá el motivo de la cancelación
            </Text>

            <View style={styles.inputWrapper}>
              <Text style={styles.inputLabel}>MOTIVO</Text>
              <TextInput
                style={[styles.input, styles.inputMultiline]}
                value={motivo}
                onChangeText={setMotivo}
                placeholder="Ej: El pasajero se bajó"
                placeholderTextColor="rgba(255, 255, 255, 0.4)"
                multiline
                numberOfLines={3}
                maxLength={200}
                editable={!isLoading}
              />
              <Text style={styles.contador}>{motivo.length}/200</Text>
            </View>

            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorTexto}>⚠️ {error}</Text>
              </View>
            )}

            <View style={styles.botonesRow}>
              <TouchableOpacity
                style={[styles.boton, styles.botonVolver]}
                onPress={handleClose}
                disabled={isLoading}
              >
                <Text style={styles.botonVolverTexto}>VOLVER</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.boton,
                  styles.botonCancelar,
                  (!isFormValid || isLoading) && styles.botonDisabled,
                ]}
                onPress={handleConfirmar}
                disabled={!isFormValid || isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color={COLORS.textPrimary} size="small" />
                ) : (
                  <Text style={styles.botonCancelarTexto}>CONFIRMAR</Text>
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
  inputMultiline: {
    minHeight: 80,
    textAlignVertical: 'top',
    paddingTop: 8,
  },
  contador: {
    color: COLORS.textPrimary,
    fontSize: 10,
    opacity: 0.5,
    textAlign: 'right',
    marginTop: 6,
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
  botonVolver: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  botonVolverTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
    letterSpacing: 1,
  },
  botonCancelar: {
    backgroundColor: COLORS.error,
  },
  botonCancelarTexto: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  botonDisabled: {
    opacity: 0.4,
  },
});