// ✅ CORREGIDO - Usa la ruta correcta
import { apiClient } from '../api'  // Apunta a lib/api.ts

export interface ResumenEjecutivo {
  vehiculo: {
    id: string
    patente: string
    marca: string
    modelo: string
    anio: number
    numero_licencia: string
    conductor_actual: string
    calificacion_promedio: number
    total_viajes_historico: number
  }
  periodo: {
    desde: string
    hasta: string
    nombre: string
  }
  viajes: {
    total: number
    km_recorridos: number
    horas_operacion: number
    ingreso_promedio_viaje: number
  }
  ingresos: {
    brutos: number
    comision_plataforma: number
    netos: number
  }
  gastos: {
    combustible: number
    mantenimiento: number
    seguro: number
    otros: number
    total: number
  }
  rentabilidad: {
    margen_neto: number
    roi: number
    margen_promedio: number
    costo_por_km: number
    ganancia_por_km: number
  }
  benchmarking: {
    ingresos_netos: {
      valor: number
      promedio_flota: number
      diferencia: number
      porcentaje: number
      comparativa: 'POR_ENCIMA' | 'POR_DEBAJO' | 'SIN_DATOS'
    }
    gastos: {
      valor: number
      promedio_flota: number
      diferencia: number
      porcentaje: number
      comparativa: 'POR_DEBAJO' | 'POR_ENCIMA' | 'SIN_DATOS'
    }
    viajes: {
      valor: number
      promedio_flota: number
      diferencia: number
    }
    puesto: number
    total_vehiculos: number
  }
  alertas: {
    ultimo_service: string | null
    ultimo_tipo: string
    proximo_service_estimado: string
    desgaste_neumaticos: number
    estado_neumaticos: 'CRITICO' | 'ALTO' | 'MEDIO' | 'BUENO'
  }
}

export interface Benchmarking {
  vehiculo: {
    id: string
    patente: string
  }
  periodo: {
    desde: string
    hasta: string
    nombre: string
  }
  posicion: {
    puesto: number
    total_vehiculos: number
    top_porcentaje: number
  }
  metricas: {
    ingresos_netos: {
      valor: number
      promedio_flota: number
      mediana_flota: number
      diferencia: number
      porcentaje_vs_promedio: number
      comparativa: 'POR_ENCIMA' | 'POR_DEBAJO' | 'SIN_DATOS'
    }
    gastos: {
      valor: number
      promedio_flota: number
      diferencia: number
      porcentaje_vs_promedio: number
      comparativa: 'POR_DEBAJO' | 'POR_ENCIMA' | 'SIN_DATOS'
    }
    viajes: {
      valor: number
      promedio_flota: number
      diferencia: number
    }
    kilometros: {
      valor: number
      promedio_flota: number
      diferencia: number
    }
    calificacion: {
      valor: number
      promedio_flota: number
      diferencia: number
    }
    roi: {
      valor: number
      promedio_flota: number
      diferencia: number
      comparativa: 'POR_ENCIMA' | 'POR_DEBAJO' | 'SIN_DATOS'
    }
  }
}

export interface CostoPorViaje {
  vehiculo_id: string
  periodo: {
    desde: string
    hasta: string
  }
  configuracion_costos: {
    combustible_por_km: number
    mantenimiento_por_dia: number
    seguro_por_dia: number
    impuesto_por_dia: number
    depreciacion_por_dia: number
  }
  viajes: {
    viaje_id: string
    fecha: string
    origen: string
    destino: string
    distancia_km: number
    duracion_minutos: number
    ingreso_bruto: number
    comision: number
    ingreso_neto: number
    costos: {
      combustible: number
      mantenimiento: number
      seguro: number
      impuesto: number
      depreciacion: number
      total: number
    }
    ganancia_neta: number
    margen: number
    estado: string
  }[]
  resumen: {
    total_viajes: number
    total_ingresos_brutos: number
    total_comisiones: number
    total_ingresos_netos: number
    total_costos: number
    total_ganancia_neta: number
    ganancia_promedio_por_viaje: number
    margen_promedio: number
  }
}

export interface RentabilidadPorZona {
  vehiculo_id: string
  periodo: {
    desde: string
    hasta: string
  }
  zonas: {
    zona: string
    total_viajes: number
    ingresos_brutos: number
    comisiones: number
    ingresos_netos: number
    costos_totales: number
    ganancia_neta: number
    distancia_promedio: number
    margen: number
    porcentaje_contribucion: number
  }[]
  resumen: {
    total_zonas: number
    total_viajes: number
    total_ganancia: number
    zona_mas_rentable: string | null
    zona_menos_rentable: string | null
  }
}

