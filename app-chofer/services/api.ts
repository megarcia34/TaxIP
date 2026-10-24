/**
 * Cliente Axios configurado con interceptores JWT + refresh token.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { navigationRef } from '../App'; // <-- CAMBIO
import { API_URL, API_TIMEOUT } from '@/constants/config';
import { useAuthStore } from '@/stores/auth.store';

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

const REFRESH_EXEMPT_URLS = ['/api/auth/login', '/api/auth/refresh'];

type RefreshFn = () => Promise<string>;
let refreshFn: RefreshFn | null = null;

export function setRefreshFn(fn: RefreshFn): void {
  refreshFn = fn;
}

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

    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    if (!refreshFn) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshFn().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      return api.request(originalRequest);
    } catch (refreshError: any) {
      const hasResponse = !!refreshError?.response;

      if (hasResponse) {
        // Redirigir al Login usando navigationRef
        if (navigationRef.isReady()) {
          navigationRef.reset({
            index: 0,
            routes: [{ name: 'Login' }],
          });
        }
      }
      return Promise.reject(refreshError);
    }
  }
);

export default api;