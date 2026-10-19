// D:\ataxip\dashboard\lib\api\client.ts
import axios from 'axios';
import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================
// AXIOS CLIENT
// ============================================
// IMPORTANTE: NO setear Content-Type por defecto.
// Axios lo detecta automaticamente:
//   - application/json para objetos JS (default)
//   - multipart/form-data con boundary para FormData
// Si forzamos 'application/json' en los defaults, los POST con
// FormData fallan (el backend no puede parsear el archivo).

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

// ============================================
// REQUEST INTERCEPTOR
// ============================================
// Agrega el token JWT de la sesion de NextAuth
// a cada request que pasa por apiClient.

apiClient.interceptors.request.use(
  async (config) => {
    try {
      const session = await getSession();
      const token = session?.user?.accessToken;

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.warn('[apiClient] Error obteniendo sesion:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================
// RESPONSE INTERCEPTOR
// ============================================
// Si el backend devuelve 401 o 403 (token vencido
// o invalido), redirigimos a /login.

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.warn(
        '[apiClient] Error de autenticacion (' +
          error.response.status +
          '), redirigiendo a login...'
      );
      if (
        typeof window !== 'undefined' &&
        !window.location.pathname.includes('/login')
      ) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;