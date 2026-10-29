import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { COLORS } from '@/constants/colors';
import { turnoService } from '@/services/turno.service';

interface ViajeHuerfano {
  viaje_id: string;
  estado: string;
  created_at: string;
  iniciado_en: string | null;
  direccion_origen: string;
  direccion_destino: string;
  pasajero_nombre: string | null;
  precio_estimado: number | null;
  origen_tipo: string;
  antiguedad_minutos: number;
}

interface ModalViajesHuerfanosProps {
  visible: boolean;
  onClose: () => void;
  onTodosCerrados: () => void; // Callback cuando ya no quedan viajes
}

const MOTIVOS = [
  { value: 'pasajero_cancelo', label: 'El pasajero canceló' },
  { value: 'pasajero_no_aparecio', label: 'El pasajero no apareció' },
  { value: 'pasajero_pidio_bajarse', label: 'El pasajero pidió bajarse' },
  { value: 'pasajero_abandono', label: 'El pasajero abandonó' },
  { value: 'emergencia', label: 'Emergencia' },
  { value: 'chofer_cancelo', label: 'Yo cancelé el viaje' },
  { value: 'error_sistema', label: 'Error del sistema' },
  { value: 'otro', label: 'Otro motivo' },
];

export function ModalViajesHuerfanos({
  visible,
  onClose,
  onTodosCerrados,
}: ModalViajesHuerfanosProps) {
  const [viajes, setViajes] = useState<ViajeHuerfano[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [motivoSeleccionado, setMotivoSeleccionado] = useState<string>('pasajero_cancelo');
  const [viajeProcesando, setViajeProcesando] = useState<string | null>(null);

  // Cargar viajes cuando se abre el modal
  useEffect(() => {
    if (visible) {
      cargarViajes();
    }
  }, [visible]);

  const cargarViajes = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await turnoService.listarViajesHuerfanos();
      setViajes(data.viajes);
      if (data.viajes.length === 0) {
        onTodosCerrados();
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error al cargar viajes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCerrarViaje = async (viajeId: string) => {
    setViajeProcesando(viajeId);
    setError(null);
    try {
      await turnoService.cerrarViajeHuerfano(viajeId, motivoSeleccionado);
      
      // Recargar la lista
      const data = await turnoService.listarViajesHuerfanos();
      setViajes(data.viajes);

      if (data.viajes.length === 0) {
        Alert.alert('Listo', 'Todos los viajes fueron cerrados. Ya podés cerrar el turno.');
        onTodosCerrados();
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error al cerrar el viaje');
    } finally {
      setViajeProcesando(null);
    }
  };

  const formatPrecio = (precio: number | null) => {
    if (precio === null) return 'N/A';
    return `$${precio.toLocaleString('es-AR')}`;
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.titulo}>⚠️ Viajes sin cerrar</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.descripcion}>
            Tenés {viajes.length} viaje(s) pendientes de cierre. Para cerrar el turno, debés cerrarlos forzadamente.
          </Text>

          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          {isLoading ? (
            <ActivityIndicator color={COLORS.primary} size="large" style={{ marginVertical: 20 }} />
          ) : (
            <ScrollView style={styles.lista}>
              {viajes.map((viaje) => (
                <View key={viaje.viaje_id} style={styles.cardViaje}>
                  <View style={styles.cardHeader}>
                    <Text style={styles.cardEstado}>{viaje.estado.toUpperCase()}</Text>
                    <Text style={styles.cardAntiguedad}>{viaje.antiguedad_minutos} min</Text>
                  </View>

                  <Text style={styles.cardDireccion}>📍 {viaje.direccion_origen}</Text>
                  <Text style={styles.cardDireccion}>🏁 {viaje.direccion_destino}</Text>

                  <View style={styles.cardFooter}>
                    <Text style={styles.cardPasajero}>
                      👤 {viaje.pasajero_nombre || 'Anónimo'}
                    </Text>
                    <Text style={styles.cardPrecio}>{formatPrecio(viaje.precio_estimado)}</Text>
                  </View>

                  <View style={styles.separador} />

                  <View style={styles.motivoContainer}>
                    <Text style={styles.motivoLabel}>Motivo del cierre:</Text>
                    <View style={styles.motivosGrid}>
                      {MOTIVOS.map((motivo) => (
                        <TouchableOpacity
                          key={motivo.value}
                          style={[
                            styles.motivoChip,
                            motivoSeleccionado === motivo.value && styles.motivoChipActivo,
                          ]}
                          onPress={() => setMotivoSeleccionado(motivo.value)}
                        >
                          <Text
                            style={[
                              styles.motivoChipText,
                              motivoSeleccionado === motivo.value && styles.motivoChipTextActivo,
                            ]}
                          >
                            {motivo.label}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>

                  <TouchableOpacity
                    style={[
                      styles.botonCerrar,
                      viajeProcesando === viaje.viaje_id && styles.botonCerrarDisabled,
                    ]}
                    onPress={() => handleCerrarViaje(viaje.viaje_id)}
                    disabled={viajeProcesando === viaje.viaje_id}
                  >
                    {viajeProcesando === viaje.viaje_id ? (
                      <ActivityIndicator color={COLORS.white} />
                    ) : (
                      <Text style={styles.botonCerrarText}>Cerrar este viaje</Text>
                    )}
                  </TouchableOpacity>
                </View>
              ))}
            </ScrollView>
          )}

          <TouchableOpacity style={styles.botonCancelar} onPress={onClose}>
            <Text style={styles.botonCancelarText}>Cancelar</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: COLORS.backgroundMedium,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '85%',
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  titulo: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeBtn: {
    padding: 4,
  },
  closeText: {
    color: COLORS.white,
    fontSize: 18,
  },
  descripcion: {
    color: COLORS.textSecondary,
    fontSize: 13,
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
  },
  errorContainer: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 12,
    marginHorizontal: 20,
    marginBottom: 8,
  },
  errorText: {
    color: COLORS.error,
    fontSize: 13,
    textAlign: 'center',
  },
  lista: {
    paddingHorizontal: 20,
    paddingTop: 8,
  },
  cardViaje: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  cardEstado: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardAntiguedad: {
    color: COLORS.textSecondary,
    fontSize: 12,
  },
  cardDireccion: {
    color: COLORS.white,
    fontSize: 13,
    marginBottom: 4,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  cardPasajero: {
    color: COLORS.textSecondary,
    fontSize: 12,
  },
  cardPrecio: {
    color: COLORS.success,
    fontSize: 14,
    fontWeight: 'bold',
  },
  separador: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginVertical: 12,
  },
  motivoContainer: {
    marginBottom: 12,
  },
  motivoLabel: {
    color: COLORS.textSecondary,
    fontSize: 12,
    marginBottom: 8,
  },
  motivosGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  motivoChip: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  motivoChipActivo: {
    backgroundColor: COLORS.primary,
  },
  motivoChipText: {
    color: COLORS.white,
    fontSize: 11,
  },
  motivoChipTextActivo: {
    color: COLORS.backgroundDark,
    fontWeight: 'bold',
  },
  botonCerrar: {
    backgroundColor: COLORS.error,
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  botonCerrarDisabled: {
    opacity: 0.5,
  },
  botonCerrarText: {
    color: COLORS.white,
    fontSize: 14,
    fontWeight: 'bold',
  },
  botonCancelar: {
    marginHorizontal: 20,
    marginTop: 12,
    paddingVertical: 12,
    alignItems: 'center',
  },
  botonCancelarText: {
    color: COLORS.textSecondary,
    fontSize: 14,
  },
});