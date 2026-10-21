// D:\aTaxip\dashboard\hooks\useDocumentos.ts
'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'  // <-- modular (baseURL con /api)
import { formatApiError } from '@/lib/utils'
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
  archivo: File
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
      // SIN /api/ (el baseURL ya lo incluye)
      const response = await apiClient.get(`/propietario/vehiculos/${targetId}/documentos`)
      
      // Calcular dias_para_vencer y estado para que se pinten los colores
      const hoy = new Date()
      hoy.setHours(0, 0, 0, 0)

      const documentosEnriquecidos = (response.data || []).map((d: any) => {
        let dias_para_vencer = null
        let estado: 'vigente' | 'proximo' | 'vencido' = 'vigente'

        if (d.fecha_vencimiento) {
          const vencimiento = new Date(d.fecha_vencimiento)
          vencimiento.setHours(0, 0, 0, 0)
          
          // Diferencia en dias
          const diffTime = vencimiento.getTime() - hoy.getTime()
          dias_para_vencer = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          
          // Regla de colores: Vencido (rojo) / Proximo (amarillo, <=30 dias) / Vigente (verde)
          if (dias_para_vencer < 0) estado = 'vencido'
          else if (dias_para_vencer <= 30) estado = 'proximo'
          else estado = 'vigente'
        }

        return { ...d, dias_para_vencer, estado }
      })

      setDocumentos(documentosEnriquecidos)
    } catch (err: any) {
      console.error('Error cargando documentos:', err)
      setError(formatApiError(err))
      setDocumentos([])
    } finally {
      setLoading(false)
    }
  }, [vehiculoId])

  // Subir documento (MULTIPART)
  const subirDocumento = useCallback(async (data: DocumentoCreateData) => {
    if (!vehiculoId) {
      toast.error('No hay vehiculo seleccionado')
      throw new Error('No hay vehiculo seleccionado')
    }

    try {
      const formData = new FormData()
      formData.append('tipo_documento', data.tipo_documento)
      formData.append('numero', data.numero)
      formData.append('fecha_vencimiento', data.fecha_vencimiento)
      if (data.fecha_emision) formData.append('fecha_emision', data.fecha_emision)
      if (data.observaciones) formData.append('observaciones', data.observaciones)
      formData.append('file', data.archivo)

      // SIN /api/ (el baseURL ya lo incluye)
      const response = await apiClient.post(
        `/propietario/vehiculos/${vehiculoId}/documentos`,
        formData
      )
      toast.success('Documento subido correctamente')
      await cargarDocumentos(vehiculoId)
      return response.data
    } catch (err: any) {
      toast.error(formatApiError(err))
      throw err
    }
  }, [vehiculoId, cargarDocumentos])

  // Eliminar documento
  const eliminarDocumento = useCallback(async (documentoId: string) => {
    try {
      // SIN /api/ (el baseURL ya lo incluye)
      await apiClient.delete(`/propietario/vehiculos/documentos/${documentoId}`)
      toast.success('Documento eliminado correctamente')
      if (vehiculoId) {
        await cargarDocumentos(vehiculoId)
      }
      return true
    } catch (err: any) {
      toast.error(formatApiError(err))
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

  // Verificar si tiene documentos minimos requeridos
  const tieneDocumentosRequeridos = useCallback(() => {
    const requeridos = ['SEGURO', 'VTV', 'CEDULA_VERDE', 'HABILITACION']
    const tiposExistentes = documentos.map(d => d.tipo_documento)
    return requeridos.every(r => tiposExistentes.includes(r))
  }, [documentos])

  // Obtener faltantes
  const getFaltantes = useCallback(() => {
    const requeridos = ['SEGURO', 'VTV', 'CEDULA_VERDE', 'HABILITACION']
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