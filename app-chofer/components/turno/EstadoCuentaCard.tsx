import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '@/constants/colors';

interface VehiculoInfo {
  patente: string;
  marca: string;
  modelo: string;
  anio?: number;
  licencia: string;
}

interface EstadoCuentaCardProps {
  vehiculo: VehiculoInfo | null;
  documentosVigentes: number;
  documentosTotal: number;
}

export function EstadoCuentaCard({
  vehiculo,
  documentosVigentes,
  documentosTotal,
}: EstadoCuentaCardProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.seccionTitulo}>ESTADO DE CUENTA</Text>

      {/* Card Vehículo */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardIcono}>
            {vehiculo ? '🚗' : '🚗'}
          </Text>
          <Text style={styles.cardTitulo}>Vehículo</Text>
          {vehiculo && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{vehiculo.patente}</Text>
            </View>
          )}
        </View>

        {vehiculo ? (
          <View>
            <Text style={styles.cardValor}>
              {vehiculo.marca} {vehiculo.modelo}
              {vehiculo.anio && ` · ${vehiculo.anio}`}
            </Text>
            <View style={styles.licenciaRow}>
              <Text style={styles.licenciaIcon}>🪪</Text>
              <Text style={styles.licenciaTexto}>
                Licencia: {vehiculo.licencia}
              </Text>
            </View>
          </View>
        ) : (
          <View>
            <Text style={styles.cardValorVacio}>Sin asignar</Text>
            <Text style={styles.cardHint}>
              Iniciá un turno para asignar un vehículo.
            </Text>
          </View>
        )}
      </View>

      {/* Card Documentos - solo si hay turno */}
      {vehiculo && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardIcono}>📄</Text>
            <Text style={styles.cardTitulo}>Documentos</Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>
                ✅ {documentosVigentes}/{documentosTotal}
              </Text>
            </View>
          </View>
          <Text style={styles.cardValor}>
            {documentosVigentes === documentosTotal
              ? 'Licencia · Sanidad · Buena Conducta'
              : `${documentosVigentes}/${documentosTotal} vigentes`}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  seccionTitulo: {
    color: COLORS.textPrimary,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.6,
    marginBottom: 10,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardIcono: {
    fontSize: 20,
    marginRight: 8,
  },
  cardTitulo: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
    flex: 1,
  },
  badge: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeText: {
    color: COLORS.success,
    fontSize: 11,
    fontWeight: 'bold',
  },
  cardValor: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  cardValorVacio: {
    color: COLORS.textPrimary,
    fontSize: 14,
    opacity: 0.5,
    marginBottom: 4,
  },
  cardHint: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.6,
    fontStyle: 'italic',
  },
  licenciaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
  },
  licenciaIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  licenciaTexto: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.85,
  },
});