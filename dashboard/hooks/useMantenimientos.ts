'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

// ============================================================
// TIPOS
// ============================================================

export interface MantenimientoVehiculo {
  id: string
  vehiculo_id: string
  vehiculo_patente: string
  tipo_servicio: string
  taller_nombre: string | null
  taller_direccion: string | null
  costo: number | null
  kilometraje: number | null
  observaciones: string | null
  fecha_servicio: string
  created_at: string
}

export interface MantenimientoCreateData {
  vehiculo_id: string
  tipo_servicio: string
  taller_nombre?: string | null
  taller_direccion?: string | null
  costo?: number | null
  kilometraje?: number | null
  observaciones?: string | null
  fecha_servicio: string
}

// Tipos de mantenimiento predefinidos
export const TIPOS_MANTENIMIENTO = [
  { value: 'SERVICE_MENOR', label: 'Service Menor' },
  { value: 'SERVICE_MAYOR', label: 'Service Mayor' },
  { value: 'CAMBIO_ACEITE', label: 'Cambio de Aceite' },
  { value: 'NEUMATICOS', label: 'Neumáticos' },
  { value: 'FRENOS', label: 'Frenos' },
  { value: 'DISTRIBUCION', label: 'Distribución' },
  { value: 'ALINEACION', label: 'Alineación' },
  { value: 'LUBRICACION', label: 'Lubricación' },
  { value: 'ELECTRICO', label: 'Eléctrico' },
  { value: 'GENERAL', label: 'General' },
]

// ============================================================
// HOOK: useMantenimientos
// ============================================================

export function useMantenimientos(vehiculoId?: string) {
  const [mantenimientos, setMantenimientos] = useState<MantenimientoVehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargarMantenimientos = useCallback(async (id?: string) => {
    const targetId = id || vehiculoId
    if (!targetId) {
      setMantenimientos([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.append('vehiculo_id', targetId)
      params.append('limit', '50')
      
      const response = await apiClient.get(`/api/propietario/mantenimientos?${params.toString()}`)
      setMantenimientos(response.data || [])
    } catch (err: any) {
      console.error('Error cargando mantenimientos:', err)
      setError(err.response?.data?.detail || 'Error al cargar mantenimientos')
      setMantenimientos([])
    } finally {
      setLoading(false)
    }
  }, [vehiculoId])

  // Registrar mantenimiento
  const registrarMantenimiento = useCallback(async (data: MantenimientoCreateData) => {
    try {
      const response = await apiClient.post('/api/propietario/mantenimiento', data)
      toast.success('Mantenimiento registrado correctamente')
      if (vehiculoId) {
        await cargarMantenimientos(vehiculoId)
      }
      return response.data
    } catch (err: any) {
      const detail = err.response?.data?.detail
      toast.error(detail || 'Error al registrar mantenimiento')
      throw err
    }
  }, [vehiculoId, cargarMantenimientos])

  // Eliminar mantenimiento (si el endpoint existe)
  const eliminarMantenimiento = useCallback(async (mantenimientoId: string) => {
    try {
      // Nota: Verificar si existe el endpoint DELETE
      await apiClient.delete(`/api/propietario/mantenimientos/${mantenimientoId}`)
      toast.success('Mantenimiento eliminado correctamente')
      if (vehiculoId) {
        await cargarMantenimientos(vehiculoId)
      }
      return true
    } catch (err: any) {
      const detail = err.response?.data?.detail
      toast.error(detail || 'Error al eliminar mantenimiento')
      throw err
    }
  }, [vehiculoId, cargarMantenimientos])

  // Efecto inicial
  useEffect(() => {
    if (vehiculoId) {
      cargarMantenimientos(vehiculoId)
    }
  }, [vehiculoId, cargarMantenimientos])

  // Obtener mantenimiento por tipo
  const getByTipo = useCallback((tipo: string) => {
    return mantenimientos.find(m => m.tipo_servicio === tipo)
  }, [mantenimientos])

  // Último mantenimiento
  const ultimo = mantenimientos.length > 0 ? mantenimientos[0] : null

  // Total de mantenimientos
  const total = mantenimientos.length

  return {
    mantenimientos,
    loading,
    error,
    total,
    ultimo,
    cargarMantenimientos,
    registrarMantenimiento,
    eliminarMantenimiento,
    getByTipo,
    recargar: cargarMantenimientos
  }
}