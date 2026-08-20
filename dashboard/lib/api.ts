import axios from 'axios'
import { getSession } from 'next-auth/react'

// ✅ URL base sin /api (los endpoints lo incluyen)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export { neumaticosAPI } from './api/neumaticos';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================
// INTERCEPTOR DE REQUEST (CON CACHE DE TOKEN)
// ============================================

let cachedToken: string | null = null
let tokenExpiry: number | null = null

apiClient.interceptors.request.use(async (config) => {
  // ✅ Si el token está en cache y no ha expirado, usarlo
  if (cachedToken && tokenExpiry && Date.now() < tokenExpiry) {
    config.headers.Authorization = `Bearer ${cachedToken}`
    return config
  }

  const session = await getSession()
  if (session?.user?.accessToken) {
    cachedToken = session.user.accessToken
    tokenExpiry = Date.now() + 3600000 // 1 hora
    config.headers.Authorization = `Bearer ${cachedToken}`
  }
  return config
})

// ============================================
// INTERCEPTOR DE RESPONSE (CON IS_REFRESHING)
// ============================================

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function onRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // ✅ Si es 401 y no hemos reintentado
    if (error.response?.status === 401 && !originalRequest._retry) {
      // ✅ Si ya está refrescando, encolar la petición
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshSubscribers.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          })
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const session = await getSession()
        if (session?.user?.accessToken) {
          cachedToken = session.user.accessToken
          tokenExpiry = Date.now() + 3600000
          
          // Notificar a los suscriptores
          onRefreshed(cachedToken)
          
          originalRequest.headers.Authorization = `Bearer ${cachedToken}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Si no se puede renovar, redirigir a login
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    // ✅ Logs de errores
    if (error.response?.status === 422) {
      console.warn('⚠️ 422 Validation Error:', error.config?.url)
      console.warn('📋 Detalles:', error.response?.data)
    }
    if (error.response?.status === 500) {
      console.error('🔴 500 Internal Server Error:', error.config?.url)
    }
    
    return Promise.reject(error)
  }
)

// ============================================
// TIPOS
// ============================================

export interface User {
  id: string
  email: string
  nombre: string
  rol: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// ============================================
// AUTH API
// ============================================

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', {
      email,
      password,
    })
    return response.data
  },
  getProfile: async () => {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },
}

// ============================================
// CONTROL BASE API
// ============================================

export const controlBaseAPI = {
  getChoferesOnline: async () => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get('/api/control-base/choferes-online')
      return response.data
    }
    return []
  },
  getSolicitudesActivas: async () => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get('/api/control-base/solicitudes-activas')
      return response.data
    }
    return []
  },
  getEstadisticas: async () => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get('/api/control-base/estadisticas')
      return response.data
    }
    return {}
  },
  getRankingChoferes: async (limit: number = 10, criterio: string = 'calificacion') => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get(`/api/control-base/ranking-choferes?limit=${limit}&criterio=${criterio}`)
      return response.data
    }
    return []
  },
  getDatosEmpresa: async () => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get('/api/control-base/datos')
      return response.data
    }
    return null
  },
  actualizarEmpresa: async (data: any) => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.put('/api/control-base/actualizar', data)
      return response.data
    }
    throw new Error('No tienes permisos para actualizar la empresa')
  },
}

// ============================================
// PROPIETARIO API (ÚNICA DEFINICIÓN)
// ============================================

export const propietarioAPI = {
  getVehiculos: async () => {
    const response = await apiClient.get('/api/propietario/vehiculos')
    return response.data
  },
  registrarGasto: async (data: any) => {
    const response = await apiClient.post('/api/propietario/gasto', data)
    return response.data
  },
  registrarMantenimiento: async (data: any) => {
    const response = await apiClient.post('/api/propietario/mantenimiento', data)
    return response.data
  },
  getResumenGastos: async (desde?: string, hasta?: string) => {
    const params = new URLSearchParams()
    if (desde) params.append('desde', desde)
    if (hasta) params.append('hasta', hasta)
    const url = `/api/propietario/gastos/resumen${params.toString() ? '?' + params.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getContratos: async (activo?: boolean) => {
    const params = new URLSearchParams()
    if (activo !== undefined) params.append('activo', String(activo))
    const url = `/api/propietario/contratos${params.toString() ? '?' + params.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  createContrato: async (data: any) => {
    const response = await apiClient.post('/api/propietario/contratos', data)
    return response.data
  },
  finalizarContrato: async (id: string) => {
    const response = await apiClient.put(`/api/propietario/contratos/${id}/finalizar`)
    return response.data
  },
  getChoferesDisponibles: async (horaInicio: string = '06:00', horaFin: string = '14:00') => {
    const response = await apiClient.get(`/api/propietario/choferes/disponibles?hora_inicio=${horaInicio}&hora_fin=${horaFin}`)
    return response.data
  },
  getAll: async (params?: { search?: string; estado?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.search) queryParams.append('search', params.search)
    if (params?.estado) queryParams.append('estado', params.estado)
    const url = `/api/admin/propietarios${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getOne: async (id: string) => {
    const response = await apiClient.get(`/api/admin/propietarios/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post('/api/auth/registro', {
      email: data.email,
      password: data.password,
      nombre: data.nombre,
      apellido: data.apellido,
      telefono: data.telefono,
      tipo: 'propietario'
    })
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/admin/propietarios/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/admin/propietarios/${id}`)
    return response.data
  },
  // ✅ Método para configurar contrato pendiente
  configurarContrato: async (contratoId: string, data: any) => {
    const response = await apiClient.post(`/api/propietario/contratos/${contratoId}/configurar`, data)
    return response.data
  },
}

// ============================================
// HELPER PARA OBTENER HEADERS (ÚNICA DEFINICIÓN)
// ============================================

export async function getAuthHeaders() {
  const sessionRes = await fetch('/api/auth/session')
  const session = await sessionRes.json()
  
  const headers: HeadersInit = {
    'Authorization': `Bearer ${session?.user?.accessToken}`,
    'Content-Type': 'application/json',
  }
  
  if (session?.user?.role === 'admin') {
    const propietarioId = localStorage.getItem('selectedPropietarioId')
    if (propietarioId) {
      headers['X-Propietario-ID'] = propietarioId
    }
  }
  
  return headers
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const headers = await getAuthHeaders()
  return fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  })
}

// ============================================
// CHOFERES API
// ============================================

export const choferesAPI = {
  getAll: async () => {
    const response = await apiClient.get('/api/choferes/lista')
    return response.data
  },
  getOne: async (id: string) => {
    const response = await apiClient.get(`/api/choferes/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post('/api/auth/registro', {
      email: data.email,
      password: data.password,
      nombre: data.nombre,
      apellido: data.apellido,
      telefono: data.telefono,
      tipo: 'chofer'
    })
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/choferes/modificar/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/choferes/eliminar/${id}`)
    return response.data
  },
  actualizarUbicacion: async (data: { latitud: number; longitud: number }) => {
    const response = await apiClient.post('/api/choferes/actualizar-ubicacion', data)
    return response.data
  },
  cambiarEstado: async (data: { estado: string }) => {
    const response = await apiClient.post('/api/choferes/cambiar-estado', data)
    return response.data
  },
}

// ============================================
// VIAJES API
// ============================================

export const viajesAPI = {
  getEstado: async (id: string) => {
    const response = await apiClient.get(`/api/viajes/${id}/estado`)
    return response.data
  },
  getHistorial: async () => {
    const response = await apiClient.get('/api/viajes/historial')
    return response.data.viajes || []
  },
  getHistorialCompleto: async () => {
    const response = await apiClient.get('/api/viajes/historial')
    return response.data
  },
  getHistorialChofer: async (id: string) => {
    const response = await apiClient.get(`/api/choferes/${id}/viajes`)
    return response.data
  },
  getHistorialPasajero: async (id: string) => {
    const response = await apiClient.get(`/api/usuarios/${id}/viajes`)
    return response.data
  },
  getListadoSolicitudes: async () => {
    const session = await getSession()
    if (session?.user?.role === 'admin') {
      const response = await apiClient.get('/api/control-base/solicitudes-activas')
      return response.data
    }
    return []
  },
  solicitar: async (data: any) => {
    const response = await apiClient.post('/api/viajes/solicitar', data)
    return response.data
  },
  aceptar: async (viajeId: string) => {
    const response = await apiClient.post(`/api/viajes/${viajeId}/aceptar`)
    return response.data
  },
  iniciar: async (viajeId: string) => {
    const response = await apiClient.post(`/api/viajes/${viajeId}/iniciar`)
    return response.data
  },
  finalizar: async (viajeId: string) => {
    const response = await apiClient.post(`/api/viajes/${viajeId}/finalizar`)
    return response.data
  },
  cancelar: async (viajeId: string, motivo?: string) => {
    const response = await apiClient.post(`/api/viajes/${viajeId}/cancelar`, { motivo })
    return response.data
  },
}

// ============================================
// CLIENTES API
// ============================================

export const clientesAPI = {
  getAll: async () => {
    const response = await apiClient.get('/api/usuarios/lista?tipo=pasajero')
    return response.data
  },
  getSolicitudesViaje: async () => {
    const response = await apiClient.get('/api/viajes/historial')
    return response.data
  },
}

// ============================================
// TARIFAS API
// ============================================

export const tarifasAPI = {
  getConfiguracion: async () => {
    const response = await apiClient.get('/api/pagos/configurar-tarifa')
    return response.data
  },
  updateConfiguracion: async (data: any) => {
    const response = await apiClient.post('/api/pagos/configurar-tarifa', data)
    return response.data
  },
}

// ============================================
// PROPIETARIO REPORTES
// ============================================

export const propietarioReportesAPI = {
  getResumenEjecutivo: async (vehiculoId: string, periodo: string = 'mes') => {
    const response = await apiClient.get(`/api/propietario/reportes/resumen-ejecutivo/${vehiculoId}?periodo=${periodo}`)
    return response.data
  },
  getBenchmarking: async (vehiculoId: string, periodo: string = 'mes') => {
    const response = await apiClient.get(`/api/propietario/reportes/benchmarking/${vehiculoId}?periodo=${periodo}`)
    return response.data
  },
  getCostoPorViaje: async (vehiculoId: string, params?: { desde?: string; hasta?: string; limit?: number }) => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    if (params?.limit) queryParams.append('limit', String(params.limit))
    const url = `/api/propietario/costo-por-viaje/${vehiculoId}${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getRentabilidadPorZona: async (vehiculoId: string, params?: { desde?: string; hasta?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    const url = `/api/propietario/rentabilidad-por-zona/${vehiculoId}${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getResumenFinanciero: async (params: { 
    periodo?: 'mensual' | 'trimestral' | 'anual';
    fecha_desde?: string;
    fecha_hasta?: string;
  } = {}) => {
    const queryParams = new URLSearchParams()
    if (params.periodo) queryParams.append('periodo', params.periodo)
    if (params.fecha_desde) queryParams.append('fecha_desde', params.fecha_desde)
    if (params.fecha_hasta) queryParams.append('fecha_hasta', params.fecha_hasta)
    const url = `/api/propietario/reportes/resumen-financiero${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getComparativoVehiculos: async (params: { 
    fecha_desde?: string;
    fecha_hasta?: string;
  } = {}) => {
    const queryParams = new URLSearchParams()
    if (params.fecha_desde) queryParams.append('fecha_desde', params.fecha_desde)
    if (params.fecha_hasta) queryParams.append('fecha_hasta', params.fecha_hasta)
    const url = `/api/propietario/reportes/comparativo${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  exportarGastos: async (params: {
    formato: 'csv' | 'excel';
    desde?: string;
    hasta?: string;
    vehiculo_id?: string;
  }) => {
    const queryParams = new URLSearchParams()
    if (params.desde) queryParams.append('desde', params.desde)
    if (params.hasta) queryParams.append('hasta', params.hasta)
    if (params.vehiculo_id) queryParams.append('vehiculo_id', params.vehiculo_id)
    const url = `/api/propietario/reportes/gastos/${params.formato}${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url, { responseType: 'blob' })
    return response.data
  },
  exportarMantenimientos: async (params: { vehiculo_id?: string } = {}) => {
    const queryParams = new URLSearchParams()
    if (params.vehiculo_id) queryParams.append('vehiculo_id', params.vehiculo_id)
    const url = `/api/propietario/reportes/mantenimientos/csv${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url, { responseType: 'blob' })
    return response.data
  },
  getReporteAnual: async (params: { anio: number }) => {
    const response = await apiClient.get(`/api/propietario/reportes/anual?anio=${params.anio}`)
    return response.data
  },
}

// ============================================
// PROPIETARIO VEHÍCULOS
// ============================================

export const propietarioVehiculosAPI = {
  getUbicacion: async (vehiculoId: string) => {
    const response = await apiClient.get(`/api/propietario/vehiculos/${vehiculoId}/ubicacion`)
    return response.data
  },
  getHistorialGPS: async (vehiculoId: string, params?: { desde?: string; hasta?: string; limit?: number }) => {
    const queryParams = new URLSearchParams()
    if (params?.desde) queryParams.append('desde', params.desde)
    if (params?.hasta) queryParams.append('hasta', params.hasta)
    if (params?.limit) queryParams.append('limit', String(params.limit))
    const url = `/api/propietario/vehiculos/${vehiculoId}/historial-gps${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
}

// ============================================
// PROPIETARIO ALERTAS
// ============================================

export const propietarioAlertasAPI = {
  getActivas: async (vehiculoId?: string) => {
    const url = vehiculoId 
      ? `/api/propietario/alertas/activas?vehiculo_id=${vehiculoId}`
      : '/api/propietario/alertas/activas'
    const response = await apiClient.get(url)
    return response.data
  },
  resolver: async (alertaId: string) => {
    const response = await apiClient.put(`/api/propietario/alertas/${alertaId}/resolver`)
    return response.data
  },
}

// ============================================
// PROPIETARIO FINANZAS
// ============================================

export const propietarioFinanzasAPI = {
  getRentabilidad: async (params?: { vehiculo_id?: string; periodo?: 'dia' | 'semana' | 'mes' | 'ano' }) => {
    const queryParams = new URLSearchParams()
    if (params?.vehiculo_id) queryParams.append('vehiculo_id', params.vehiculo_id)
    if (params?.periodo) queryParams.append('periodo', params.periodo)
    const url = `/api/propietario/rentabilidad${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getFlujoEfectivo: async () => {
    const response = await apiClient.get('/api/propietario/flujo-efectivo')
    return response.data
  },
  getDeudaChoferes: async () => {
    const response = await apiClient.get('/api/propietario/deuda-choferes')
    return response.data
  },
  getResumenFinanciero: async (periodo: string = 'mes') => {
    const response = await apiClient.get(`/api/propietario/resumen-financiero?periodo=${periodo}`)
    return response.data
  },
}

// ============================================
// VEHÍCULOS API (READ-ONLY)
// ============================================

export const vehiculosAPI = {
  getAll: async (activo?: boolean) => {
    const params = new URLSearchParams()
    if (activo !== undefined) {
      params.append('activo', String(activo))
    }
    const url = `/api/vehiculos/lista${params.toString() ? '?' + params.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getOne: async (id: string) => {
    const response = await apiClient.get(`/api/vehiculos/${id}`)
    return response.data
  },
  suspender: async (id: string, data: { motivo: string; tipo_suspension: string; fecha_fin?: string }) => {
    const response = await apiClient.post(`/api/vehiculos/${id}/suspender`, data)
    return response.data
  },
  reactivar: async (id: string) => {
    const response = await apiClient.post(`/api/vehiculos/${id}/reactivar`)
    return response.data
  },
  getSuspensiones: async (id: string, activas?: boolean) => {
    const params = new URLSearchParams()
    if (activas !== undefined) {
      params.append('activas', String(activas))
    }
    const url = `/api/vehiculos/${id}/suspensiones${params.toString() ? '?' + params.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getSuspensionesActivas: async (limit: number = 50) => {
    const response = await apiClient.get(`/api/vehiculos/suspensiones/activas?limit=${limit}`)
    return response.data
  },
  generarQR: async (id: string) => {
    const response = await apiClient.post(`/api/vehiculo/qr/generar`, { vehiculo_id: id })
    return response.data
  },
}

// ============================================
// EMPRESAS API (Admin)
// ============================================

export const empresasAPI = {
  getAll: async (params?: { search?: string; estado?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.search) queryParams.append('search', params.search)
    if (params?.estado) queryParams.append('estado', params.estado)
    const url = `/api/admin/empresas${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },
  getOne: async (id: string) => {
    const response = await apiClient.get(`/api/admin/empresas/${id}`)
    return response.data
  },
  create: async (data: any) => {
    const response = await apiClient.post('/api/admin/empresas', data)
    return response.data
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/admin/empresas/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/api/admin/empresas/${id}`)
    return response.data
  },
  getCuentaCorriente: async (id: string) => {
    const response = await apiClient.get(`/api/admin/empresas/${id}/cuenta-corriente`)
    return response.data
  },
  getEmpleados: async (id: string) => {
    const response = await apiClient.get(`/api/admin/empresas/${id}/empleados`)
    return response.data
  },
  getViajes: async (id: string, limit: number = 50) => {
    const response = await apiClient.get(`/api/admin/empresas/${id}/viajes?limit=${limit}`)
    return response.data
  },
  getEstadisticas: async (id: string) => {
    const response = await apiClient.get(`/api/admin/empresas/${id}/estadisticas`)
    return response.data
  }
}

// ============================================
// REGISTRO PROPIETARIO
// ============================================

export const propietarioRegistroAPI = {
  getCiudadesOperativas: async () => {
    const response = await apiClient.get('/api/geo/ciudades-operativas')
    return response.data
  },
  registrarPropietario: async (data: {
    nombre: string
    apellido: string
    email: string
    password: string
    telefono?: string
    ciudad_id: string
    acepta_terminos: boolean
  }) => {
    const response = await apiClient.post('/api/auth/registro/propietario', data)
    return response.data
  },
}

// ============================================
// ADMIN API
// ============================================

export const adminAPI = {
  getDashboard: async () => {
    const response = await apiClient.get('/api/admin/dashboard')
    return response.data
  },
  getTarifas: async () => {
    const response = await apiClient.get('/api/admin/tarifas/mi-tenant')
    return response.data
  },
  updateTarifas: async (data: any) => {
    const response = await apiClient.put('/api/admin/tarifas/mi-tenant', data)
    return response.data
  },
  getTenants: async () => {
    const response = await apiClient.get('/api/admin/tenants')
    return response.data
  },
  getTenant: async (id: string) => {
    const response = await apiClient.get(`/api/admin/tenants/${id}`)
    return response.data
  },
  createTenant: async (data: any) => {
    const response = await apiClient.post('/api/admin/tenants', data)
    return response.data
  },
  updateTenant: async (id: string, data: any) => {
    const response = await apiClient.put(`/api/admin/tenants/${id}`, data)
    return response.data
  },
  deleteTenant: async (id: string) => {
    const response = await apiClient.delete(`/api/admin/tenants/${id}`)
    return response.data
  },
}

// ============================================
// SUPER ADMIN API
// ============================================

export const superAdminAPI = {
  getDashboardGlobal: async (periodo: 'dia' | 'semana' | 'mes' = 'mes') => {
    const response = await apiClient.get(`/api/super-admin/dashboard/global?periodo=${periodo}`)
    return response.data
  },
}