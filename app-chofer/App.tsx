import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';

// Auth
import LoginScreen from './src/screens/auth/LoginScreen';
import SplashScreen from './src/screens/auth/SplashScreen';

// App
import HomeScreen from './src/screens/app/HomeScreen';
import TurnosScreen from './src/screens/app/TurnosScreen';
import PerfilScreen from './src/screens/app/PerfilScreen';
import ConfiguracionScreen from './src/screens/app/ConfiguracionScreen';
import ViajeCalleScreen from './src/screens/app/ViajeCalleScreen';
import ViajeDetalleScreen from './src/screens/app/ViajeDetalleScreen';

// Registro (si querés incluirlos en el flujo)
import Paso1Screen from './src/screens/registro/Paso1Screen';
import Paso2Screen from './src/screens/registro/Paso2Screen';
import Paso3Screen from './src/screens/registro/Paso3Screen';
import Paso4Screen from './src/screens/registro/Paso4Screen';
import Paso5Screen from './src/screens/registro/Paso5Screen';
import Paso6Screen from './src/screens/registro/Paso6Screen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
        {/* Pantallas de Autenticación */}
        <Stack.Screen name="Splash" component={SplashScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />

        {/* Pantallas Principales */}
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Turnos" component={TurnosScreen} />
        <Stack.Screen name="Perfil" component={PerfilScreen} />
        <Stack.Screen name="Configuracion" component={ConfiguracionScreen} />
        
        {/* Viajes */}
        <Stack.Screen name="ViajeCalle" component={ViajeCalleScreen} />
        <Stack.Screen name="ViajeDetalle" component={ViajeDetalleScreen} />

        {/* Registro */}
        <Stack.Screen name="Paso1" component={Paso1Screen} />
        <Stack.Screen name="Paso2" component={Paso2Screen} />
        <Stack.Screen name="Paso3" component={Paso3Screen} />
        <Stack.Screen name="Paso4" component={Paso4Screen} />
        <Stack.Screen name="Paso5" component={Paso5Screen} />
        <Stack.Screen name="Paso6" component={Paso6Screen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}