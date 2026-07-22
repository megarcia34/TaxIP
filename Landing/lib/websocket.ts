// ============================================
// WEBSOCKET SERVICE
// ============================================

type MessageHandler = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private isConnecting = false;
  private userId: string | null = null;
  private bookingId: string | null = null;

  // ============================================
  // CONEXIÓN
  // ============================================
  connect(userId: string, bookingId?: string): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket ya está conectado o conectando');
      return;
    }

    this.userId = userId;
    this.bookingId = bookingId || null;
    this.isConnecting = true;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/ws/${userId}${bookingId ? `?booking_id=${bookingId}` : ''}`;
    
    console.log(`🔄 Conectando WebSocket a: ${url}`);

    try {
      this.ws = new WebSocket(url);
      this.setupEventListeners();
    } catch (error) {
      console.error('Error al conectar WebSocket:', error);
      this.isConnecting = false;
      this.handleReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('✅ WebSocket conectado');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected', { status: 'connected' });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Mensaje WebSocket recibido:', data);
        
        // Emitir evento según el tipo
        if (data.type) {
          this.emit(data.type, data);
        }
        // Si no tiene tipo, emitir como 'message'
        this.emit('message', data);
      } catch (error) {
        console.error('Error al parsear mensaje WebSocket:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`🔴 WebSocket cerrado: ${event.code} - ${event.reason}`);
      this.isConnecting = false;
      this.ws = null;
      
      if (event.code !== 1000) {
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ Error en WebSocket:', error);
      this.isConnecting = false;
    };
  }

  // ============================================
  // RECONEXIÓN
  // ============================================
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('❌ Máximos intentos de reconexión alcanzados');
      this.emit('error', { 
        message: 'No se pudo mantener la conexión con el servidor' 
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
    
    console.log(`🔄 Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.userId) {
        this.connect(this.userId, this.bookingId || undefined);
      }
    }, delay);
  }

  // ============================================
  // ENVÍO DE MENSAJES
  // ============================================
  send(data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket no está abierto, no se puede enviar mensaje');
      return;
    }

    const message = typeof data === 'string' ? data : JSON.stringify(data);
    this.ws.send(message);
  }

  // ============================================
  // EVENTOS
  // ============================================
  on(event: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, []);
    }
    this.messageHandlers.get(event)!.push(handler);
  }

  off(event: string, handler?: MessageHandler): void {
    if (!handler) {
      this.messageHandlers.delete(event);
      return;
    }
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any): void {
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error en handler de evento '${event}':`, error);
        }
      });
    }
  }

  // ============================================
  // DESCONEXIÓN
  // ============================================
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Desconexión manual');
      this.ws = null;
    }
    this.isConnecting = false;
    this.messageHandlers.clear();
    console.log('🔌 WebSocket desconectado manualmente');
  }

  // ============================================
  // ESTADO
  // ============================================
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  isConnectingState(): boolean {
    return this.isConnecting;
  }
}

// Instancia única (singleton)
export const wsService = new WebSocketService();

// ============================================
// HOOK PARA USAR WEBSOCKET
// ============================================
import { useState, useEffect, useRef } from 'react';

interface UseWebSocketOptions {
  userId: string | null;
  bookingId?: string;
  autoConnect?: boolean;
}

export function useWebSocket({ userId, bookingId, autoConnect = true }: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!userId || !autoConnect) return;

    const handleConnected = () => {
      if (mountedRef.current) {
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
      }
    };

    const handleMessage = (data: any) => {
      if (mountedRef.current) {
        setLastMessage(data);
      }
    };

    const handleError = (data: any) => {
      if (mountedRef.current) {
        setError(data.message || 'Error en WebSocket');
        setIsConnected(false);
        setIsConnecting(false);
      }
    };

    wsService.on('connected', handleConnected);
    wsService.on('message', handleMessage);
    wsService.on('error', handleError);

    setIsConnecting(true);
    wsService.connect(userId, bookingId);

    return () => {
      wsService.off('connected', handleConnected);
      wsService.off('message', handleMessage);
      wsService.off('error', handleError);
    };
  }, [userId, bookingId, autoConnect]);

  const sendMessage = (data: any) => {
    wsService.send(data);
  };

  const disconnect = () => {
    wsService.disconnect();
    setIsConnected(false);
    setIsConnecting(false);
  };

  return {
    isConnected,
    isConnecting,
    lastMessage,
    error,
    sendMessage,
    disconnect,
  };
}