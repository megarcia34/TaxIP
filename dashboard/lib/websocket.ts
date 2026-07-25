'use client'

class WebSocketClient {
  private socket: WebSocket | null = null
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(userId: string, token: string) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return
    }

    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    this.socket = new WebSocket(`${WS_URL}/ws/${userId}`)

    this.socket.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      // Enviar rol (admin/observador)
      this.send({ type: 'set_role', data: { role: 'admin' } })
      this.emitEvent('connected', {})
    }

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emitEvent('error', error)
    }

    this.socket.onclose = () => {
      console.log('WebSocket disconnected')
      this.emitEvent('disconnected', {})
      this.attemptReconnect(userId, token)
    }
  }

  private attemptReconnect(userId: string, token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
        this.connect(userId, token)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  private handleMessage(message: any) {
    const eventMap: Record<string, string> = {
      'driver_location_update': 'chofer_location_update',
      'new_trip_request': 'nueva_solicitud',
      'trip_accepted': 'solicitud_aceptada',
      'trip_cancelled': 'viaje_cancelado',
      'panic_alert': 'alerta_panico',
      'driver_status_change': 'chofer_status_change',
    }

    const eventType = eventMap[message.type] || message.type
    this.emitEvent(eventType, message.data || message)
  }

  send(message: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    }
  }

  private emitEvent(event: string, data: any) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach((callback) => callback(data))
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)?.add(callback)
  }

  off(event: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.delete(callback)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new WebSocketClient()