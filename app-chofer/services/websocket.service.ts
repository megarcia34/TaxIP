/**
 * Servicio del Módulo 3 - WebSocket.
 *
 * Implementación real:
 * - Conexión a ws://.../ws/{userId}?token={jwt}.
 * - Heartbeat: envía `ping` cada 30s; si no hay `pong` en 90s, cierra.
 * - Reconexión exponencial: 1s, 2s, 4s, 8s, 16s, 30s... (máx 10 intentos).
 * - Jitter ±20% para evitar thundering herd.
 * - El service NO toca el store. Solo dispara callbacks.
 *
 * Ref: app/websocket/events.py, handlers.py (backend).
 */
import { WS_URL } from '@/constants/config';
import {
  WS_CLOSE_CODES,
  WS_HEARTBEAT_INTERVAL_SECONDS,
  WS_HEARTBEAT_TIMEOUT_SECONDS,
  type MensajeWS,
  type PayloadError,
  type TipoMensajeWS,
} from '@/types/websocket.types';

type MensajeCallback = (mensaje: MensajeWS) => void;
type ConectadoCallback = () => void;
type DesconectadoCallback = (code: number, reason: string) => void;
type ErrorCallback = (error: unknown) => void;

const MAX_INTENTOS_RECONEXION = 10;
const BACKOFF_BASE_MS = 1000;
const BACKOFF_MAX_MS = 30000;
const JITTER_PCT = 0.2;

class WebSocketService {
  private ws: WebSocket | null = null;
  private userId: string | null = null;
  private token: string | null = null;

  private reconectarActivo = false;
  private intentosReconexion = 0;
  private timeoutReconexion: ReturnType<typeof setTimeout> | null = null;

  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private ultimoPongRecibido = 0;

  private onMensajeCb: MensajeCallback | null = null;
  private onConectadoCb: ConectadoCallback | null = null;
  private onDesconectadoCb: DesconectadoCallback | null = null;
  private onErrorCb: ErrorCallback | null = null;

  // ============================================================
  // API PÚBLICA
  // ============================================================

  conectar(userId: string, token: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.warn('[WS] ya conectado, ignorando conectar()');
      return;
    }

    this.userId = userId;
    this.token = token;
    this.reconectarActivo = true;
    this.intentosReconexion = 0;
    this.abrirSocket();
  }

  desconectar(): void {
    this.reconectarActivo = false;
    this.limpiarTimers();
    if (this.ws) {
      try {
        this.ws.close(WS_CLOSE_CODES.NORMAL, 'cliente cierra');
      } catch {
        // no-op
      }
      this.ws = null;
    }
    this.userId = null;
    this.token = null;
    this.intentosReconexion = 0;
  }

  enviar(mensaje: MensajeWS): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WS] enviar() con socket cerrado, descartado:', mensaje.type);
      return;
    }
    try {
      this.ws.send(JSON.stringify(mensaje));
    } catch (e) {
      console.warn('[WS] error al enviar:', e);
    }
  }

  onMensaje(cb: MensajeCallback): void {
    this.onMensajeCb = cb;
  }

  onConectado(cb: ConectadoCallback): void {
    this.onConectadoCb = cb;
  }

  onDesconectado(cb: DesconectadoCallback): void {
    this.onDesconectadoCb = cb;
  }

  onError(cb: ErrorCallback): void {
    this.onErrorCb = cb;
  }

  estaConectado(): boolean {
    return !!this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  getUserId(): string | null {
    return this.userId;
  }

  // ============================================================
  // INTERNOS
  // ============================================================

  private abrirSocket(): void {
    if (!this.userId || !this.token) return;

    const url = `${WS_URL}/ws/${this.userId}?token=${this.token}`;
    console.log('[WS] conectando a', `${WS_URL}/ws/${this.userId}?token=***`);

    try {
      this.ws = new WebSocket(url);
    } catch (e) {
      console.warn('[WS] error al crear socket:', e);
      this.onErrorCb?.(e);
      this.programarReconexion();
      return;
    }

    this.ws.onopen = () => {
      console.log('[WS] conectado');
      this.intentosReconexion = 0;
      this.ultimoPongRecibido = Date.now();
      this.iniciarHeartbeat();
      this.onConectadoCb?.();
    };

    this.ws.onmessage = (event) => {
      this.procesarMensaje(event.data);
    };

    this.ws.onerror = () => {
      // No logueamos el evento completo: es enorme y ruidoso.
      // El onclose que sigue ya da el código y motivo.
      this.onErrorCb?.(new Error('WS error'));
    }; 

    this.ws.onclose = (event) => {
      console.log('[WS] cerrado:', event.code, event.reason);
      this.limpiarTimers();
      this.ws = null;
      this.onDesconectadoCb?.(event.code, event.reason);

      if (this.reconectarActivo) {
        this.programarReconexion();
      }
    };
  }

  private procesarMensaje(data: unknown): void {
    if (typeof data !== 'string') return;

    let mensaje: MensajeWS;
    try {
      mensaje = JSON.parse(data);
    } catch {
      console.warn('[WS] mensaje no-JSON ignorado');
      return;
    }

    if (!mensaje || typeof mensaje.type !== 'string') {
      console.warn('[WS] mensaje sin type, ignorado');
      return;
    }

    // Interceptar pong: actualiza heartbeat, no lo propaga.
    if (mensaje.type === 'pong') {
      this.ultimoPongRecibido = Date.now();
      return;
    }

    // Interceptar error: llama al callback y también lo propaga.
    if (mensaje.type === 'error') {
      const payload = mensaje.data as PayloadError | undefined;
      console.warn('[WS] error del server:', payload?.message ?? 'sin mensaje');
    }

    this.onMensajeCb?.(mensaje);
  }

  private iniciarHeartbeat(): void {
    this.limpiarHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      // ¿Último pong dentro del timeout?
      const desdeUltimoPong = Date.now() - this.ultimoPongRecibido;
      if (desdeUltimoPong > WS_HEARTBEAT_TIMEOUT_SECONDS * 1000) {
        console.warn('[WS] heartbeat timeout, cerrando');
        if (this.ws) {
          try {
            this.ws.close(WS_CLOSE_CODES.GOING_AWAY, 'heartbeat timeout');
          } catch {
            // no-op
          }
        }
        return;
      }

      this.enviar({ type: 'ping' });
    }, WS_HEARTBEAT_INTERVAL_SECONDS * 1000);
  }

  private limpiarHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private limpiarTimers(): void {
    this.limpiarHeartbeat();
    if (this.timeoutReconexion) {
      clearTimeout(this.timeoutReconexion);
      this.timeoutReconexion = null;
    }
  }

  private programarReconexion(): void {
    if (!this.reconectarActivo) return;

    if (this.intentosReconexion >= MAX_INTENTOS_RECONEXION) {
      console.warn('[WS] máx intentos alcanzado, abandono');
      this.reconectarActivo = false;
      return;
    }

    const intento = this.intentosReconexion;
    this.intentosReconexion++;

    // Backoff exponencial con tope y jitter.
    const base = Math.min(BACKOFF_BASE_MS * 2 ** intento, BACKOFF_MAX_MS);
    const jitter = base * JITTER_PCT * (Math.random() * 2 - 1);
    const delay = Math.max(0, Math.round(base + jitter));

    console.log(
      `[WS] reconexión en ${delay}ms (intento ${this.intentosReconexion}/${MAX_INTENTOS_RECONEXION})`
    );

    this.timeoutReconexion = setTimeout(() => {
      this.timeoutReconexion = null;
      this.abrirSocket();
    }, delay);
  }
}

export const websocketService = new WebSocketService();