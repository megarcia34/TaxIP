import api from './api';

export interface PerfilUsuario {
  nombre: string;
  apellido: string;
  telefono: string;
  documento: string;
  foto_perfil_url: string | null;
}

export interface UserMeResponse {
  id: string;
  email: string;
  tipo_usuario: string;
  control_base_id: string | null;
  perfil: PerfilUsuario | null;
  tenant: {
    nombre: string;
    email: string;
    telefono: string;
  } | null;
}

export const userService = {
  async obtenerMisDatos(): Promise<UserMeResponse> {
    const response = await api.get<UserMeResponse>('/api/auth/me');
    return response.data;
  },
};