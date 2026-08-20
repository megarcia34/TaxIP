'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'
import { Vehiculo } from '@/types'

export function useVehiculos() {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargarVehiculos = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get('/api/propietario/vehiculos')
      const data = response.data || []
      setVehiculos(data)
    } catch (err: any) {
      console.error('Error cargando vehículos:', err)
      setError(err.response?.data?.detail || 'Error al cargar vehículos')
    } finally {
      setLoading(false)
    }
  }, [])

  const recargar = useCallback(() => {
    return cargarVehiculos()
  }, [cargarVehiculos])

  // Cargar al montar
  useEffect(() => {
    cargarVehiculos()
  }, [cargarVehiculos])

  return {
    vehiculos,
    loading,
    error,
    recargar,
    // Utilidades
    getVehiculoById: useCallback((id: string) => {
      return vehiculos.find(v => v.id === id)
    }, [vehiculos]),
    getVehiculoByPatente: useCallback((patente: string) => {
      return vehiculos.find(v => v.patente?.toUpperCase() === patente.toUpperCase())
    }, [vehiculos]),
  }
}