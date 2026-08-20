'use client'

import { useState, useEffect, useCallback } from 'react'
import { neumaticosAPI } from '@/lib/api'
import { toast } from 'sonner'
import { NeumaticosActivosResponse, ConfiguracionNeumaticos } from '@/lib/api/neumaticos'

// ✅ Validación de UUID
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

// ✅ Helper para crear estructura vacía de neumáticos
function crearEstructuraVacia(vehiculoId: string, patente: string = 'Sin vehículo', vehiculo_marca: string = '', vehiculo_modelo: string = ''): NeumaticosActivosResponse {
  return {
    vehiculo_id: vehiculoId,
    patente: patente,
    vehiculo_marca: vehiculo_marca,
    vehiculo_modelo: vehiculo_modelo,
    neumaticos: {
      DI: undefined,
      DD: undefined,
      TI: undefined,
      TD: undefined
    },
    resumen: {
      total_neumaticos: 0,
      estado_verde: 0,
      estado_amarillo: 0,
      estado_rojo: 0
    }
  }
}

export function useNeumaticos(vehiculoId?: string) {
  const [activos, setActivos] = useState<NeumaticosActivosResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [configuracion, setConfiguracion] = useState<ConfiguracionNeumaticos | null>(null)
  const [loadingConfig, setLoadingConfig] = useState(true)

  // Cargar neumáticos activos
  const cargarActivos = useCallback(async (id?: string) => {
    const targetId = id || vehiculoId
    
    // ✅ Validar que el ID sea un UUID válido
    if (!targetId || !UUID_REGEX.test(targetId)) {
      console.warn('⚠️ ID de vehículo inválido, no se cargan neumáticos:', targetId)
      setActivos(null)
      setLoading(false)
      return
    }
    
    setLoading(true)
    try {
      const data = await neumaticosAPI.getActivos(targetId)
      
      // Si no hay datos o no hay neumáticos, crear estructura vacía
      if (!data || !data.neumaticos || Object.keys(data.neumaticos).length === 0) {
        let patente = 'Sin vehículo'
        let vehiculo_marca = ''
        let vehiculo_modelo = ''
        
        try {
          if (data) {
            patente = data.patente || 'Sin vehículo'
            vehiculo_marca = data.vehiculo_marca || ''
            vehiculo_modelo = data.vehiculo_modelo || ''
          }
        } catch (e) {
          // Ignorar errores
        }
        
        setActivos(crearEstructuraVacia(targetId, patente, vehiculo_marca, vehiculo_modelo))
        setLoading(false)
        return
      }
      
      setActivos(data)
    } catch (error) {
      console.error('Error cargando neumáticos activos:', error)
      // Establecer estado vacío en caso de error
      setActivos(crearEstructuraVacia(targetId, 'Error al cargar', '', ''))
    } finally {
      setLoading(false)
    }
  }, [vehiculoId])

  // Cargar configuración
  const cargarConfiguracion = useCallback(async () => {
    setLoadingConfig(true)
    try {
      const data = await neumaticosAPI.getConfiguracion()
      setConfiguracion(data)
    } catch (error) {
      console.error('Error cargando configuración:', error)
    } finally {
      setLoadingConfig(false)
    }
  }, [])

  // Rotar neumáticos
  const rotar = useCallback(async (vehiculoId: string, km_vehiculo_actual: number, observaciones?: string) => {
    try {
      const result = await neumaticosAPI.rotar(vehiculoId, { km_vehiculo_actual, observaciones })
      await cargarActivos(vehiculoId)
      toast.success(result.message || 'Rotación realizada correctamente')
      return result
    } catch (error: any) {
      console.error('Error al rotar:', error)
      toast.error(error.response?.data?.detail || 'Error al rotar neumáticos')
      throw error
    }
  }, [cargarActivos])

  // Registrar medición
  const medir = useCallback(async (neumaticoId: string, profundidad_mm: number, observaciones?: string) => {
    try {
      const result = await neumaticosAPI.registrarMedicion(neumaticoId, { profundidad_mm, observaciones })
      toast.success(result.message || 'Medición registrada correctamente')
      return result
    } catch (error: any) {
      console.error('Error al registrar medición:', error)
      toast.error(error.response?.data?.detail || 'Error al registrar medición')
      throw error
    }
  }, [])

  // Desmontar neumático
  const desmontar = useCallback(async (neumaticoId: string, km_vehiculo_actual: number, motivo: string, observaciones?: string) => {
    try {
      const result = await neumaticosAPI.desmontar(neumaticoId, { km_vehiculo_actual, motivo, observaciones })
      toast.success(result.message || 'Neumático desmontado correctamente')
      return result
    } catch (error: any) {
      console.error('Error al desmontar:', error)
      toast.error(error.response?.data?.detail || 'Error al desmontar neumático')
      throw error
    }
  }, [])

  // Cambiar estado
  const cambiarEstado = useCallback(async (neumaticoId: string, estado: 'BAJA' | 'DESECHADO', motivo?: string, observaciones?: string) => {
    try {
      const result = await neumaticosAPI.cambiarEstado(neumaticoId, { estado, motivo, observaciones })
      toast.success(result.message || `Estado cambiado a ${estado}`)
      return result
    } catch (error: any) {
      console.error('Error al cambiar estado:', error)
      toast.error(error.response?.data?.detail || 'Error al cambiar estado')
      throw error
    }
  }, [])

  // Montar neumáticos
  const montar = useCallback(async (vehiculoId: string, data: any) => {
    try {
      const result = await neumaticosAPI.montar(vehiculoId, data)
      await cargarActivos(vehiculoId)
      toast.success(result.message || 'Neumáticos montados correctamente')
      return result
    } catch (error: any) {
      console.error('Error al montar:', error)
      toast.error(error.response?.data?.detail || 'Error al montar neumáticos')
      throw error
    }
  }, [cargarActivos])

  // Recargar todo
  const recargar = useCallback(async (id?: string) => {
    const targetId = id || vehiculoId
    
    // ✅ Validar antes de recargar
    if (targetId && UUID_REGEX.test(targetId)) {
      await Promise.all([
        cargarActivos(targetId),
        cargarConfiguracion()
      ])
    } else {
      console.warn('⚠️ No se puede recargar: ID de vehículo inválido')
    }
  }, [vehiculoId, cargarActivos, cargarConfiguracion])

  // Efecto inicial
  useEffect(() => {
    if (vehiculoId && UUID_REGEX.test(vehiculoId)) {
      cargarActivos(vehiculoId)
    } else {
      setLoading(false)
    }
    cargarConfiguracion()
  }, [vehiculoId, cargarActivos, cargarConfiguracion])

  return {
    activos,
    loading,
    configuracion,
    loadingConfig,
    cargarActivos,
    cargarConfiguracion,
    rotar,
    medir,
    desmontar,
    cambiarEstado,
    montar,
    recargar
  }
}