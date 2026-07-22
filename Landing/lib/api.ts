import axios from 'axios';

// ============================================
// CONFIGURACIÓN
// ============================================
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

console.log('🔗 API URL:', API_URL);

// Cliente para endpoints públicos (SIN autenticación)
export const publicApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Cliente para endpoints privados (CON autenticación)
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// ============================================
// INTERCEPTOR - REQUEST (API privada)
// ============================================
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    console.log(`📤 ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// ============================================
// INTERCEPTOR - RESPONSE (API privada)
// ============================================
api.interceptors.response.use(
  (response) => {
    console.log(`📥 ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error('❌ API Error:', error.message);
    
    if (error.code === 'ECONNABORTED') {
      console.error('⏰ Timeout - El servidor no respondió');
    }
    
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          console.log('🔄 Refrescando token...');
          const response = await api.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return api(error.config);
        } catch (refreshError) {
          console.error('❌ Error refrescando token:', refreshError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_id');
          localStorage.removeItem('tipo_usuario');
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// ============================================
// TIPOS
// ============================================
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  user_id: string;
  email: string;
  tipo_usuario: string;
  nombre_completo: string;
  control_base_id?: string | null;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  apellido: string;
  telefono: string;
  tipo: 'pasajero';
}

export interface RegisterResponse {
  success: boolean;
  user_id: string;
  email: string;
  message: string;
}

// ============================================
// FUNCIONES DE AUTENTICACIÓN
// ============================================
export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    console.log('🔐 Login:', email);
    const response = await api.post<LoginResponse>('/api/auth/login', {
      email,
      password,
    });
    
    if (response.data.success) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('tipo_usuario', response.data.tipo_usuario);
      console.log('✅ Login exitoso:', response.data.user_id);
    }
    
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    console.log('📝 Registro:', data.email);
    const response = await api.post<RegisterResponse>('/api/auth/registro', data);
    console.log('✅ Registro exitoso:', response.data.user_id);
    return response.data;
  },

  logout: () => {
    console.log('🔓 Logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('tipo_usuario');
  },

  getCurrentUser: () => {
    const userId = localStorage.getItem('user_id');
    const tipoUsuario = localStorage.getItem('tipo_usuario');
    const accessToken = localStorage.getItem('access_token');
    
    if (!userId || !accessToken) return null;
    
    return { userId, tipoUsuario, accessToken };
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

// ============================================
// FUNCIONES DE VIAJES (PÚBLICO - LANDING)
// ============================================
export const viajesService = {
  // Calcular tarifa (público)
  calcularTarifa: async (data: {
    origen_lat: number;
    origen_lng: number;
    destino_lat: number;
    destino_lng: number;
  }): Promise<{
    success: boolean;
    tarifa: number;
    distancia_km: number;
    tiempo_estimado_min: number;
    tarifa_base: number;
    precio_por_km: number;
  }> => {
    console.log('📊 Calculando tarifa pública...');
    const response = await publicApi.post('/api/public/viajes/calcular-tarifa', null, {
      params: {
        origen_lat: data.origen_lat,
        origen_lng: data.origen_lng,
        destino_lat: data.destino_lat,
        destino_lng: data.destino_lng,
      },
    });
    console.log('✅ Tarifa calculada:', response.data);
    return response.data;
  },

  // Solicitar viaje (público - sin autenticación)
  solicitarViajePublico: async (data: {
    direccion_origen: string;
    origen_lat: number;
    origen_lng: number;
    direccion_destino: string;
    destino_lat: number;
    destino_lng: number;
    metodo_pago?: string;
    precio_estimado?: number;
    nombre_pasajero?: string;
    telefono_pasajero?: string;
  }): Promise<{
    success: boolean;
    viaje_id: string;
    mensaje: string;
    chofer_asignado?: any;
    tiempo_espera_estimado?: number;
  }> => {
    console.log('🚕 Solicitando viaje público...');
    const response = await publicApi.post('/api/public/viajes/solicitar', data);
    console.log('✅ Viaje solicitado:', response.data);
    return response.data;
  },

  // Obtener estado del viaje (público - sin autenticación)
  getEstadoViaje: async (viajeId: string): Promise<any> => {
    console.log('📋 Obteniendo estado del viaje público:', viajeId);
    const response = await publicApi.get(`/api/public/viajes/${viajeId}/estado`);
    console.log('✅ Estado obtenido:', response.data);
    return response.data;
  },

  // Cancelar viaje (público - sin autenticación)
  cancelarViaje: async (viajeId: string, motivo?: string): Promise<any> => {
    console.log('🚫 Cancelando viaje público:', viajeId);
    const response = await publicApi.post(`/api/public/viajes/${viajeId}/cancelar`, { motivo });
    return response.data;
  },

  // Calificar viaje (requiere autenticación)
  calificarViaje: async (viajeId: string, puntaje: number, comentario?: string): Promise<any> => {
    console.log('⭐ Calificando viaje:', viajeId);
    const response = await api.post(`/api/viajes/${viajeId}/calificar`, { puntaje, comentario });
    return response.data;
  },
};