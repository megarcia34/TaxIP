import axios from 'axios';
import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

// REQUEST INTERCEPTOR
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

// RESPONSE INTERCEPTOR
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const url = originalRequest?.url || '';

    // Si es 401 y no hemos reintentado aún
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Forzamos a NextAuth a refrescar la sesión
        // Al llamar a getSession(), NextAuth ejecuta el callback jwt,
        // el cual detectará que el token expiró y pedirá uno nuevo al backend.
        const session = await getSession();
        
        if (session?.user?.accessToken) {
          // Reintentamos la petición con el nuevo token
          originalRequest.headers.Authorization = `Bearer ${session.user.accessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error('[apiClient] Error al refrescar token:', refreshError);
      }

      // Si falla el refresh, redirigir a login
      console.warn('[apiClient] No se pudo refrescar el token, redirigiendo a login...');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } 
    else if (status === 403) {
      // ... (tu lógica de errores de negocio igual)
      const esErrorDeNegocio = 
        url.includes('/propietario/perfil') || 
        url.includes('/pagos/medios') ||
        url.includes('/propietario/cuentas-cobro') ||
        url.includes('/propietario/documentos') ||
        url.includes('/propietario/postulacion');
      
      if (!esErrorDeNegocio) {
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;