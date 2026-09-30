import { useState } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { COLORS } from '@/constants/colors';
import { OTPInput } from '@/components/registro/OTPInput';

interface ModalCodigoProps {
  visible: boolean;
  onClose: () => void;
  onValidar: (codigo: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export function ModalCodigo({
  visible,
  onClose,
  onValidar,
  isLoading = false,
  error = null,
}: ModalCodigoProps) {
  const [codigo, setCodigo] = useState('');

  const handleValidar = async () => {
    if (codigo.length !== 6) return;
    await onValidar(codigo);
  };

  const handleClose = () => {
    setCodigo('');
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
        {/* Fondo oscuro táctil */}
        <TouchableOpacity
          style={styles.backdrop}
          activeOpacity={1}
          onPress={handleClose}
        />

        {/* Contenedor del modal */}
        <View style={styles.container}>
          <ScrollView
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <Text style={styles.titulo}>🔑 Ingresá el código</Text>
            <Text style={styles.subtitulo}>
              Tu propietario te dio un código de 6 dígitos.
            </Text>

            <View style={styles.otpContainer}>
              <OTPInput
                length={6}
                onComplete={(code) => setCodigo(code)}
                onChangeText={setCodigo}
              />
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
                  styles.botonValidar,
                  (codigo.length !== 6 || isLoading) && styles.botonDisabled,
                ]}
                onPress={handleValidar}
                disabled={codigo.length !== 6 || isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color={COLORS.textDark} size="small" />
                ) : (
                  <Text style={styles.botonValidarTexto}>VALIDAR</Text>
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
  otpContainer: {
    marginBottom: 24,
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
  botonValidar: {
    backgroundColor: COLORS.primary,
  },
  botonValidarTexto: {
    color: COLORS.textDark,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  botonDisabled: {
    opacity: 0.4,
  },
});