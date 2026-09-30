import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '@/constants/colors';

interface HeaderTurnosProps {
  nombre: string;
  estadoLaboral: 'fuera_servicio' | 'libre' | 'ocupado';
}

export function HeaderTurnos({ nombre, estadoLaboral }: HeaderTurnosProps) {
  const getEstadoInfo = () => {
    switch (estadoLaboral) {
      case 'libre':
        return { icono: '🟢', texto: 'Turno activo', color: COLORS.success };
      case 'ocupado':
        return { icono: '🟠', texto: 'En viaje', color: COLORS.warning };
      case 'fuera_servicio':
      default:
        return {
          icono: '⚪',
          texto: 'Fuera de servicio',
          color: COLORS.gray,
        };
    }
  };

  const estado = getEstadoInfo();

  return (
    <View style={styles.container}>
      <Text style={styles.saludo}>¡Hola, {nombre}!</Text>
      <View style={styles.estadoRow}>
        <Text style={styles.estadoIcono}>{estado.icono}</Text>
        <Text style={[styles.estadoTexto, { color: estado.color }]}>
          {estado.texto}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
  },
  saludo: {
    color: COLORS.textPrimary,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  estadoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  estadoIcono: {
    fontSize: 14,
    marginRight: 6,
  },
  estadoTexto: {
    fontSize: 14,
    fontWeight: '600',
  },
});