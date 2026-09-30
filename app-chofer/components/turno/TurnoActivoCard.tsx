import { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '@/constants/colors';
import { COMBUSTIBLE_LABELS, COMBUSTIBLE_ICONS } from '@/types/turno.types';
import type { TurnoActivo } from '@/types/turno.types';

interface TurnoActivoCardProps {
  turno: TurnoActivo;
}

export function TurnoActivoCard({ turno }: TurnoActivoCardProps) {
  // Usar duracionFormateada del backend como valor inicial
  const [duracion, setDuracion] = useState(
    turno.duracionFormateada || '00:00:00'
  );

  useEffect(() => {
    // Si el backend provee duracionFormateada, usarla como base
    if (turno.duracionFormateada) {
      setDuracion(turno.duracionFormateada);
    }

    // Actualizar cada segundo para que la UI muestre el tiempo real
    const interval = setInterval(() => {
      const inicio = new Date(turno.inicioTurno).getTime();
      const ahora = Date.now();
      const diffMs = ahora - inicio;

      if (diffMs < 0 || isNaN(diffMs)) {
        setDuracion('00:00:00');
        return;
      }

      const horas = Math.floor(diffMs / (1000 * 60 * 60));
      const minutos = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
      const segundos = Math.floor((diffMs % (1000 * 60)) / 1000);

      setDuracion(
        `${horas.toString().padStart(2, '0')}:${minutos
          .toString()
          .padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [turno.inicioTurno, turno.duracionFormateada]);

  const getEstadoLaboralLabel = () => {
    switch (turno.estadoLaboral) {
      case 'libre':
        return { texto: 'LIBRE', color: COLORS.success };
      case 'ocupado':
        return { texto: 'OCUPADO', color: COLORS.warning };
      default:
        return { texto: 'FUERA DE SERVICIO', color: COLORS.gray };
    }
  };

  const estadoInfo = getEstadoLaboralLabel();

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.titulo}>🟢 TURNO ACTIVO</Text>
        <View
          style={[
            styles.estadoBadge,
            { backgroundColor: estadoInfo.color + '20' },
          ]}
        >
          <Text style={[styles.estadoText, { color: estadoInfo.color }]}>
            {estadoInfo.texto}
          </Text>
        </View>
      </View>

      <View style={styles.duracionContainer}>
        <Text style={styles.duracionLabel}>Duración del turno</Text>
        <Text style={styles.duracion}>{duracion}</Text>
      </View>

      <View style={styles.infoGrid}>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Vehículo</Text>
          <Text style={styles.infoValue}>{turno.patente}</Text>
        </View>

        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Km inicial</Text>
          <Text style={styles.infoValue}>
            {turno.kmInicial.toLocaleString('es-AR')}
          </Text>
        </View>

        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Combustible</Text>
          <Text style={styles.infoValue}>
            {COMBUSTIBLE_ICONS[turno.combustibleInicial]}{' '}
            {COMBUSTIBLE_LABELS[turno.combustibleInicial]}
          </Text>
        </View>
      </View>

      {turno.estadoLaboral === 'libre' && (
        <View style={styles.mensajeContainer}>
          <Text style={styles.mensaje}>Esperando solicitudes de viaje...</Text>
        </View>
      )}

      {turno.estadoLaboral === 'ocupado' && (
        <View style={styles.mensajeContainer}>
          <Text style={styles.mensaje}>🚗 En viaje actualmente</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.success,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  titulo: {
    color: COLORS.success,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  estadoBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  estadoText: {
    fontSize: 11,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  duracionContainer: {
    alignItems: 'center',
    paddingVertical: 16,
    marginBottom: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    borderRadius: 8,
  },
  duracionLabel: {
    color: COLORS.textPrimary,
    fontSize: 11,
    opacity: 0.7,
    marginBottom: 4,
    letterSpacing: 1,
  },
  duracion: {
    color: COLORS.textPrimary,
    fontSize: 36,
    fontWeight: 'bold',
    letterSpacing: 2,
    fontVariant: ['tabular-nums'],
  },
  infoGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  infoItem: {
    flex: 1,
    alignItems: 'center',
  },
  infoLabel: {
    color: COLORS.textPrimary,
    fontSize: 10,
    opacity: 0.6,
    marginBottom: 4,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  infoValue: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
  },
  mensajeContainer: {
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
    alignItems: 'center',
  },
  mensaje: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.85,
    fontStyle: 'italic',
  },
});