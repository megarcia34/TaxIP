// hooks/useMapWebSocket.ts
'use client'

import { useEffect, useState, useRef } from 'react'
import { useSession } from 'next-auth/react'  // ✅ CORREGIDO
import { wsClient } from '@/lib/websocket'

interface Chofer {
  id: string
  nombre: string
  patente: string
  latitud: number
  longitud: number
  estado: string
  calificacion: number
}

export function useMapWebSocket() {
  const { data: session } = useSession()
  const [isConnected, setIsConnected] = useState(false)
  const [choferes, setChoferes] = useState<Chofer[]>([])
  const isMounted = useRef(true)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  // Conectar al WebSocket
  useEffect(() => {
    if (!session?.user?.id) return

    const userId = session.user.id
    // ✅ CORREGIDO: session.user?.accessToken
    const token = session.user?.accessToken

    if (!token) {
      console.warn('⚠️ No hay token de acceso para WebSocket')
      return
    }

    // Función para conectar
    const connect = () => {
      if (!isMounted.current) return
      
      // Verificar si ya está conectado
      if (wsClient.isConnected()) {
        setIsConnected(true)
        return
      }

      // Conectar WebSocket
      wsClient.connect(userId, token)
      
      // Escuchar eventos
      wsClient.on('connected', () => {
        if (isMounted.current) {
          setIsConnected(true)
          console.log('✅ WebSocket conectado')
        }
      })

      wsClient.on('chofer_location_update', (data: any) => {
        if (isMounted.current) {
          setChoferes((prev) => {
            const index = prev.findIndex(c => c.id === data.chofer_id)
            if (index === -1) {
              // Nuevo chofer
              return [...prev, {
                id: data.chofer_id,
                nombre: data.nombre || 'Chofer',
                patente: data.patente || 'N/A',
                latitud: data.latitud,
                longitud: data.longitud,
                estado: data.estado || 'libre',
                calificacion: data.calificacion || 0
              }]
            } else {
              // Actualizar chofer
              const updated = [...prev]
              updated[index] = {
                ...updated[index],
                latitud: data.latitud,
                longitud: data.longitud,
                estado: data.estado || updated[index].estado
              }
              return updated
            }
          })
        }
      })

      wsClient.on('disconnected', () => {
        if (isMounted.current) {
          setIsConnected(false)
          console.warn('⚠️ WebSocket desconectado, reconectando...')
          // Intentar reconectar después de 3 segundos
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMounted.current) {
              connect()
            }
          }, 3000)
        }
      })
    }

    connect()

    // Cleanup al desmontar
    return () => {
      isMounted.current = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      // No desconectar el WebSocket global, solo limpiar listeners
      // El WebSocket sigue vivo para otros componentes
      wsClient.off('connected', () => {})
      wsClient.off('chofer_location_update', () => {})
      wsClient.off('disconnected', () => {})
    }
  }, [session])

  return { choferes, isConnected }
}