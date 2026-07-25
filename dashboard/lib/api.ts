import axios from 'axios'
import { getSession } from 'next-auth/react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================
// INTERCEPTOR DE REQUEST - CON X-Propietario-ID
// ============================================
apiClient.interceptors.request.use(async (config) => {
  console.log('🔍 [apiClient] Interceptor - URL:', config.url)
  const session = await getSession()
  console.log('🔍 [apiClient] Session:', session?.user?.accessToken ? '✅ Token presente' : '❌ No hay token')
  // Agregar token de autenticación
  if (session?.user?.accessToken) {
    config.headers.Authorization = `Bearer ${session.user.accessToken}`
    console.log('✅ [apiClient] Token agregado a:', config.url)
  }
  
  // ============================================
  // AGREGAR X-Propietario-ID para ADMIN
  // ============================================
  if (session?.user?.role === 'admin') {
    // Obtener el propietario_id de localStorage
    const propietarioId = localStorage.getItem('selectedPropietarioId')
    if (propietarioId) {
      config.headers['X-Propietario-ID'] = propietarioId
    }
  }
  
  return config
})

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.error('🔴 [apiClient] 401 Unauthorized:', error.config?.url)
    }
    return Promise.reject(error)
  }
)

// Tipos
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

// Funciones de API
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

export const controlBaseAPI = {
  getChoferesOnline: async () => {
    const response = await apiClient.get('/api/control-base/choferes-online')
    return response.data
  },
  getSolicitudesActivas: async () => {
    const response = await apiClient.get('/api/control-base/solicitudes-activas')
    return response.data
  },
  getEstadisticas: async () => {
    const response = await apiClient.get('/api/control-base/estadisticas')
    return response.data
  },
  getRankingChoferes: async (limit: number = 10, criterio: string = 'calificacion') => {
    const response = await apiClient.get(`/api/control-base/ranking-choferes?limit=${limit}&criterio=${criterio}`)
    return response.data
  },
  getDatosEmpresa: async () => {
    const response = await apiClient.get('/api/control-base/datos')
    return response.data
  },
  actualizarEmpresa: async (data: any) => {
    const response = await apiClient.put('/api/control-base/actualizar', data)
    return response.data
  },
}

// Choferes API
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

// Viajes API
export const viajesAPI = {
  getEstado: async (id: string) => {
    const response = await apiClient.get(`/api/viajes/${id}/estado`)
    return response.data
  },
  getHistorial: async () => {
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
    const response = await apiClient.get('/api/control-base/solicitudes-activas')
    return response.data
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

// Clientes API
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

// Tarifas API
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

// Propietario API
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
  getChoferesDisponibles: async (turno: string) => {
    const response = await apiClient.get(`/api/propietario/choferes/disponibles?turno=${turno}`)
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
}

// ============================================
// VEHÍCULOS API - UNIFICADA (SOLO LECTURA EN DASHBOARD)
// ============================================
export const vehiculosAPI = {
  // READ-ONLY para el dashboard
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
  
  // SUSPENSIÓN DE VEHÍCULOS
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
  
  // GENERAR QR
  generarQR: async (id: string) => {
    const response = await apiClient.post(`/api/vehiculo/qr/generar`, { vehiculo_id: id })
    return response.data
  },
  
  // NOTA: create, update, delete SOLO están disponibles en propietarioAPI
}

// ============================================
// HELPER PARA OBTENER HEADERS CON AUTENTICACIÓN
// ============================================
export async function getAuthHeaders() {
  const sessionRes = await fetch('/api/auth/session')
  const session = await sessionRes.json()
  
  const headers: HeadersInit = {
    'Authorization': `Bearer ${session?.user?.accessToken}`,
    'Content-Type': 'application/json',
  }
  
  // Si es admin, agregar X-Propietario-ID
  if (session?.user?.role === 'admin') {
    const propietarioId = localStorage.getItem('selectedPropietarioId')
    if (propietarioId) {
      headers['X-Propietario-ID'] = propietarioId
      console.log('✅ X-Propietario-ID agregado:', propietarioId)
    }
  }
  
  return headers
}

// Helper para fetch con autenticación
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
// Empresas API (Admin)
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
// ============================================================
// REGISTRO DE PROPIETARIO
// ============================================================

export const propietarioRegistroAPI = {
  // Obtener ciudades operativas (con tenant activo)
  getCiudadesOperativas: async () => {
    const response = await apiClient.get('/api/geo/ciudades-operativas');
    return response.data;
  },

  // Registrar nuevo propietario
  registrarPropietario: async (data: {
    nombre: string;
    apellido: string;
    email: string;
    password: string;
    telefono?: string;
    ciudad_id: string;
    acepta_terminos: boolean;
  }) => {
    const response = await apiClient.post('/api/auth/registro/propietario', data);
    return response.data;
  },
};