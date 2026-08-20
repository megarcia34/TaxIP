'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

// ============================================================
// TIPOS
// ============================================================

export interface DocumentoVehiculo {
  id: string
  tipo_documento: string
  numero: string
  fecha_emision: string | null
  fecha_vencimiento: string | null
  observaciones: string | null
  url_archivo: string | null
  created_at: string
  dias_para_vencer: number | null
  estado: 'vigente' | 'proximo' | 'vencido'
}

export interface DocumentoCreateData {
  tipo_documento: string
  numero: string
  fecha_emision?: string | null
  fecha_vencimiento: string
  observaciones?: string | null
  url_imagen?: string | null
}

// ============================================================
// HOOK: useDocumentos
// ============================================================

export function useDocumentos(vehiculoId?: string) {
  const [documentos, setDocumentos] = useState<DocumentoVehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargarDocumentos = useCallback(async (id?: string) => {
    const targetId = id || vehiculoId
    if (!targetId) {
      setDocumentos([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get(`/api/propietario/vehiculos/${targetId}/documentos`)
      setDocumentos(response.data || [])
    } catch (err: any) {
      console.error('Error cargando documentos:', err)
      setError(err.response?.data?.detail || 'Error al cargar documentos')
      setDocumentos([])
    } finally {
      setLoading(false)
    }
  }, [vehiculoId])

  // Subir documento
  const subirDocumento = useCallback(async (data: DocumentoCreateData) => {
    if (!vehiculoId) {
      toast.error('No hay vehículo seleccionado')
      throw new Error('No hay vehículo seleccionado')
    }

    try {
      const response = await apiClient.post(
        `/api/propietario/vehiculos/${vehiculoId}/documentos`,
        data
      )
      toast.success('Documento subido correctamente')
      await cargarDocumentos(vehiculoId)
      return response.data
    } catch (err: any) {
      const detail = err.response?.data?.detail
      toast.error(detail || 'Error al subir documento')
      throw err
    }
  }, [vehiculoId, cargarDocumentos])

  // Eliminar documento
  const eliminarDocumento = useCallback(async (documentoId: string) => {
    try {
      await apiClient.delete(`/api/propietario/vehiculos/documentos/${documentoId}`)
      toast.success('Documento eliminado correctamente')
      if (vehiculoId) {
        await cargarDocumentos(vehiculoId)
      }
      return true
    } catch (err: any) {
      const detail = err.response?.data?.detail
      toast.error(detail || 'Error al eliminar documento')
      throw err
    }
  }, [vehiculoId, cargarDocumentos])

  // Efecto inicial
  useEffect(() => {
    if (vehiculoId) {
      cargarDocumentos(vehiculoId)
    }
  }, [vehiculoId, cargarDocumentos])

  // Contar documentos por estado
  const total = documentos.length
  const vigentes = documentos.filter(d => d.estado === 'vigente').length
  const proximos = documentos.filter(d => d.estado === 'proximo').length
  const vencidos = documentos.filter(d => d.estado === 'vencido').length

  // Verificar si tiene documentos mínimos requeridos
  const tieneDocumentosRequeridos = useCallback(() => {
    const requeridos = ['SEGURO', 'VTV', 'CEDULA']
    const tiposExistentes = documentos.map(d => d.tipo_documento)
    return requeridos.every(r => tiposExistentes.includes(r))
  }, [documentos])

  // Obtener faltantes
  const getFaltantes = useCallback(() => {
    const requeridos = ['SEGURO', 'VTV', 'CEDULA']
    const tiposExistentes = documentos.map(d => d.tipo_documento)
    return requeridos.filter(r => !tiposExistentes.includes(r))
  }, [documentos])

  // Obtener documento por tipo
  const getByTipo = useCallback((tipo: string) => {
    return documentos.find(d => d.tipo_documento === tipo)
  }, [documentos])

  return {
    documentos,
    loading,
    error,
    total,
    vigentes,
    proximos,
    vencidos,
    cargarDocumentos,
    subirDocumento,
    eliminarDocumento,
    tieneDocumentosRequeridos,
    getFaltantes,
    getByTipo,
    recargar: cargarDocumentos
  }
}