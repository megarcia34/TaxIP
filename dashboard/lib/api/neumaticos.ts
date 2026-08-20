// D:\ataxip\dashboard\lib\api\neumaticos.ts
import { apiClient } from './client';

// ============================================================
// TIPOS
// ============================================================

export interface Neumatico {
  id: string;
  codigo_interno: string;
  marca: string;
  modelo_dibujo?: string;
  medida?: string;
  tipo_neumatico: string;
  estado: 'ACTIVO' | 'BAJA' | 'DESECHADO';
  posicion_actual?: 'DI' | 'DD' | 'TI' | 'TD' | 'REPUESTO';
  km_totales_acumulados: number;
  km_en_posicion_actual?: number;
  fecha_alta: string;
  fecha_baja?: string;
  observaciones?: string;
  activo: boolean;
  ultima_profundidad_mm?: number;
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO';
  ultima_medicion_fecha?: string;
  mediciones?: MedicionItem[];
  operaciones?: OperacionItem[];
}

export interface MedicionItem {
  id: string;
  fecha: string;
  profundidad_mm: number;
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO';
  medido_por: string | null;
  observaciones: string | null;
}

export interface OperacionItem {
  tipo: string;
  fecha: string;
  km_vehiculo: number;
  descripcion: string | null;
}

export interface NeumaticoActivo {
  id: string;
  codigo_interno: string;
  marca: string;
  modelo_dibujo?: string;
  medida?: string;
  km_montaje: number;
  km_recorridos: number;
  ultima_profundidad_mm?: number;
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO';
  sugerencia?: string;
}

export interface NeumaticosActivosResponse {
  vehiculo_id: string;
  patente: string;
  vehiculo_marca: string;
  vehiculo_modelo: string;
  neumaticos: {
    DI?: NeumaticoActivo;
    DD?: NeumaticoActivo;
    TI?: NeumaticoActivo;
    TD?: NeumaticoActivo;
  };
  resumen: {
    total_neumaticos: number;
    estado_verde: number;
    estado_amarillo: number;
    estado_rojo: number;
  };
}

export interface Sugerencia {
  id: string;
  tipo: string;
  neumatico?: string;
  posicion?: string;
  mensaje: string;
  prioridad: 'CRITICA' | 'ALTA' | 'MEDIA' | 'BAJA';
  color: 'ROJO' | 'AMARILLO' | 'VERDE';
  km_actual: number;
  km_umbral: number;
  fecha_generacion: string;
  estado: 'PENDIENTE' | 'ATENDIDA' | 'DESESTIMADA';
  dias_activa?: number;
}

export interface ConfiguracionNeumaticos {
  control_base_id: string;
  vida_util_km: number;
  umbral_rotacion_km: number;
  umbral_cambio_km: number;
  profundidad_minima_mm: number;
  factor_desgaste_delantero: number;
  colores: {
    verde: { max_km: number; min_profundidad: number };
    amarillo: { max_km: number; min_profundidad: number };
    rojo: { max_km: number; min_profundidad: number };
  };
  ultima_actualizacion: string;
}

export interface ResumenNeumaticos {
  vehiculo_id: string;
  patente: string;
  resumen: {
    total_neumaticos: number;
    neumaticos_activos: number;
    neumaticos_baja: number;
    promedio_profundidad: number;
    estado_verde: number;
    estado_amarillo: number;
    estado_rojo: number;
  };
  neumaticos: Neumatico[];
  alertas: {
    criticas: Sugerencia[];
    pendientes: Sugerencia[];
  };
}

export interface EstadoFlotaNeumaticos {
  propietario_id: string;
  total_vehiculos: number;
  total_neumaticos: number;
  resumen_global: {
    activos: number;
    baja: number;
    desechados: number;
  };
  vehiculos: {
    vehiculo_id: string;
    patente: string;
    total_neumaticos: number;
    estado_verde: number;
    estado_amarillo: number;
    estado_rojo: number;
    promedio_profundidad: number;
  }[];
  sugerencias_totales: number;
  alertas_criticas: number;
  promedio_profundidad_flota: number;
}

// ============================================================
// API
// ============================================================

