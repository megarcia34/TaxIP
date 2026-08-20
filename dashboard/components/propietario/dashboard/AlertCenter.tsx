// types/propietario.ts

export interface ChoferDisponible {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string;
  calificacion_promedio: number;
  total_calificaciones: number;
}

export interface Vehiculo {
  id: string;
  patente: string;
  marca: string;
  modelo: string;
  anio: number;
  activo: boolean;
  chofer_asignado?: string;
  estado_laboral?: string;
  qr_uuid?: string;
  qr_activo?: boolean;
}

export interface Contrato {
  id: string;
  vehiculo_id: string;
  patente: string;
  marca: string;
  modelo: string;
  chofer_id: string;
  chofer_nombre: string;
  chofer_apellido: string;
  tipo_contrato: 'AUTO_GESTION' | 'PORCENTAJE' | 'ALQUILER';
  
  // NUEVOS CAMPOS (horarios flexibles)
  hora_inicio?: string;
  hora_fin?: string;
  duracion_minima_horas?: number;
  permite_extension?: boolean;
  hora_fin_extension?: string | null;
  
  // ALQUILER
  canon_diario?: number | null;
  km_incluidos_dia?: number | null;
  valor_km_excedente?: number | null;
  modalidad_computo?: 'DIARIO' | 'SEMANAL' | null;
  dias_contractuales?: string[];
  tratamiento_dia_no_trabajado?: string | null;
  dia_inicio_semana?: string | null;
  
  // PORCENTAJE
  porcentaje_chofer?: number | null;
  
  // Vigencia
  fecha_inicio: string;
  fecha_fin: string | null;
  activo: boolean;
  estado_contrato?: 'PENDIENTE_CONFIGURACION' | 'PROGRAMADO' | 'ACTIVO' | 'FINALIZADO';
  created_at: string;
}

// ============================================
// NUEVO: ViajePropietario
// ============================================

export type ViajePropietario = {
  id: string;
  vehiculo_id: string;
  patente: string;
  chofer_id: string;
  chofer_nombre: string;
  chofer_apellido: string;
  pasajero_nombre?: string;
  direccion_origen: string;
  direccion_destino: string;
  precio_final: number;
  estado: string;
  created_at: string;
  finalizado_at?: string;
  distancia_metros?: number;
  tiempo_estimado_segundos?: number;
  metodo_pago?: string;
  turno_id?: string;
  facturado?: boolean;
};