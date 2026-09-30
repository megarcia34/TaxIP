/**
 * Hook de WebSocket.
 *
 * Responsabilidades:
 * - Conectar el websocketService cuando hay token + userId.
 * - Registrar callbacks que sincronizan el estado de conexión con el
 *   conexion.store y enrutan los mensajes entrantes al viaje.store.
 * - Desconectar al desmontar.
 *
 * El enrutamiento de mensajes es defensivo: si el payload no trae los
 * campos esperados, se loguea un warn y se ignora.
 *
 * Ref: app/websocket/events.py (payloads del backend).
 */
import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/stores/auth.store';
import { useConexionStore } from '@/stores/conexion.store';
import { useViajeStore } from '@/stores/viaje.store';
import { websocketService } from '@/services/websocket.service';
import type {
  MensajeWS,
  PayloadNuevoViaje,
  PayloadViajeTomado,
  PayloadExcluidoDeViaje,
  PayloadViajeCancelado,
  PayloadViajeExpirado,
} from '@/types/websocket.types';
import type { ViajeSolicitado } from '@/types/viaje.types';

export function useWebSocket() {
  const token = useAuthStore((s) => s.token);
  const userId = useAuthStore((s) => s.user?.id);
  const estadoWS = useConexionStore((s) => s.estadoWS);

  // Refs para acceder a las acciones del store sin re-suscribir el effect.
  const setEstadoWS = useConexionStore((s) => s.setEstadoWS);
  const setUltimaConexion = useConexionStore((s) => s.setUltimaConexion);
  const incrementarIntentos = useConexionStore((s) => s.incrementarIntentos);
  const resetearIntentos = useConexionStore((s) => s.resetear);

  const agregarViajeDisponible = useViajeStore((s) => s.agregarViajeDisponible);
  const quitarViajeDisponible = useViajeStore((s) => s.quitarViajeDisponible);

  // Guard para no re-conectar dos veces por el mismo user/token.
  const conectadoConRef = useRef<string | null>(null);

  useEffect(() => {
    if (!token || !userId) {
      return;
    }

    const claveConexion = `${userId}:${token}`;
    if (conectadoConRef.current === claveConexion) {
      return;
    }
    conectadoConRef.current = claveConexion;

    // --- Callbacks ---
    websocketService.onConectado(() => {
      setEstadoWS('conectado');
      setUltimaConexion(Date.now());
      resetearIntentos();
    });

    websocketService.onDesconectado(() => {
      setEstadoWS('desconectado');
    });

    websocketService.onError(() => {
      setEstadoWS('error');
    });

    websocketService.onMensaje((mensaje: MensajeWS) => {
      enrutarMensaje(mensaje);
    });

    // --- Conectar ---
    setEstadoWS('conectando');
    websocketService.conectar(userId, token);

    return () => {
      websocketService.desconectar();
      conectadoConRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, userId]);

  // ------------------------------------------------------------
  // ENRUTAMIENTO DE MENSAJES
  // ------------------------------------------------------------
  function enrutarMensaje(mensaje: MensajeWS): void {
    switch (mensaje.type) {
      case 'nuevo_viaje': {
        const p = mensaje.data as PayloadNuevoViaje | undefined;
        if (!p?.viaje_id) {
          console.warn('[WS] nuevo_viaje sin viaje_id');
          return;
        }
        // Adaptamos el payload mínimo del WS a ViajeSolicitado.
        // ⚠️ DEUDA E3: la forma exacta del payload se confirma cuando el
        // backend emita un nuevo_viaje real.
        const viaje: ViajeSolicitado = adaptarNuevoViaje(p);
        agregarViajeDisponible(viaje);
        break;
      }

      case 'viaje_tomado': {
        const p = mensaje.data as PayloadViajeTomado | undefined;
        if (p?.viaje_id) quitarViajeDisponible(p.viaje_id);
        break;
      }

      case 'excluido_de_viaje': {
        const p = mensaje.data as PayloadExcluidoDeViaje | undefined;
        if (p?.viaje_id) quitarViajeDisponible(p.viaje_id);
        break;
      }

      case 'viaje_cancelado': {
        const p = mensaje.data as PayloadViajeCancelado | undefined;
        if (p?.viaje_id) quitarViajeDisponible(p.viaje_id);
        break;
      }

      case 'viaje_expirado': {
        const p = mensaje.data as PayloadViajeExpirado | undefined;
        if (p?.viaje_id) quitarViajeDisponible(p.viaje_id);
        break;
      }

      case 'viaje_reasignado':
      case 'cobro_pendiente':
      case 'pago_confirmado':
        // TODO Fase 9.3/Etapa 11: manejar estos casos.
        console.log('[WS] evento sin handler:', mensaje.type);
        break;

      default:
        console.log('[WS] evento desconocido:', mensaje.type);
    }
  }

  return { estadoWS };
}

// ------------------------------------------------------------
// ADAPTADOR
// ------------------------------------------------------------
/**
 * Adapta el payload del WS `nuevo_viaje` a un `ViajeSolicitado`.
 *
 * El payload del WS trae solo los campos necesarios para mostrar la
 * tarjeta del viaje entrante. Los campos que no vienen se rellenan con
 * null / defaults. La forma completa se obtiene luego con
 * `GET /api/viajes/{id}/estado` si el chofer quiere más detalle.
 *
 * ⚠️ DEUDA E3: confirmar campos exactos del payload cuando se pruebe
 * con un nuevo_viaje real.
 */
function adaptarNuevoViaje(p: PayloadNuevoViaje): ViajeSolicitado {
  const ahora = new Date().toISOString();
  return {
    id: p.viaje_id,
    control_base_id: '',
    pasajero_id: '',
    chofer_id: null,
    chofer_vehiculo_id: null,
    vehiculo_id: null,
    turno_id: null,

    origen_lat: p.origen_lat,
    origen_lng: p.origen_lng,
    destino_lat: p.destino_lat ?? null,
    destino_lng: p.destino_lng ?? null,
    direccion_origen: p.direccion_origen,
    direccion_destino: p.direccion_destino ?? null,

    estado: 'publicado',

    precio_estimado: p.precio_estimado ?? null,
    precio_final: null,
    moneda: 'ARS',

    tiempo_estimado_segundos: p.tiempo_estimado_segundos ?? null,
    distancia_metros: p.distancia_metros ?? null,

    url_seguimiento: null,
    codigo_compartido: null,

    solicitado_en: ahora,
    aceptado_en: null,
    iniciado_en: null,
    finalizado_en: null,
    cancelado_en: null,
    cancelado_por: null,
    motivo_cancelacion: null,

    fecha_programada: null,
    reserva_procesada: false,

    comercio_id: null,
    empresa_id: null,
    nombre_pasajero: null,
    notas: null,
    facturado: false,

    origen_tipo: null,
    metodo_pago: null,
  };
}