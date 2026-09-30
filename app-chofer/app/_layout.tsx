import { useEffect, useState } from 'react';
import { LogBox } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import * as SplashScreen from 'expo-splash-screen';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Ignorar los logs de conflicto interno de hooks de Expo Go / ContextNavigator
LogBox.ignoreLogs([
  'React has detected a change in the order of Hooks',
  "Cannot read property 'length' of undefined",
]);

// Bloquea el splash screen nativo hasta que el estado inicial esté montado
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Limpieza de debugging
        await AsyncStorage.removeItem('taxip-turno');
        console.log('🧹 AsyncStorage: clave "taxip-turno" limpiada');
      } catch (e) {
        console.warn('⚠️ Error al limpiar AsyncStorage:', e);
      } finally {
        setIsReady(true);
      }
    }

    prepare();
  }, []);

  useEffect(() => {
    if (isReady) {
      // Oculta el splash de forma segura cuando React ya tiene el estado montado
      SplashScreen.hideAsync();
    }
  }, [isReady]);

  // Si no está listo, retener el render evita la desalineación de Hooks en Expo Go
  if (!isReady) {
    return null;
  }

  return (
    <>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(app)" />
      </Stack>
    </>
  );
}