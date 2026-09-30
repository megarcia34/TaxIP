import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '@/constants/colors';
import { ScreenHeader } from '@/components/common/ScreenHeader';

export default function PerfilScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <View style={[styles.content, { paddingHorizontal: 20 }]}>
        <ScreenHeader
          titulo="MI CUENTA"
          textoIzquierda="← HOME"
          onIzquierda={() => router.replace('/(app)/home' as any)}
          conSafeArea={false}
          style={{ paddingTop: insets.top + 12 }}
        />

        <View style={styles.body}>
          <Text style={styles.text}>PERFIL DEL CHOFER</Text>
          <Text style={styles.subtitulo}>
            Pantalla en construcción
          </Text>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
  body: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: COLORS.textPrimary,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitulo: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.6,
    fontStyle: 'italic',
  },
});