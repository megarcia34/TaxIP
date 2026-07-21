'use client'

import { useEffect, useCallback, useRef } from 'react'
import { useSession } from 'next-auth/react'
import { wsClient } from '@/lib/websocket'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

type WebSocketEvent = 
  | 'chofer_location_update'
  | 'nueva_solicitud'
  | 'solicitud_aceptada'
  | 'viaje_cancelado'
  | 'alerta_panico'
  | 'chofer_status_change'
  | 'connected'
  | 'disconnected'
  | 'error'

export function useWebSocket() {
  const { data: session, status } = useSession()
  const queryClient = useQueryClient()
  const isConnected = useRef(false)

  const connect = useCallback(() => {
    if (status === 'authenticated' && session?.user?.id && session?.user?.accessToken) {
      wsClient.connect(session.user.id, session.user.accessToken)
      isConnected.current = true
    }
  }, [status, session])

  const disconnect = useCallback(() => {
    wsClient.disconnect()
    isConnected.current = false
  }, [])

  useEffect(() => {
    if (status === 'authenticated') {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [status, connect, disconnect])

  // Manejar eventos de ubicación de choferes
  useEffect(() => {
    const handleLocationUpdate = (data: any) => {
      // Actualizar el caché de choferes online
      queryClient.setQueryData(['choferes-online'], (oldData: any) => {
        if (!oldData) return oldData
        const updated = oldData.map((chofer: any) => {
          if (chofer.id === data.chofer_id) {
            return { ...chofer, latitud: data.latitud, longitud: data.longitud }
          }
          return chofer
        })
        return updated
      })
    }

    const handleNuevaSolicitud = (data: any) => {
      toast.info(`Nueva solicitud de viaje`, {
        description: `Origen: ${data.origen}`,
        duration: 5000,
        action: {
          label: 'Ver',
          onClick: () => {
            window.location.href = `/viajes/${data.id}`
          },
        },
      })
      // Invalidar caché de solicitudes activas
      queryClient.invalidateQueries({ queryKey: ['solicitudes-activas'] })
    }

    const handleAlertaPanico = (data: any) => {
      toast.error(`⚠️ ALERTA DE PÁNICO`, {
        description: `Chofer: ${data.chofer_nombre} | Ubicación: ${data.latitud}, ${data.longitud}`,
        duration: 10000,
        action: {
          label: 'Ver en mapa',
          onClick: () => {
            // Centrar mapa en la ubicación
            window.dispatchEvent(new CustomEvent('center-map', { detail: { lat: data.latitud, lng: data.longitud } }))
          },
        },
      })
    }

    const handleChoferStatusChange = (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['choferes-online'] })
      queryClient.invalidateQueries({ queryKey: ['estadisticas'] })
    }

    wsClient.on('chofer_location_update', handleLocationUpdate)
    wsClient.on('nueva_solicitud', handleNuevaSolicitud)
    wsClient.on('alerta_panico', handleAlertaPanico)
    wsClient.on('chofer_status_change', handleChoferStatusChange)

    return () => {
      wsClient.off('chofer_location_update', handleLocationUpdate)
      wsClient.off('nueva_solicitud', handleNuevaSolicitud)
      wsClient.off('alerta_panico', handleAlertaPanico)
      wsClient.off('chofer_status_change', handleChoferStatusChange)
    }
  }, [queryClient])

  return {
    isConnected: isConnected.current && wsClient.isConnected(),
    connect,
    disconnect,
  }
}