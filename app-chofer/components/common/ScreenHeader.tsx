import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '@/constants/colors';

interface ScreenHeaderProps {
  /** Título centrado. Si no se pasa, no se muestra. */
  titulo?: string;
  /** Texto del botón izquierdo. Ej. "← HOME" o "← VOLVER". */
  textoIzquierda?: string;
  /** Acción al tocar el botón izquierdo. Si no se pasa, no se muestra. */
  onIzquierda?: () => void;
  /** Ícono o texto del botón derecho. Ej. "👤". */
  iconoDerecha?: string;
  /** Acción al tocar el botón derecho. Si no se pasa, no se muestra. */
  onDerecha?: () => void;
  /** Si true, agrega paddingTop según safe area (default true). */
  conSafeArea?: boolean;
  /** Si true, el botón izquierdo muestra solo la flecha "←" sin texto. */
  soloFlecha?: boolean;
  /** Estilo extra para el contenedor. */
  style?: object;
}

export function ScreenHeader({
  titulo,
  textoIzquierda,
  onIzquierda,
  iconoDerecha,
  onDerecha,
  conSafeArea = true,
  soloFlecha = false,
  style,
}: ScreenHeaderProps) {
  const insets = useSafeAreaInsets();

  const mostrarIzquierda = onIzquierda != null;
  const mostrarDerecha = onDerecha != null && iconoDerecha != null;

  return (
    <View
      style={[
        styles.container,
        conSafeArea && { paddingTop: insets.top + 12 },
        style,
      ]}
    >
      <View style={styles.lado}>
        {mostrarIzquierda && (
          <TouchableOpacity
            style={styles.boton}
            onPress={onIzquierda}
            activeOpacity={0.7}
          >
            <Text style={styles.botonTexto}>
              {soloFlecha ? '←' : textoIzquierda || '←'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.centro}>
        {titulo && <Text style={styles.titulo}>{titulo}</Text>}
      </View>

      <View style={styles.lado}>
        {mostrarDerecha && (
          <TouchableOpacity
            style={styles.boton}
            onPress={onDerecha}
            activeOpacity={0.7}
          >
            <Text style={styles.botonIcono}>{iconoDerecha}</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 12,
  },
  lado: {
    minWidth: 80,
    flexDirection: 'row',
    alignItems: 'center',
  },
  centro: {
    flex: 1,
    alignItems: 'center',
  },
  titulo: {
    color: COLORS.textPrimary,
    fontSize: 16,
    fontWeight: 'bold',
    letterSpacing: 1.5,
  },
  boton: {
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  botonTexto: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  botonIcono: {
    color: COLORS.textPrimary,
    fontSize: 22,
  },
});