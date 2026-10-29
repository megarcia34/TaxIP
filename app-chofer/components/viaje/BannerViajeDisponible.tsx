import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { navigationRef } from '@/src/navigation/navigationRef'; // ✅ Importamos navigationRef
import { COLORS } from '@/constants/colors';
import { useViajeStore } from '@/stores/viaje.store';

// ✅ Recibimos la ruta actual como prop
interface BannerViajeDisponibleProps {
  rutaActual: string;
}

export function BannerViajeDisponible({ rutaActual }: BannerViajeDisponibleProps) {
  const insets = useSafeAreaInsets();
  
  const viajesDisponibles = useViajeStore((s) => s.viajesDisponibles);

  // No mostrar el banner si ya estamos en la pantalla de viajes
  if (rutaActual === 'GestionViajes') return null;
  
  // No mostrar si no hay viajes
  if (viajesDisponibles.length === 0) return null;

  const handlePress = () => {
    if (navigationRef.isReady()) {
      navigationRef.navigate('GestionViajes');
    }
  };

  return (
    <TouchableOpacity
      style={[styles.banner, { top: insets.top + 10 }]}
      onPress={handlePress}
      activeOpacity={0.9}
    >
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>🚕</Text>
      </View>
      <View style={styles.textContainer}>
        <Text style={styles.title}>¡Nuevo viaje disponible!</Text>
        <Text style={styles.subtitle}>
          {viajesDisponibles.length} {viajesDisponibles.length === 1 ? 'viaje' : 'viajes'} en tu zona
        </Text>
      </View>
      <Text style={styles.action}>Ver →</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  banner: {
    position: 'absolute',
    left: 16,
    right: 16,
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
    zIndex: 9999,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  icon: { fontSize: 20 },
  textContainer: { flex: 1 },
  title: {
    color: '#1a1a1a',
    fontWeight: 'bold',
    fontSize: 14,
  },
  subtitle: {
    color: '#1a1a1a',
    fontSize: 12,
    opacity: 0.8,
    marginTop: 2,
  },
  action: {
    color: '#1a1a1a',
    fontWeight: 'bold',
    fontSize: 14,
  },
});