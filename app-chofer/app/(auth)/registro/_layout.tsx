import { Stack } from 'expo-router';

export default function RegistroLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="paso1-cuenta" />
      <Stack.Screen name="paso2-validar-email" />
      <Stack.Screen name="paso3-datos-personales" />
      <Stack.Screen name="paso4-documentos" />
      <Stack.Screen name="paso5-selfie" />
      <Stack.Screen name="paso6-bloqueo" />
    </Stack>
  );
}