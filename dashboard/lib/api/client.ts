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
// Si el backend devuelve 401 (token vencido) redirigimos a login.
// Si devuelve 403, solo redirigimos si es un error de token, NO si es un
// error de negocio (ej: "no tienes vehículos", "no eres propietario").

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';

    if (status === 401) {
      console.warn('[apiClient] Token inválido/expirado, redirigiendo a login...');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } 
    else if (status === 403) {
      // ✅ NUEVO: No redirigir si es un error de negocio (ej: perfil sin vehículos)
      const esErrorDeNegocio = 
        url.includes('/propietario/perfil') || 
        url.includes('/pagos/medios') ||
        url.includes('/propietario/cuentas-cobro') ||  // ✅ NUEVO
        url.includes('/propietario/documentos') ||      // ✅ NUEVO (por si acaso)
        url.includes('/propietario/postulacion');        // ✅ NUEVO
      
      if (!esErrorDeNegocio) {
        console.warn('[apiClient] Error de autenticación (403), redirigiendo a login...');
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      } else {
        console.log('[apiClient] Error de negocio (403), no se redirige:', url);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;