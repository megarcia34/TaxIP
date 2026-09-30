/**
 * Servicio del Módulo 3 - Notificaciones.
 *
 * Wrapper de expo-notifications.
 * STUB de Fase 9.2: solo la estructura. El registro de push tokens reales
 * (FCM/APNs) se implementa cuando el backend los soporte.
 */
import * as Notifications from 'expo-notifications';

const PENDIENTE = '[Notif] pendiente Fase 9.3';

export const notificacionService = {
  /**
   * Solicita permisos de notificaciones.
   */
  async pedirPermisos(): Promise<boolean> {
    const { status } = await Notifications.requestPermissionsAsync();
    return status === 'granted';
  },

  /**
   * Muestra una notificación local inmediata.
   */
  async mostrarNotificacionLocal(
    titulo: string,
    cuerpo: string
  ): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: { title: titulo, body: cuerpo },
      trigger: null,
    });
  },

  /**
   * Registra el token push del dispositivo en el backend.
   * STUB: el backend todavía no expone endpoint para registrar tokens.
   */
  async registrarTokenPush(): Promise<string | null> {
    console.warn(PENDIENTE, 'registrarTokenPush()');
    return null;
  },
};