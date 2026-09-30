import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { COLORS } from '@/constants/colors';

export interface VehiculoDisponible {
  id: string;
  patente: string;
  marca?: string;
  modelo?: string;
  anio?: number;
}

interface ModalSeleccionVehiculoProps {
  visible: boolean;
  onClose: () => void;
  vehiculos: VehiculoDisponible[];
  onSeleccionar: (vehiculo: VehiculoDisponible) => void;
  isLoading?: boolean;
}

export function ModalSeleccionVehiculo({
  visible,
  onClose,
  vehiculos,
  onSeleccionar,
  isLoading = false,
}: ModalSeleccionVehiculoProps) {
  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
      statusBarTranslucent={true}
    >
      <View style={styles.overlay}>
        <TouchableOpacity
          style={styles.backdrop}
          activeOpacity={1}
          onPress={onClose}
        />

        <View style={styles.container}>
          <ScrollView
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <Text style={styles.titulo}>🚗 Elegí el vehículo</Text>
            <Text style={styles.subtitulo}>
              Trabajás con tus propios vehículos. Elegí con cuál vas a
              iniciar turno.
            </Text>

            {vehiculos.map((vehiculo) => (
              <TouchableOpacity
                key={vehiculo.id}
                style={styles.vehiculoCard}
                onPress={() => onSeleccionar(vehiculo)}
                disabled={isLoading}
                activeOpacity={0.7}
              >
                <View style={styles.vehiculoIconContainer}>
                  <Text style={styles.vehiculoIcon}>🚗</Text>
                </View>

                <View style={styles.vehiculoInfo}>
                  <Text style={styles.vehiculoPatente}>
                    {vehiculo.patente}
                  </Text>
                  <Text style={styles.vehiculoDetalle}>
                    {vehiculo.marca} {vehiculo.modelo}
                    {vehiculo.anio && ` · ${vehiculo.anio}`}
                  </Text>
                </View>

                <Text style={styles.vehiculoArrow}>▶</Text>
              </TouchableOpacity>
            ))}

            {vehiculos.length === 0 && (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>😕</Text>
                <Text style={styles.emptyText}>
                  No tenés vehículos disponibles
                </Text>
              </View>
            )}

            <TouchableOpacity
              style={styles.botonCancelar}
              onPress={onClose}
              disabled={isLoading}
            >
              <Text style={styles.botonCancelarTexto}>CANCELAR</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </View>
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
    lineHeight: 19,
  },
  vehiculoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
  },
  vehiculoIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: 'rgba(249, 200, 14, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  vehiculoIcon: {
    fontSize: 24,
  },
  vehiculoInfo: {
    flex: 1,
  },
  vehiculoPatente: {
    color: COLORS.textPrimary,
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  vehiculoDetalle: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.7,
  },
  vehiculoArrow: {
    color: COLORS.primary,
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  emptyIcon: {
    fontSize: 40,
    marginBottom: 8,
  },
  emptyText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    opacity: 0.7,
  },
  botonCancelar: {
    marginTop: 8,
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
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
});