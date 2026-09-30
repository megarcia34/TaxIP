/**
 * Servicio del Módulo 3 - Viajes.
 *
 * Traduce entre camelCase (frontend) y snake_case (backend) donde aplica.
 * Ref: app/routers/viajes/viaje_schemas.py.
 */
import api from './api';
import type {
  AccionViajeResponse,
  CalcularCostoRequest,
  CalcularCostoResponse,
  CancelarViajeRequest,
  EstadoViaje,
  FinalizarViajeResponse,
  HistorialViajeItem,
  MapaEstaticoResponse,
  ReverseGeocodeResponse,
  SolicitarViajeCalleRequest,   
  SolicitarViajeResponse,
  ViajeSolicitado,
} from '@/types/viaje.types';

export const viajeService = {
  // ============================================================
  // VIAJE DE CALLE (Etapa 10)
  // ============================================================
  /**
   * Registra un viaje de calle tomado por el chofer.
   * POST /api/viajes/calle
   *
   * El backend crea el viaje directo en estado 'en_curso' porque el
   * pasajero ya está a bordo. Requiere que el chofer tenga turno activo.
   *
   * El body va tal cual en snake_case (coincide con el backend).
   * La response también viene en snake_case y se devuelve tal cual;
   * el store se encarga de mapear si hace falta.
   */
  async solicitarViajeCalle(
    datos: SolicitarViajeCalleRequest
  ): Promise<ViajeSolicitado> {
    const response = await api.post<ViajeSolicitado>(
      '/api/viajes/calle',
      datos
    );
    return response.data;
  },

  // ============================================================
  // CICLO DE VIDA DEL VIAJE (Fase B + Etapa 4)
  // ============================================================
  /**
   * Aceptar un viaje (chofer). Atómico en el backend.
   * POST /api/viajes/{viaje_id}/aceptar
   */
  async aceptarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/aceptar`
    );
    return response.data;
  },

  /**
   * Rechazar un viaje (chofer). No penaliza; el viaje sigue publicado.
   * POST /api/viajes/{viaje_id}/rechazar
   */
  async rechazarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/rechazar`
    );
    return response.data;
  },

  /**
   * Iniciar un viaje (chofer).
   * POST /api/viajes/{viaje_id}/iniciar
   */
  async iniciarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/iniciar`
    );
    return response.data;
  },

    /**
   * Finalizar un viaje (chofer).
   * POST /api/viajes/{viaje_id}/finalizar
   * Sin body.
   *
   * Devuelve el precio final calculado por el motor unificado,
   * la moneda y el desglose. Ver G44.
   */
  async finalizarViaje(viajeId: string): Promise<FinalizarViajeResponse> {
    const response = await api.post<FinalizarViajeResponse>(
      `/api/viajes/${viajeId}/finalizar`
    );
    return response.data;
  },
  
  /**
   * Cancelar un viaje.
   * POST /api/viajes/{viaje_id}/cancelar
   */
  async cancelarViaje(
    viajeId: string,
    motivo?: string
  ): Promise<AccionViajeResponse> {
    const body: CancelarViajeRequest = { motivo };
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/cancelar`,
      body
    );
    return response.data;
  },

  // ============================================================
  // CONSULTAS
  // ============================================================
  /**
   * Obtiene el estado actual de un viaje.
   * GET /api/viajes/{viaje_id}/estado
   */
  async obtenerEstado(viajeId: string): Promise<ViajeSolicitado> {
    const response = await api.get<ViajeSolicitado>(
      `/api/viajes/${viajeId}/estado`
    );
    return response.data;
  },

  /**
   * Obtiene el historial de viajes del chofer autenticado.
   * GET /api/viajes/historial?limit=&offset=&estado=
   */
  async obtenerHistorial(filtros?: {
    limit?: number;
    offset?: number;
    estado?: EstadoViaje;
  }): Promise<HistorialViajeItem[]> {
    const params = new URLSearchParams();
    if (filtros?.limit != null) params.append('limit', String(filtros.limit));
    if (filtros?.offset != null) params.append('offset', String(filtros.offset));
    if (filtros?.estado) params.append('estado', filtros.estado);

    const qs = params.toString();
    const url = qs
      ? `/api/viajes/historial?${qs}`
      : '/api/viajes/historial';

    const response = await api.get<HistorialViajeItem[]>(url);
    return response.data;
  },

  /**
   * Reverse geocoding: convierte (lat, lng) en una dirección legible.
   * GET /api/viajes/geocode/reverse?lat=&lng=
   *
   * El backend cachea con TTL 1 hora. Timeout 3s. Fallback a
   * coordenadas formateadas si Google falla.
   */
  async reverseGeocode(
    lat: number,
    lng: number
  ): Promise<ReverseGeocodeResponse> {
    const params = new URLSearchParams({
      lat: String(lat),
      lng: String(lng),
    });
    const response = await api.get<ReverseGeocodeResponse>(
      `/api/viajes/geocode/reverse?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Obtiene la URL del mapa estático entre origen y destino.
   * GET /api/viajes/mapa-estatico?origen_lat=&origen_lng=&destino_lat=&destino_lng=
   *
   * El backend solo genera la URL (no hace request a Google). El frontend
   * la usa directo en <Image />.
   */
  async obtenerUrlMapa(params: {
    origen_lat: number;
    origen_lng: number;
    destino_lat: number;
    destino_lng: number;
    ancho?: number;
    alto?: number;
  }): Promise<MapaEstaticoResponse> {
    const qs = new URLSearchParams({
      origen_lat: String(params.origen_lat),
      origen_lng: String(params.origen_lng),
      destino_lat: String(params.destino_lat),
      destino_lng: String(params.destino_lng),
    });
    if (params.ancho != null) qs.append('ancho', String(params.ancho));
    if (params.alto != null) qs.append('alto', String(params.alto));

    const response = await api.get<MapaEstaticoResponse>(
      `/api/viajes/mapa-estatico?${qs.toString()}`
    );
    return response.data;
  },

  // ============================================================
  // CÁLCULO DE COSTO
  // ============================================================
  /**
   * Calcula el costo estimado de un viaje.
   * POST /api/viajes/calcular-costo
   */
  async calcularCosto(
    datos: CalcularCostoRequest
  ): Promise<CalcularCostoResponse> {
    const response = await api.post<CalcularCostoResponse>(
      '/api/viajes/calcular-costo',
      datos
    );
    return response.data;
  },
};