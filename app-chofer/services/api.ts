/**
 * Cliente Axios configurado con interceptores JWT + refresh token.
 *
 * - Request interceptor: agrega Authorization desde el store (no AsyncStorage).
 * - Response interceptor: en 401, intenta refresh con mutex y reintenta la request.
 *
 * Excepciones:
 * - 401 de /api/auth/login y /api/auth/refresh no se interceptan.
 * - Requests ya reintentadas (config._retry === true) no se reintentan.
 * - Si el refresh falla por red (sin response), NO se limpia sesión (Decisión E1).
 *
 * El refresh NO se importa directamente para evitar un require cycle con
 * auth.service.ts. En su lugar, auth.service.ts se registra llamando a
 * setRefreshFn() al cargarse.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { router } from 'expo-router';
import { API_URL, API_TIMEOUT } from '@/constants/config';
import { useAuthStore } from '@/stores/auth.store';

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * URLs que NO deben pasar por el flujo de refresh.
 * Un 401 en estas rutas es "credenciales malas", no "token vencido".
 */
const REFRESH_EXEMPT_URLS = ['/api/auth/login', '/api/auth/refresh'];

/**
 * Función de refresh inyectada por auth.service.ts.
 * No se importa directamente para evitar el require cycle.
 */
type RefreshFn = () => Promise<string>;
let refreshFn: RefreshFn | null = null;

/**
 * Registra la función de refresh. Llamado por auth.service.ts al cargarse.
 */
export function setRefreshFn(fn: RefreshFn): void {
  refreshFn = fn;
}

/**
 * Mutex del refresh. Mientras hay un refresh en vuelo, las requests que reciben
 * 401 esperan esta promesa en vez de disparar otro refresh.
 * Se resetea a null cuando la promesa resuelve o rechaza.
 */
let refreshPromise: Promise<string> | null = null;

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    // No es 401, no hay config, o la URL está exenta → propagar.
    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      !originalRequest.url
    ) {
      return Promise.reject(error);
    }

    const isExempt = REFRESH_EXEMPT_URLS.some((url) =>
      originalRequest.url!.includes(url)
    );
    if (isExempt) {
      return Promise.reject(error);
    }

    // Ya se reintentó esta request → no loop infinito.
    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    // Si no hay función de refresh registrada, propagar sin intentar.
    // Pasa si auth.service.ts todavía no se cargó (raro, pero defensivo).
    if (!refreshFn) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      // Mutex: si hay refresh en vuelo, esperar esa promesa.
      // Si no, disparar uno y guardarlo.
      if (!refreshPromise) {
        refreshPromise = refreshFn().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;

      // Reintentar la request original con el token nuevo.
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      return api.request(originalRequest);
    } catch (refreshError: any) {
      // Discriminar red vs auth (Decisión E1).
      const hasResponse = !!refreshError?.response;

      if (hasResponse) {
        // Refresh rechazado por el backend → sesión inválida.
        // authService.refresh() ya hizo clearSession().
        router.replace('/(auth)/login');
      }
      // Sin response: error de red. No redirigir, propagar.
      // El caller decide (reintentar, mostrar mensaje, etc.).
      return Promise.reject(refreshError);
    }
  }
);

export default api;