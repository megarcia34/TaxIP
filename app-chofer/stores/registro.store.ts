/**
 * Store temporal para el wizard de registro.
 * Guarda datos entre pasos sin necesidad de pasarlos por navegación.
 */
import { create } from 'zustand';

interface RegistroState {
  // Datos del paso 1
  email: string;
  userId: string | null;

  // Datos del paso 2
  emailVerificado: boolean;

  // Acciones
  setEmail: (email: string) => void;
  setUserId: (userId: string | null) => void;
  setEmailVerificado: (verificado: boolean) => void;
  reset: () => void;
}

export const useRegistroStore = create<RegistroState>((set) => ({
  email: '',
  userId: null,
  emailVerificado: false,

  setEmail: (email) => set({ email }),
  setUserId: (userId) => set({ userId }),
  setEmailVerificado: (emailVerificado) => set({ emailVerificado }),

  reset: () =>
    set({
      email: '',
      userId: null,
      emailVerificado: false,
    }),
}));