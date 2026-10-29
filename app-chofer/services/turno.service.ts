/**
 * Servicio del Módulo 2 - Turno.
 */
import api from './api';
import type {
  EstadoChofer,
  TurnoActivo,
  ValidarCodigoResponse,
  CheckInResponse,
  CheckOutResponse,
  TurnoHistorial,
  DetalleTurno,
  Combustible,
} from '@/types/turno.types';

export const turnoService = {
  /**
   * Obtiene el estado completo del chofer.
   * GET /api/chofer/turno/estado
   */
  async obtenerEstado(): Promise<EstadoChofer> {
    const response = await api.get<EstadoChofer>('/api/chofer/turno/estado');
    return response.data;
  },

  /**
   * Obtiene el turno activo (si existe).
   * GET /api/chofer/turno/activo
   */
  async obtenerTurnoActivo(): Promise<{
    tieneTurnoActivo: boolean;
    turnoId?: string;
    estado?: string;
    inicioTurno?: string;
    vehiculoId?: string;
    patente?: string;
    marca?: string;
    modelo?: string;
    anio?: number;
    estadoLaboral?: string;
    kmInicial?: number;
    combustibleInicial?: string;
    contratoId?: string;
    duracionMinutos?: number;
    duracionFormateada?: string;
  }> {
    const response = await api.get('/api/chofer/turno/activo');
    return response.data;
  },

  /**
   * Valida el código de 6 dígitos proporcionado por el propietario.
   * POST /api/chofer/turno/validar-codigo
   */
  async validarCodigo(codigo: string): Promise<ValidarCodigoResponse> {
    const response = await api.post<ValidarCodigoResponse>(
      '/api/chofer/turno/validar-codigo',
      { codigo }
    );
    return response.data;
  },

  /**
   * Inicia el turno con la autorización temporal.
   * POST /api/chofer/turno/check-in
   */
  async checkIn(
    authToken: string,
    kmInicial: number,
    combustibleInicial: Combustible
  ): Promise<CheckInResponse> {
    const response = await api.post<CheckInResponse>(
      '/api/chofer/turno/check-in',
      {
        auth_token: authToken,
        km_inicial: kmInicial,
        combustible_inicial: combustibleInicial,
      }
    );
    return response.data;
  },

  /**
   * Finaliza el turno.
   * POST /api/chofer/turno/check-out
   */
  async checkOut(
    kmFinal: number,
    combustibleFinal: Combustible,
    recaudacionTicketera: number
  ): Promise<CheckOutResponse> {
    const response = await api.post<CheckOutResponse>(
      '/api/chofer/turno/check-out',
      {
        km_final: kmFinal,
        combustible_final: combustibleFinal,
        recaudacion_ticketera: recaudacionTicketera,
      }
    );
    return response.data;
  },

  /**
   * Obtiene el historial de turnos.
   * GET /api/chofer/turno/historial
   */
  async obtenerHistorial(
    limit: number = 20,
    offset: number = 0
  ): Promise<TurnoHistorial[]> {
    const response = await api.get<TurnoHistorial[]>(
      `/api/chofer/turno/historial?limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  /**
   * Obtiene el detalle de un turno.
   * GET /api/chofer/turno/{turno_id}
   */
  async obtenerDetalle(turnoId: string): Promise<DetalleTurno> {
    const response = await api.get<DetalleTurno>(
      `/api/chofer/turno/${turnoId}`
    );
    return response.data;
  },

  /**
   * Obtiene el resumen de actividad de los últimos N días.
   * GET /api/chofer/turno/resumen?dias=N
   *
   * Parámetros:
   * - dias=1: ayer
   * - dias=7: última semana
   * - dias=30: último mes
   * - dias=0: hoy
   */
  async obtenerResumen(dias: number = 1): Promise<{
    fecha_inicio: string;
    fecha_fin: string;
    dias: number;
    viajes: number;
    recaudado: number;
    km_recorridos: number;
    duracion_minutos: number;
    viaje_mas_caro: number;
    viaje_mas_bajo: number;
    promedio_viaje: number;
  }> {
    const response = await api.get(
      `/api/chofer/turno/resumen?dias=${dias}`
    );
    return response.data;
  },

  /**
   * Detecta el modo de inicio de turno del usuario.
   * GET /api/chofer/turno/modo-inicio
   *
   * ⚠️ El backend devuelve camelCase (esPropietario, requiereCodigo,
   * vehiculosDisponibles), a diferencia del resto de los endpoints M2.
   * Ref: ModoInicioResponse en chofer_turnos_schemas.py.
   */
  async obtenerModoInicio(): Promise<{
    esPropietario: boolean;
    requiereCodigo: boolean;
    vehiculosDisponibles: Array<{
      id: string;
      patente: string;
      marca?: string;
      modelo?: string;
      anio?: number;
    }>;
  }> {
    const response = await api.get('/api/chofer/turno/modo-inicio');
    return response.data;
  },

  /**
   * Inicia turno directamente con un vehículo propio (sin código).
   * POST /api/chofer/turno/check-in-directo
   */
  async checkInDirecto(
    vehiculoId: string,
    kmInicial: number,
    combustibleInicial: Combustible
  ): Promise<CheckInResponse> {
    const response = await api.post<CheckInResponse>(
      '/api/chofer/turno/check-in-directo',
      {
        vehiculo_id: vehiculoId,
        km_inicial: kmInicial,
        combustible_inicial: combustibleInicial,
      }
    );
    return response.data;
  },

  /**
   * Lista los viajes huérfanos del turno activo (bloquean el check-out).
   * GET /api/chofer/turno/viajes-huerfanos
   */
  async listarViajesHuerfanos(): Promise<{
    total: number;
    puede_cerrar_turno: boolean;
    viajes: Array<{
      viaje_id: string;
      estado: string;
      created_at: string;
      iniciado_en: string | null;
      direccion_origen: string;
      direccion_destino: string;
      pasajero_nombre: string | null;
      precio_estimado: number | null;
      origen_tipo: string;
      antiguedad_minutos: number;
    }>;
  }> {
    const response = await api.get('/api/chofer/turno/viajes-huerfanos');
    return response.data;
  },

  /**
   * Cierra forzadamente un viaje huérfano.
   * POST /api/chofer/turno/viajes-huerfanos/{viaje_id}/cerrar
   */
  async cerrarViajeHuerfano(
    viajeId: string,
    motivo: string,
    notas?: string
  ): Promise<{
    success: boolean;
    viaje_id: string;
    estado_previo: string;
    estado_nuevo: string;
    motivo: string;
    motivo_label: string;
    precio_final: number | null;
    puede_cerrar_turno: boolean;
    message: string;
  }> {
    const response = await api.post(
      `/api/chofer/turno/viajes-huerfanos/${viajeId}/cerrar`,
      { motivo, notas }
    );
    return response.data;
  },
};