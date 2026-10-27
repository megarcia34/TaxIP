/**
 * Servicio del Módulo 3 - Viajes.
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

export interface GeocodeForwardResponse {
  lat: number;
  lng: number;
  direccion_formateada: string;
}

export interface AutocompletePrediction {
  description: string;
  place_id: string;
}

export interface PlaceDetailsResponse {
  lat: number;
  lng: number;
  direccion_formateada: string;
}

export const viajeService = {
  // ============================================================
  // VIAJE DE CALLE
  // ============================================================
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
  // CICLO DE VIDA DEL VIAJE
  // ============================================================
  async aceptarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/aceptar`
    );
    return response.data;
  },

  async rechazarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/rechazar`
    );
    return response.data;
  },

  async iniciarViaje(viajeId: string): Promise<AccionViajeResponse> {
    const response = await api.post<AccionViajeResponse>(
      `/api/viajes/${viajeId}/iniciar`
    );
    return response.data;
  },

  async finalizarViaje(viajeId: string): Promise<FinalizarViajeResponse> {
    const response = await api.post<FinalizarViajeResponse>(
      `/api/viajes/${viajeId}/finalizar`
    );
    return response.data;
  },

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
  async obtenerEstado(viajeId: string): Promise<ViajeSolicitado> {
    const response = await api.get<ViajeSolicitado>(
      `/api/viajes/${viajeId}/estado`
    );
    return response.data;
  },

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

  // ============================================================
  // GEOCODING Y AUTOCOMPLETE
  // ============================================================
  async geocodeAddress(
    address: string,
    lat?: number,
    lng?: number
  ): Promise<GeocodeForwardResponse> {
    const response = await api.post<GeocodeForwardResponse>(
      '/api/viajes/geocode/forward',
      { address, lat, lng }
    );
    return response.data;
  },

  async autocomplete(
    input: string,
    lat?: number,
    lng?: number
  ): Promise<AutocompletePrediction[]> {
    const response = await api.post<{ predictions: AutocompletePrediction[] }>(
      '/api/viajes/autocomplete',
      { input, lat, lng }
    );
    return response.data.predictions;
  },

  async geocodePlace(placeId: string): Promise<PlaceDetailsResponse> {
    const response = await api.post<PlaceDetailsResponse>(
      '/api/viajes/geocode/place-details',
      { place_id: placeId }
    );
    return response.data;
  },

  // ============================================================
  // MAPA ESTÁTICO
  // ============================================================
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
  async calcularCosto(
    datos: CalcularCostoRequest
  ): Promise<CalcularCostoResponse> {
    const response = await api.post<CalcularCostoResponse>(
      '/api/viajes/calcular-costo',
      datos
    );
    return response.data;
  },

  // ============================================================
  // VIAJE ACTIVO (NUEVO - J15)
  // ============================================================
  async obtenerViajeActivo(): Promise<any | null> {
    try {
      const response = await api.get<{ viaje_activo: any | null }>(
        '/api/viajes/activo'
      );
      return response.data.viaje_activo;
    } catch (error) {
      return null;
    }
  },
};