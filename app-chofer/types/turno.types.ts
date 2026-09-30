/**
 * Tipos del Módulo 2 - Home y Turno.
 * Alineados con la API del backend (camelCase).
 */

// ============================================
// ESTADOS
// ============================================

export type EstadoLaboral = 'fuera_servicio' | 'libre' | 'ocupado';

export type EstadoTurno = 'ACTIVO' | 'PENDIENTE_CONFIRMACION' | 'CERRADO';

export type Combustible = 'RESERVA' | '1/4' | '1/2' | '3/4' | 'LLENO';

export type EstadoAprobacion = 'pendiente' | 'en_revision' | 'aprobado' | 'rechazado';

// ============================================
// TURNO ACTIVO
// ============================================

export interface TurnoActivo {
  id: string;
  estado: EstadoTurno;
  inicioTurno: string;
  vehiculoId: string;
  patente: string;
  marca?: string;
  modelo?: string;
  anio?: number;
  estadoLaboral: EstadoLaboral;
  kmInicial: number;
  combustibleInicial: Combustible;
  duracionMinutos?: number;
  duracionFormateada?: string;
}

// ============================================
// ESTADO DEL CHOFER
// ============================================

export interface EstadoChofer {
  puedeOperar: boolean;
  motivo: string | null;
  estadoAprobacion: EstadoAprobacion;
  estadoLaboral: EstadoLaboral;
  tieneTurnoActivo: boolean;
  tieneVehiculo: boolean;
  tieneContratoActivo: boolean;
}

// ============================================
// VALIDAR CÓDIGO
// ============================================

export interface ValidarCodigoRequest {
  codigo: string;
}

export interface VehiculoInfo {
  id: string;
  patente: string;
  marca?: string;
  modelo?: string;
  anio?: number;
}

export interface ValidarCodigoResponse {
  success: boolean;
  message: string;
  authToken: string;
  expiresAt: string;
  contratoId: string;
  vehiculo: VehiculoInfo;
  licencia?: string;
}

// ============================================
// CHECK-IN
// ============================================

export interface CheckInRequest {
  authToken: string;
  kmInicial: number;
  combustibleInicial: Combustible;
}

export interface CheckInResponse {
  success: boolean;
  message: string;
  turnoId: string;
  vehiculoId: string;
  patente: string;
  marca?: string;
  modelo?: string;
  anio?: number;
  inicioTurno: string;
  estadoLaboral: EstadoLaboral;
  kmInicial: number;
  combustibleInicial: Combustible;
  duracionMinutos: number;
  duracionFormateada: string;
}

// ============================================
// CHECK-OUT
// ============================================

export interface CheckOutRequest {
  kmFinal: number;
  combustibleFinal: Combustible;
  recaudacionTicketera: number;
}

export interface CheckOutResponse {
  success: boolean;
  message: string;
  turnoId: string;
  estado: EstadoTurno;
  kmRecorridos: number;
  duracionHoras: number;
  ingresosRegistrados: number;
  liquidacionId: string | null;
}

// ============================================
// HISTORIAL
// ============================================

export interface TurnoHistorial {
  id: string;
  estado: EstadoTurno;
  inicioTurno: string;
  finTurno: string | null;
  kmInicial: number;
  kmFinal: number | null;
  combustibleInicial: Combustible;
  combustibleFinal: Combustible | null;
  patente: string;
  marca: string | null;
  modelo: string | null;
  montoBruto: number;
  totalChofer: number;
  estadoLiquidacion: string | null;
}

export interface DetalleTurno {
  id: string;
  estado: EstadoTurno;
  inicioTurno: string;
  finTurno: string | null;
  kmInicial: number;
  kmFinal: number | null;
  kmRecorridos: number | null;
  combustibleInicial: Combustible;
  combustibleFinal: Combustible | null;
  vehiculo: {
    id: string;
    patente: string;
    marca: string | null;
    modelo: string | null;
  };
  contrato: {
    tipo: string;
    porcentajeChofer: number | null;
    montoDiario: number | null;
  };
  liquidacion: {
    id: string | null;
    montoBruto: number;
    totalChofer: number;
    totalPropietario: number;
    estado: string | null;
  };
  gastos: Array<{
    id: string;
    tipoGasto: string;
    monto: number;
    kmRegistro: number | null;
    urlComprobante: string | null;
    createdAt: string;
  }>;
  ingresos: Array<{
    id: string;
    tipoIngreso: string;
    medioPago: string | null;
    origen: string;
    monto: number;
    moneda: string;
    estado: string;
    createdAt: string;
  }>;
}

// ============================================
// CONSTANTES
// ============================================

export const COMBUSTIBLES: Combustible[] = [
  'RESERVA',
  '1/4',
  '1/2',
  '3/4',
  'LLENO',
];

export const COMBUSTIBLE_LABELS: Record<Combustible, string> = {
  RESERVA: 'Reserva',
  '1/4': '1/4',
  '1/2': '1/2',
  '3/4': '3/4',
  LLENO: 'Lleno',
};

export const COMBUSTIBLE_ICONS: Record<Combustible, string> = {
  RESERVA: '🔴',
  '1/4': '🟠',
  '1/2': '🟡',
  '3/4': '🟢',
  LLENO: '🟢',
};