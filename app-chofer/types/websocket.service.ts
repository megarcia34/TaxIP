/**
 * Servicio del Módulo 3 - WebSocket.
 *
 * STUB de Fase 9.2: solo la estructura. La conexión real se implementa en
 * Fase 9.3 (reconexión exponencial, heartbeat, integración con el store).
 *
 * Este service NO toca el store. Los callbacks son responsabilidad del
 * hook useWebSocket.
 */
import type { MensajeWS } from '@/types/websocket.types';

type MensajeCallback = (mensaje: MensajeWS) => void;
type ConectadoCallback = () => void;
type DesconectadoCallback = (code: number, reason: string) => void;
type ErrorCallback = (error: unknown) => void;

const PENDIENTE = '[WS] pendiente Fase 9.3';

class WebSocketService {
  private userId: string | null = null;
  private token: string | null = null;

  private onMensajeCb: MensajeCallback | null = null;
  private onConectadoCb: ConectadoCallback | null = null;
  private onDesconectadoCb: DesconectadoCallback | null = null;
  private onErrorCb: ErrorCallback | null = null;

  // ============================================================
  // CICLO DE CONEXIÓN
  // ============================================================
  conectar(userId: string, token: string): void {
    this.userId = userId;
    this.token = token;
    console.warn(PENDIENTE, 'conectar()');
  }

  desconectar(): void {
    this.userId = null;
    this.token = null;
    console.warn(PENDIENTE, 'desconectar()');
  }

  // ============================================================
  // ENVÍO
  // ============================================================
  enviar(mensaje: MensajeWS): void {
    console.warn(PENDIENTE, 'enviar()', mensaje.type);
  }

  // ============================================================
  // CALLBACKS
  // ============================================================
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

  // ============================================================
  // GETTERS DE ESTADO (para debug en Fase 9.3)
  // ============================================================
  estaConectado(): boolean {
    return false;
  }

  getUserId(): string | null {
    return this.userId;
  }
}

export const websocketService = new WebSocketService();