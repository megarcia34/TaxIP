// D:\ataxip\dashboard\lib\api\client.ts
import axios from 'axios';
import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ✅ Interceptor para agregar token desde NextAuth session
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // ✅ Obtener token de NextAuth session
      const session = await getSession();
      const token = session?.user?.accessToken;
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('✅ [apiClient] Token agregado a:', config.url);
      } else {
        // Fallback: intentar obtener de localStorage
        const localToken = localStorage.getItem('access_token');
        if (localToken) {
          config.headers.Authorization = `Bearer ${localToken}`;
          console.log('✅ [apiClient] Token (localStorage) agregado a:', config.url);
        } else {
          console.warn('⚠️ [apiClient] No hay token para:', config.url);
        }
      }
    } catch (error) {
      console.warn('⚠️ [apiClient] Error obteniendo sesión:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // ✅ Manejar 401 y 403 (no autorizado)
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.warn('⚠️ [apiClient] Error de autenticación (', error.response.status, '), redirigiendo a login...');
      localStorage.removeItem('access_token');
      // Evitar redirección múltiple
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;