export const neumaticosAPI = {
  // ---- Configuración ----
  getConfiguracion: async (): Promise<ConfiguracionNeumaticos> => {
    const response = await apiClient.get('/propietario/configuracion/neumaticos');
    return response.data;
  },

  updateConfiguracion: async (data: {
    vida_util_km?: number;
    umbral_rotacion_km?: number;
    umbral_cambio_km?: number;
    profundidad_minima_mm?: number;
    factor_desgaste_delantero?: number;
  }): Promise<ConfiguracionNeumaticos> => {
    const response = await apiClient.put('/propietario/configuracion/neumaticos', data);
    return response.data;
  },

  // ---- Vehículo - Neumáticos ----
  getByVehiculo: async (vehiculoId: string, estado?: string): Promise<Neumatico[]> => {
    const url = estado 
      ? `/propietario/vehiculos/${vehiculoId}/neumaticos?estado=${estado}`
      : `/propietario/vehiculos/${vehiculoId}/neumaticos`;
    const response = await apiClient.get(url);
    return response.data;
  },

  getActivos: async (vehiculoId: string): Promise<NeumaticosActivosResponse> => {
    const response = await apiClient.get(`/propietario/vehiculos/${vehiculoId}/neumaticos/activos`);
    return response.data;
  },

  getHistorial: async (vehiculoId: string, limit?: number, offset?: number): Promise<Neumatico[]> => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', String(limit));
    if (offset) params.append('offset', String(offset));
    const url = `/propietario/vehiculos/${vehiculoId}/neumaticos/historial${params.toString() ? '?' + params.toString() : ''}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  // ---- Montaje y Rotación ----
  montar: async (vehiculoId: string, data: {
    neumaticos: {
      marca: string;
      modelo_dibujo?: string;
      medida?: string;
      tipo_neumatico: string;
      posicion: 'DI' | 'DD' | 'TI' | 'TD';
      observaciones?: string;
    }[];
    km_vehiculo_actual: number;
    observaciones_generales?: string;
  }): Promise<{ success: boolean; message: string; neumaticos: Neumatico[] }> => {
    const response = await apiClient.post(`/propietario/vehiculos/${vehiculoId}/neumaticos/montar`, data);
    return response.data;
  },

  rotar: async (vehiculoId: string, data: { km_vehiculo_actual: number; observaciones?: string }): Promise<{
    success: boolean;
    message: string;
    neumaticos: Neumatico[];
  }> => {
    const response = await apiClient.post(`/propietario/vehiculos/${vehiculoId}/neumaticos/rotacion`, data);
    return response.data;
  },

  // ---- Neumático Individual ----
  getOne: async (neumaticoId: string): Promise<Neumatico> => {
    const response = await apiClient.get(`/propietario/neumaticos/${neumaticoId}`);
    return response.data;
  },

  desmontar: async (neumaticoId: string, data: { km_vehiculo_actual: number; motivo: string; observaciones?: string }): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await apiClient.put(`/propietario/neumaticos/${neumaticoId}/desmontar`, data);
    return response.data;
  },

  cambiarEstado: async (neumaticoId: string, data: { estado: 'BAJA' | 'DESECHADO'; motivo?: string; observaciones?: string }): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await apiClient.put(`/propietario/neumaticos/${neumaticoId}/estado`, data);
    return response.data;
  },

  // ---- Mediciones ----
  registrarMedicion: async (neumaticoId: string, data: { profundidad_mm: number; observaciones?: string }): Promise<{
    success: boolean;
    message: string;
    medicion: MedicionItem;
  }> => {
    const response = await apiClient.post(`/propietario/neumaticos/${neumaticoId}/medicion`, data);
    return response.data;
  },

  getMediciones: async (neumaticoId: string, limit?: number): Promise<MedicionItem[]> => {
    const url = limit 
      ? `/propietario/neumaticos/${neumaticoId}/mediciones?limit=${limit}`
      : `/propietario/neumaticos/${neumaticoId}/mediciones`;
    const response = await apiClient.get(url);
    return response.data;
  },

  // ---- Sugerencias ----
  getSugerencias: async (vehiculoId: string, estado?: string, prioridad?: string): Promise<Sugerencia[]> => {
    const params = new URLSearchParams();
    if (estado) params.append('estado', estado);
    if (prioridad) params.append('prioridad', prioridad);
    const url = `/propietario/vehiculos/${vehiculoId}/neumaticos/sugerencias${params.toString() ? '?' + params.toString() : ''}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  atenderSugerencia: async (sugerenciaId: string, observaciones?: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.put(`/propietario/sugerencias/${sugerenciaId}/atender`, { observaciones });
    return response.data;
  },

  desestimarSugerencia: async (sugerenciaId: string, motivo: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.put(`/propietario/sugerencias/${sugerenciaId}/desestimar`, { motivo });
    return response.data;
  },

  // ---- Operaciones ----
  getOperaciones: async (vehiculoId: string, params?: { tipo?: string; desde?: string; hasta?: string; limit?: number; offset?: number }): Promise<{
    total: number;
    operaciones: OperacionItem[];
  }> => {
    const queryParams = new URLSearchParams();
    if (params?.tipo) queryParams.append('tipo', params.tipo);
    if (params?.desde) queryParams.append('desde', params.desde);
    if (params?.hasta) queryParams.append('hasta', params.hasta);
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.offset) queryParams.append('offset', String(params.offset));
    const url = `/propietario/operaciones/vehiculo/${vehiculoId}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  registrarReparacion: async (data: {
    vehiculo_id: string;
    neumatico_id: string;
    tipo_reparacion: string;
    km_vehiculo_actual: number;
    proveedor?: string;
    costo?: number;
    observaciones?: string;
  }): Promise<{ success: boolean; message: string; operacion: OperacionItem }> => {
    const response = await apiClient.post('/propietario/operaciones/reparacion', data);
    return response.data;
  },

  // ---- Imágenes ----
  subirImagen: async (neumaticoId: string, file: File, tipo_imagen: string, descripcion?: string): Promise<{
    success: boolean;
    message: string;
    imagen: { id: string; url: string };
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tipo_imagen', tipo_imagen);
    if (descripcion) formData.append('descripcion', descripcion);
    
    const response = await apiClient.post(`/propietario/neumaticos/${neumaticoId}/imagenes`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getImagenes: async (neumaticoId: string): Promise<{
    id: string;
    url: string;
    tipo_imagen: string;
    descripcion: string | null;
    fecha_subida: string;
  }[]> => {
    const response = await apiClient.get(`/propietario/neumaticos/${neumaticoId}/imagenes`);
    return response.data;
  },

  eliminarImagen: async (imagenId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.delete(`/propietario/imagenes/${imagenId}`);
    return response.data;
  },

  // ---- Resumen y Estado ----
  getResumen: async (vehiculoId: string): Promise<ResumenNeumaticos> => {
    const response = await apiClient.get(`/propietario/vehiculos/${vehiculoId}/neumaticos/resumen`);
    return response.data;
  },

  getEstadoFlota: async (): Promise<EstadoFlotaNeumaticos> => {
    const response = await apiClient.get('/propietario/neumaticos/estado-flota');
    return response.data;
  },
};