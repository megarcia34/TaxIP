
/**
 * Tipos de la respuesta del endpoint /api/chofer/splash-estado.
 */

export type EtapaActual =
  | 'registro'
  | 'datos'
  | 'documentos'
  | 'selfie'
  | 'revision'
  | 'esperando_vehiculo'
  | 'contrato_pendiente'
  | 'listo'
  | 'home';

export interface Progreso {
  datos_personales: boolean;
  documentos_basicos: boolean;
  selfie: boolean;
}

export interface VehiculoInfo {
  id: string;
  patente: string;
}

export interface TurnoInfo {
  id: string;
  inicio_turno: string;
}

export interface ContratoInfo {
  id: string;
  tipo: string;
}

export interface SplashEstado {
  autenticado: boolean;
  estado_aprobacion: string;
  estado_laboral: string;
  puede_operar: boolean;
  tiene_vehiculo: boolean;
  tiene_contrato_activo: boolean;
  tiene_turno_activo: boolean;
  etapa_actual: EtapaActual;
  documentos_faltantes: string[];
  progreso: Progreso;
  motivo_bloqueo: string | null;
  tenant_nombre: string | null;
  vehiculo: VehiculoInfo | null;
  turno: TurnoInfo | null;
  contrato: ContratoInfo | null;
}
