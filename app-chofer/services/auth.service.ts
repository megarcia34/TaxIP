/**
 * Servicio de autenticación.
 *
 * El servicio es dueño del ciclo de login/logout/refresh:
 * - login() escribe la sesión al store (no a AsyncStorage directo).
 * - logout() limpia el store (persist limpia AsyncStorage solo).
 * - refresh() rota el access token y devuelve el nuevo.
 * - getToken()/getStoredUser() leen del store, no de AsyncStorage.
 *
 * Al final del archivo se registra refresh() en api.ts vía setRefreshFn()
 * para romper el require cycle entre api.ts y auth.service.ts.
 */
import api, { setRefreshFn } from './api';
import { useAuthStore } from '@/stores/auth.store';
import type {
  LoginResponse,
  RefreshTokenResponse,
  User,
} from '@/types/auth.types';

export const authService = {
  /**
   * Login con email y password.
   * POST /api/auth/login
   *
   * Setea el store con setSession() (atómico). No escribe AsyncStorage directo.
   */
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const response = await api.post<LoginResponse>('/api/auth/login', {
      email,
      password,
    });

    const data = response.data;

    const user: User = {
      id: data.user_id,
      email: data.email,
      tipo: data.tipo_usuario as User['tipo'],
      nombreCompleto: data.nombre_completo ?? undefined,
      controlBaseId: data.control_base_id ?? undefined,
    };

    useAuthStore.getState().setSession(user, data.access_token, data.refresh_token ?? null);

    return { token: data.access_token, user };
  },

  /**
   * Cerrar sesión.
   * Limpia el store. persist limpia AsyncStorage solo.
   */
  async logout(): Promise<void> {
    useAuthStore.getState().clearSession();
  },

  /**
   * Obtener usuario actual desde el backend.
   * GET /api/auth/me
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },

  /**
   * Verificar si hay token en el store.
   */
  async hasToken(): Promise<boolean> {
    return !!useAuthStore.getState().token;
  },

  /**
   * Obtener token del store.
   */
  async getToken(): Promise<string | null> {
    return useAuthStore.getState().token;
  },

  /**
   * Obtener usuario del store.
   */
  async getStoredUser(): Promise<User | null> {
    return useAuthStore.getState().user;
  },

  /**
   * Refrescar access token.
   * POST /api/auth/refresh
   *
   * Devuelve el nuevo access_token.
   * El backend NO rota el refresh_token.
   *
   * Errores:
   * - 401/403: refresh inválido/expirado → limpia sesión y propaga.
   * - Sin response (timeout, red caída): NO limpia sesión (Decisión E1).
   *   El caller decide qué hacer (el interceptor de api.ts propaga error).
   */
  async refresh(): Promise<string> {
    const state = useAuthStore.getState();
    const refreshToken = state.refreshToken;

    if (!refreshToken) {
      useAuthStore.getState().clearSession();
      throw new Error('No hay refresh token — sesión cerrada');
    }

    try {
      const response = await api.post<RefreshTokenResponse>('/api/auth/refresh', {
        refresh_token: refreshToken,
      });

      const newToken = response.data.access_token;
      const currentUser = state.user;

      if (!currentUser) {
        useAuthStore.getState().clearSession();
        throw new Error('No hay usuario en el store — sesión cerrada');
      }

      useAuthStore.getState().setSession(currentUser, newToken, refreshToken);
      return newToken;
    } catch (error: any) {
      const hasResponse = !!error?.response;

      if (hasResponse) {
        // 401/403 u otro error con respuesta: refresh inválido → limpiar.
        useAuthStore.getState().clearSession();
      }
      // Sin response (red/timeout): propagar sin limpiar (Decisión E1).
      throw error;
    }
  },
};

// Registrar refresh() en api.ts para romper el require cycle.
// Debe ir después de la definición de authService.
setRefreshFn(authService.refresh);