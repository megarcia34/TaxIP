import { useEffect, useState } from 'react';
import { Stack } from 'expo-router';
import { ActivityIndicator, View } from 'react-native';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUbicacion } from '@/hooks/useUbicacion';
import { useSincronizacionEstadoLaboral } from '@/hooks/useSincronizacionEstadoLaboral';
import { useTurnoStore } from '@/stores/turno.store';
import { COLORS } from '@/constants/colors';

export default function AppLayout() {
  const cargarEstado = useTurnoStore((s) => s.cargarEstado);
  const cargarTurnoActivo = useTurnoStore((s) => s.cargarTurnoActivo);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let isMounted = true;
    
    // Esperar a que los datos del store estén cargados antes de activar el ciclo de vida
    Promise.all([
      cargarEstado().catch(() => {}),
      cargarTurnoActivo().catch(() => {}),
    ]).finally(() => {
      if (isMounted) setIsReady(true);
    });

    return () => {
      isMounted = false;
    };
  }, []);

  // Solo activar los hooks de tracking/WS cuando el estado inicial ya se asentó
  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.backgroundDark }}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return <AppLayoutContent />;
}

// Componente interno para aislar los hooks del ciclo de carga inicial
function AppLayoutContent() {
  useWebSocket();
  useUbicacion();
  useSincronizacionEstadoLaboral();

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="home" />
      <Stack.Screen name="turnos" />
      <Stack.Screen name="perfil" />
      <Stack.Screen name="configuracion" />
      <Stack.Screen name="viajes/calle" />
      <Stack.Screen name="viajes/[id]" />
    </Stack>
  );
}