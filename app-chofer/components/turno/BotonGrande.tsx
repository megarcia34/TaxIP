import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  View,
} from 'react-native';
import { COLORS } from '@/constants/colors';

type ModoBoton = 'iniciar_con_codigo' | 'iniciar_directo' | 'finalizar';

interface BotonGrandeProps {
  modo: ModoBoton;
  onPress: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function BotonGrande({
  modo,
  onPress,
  isLoading = false,
  disabled = false,
}: BotonGrandeProps) {
  const getConfig = () => {
    switch (modo) {
      case 'iniciar_con_codigo':
        return {
          backgroundColor: COLORS.error,
          textColor: COLORS.textPrimary,
          icono: '🔑',
          label: 'INICIAR TURNO',
        };
      case 'iniciar_directo':
        return {
          backgroundColor: COLORS.success,
          textColor: COLORS.textPrimary,
          icono: '🚗',
          label: 'INICIAR TURNO',
        };
      case 'finalizar':
        return {
          backgroundColor: COLORS.success,
          textColor: COLORS.textPrimary,
          icono: '🏁',
          label: 'FINALIZAR TURNO',
        };
    }
  };

  const config = getConfig();

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[
          styles.button,
          { backgroundColor: config.backgroundColor },
          (disabled || isLoading) && styles.buttonDisabled,
        ]}
        onPress={onPress}
        disabled={disabled || isLoading}
        activeOpacity={0.8}
      >
        {isLoading ? (
          <ActivityIndicator color={config.textColor} size="large" />
        ) : (
          <>
            <Text style={styles.icono}>{config.icono}</Text>
            <Text style={[styles.text, { color: config.textColor }]}>
              {config.label}
            </Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginVertical: 24,
  },
  button: {
    width: 200,
    height: 200,
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 10,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  icono: {
    fontSize: 42,
    marginBottom: 12,
  },
  text: {
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1.5,
    textAlign: 'center',
    paddingHorizontal: 16,
  },
});