import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS } from '@/constants/colors';

interface ModuloCardProps {
  icono: string;
  titulo: string;
  descripcion: string;
  onPress: () => void;
  disabled?: boolean;
}

export function ModuloCard({
  icono,
  titulo,
  descripcion,
  onPress,
  disabled = false,
}: ModuloCardProps) {
  return (
    <TouchableOpacity
      style={[styles.card, disabled && styles.cardDisabled]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Text style={styles.icono}>{icono}</Text>
      </View>

      <View style={styles.content}>
        <Text style={styles.titulo}>{titulo}</Text>
        <Text style={styles.descripcion}>{descripcion}</Text>
      </View>

      <Text style={styles.arrow}>→</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  cardDisabled: {
    opacity: 0.4,
  },
  iconContainer: {
    width: 52,
    height: 52,
    borderRadius: 12,
    backgroundColor: 'rgba(249, 200, 14, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  icono: {
    fontSize: 26,
  },
  content: {
    flex: 1,
  },
  titulo: {
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 0.5,
    marginBottom: 3,
  },
  descripcion: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.65,
    lineHeight: 16,
  },
  arrow: {
    color: COLORS.primary,
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});