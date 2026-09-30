/**
 * Tipos de autenticación.
 *
 * Convención:
 * - Requests al backend: snake_case.
 * - Responses del backend: snake_case (se traducen en el servicio).
 * - Estado interno del store: camelCase.
 */

export type EstadoAprobacion = 'pendiente' | 'en_revision' | 'aprobado' | 'rechazado';
export type EstadoLaboral = 'fuera_servicio' | 'libre' | 'ocupado';
export type TipoUsuario = 'chofer' | 'propietario' | 'admin' | 'pasajero' | 'empleado';

export interface User {
  id: string;
  email: string;
  tipo: TipoUsuario;
  nombreCompleto?: string;
  controlBaseId?: string;
  estadoAprobacion?: EstadoAprobacion;
  estadoLaboral?: EstadoLaboral;
}

export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Estructura exacta que devuelve POST /api/auth/login (snake_case).
 */
export interface LoginResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  email: string;
  tipo_usuario: string;
  nombre_completo: string | null;
  control_base_id: string | null;
}

/**
 * Estructura exacta de POST /api/auth/refresh (snake_case).
 * El backend NO rota el refresh token.
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Estado de autenticación en el store (camelCase).
 *
 * Notas:
 * - `isAuthenticated` NO vive acá. Se deriva en el consumidor
 *   con `useAuthStore(s => !!s.token)`.
 * - `_hasHydrated` lo setea `onRehydrateStorage` de persist.
 *   Sirve para que splash no redirija antes de leer AsyncStorage.
 */
export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  _hasHydrated: boolean;

  setSession: (user: User, token: string, refreshToken: string | null) => void;
  clearSession: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setHasHydrated: (value: boolean) => void;
}