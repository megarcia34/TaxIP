/**
 * Tipos del protocolo WebSocket de M3.
 *
 * Formato de mensaje (bidireccional):
 *   { type: string, data?: object }
 *
 * Ref: app/websocket/events.py (EventType) y app/websocket/handlers.py.
 *
 * Se tipan solo los eventos relevantes para la App Chofer en M3.
 * Los eventos legacy (ROLE_SET, SUBSCRIBED, DRIVER_ARRIVED,
 * DRIVER_LOCATION_UPDATE) se omiten a propósito: el frontend los ignora
 * si llegan.
 */

/**
 * Tipos de mensaje WebSocket que la App Chofer recibe del servidor.
 */
export type TipoMensajeWSRecibido =
  | 'pong'
  | 'error'
  | 'nuevo_viaje'
  | 'viaje_tomado'
  | 'excluido_de_viaje'
  | 'viaje_cancelado'
  | 'viaje_reasignado'
  | 'viaje_expirado'
  | 'cobro_pendiente'
  | 'pago_confirmado';

/**
 * Estado de la conexión WebSocket del cliente.
 *
 * No es un evento del protocolo: es estado local del cliente que la app
 * usa para reflejar la conexión en la UI y decidir la reconexión.
 */
export type EstadoWS =
  | 'desconectado'
  | 'conectando'
  | 'conectado'
  | 'reconectando'
  | 'error';

/**
 * Tipos de mensaje WebSocket que la App Chofer envía al servidor.
 */
export type TipoMensajeWSEnviado =
  | 'ping'
  | 'set_role'
  | 'location_update'
  | 'arrived'
  | 'subscribe_trip';

/**
 * Todos los tipos de mensaje WS que la App Chofer maneja.
 */
export type TipoMensajeWS = TipoMensajeWSRecibido | TipoMensajeWSEnviado;

/**
 * Mensaje WS genérico.
 */
export interface MensajeWS<T = unknown> {
  type: TipoMensajeWS;
  data?: T;
}

/**
 * Códigos de cierre del WebSocket.
 * Ref: WsCloseCode en events.py.
 */
export const WS_CLOSE_CODES = {
  NORMAL: 1000,
  GOING_AWAY: 1001,
  PROTOCOL_ERROR: 1002,
  UNSUPPORTED_DATA: 1003,
  POLICY_VIOLATION: 1008,
  INTERNAL_ERROR: 1011,
  UNAUTHORIZED: 4001,
  FORBIDDEN: 4003,
  TOO_MANY_CONNECTIONS: 4008,
  INVALID_ROLE: 4009,
} as const;

export type WsCloseCode = (typeof WS_CLOSE_CODES)[keyof typeof WS_CLOSE_CODES];

/**
 * Constantes del heartbeat.
 * Ref: events.py.
 */
export const WS_HEARTBEAT_INTERVAL_SECONDS = 30;
export const WS_HEARTBEAT_TIMEOUT_SECONDS = 90;
export const WS_AUTH_TIMEOUT_SECONDS = 5;

// ============================================================
// PAYLOADS DE EVENTOS ESPECÍFICOS
// ============================================================
//
// ⚠️ DEUDA: los payloads exactos de nuevo_viaje, viaje_tomado, etc. se
// confirman en Fase 9.3 cuando se conecte el WS real. Las formas de abajo
// son estimadas según la estructura del modelo ViajeSolicitado.
//
// Si al conectar el WS real la forma no coincide, se ajustan acá y se
// actualizan los consumidores.

/**
 * Payload de `nuevo_viaje`. Se emite a los choferes cuando se publica
 * un viaje en broadcast.
 */
export interface PayloadNuevoViaje {
  viaje_id: string;
  origen_lat: number;
  origen_lng: number;
  direccion_origen: string;
  destino_lat?: number | null;
  destino_lng?: number | null;
  direccion_destino?: string | null;
  precio_estimado?: number | null;
  distancia_metros?: number | null;
  tiempo_estimado_segundos?: number | null;
  /** Tiempo que tenés para aceptar antes de que se asigne a otro. */
  tiempo_aceptacion_segundos?: number;
}

/**
 * Payload de `viaje_tomado`. Se emite a los choferes que NO aceptaron
 * (para que sepan que ya fue tomado y lo saquen de su lista).
 */
export interface PayloadViajeTomado {
  viaje_id: string;
  chofer_id: string;
  chofer_nombre?: string;
}

/**
 * Payload de `excluido_de_viaje`. Se emite a un chofer específico
 * cuando el broadcast se cierra para él.
 */
export interface PayloadExcluidoDeViaje {
  viaje_id: string;
  motivo: string;
}

/**
 * Payload de `viaje_cancelado`.
 */
export interface PayloadViajeCancelado {
  viaje_id: string;
  cancelado_por: string;
  motivo?: string | null;
}

/**
 * Payload de `viaje_reasignado`.
 */
export interface PayloadViajeReasignado {
  viaje_id: string;
  chofer_id: string;
  motivo?: string | null;
}

/**
 * Payload de `viaje_expirado`.
 */
export interface PayloadViajeExpirado {
  viaje_id: string;
}

/**
 * Payload de `cobro_pendiente`. Se emite al chofer cuando el viaje
 * se finalizó y hay que cobrar.
 */
export interface PayloadCobroPendiente {
  viaje_id: string;
  precio_final: number;
  moneda: string;
  metodo_pago: string;
}

/**
 * Payload de `pago_confirmado`.
 */
export interface PayloadPagoConfirmado {
  viaje_id: string;
  monto: number;
  moneda: string;
}

/**
 * Payload de `error`.
 */
export interface PayloadError {
  message: string;
  code?: string;
}