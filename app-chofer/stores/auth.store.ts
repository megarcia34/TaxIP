/**
 * Store de autenticación con Zustand + persist.
 *
 * Convención (alineada con turno.store.ts):
 * - El store es la fuente de verdad de la sesión.
 * - Persiste solo user, token y refreshToken en AsyncStorage.
 * - isAuthenticated NO vive acá: se deriva en el consumidor
 *   con `useAuthStore(s => !!s.token)`.
 * - _hasHydrated lo setea onRehydrateStorage para que splash no
 *   redirija antes de leer AsyncStorage.
 */
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { AuthState, User } from '@/types/auth.types';
import { STORAGE_KEYS } from '@/constants/config';

const STORAGE_KEY = STORAGE_KEYS.AUTH_STORE;

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
      error: null,
      _hasHydrated: false,

      setSession: (user: User, token: string, refreshToken: string | null) =>
        set({
          user,
          token,
          refreshToken,
          error: null,
        }),

      clearSession: () =>
        set({
          user: null,
          token: null,
          refreshToken: null,
          error: null,
        }),

      setLoading: (isLoading: boolean) => set({ isLoading }),

      setError: (error: string | null) => set({ error }),

      clearError: () => set({ error: null }),

      setHasHydrated: (value: boolean) => set({ _hasHydrated: value }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);