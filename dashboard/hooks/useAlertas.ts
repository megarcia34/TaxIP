'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'

interface AlertasResponse {
  conteos: {
    vencido: number
    critico: number
    urgente: number
    preventivo: number
    vigente: number
    total: number
  }
  alertas: any[]
  todas: any[]
}

export function useAlertas() {
  const [alertas, setAlertas] = useState<AlertasResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [totalUrgentes, setTotalUrgentes] = useState(0)

  const cargarAlertas = async () => {
    setLoading(true)
    try {
      // ✅ CORREGIDO: endpoint correcto
      const res = await apiClient.get('/api/propietario/documentos/vencimientos?dias_previos=30')
      
      // Transformar respuesta al formato esperado por el frontend
      const alertasData = res.data || []
      
      // Calcular conteos
      const conteos = {
        vencido: alertasData.filter((a: any) => a.dias_restantes < 0).length,
        critico: alertasData.filter((a: any) => a.dias_restantes >= 0 && a.dias_restantes <= 7).length,
        urgente: alertasData.filter((a: any) => a.dias_restantes > 7 && a.dias_restantes <= 15).length,
        preventivo: alertasData.filter((a: any) => a.dias_restantes > 15 && a.dias_restantes <= 30).length,
        vigente: alertasData.filter((a: any) => a.dias_restantes > 30).length,
        total: alertasData.length
      }
      
      // Alertas urgentes (vencidos, críticos y urgentes)
      const alertasUrgentes = alertasData.filter(
        (a: any) => a.dias_restantes <= 15
      )
      
      setAlertas({
        conteos,
        alertas: alertasUrgentes,
        todas: alertasData
      })
      
      const total = conteos.vencido + conteos.critico + conteos.urgente
      setTotalUrgentes(total)
      
    } catch (error) {
      console.error('Error cargando alertas:', error)
      setTotalUrgentes(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarAlertas()
    
    // Recargar cada 60 segundos
    const interval = setInterval(cargarAlertas, 60000)
    
    return () => clearInterval(interval)
  }, [])

  return {
    alertas,
    loading,
    totalUrgentes,
    recargar: cargarAlertas
  }
}