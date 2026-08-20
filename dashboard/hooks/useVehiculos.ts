'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

export interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  anio: number | null
  numero_licencia: string | null
  chofer_asignado: string | null
  estado_laboral: string
}

// ============================================================
// HOOK: useVehiculos (LISTADO)
// ============================================================

export function useVehiculos() {
  const [data, setData] = useState<Vehiculo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.get('/api/propietario/vehiculos')
      setData(response.data || [])
    } catch (err: any) {
      setError(err)
      console.error('Error cargando vehículos:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, isLoading, error, refetch }
}

// ============================================================
// HOOK: useVehiculo (DETALLE)
// ============================================================

export function useVehiculo(id: string | undefined) {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!id) {
      setIsLoading(false)
      return
    }

    const fetchVehiculo = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await apiClient.get(`/api/propietario/vehiculos/${id}`)
        setData(response.data)
      } catch (err: any) {
        setError(err)
        console.error('Error cargando vehículo:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchVehiculo()
  }, [id])

  return { data, isLoading, error }
}

// ============================================================
// MUTATION: useCreateVehiculo
// ============================================================

export function useCreateVehiculo() {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const mutate = useCallback(
    async (data: any, options?: { onSuccess?: (data: any) => void; onError?: (error: any) => void }) => {
      setIsPending(true)
      setError(null)
      try {
        const response = await apiClient.post('/api/propietario/vehiculos', {
          patente: data.patente.toUpperCase(),
          marca: data.marca,
          modelo: data.modelo,
          anio: data.anio || null,
          numero_licencia: data.numero_licencia || null,
        })
        toast.success('Vehículo creado correctamente')
        if (options?.onSuccess) options.onSuccess(response.data)
        return response.data
      } catch (err: any) {
        const detail = err.response?.data?.detail
        if (Array.isArray(detail)) {
          toast.error(detail.map((d: any) => d.msg).join(', '))
        } else {
          toast.error(detail || 'Error al crear el vehículo')
        }
        if (options?.onError) options.onError(err)
        throw err
      } finally {
        setIsPending(false)
      }
    },
    []
  )

  const mutateAsync = useCallback(
    async (data: any) => {
      return mutate(data)
    },
    [mutate]
  )

  return { mutate, mutateAsync, isPending, error }
}

// ============================================================
// MUTATION: useUpdateVehiculo
// ============================================================

export function useUpdateVehiculo() {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const mutate = useCallback(
    async (params: { id: string; data: any }, options?: { onSuccess?: (data: any) => void; onError?: (error: any) => void }) => {
      setIsPending(true)
      setError(null)
      try {
        const response = await apiClient.put(`/api/propietario/vehiculos/${params.id}`, {
          patente: params.data.patente?.toUpperCase(),
          marca: params.data.marca,
          modelo: params.data.modelo,
          anio: params.data.anio || null,
          numero_licencia: params.data.numero_licencia || null,
        })
        toast.success('Vehículo actualizado correctamente')
        if (options?.onSuccess) options.onSuccess(response.data)
        return response.data
      } catch (err: any) {
        const detail = err.response?.data?.detail
        if (Array.isArray(detail)) {
          toast.error(detail.map((d: any) => d.msg).join(', '))
        } else {
          toast.error(detail || 'Error al actualizar el vehículo')
        }
        if (options?.onError) options.onError(err)
        throw err
      } finally {
        setIsPending(false)
      }
    },
    []
  )

  const mutateAsync = useCallback(
    async (params: { id: string; data: any }) => {
      return mutate(params)
    },
    [mutate]
  )

  return { mutate, mutateAsync, isPending, error }
}

// ============================================================
// MUTATION: useDeleteVehiculo
// ============================================================

export function useDeleteVehiculo() {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const mutate = useCallback(
    async (id: string, options?: { onSuccess?: () => void; onError?: (error: any) => void }) => {
      setIsPending(true)
      setError(null)
      try {
        await apiClient.delete(`/api/propietario/vehiculos/${id}`)
        toast.success('Vehículo eliminado correctamente')
        if (options?.onSuccess) options.onSuccess()
        return id
      } catch (err: any) {
        const detail = err.response?.data?.detail
        toast.error(detail || 'Error al eliminar el vehículo')
        if (options?.onError) options.onError(err)
        throw err
      } finally {
        setIsPending(false)
      }
    },
    []
  )

  const mutateAsync = useCallback(
    async (id: string) => {
      return mutate(id)
    },
    [mutate]
  )

  return { mutate, mutateAsync, isPending, error }
}