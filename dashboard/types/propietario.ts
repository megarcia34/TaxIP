export interface Contrato {
  id: string;
  vehiculo_id: string;
  patente: string;
  marca: string;
  modelo: string;
  chofer_id: string;
  chofer_nombre: string;
  chofer_apellido: string;
  tipo_contrato: 'AUTO_GESTION' | 'PORCENTAJE' | 'CANON_FIJO';
  turno_asignado: 'DIURNO' | 'NOCTURNO' | 'COMPLETO';
  porcentaje_chofer?: number;
  monto_diario?: number;
  fecha_inicio: string;
  fecha_fin?: string;
  activo: boolean;
}

export interface ChoferDisponible {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string;
  calificacion_promedio: number;
  total_calificaciones: number;
}