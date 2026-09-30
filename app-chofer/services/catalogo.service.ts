import api from './api';
import type { Prestadora, Ciudad } from '@/types/catalogo.types';

export const catalogoService = {
  async getPrestadoras(): Promise<Prestadora[]> {
    const response = await api.get<Prestadora[]>('/api/catalogo/prestadoras');
    return response.data;
  },

  async getCiudades(): Promise<Ciudad[]> {
    const response = await api.get<Ciudad[]>('/api/geo/ciudades-operativas');
    return response.data;
  },
};