export interface UbicacionGPS {
  vehiculo_id: string
  ubicacion: {
    latitud: number
    longitud: number
    ultima_actualizacion: string
  }
  conductor: {
    email: string
    nombre: string
  }
  estado: {
    laboral: string
    ultima_conexion: string
    calificacion_promedio: number
  }
  viaje_actual: {
    id: string
    origen: string
    destino: string
    inicio: string
  } | null
}

export interface Alerta {
  id: string
  tipo: string
  vehiculo_patente: string
  conductor: string | null
  mensaje: string
  distancia_desvio: number | null
  ubicacion: {
    latitud: number
    longitud: number
  } | null
  fecha: string
  resuelto: boolean
  viaje_id: string | null
}

export interface AlertasResponse {
  total_alertas: number
  alertas: Alerta[]
}

// ============================================================
// SERVICIOS DEL MÓDULO PROPIETARIO
// ============================================================

export const propietarioReportesAPI = {
  getResumenEjecutivo: async (
    vehiculoId: string,
    periodo: 'dia' | 'semana' | 'mes' = 'mes'
  ): Promise<ResumenEjecutivo> => {
    const response = await apiClient.get(
      `/propietario/reportes/resumen-ejecutivo/${vehiculoId}?periodo=${periodo}`
    )
    return response.data
  },

  getBenchmarking: async (
    vehiculoId: string,
    periodo: 'dia' | 'semana' | 'mes' = 'mes'
  ): Promise<Benchmarking> => {
    const response = await apiClient.get(
      `/propietario/reportes/benchmarking/${vehiculoId}?periodo=${periodo}`
    )
    return response.data
  },

  getCostoPorViaje: async (
    vehiculoId: string,
    params?: {
      desde?: string
      hasta?: string
      limit?: number
    }
  ): Promise<CostoPorViaje> => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    if (params?.limit) queryParams.append('limit', String(params.limit))
    
    const url = `/propietario/costo-por-viaje/${vehiculoId}${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },

  getRentabilidadPorZona: async (
    vehiculoId: string,
    params?: {
      desde?: string
      hasta?: string
    }
  ): Promise<RentabilidadPorZona> => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    
    const url = `/propietario/rentabilidad-por-zona/${vehiculoId}${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
}

export const propietarioVehiculosAPI = {
  getUbicacion: async (vehiculoId: string): Promise<UbicacionGPS> => {
    const response = await apiClient.get(`/propietario/vehiculos/${vehiculoId}/ubicacion`)
    return response.data
  },

  getHistorialGPS: async (
    vehiculoId: string,
    params?: {
      desde?: string
      hasta?: string
      limit?: number
    }
  ): Promise<{
    vehiculo_id: string
    periodo: { desde: string; hasta: string }
    total_puntos: number
    puntos: {
      latitud: number
      longitud: number
      fecha: string
      viaje_id: string | null
      origen: string | null
      destino: string | null
    }[]
  }> => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    if (params?.limit) queryParams.append('limit', String(params.limit))
    
    const url = `/propietario/vehiculos/${vehiculoId}/historial-gps${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
}

export const propietarioAlertasAPI = {
  getActivas: async (vehiculoId?: string): Promise<AlertasResponse> => {
    const url = vehiculoId 
      ? `/propietario/alertas/activas?vehiculo_id=${vehiculoId}`
      : '/propietario/alertas/activas'
    const response = await apiClient.get(url)
    return response.data
  },

  resolver: async (alertaId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.put(`/propietario/alertas/${alertaId}/resolver`)
    return response.data
  },
}

export const propietarioFinanzasAPI = {
  getRentabilidad: async (
    params?: {
      vehiculo_id?: string
      periodo?: 'dia' | 'semana' | 'mes' | 'ano'
    }
  ): Promise<any> => {
    const queryParams = new URLSearchParams()
    if (params?.vehiculo_id) queryParams.append('vehiculo_id', params.vehiculo_id)
    if (params?.periodo) queryParams.append('periodo', params.periodo)
    
    const url = `/propietario/rentabilidad${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },

  getFlujoEfectivo: async (): Promise<any> => {
    const response = await apiClient.get('/propietario/flujo-efectivo')
    return response.data
  },

  getDeudaChoferes: async (): Promise<any> => {
    const response = await apiClient.get('/propietario/deuda-choferes')
    return response.data
  },
}