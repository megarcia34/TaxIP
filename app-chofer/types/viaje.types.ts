/**
 * Tipos de viajes (M3).
 *
 * Reflejan los schemas del backend en app/routers/viajes/viaje_schemas.py
 * y app/routers/chofer/chofer_splash_schemas.py.
 *
 * Convención: snake_case en los tipos que reflejan la respuesta del backend.
 * El service traduce a camelCase antes de devolver al store.
 */

import type { Coordenada } from './ubicacion.types';

/**
 * Estados posibles de trip.viaje_solicitado.estado.
 *
 * Confirmados en el código del backend (trip_service.py, routes.py,
 * broadcast_service.py, scheduler.py, pagos.py):
 * - `pendiente`: creado, esperando asignación o broadcast.
 * - `publicado`: en broadcast, esperando aceptación de un chofer.
 * - `programada`: reserva anticipada, esperando fecha_programada.
 * - `aceptado`: un chofer lo aceptó.
 * - `en_curso`: el pasajero subió, viaje en progreso.
 * - `finalizado`: llegó a destino.
 * - `cancelado`: cancelado por alguna de las partes.
 * - `pagado`: cobrado y cerrado (para pagos electrónicos).
 * - `expirado`: broadcast venció sin aceptación.
 */
export type EstadoViaje =
  | 'pendiente'
  | 'publicado'
  | 'programada'
  | 'aceptado'
  | 'en_curso'
  | 'finalizado'
  | 'cancelado'
  | 'pagado'
  | 'expirado';

/**
 * Canal por el que ingresó el viaje.
 *
 * ✅ Refleja el CHECK constraint real de la DB:
 *    ck_viaje_solicitado_ck_viaje_origen_tipo
 *    Valores permitidos: plataforma, via_publica, qr_comercio,
 *    corporativo, despacho_manual.
 *
 * Si el backend agrega un valor nuevo, agregarlo acá y en el CHECK.
 */
export type OrigenTipo =
  | 'plataforma'
  | 'via_publica'
  | 'qr_comercio'
  | 'corporativo'
  | 'despacho_manual';

/**
 * Métodos de pago aceptados por el backend para un viaje.
 * Ref: SolicitarViajeRequest.metodo_pago en viaje_schemas.py.
 *
 * ⚠️ DEUDA: el backend tiene valores inconsistentes en otros módulos
 * (`qr`, `vehiculo`, `transferencia`). Este tipo refleja solo el contrato
 * del endpoint de viajes.
 */
export type MetodoPago =
  | 'efectivo'
  | 'billetera'
  | 'tarjeta_credito'
  | 'tarjeta_debito';

/**
 * Subset de métodos de pago aceptados por POST /api/viajes/calle.
 *
 * El handler valida estrictamente:
 *   METODOS_VALIDOS = {"efectivo", "billetera", "tarjeta_debito"}
 *
 * Si el backend amplía la lista, actualizar acá.
 */
export type MetodoPagoCalle =
  | 'efectivo'
  | 'billetera'
  | 'tarjeta_debito';

/**
 * Viaje solicitado (forma completa del backend).
 * Mezcla de ViajeSolicitado (modelo SQLAlchemy) + ViajeEstadoResponse +
 * HistorialViajeResponse.
 */
export interface ViajeSolicitado {
  id: string;
  control_base_id: string;
  /**
   * Puede ser NULL en viajes anónimos (origen_tipo = 'via_publica').
   * El backend devuelve 'Pasajero anónimo' como nombre en ese caso.
   */
  pasajero_id: string | null;
  chofer_id: string | null;
  chofer_vehiculo_id: string | null;
  vehiculo_id: string | null;
  turno_id: string | null;

  // Ubicación
  origen_lat: number | null;
  origen_lng: number | null;
  destino_lat: number | null;
  destino_lng: number | null;
  direccion_origen: string | null;
  direccion_destino: string | null;

  // Estado
  estado: EstadoViaje;

  // Precios
  precio_estimado: number | null;
  precio_final: number | null;
  moneda: string;

  // Tiempo y distancia
  tiempo_estimado_segundos: number | null;
  distancia_metros: number | null;

  // Compartir
  url_seguimiento: string | null;
  codigo_compartido: string | null;

  // Timestamps
  solicitado_en: string;
  aceptado_en: string | null;
  iniciado_en: string | null;
  finalizado_en: string | null;
  cancelado_en: string | null;
  cancelado_por: string | null;
  motivo_cancelacion: string | null;

  // Reservas
  fecha_programada: string | null;
  reserva_procesada: boolean;

  // Metadata
  comercio_id: string | null;
  empresa_id: string | null;
  nombre_pasajero: string | null;
  notas: string | null;
  facturado: boolean;

  // Datos calculados (vienen en las responses)
  origen_tipo?: OrigenTipo | null;
  metodo_pago?: MetodoPago | null;
  pasajero_nombre?: string | null;
  calificacion_dada?: number | null;

  // Campos que el backend agrega en las queries (queries.py).
  // No están en el modelo SQLAlchemy, pero sí en la respuesta.
  empresa?: string | null;
  patente?: string | null;
  propietario?: string | null;
}

/**
 * Viaje activo del chofer (el que tiene en curso).
 * Forma reducida con la info mínima para la pantalla de viaje en curso.
 */
export interface ViajeActivo {
  id: string;
  estado: EstadoViaje;

  // Origen y destino
  origen: Coordenada | null;
  destino: Coordenada | null;
  direccion_origen: string | null;
  direccion_destino: string | null;

  // Pasajero
  pasajero_id: string;
  pasajero_nombre: string | null;

  // Precios
  precio_estimado: number | null;
  precio_final: number | null;
  moneda: string;

  // Tiempo y distancia
  tiempo_estimado_segundos: number | null;
  distancia_metros: number | null;

  // Timestamps (los importantes para la UI)
  solicitado_en: string;
  aceptado_en: string | null;
  iniciado_en: string | null;

  // Canal y método de pago
  origen_tipo: OrigenTipo | null;
  metodo_pago: MetodoPago | null;
}

/**
 * Request para solicitar un viaje (cualquier canal).
 * Ref: SolicitarViajeRequest en viaje_schemas.py.
 *
 * ⚠️ DEUDA: Este tipo refleja el schema legacy `/api/viajes/solicitar`.
 * El endpoint M3 `/api/viajes/solicitar-broadcast` usa `origen_lat`/`origen_lng`
 * (sin "itud"). Unificar en Etapa 11.
 */
export interface SolicitarViajeRequest {
  origen_latitud: number;
  origen_longitud: number;
  direccion_origen: string;
  destino_latitud?: number;
  destino_longitud?: number;
  direccion_destino?: string;
  metodo_pago?: MetodoPago;
}

/**
 * Request para el endpoint M3 POST /api/viajes/calle.
 *
 * Ref: SolicitarViajeCalleRequest en app/routers/viajes/schemas.py.
 *
 * Reglas del backend:
 * - Chofer autenticado (get_current_driver_user).
 * - Chofer con vehículo activo en el tenant.
 * - Chofer con turno activo (fleet.turno_chofer.estado = 'ACTIVO').
 * - Destino obligatorio.
 * - El viaje se crea directo en estado 'en_curso'.
 */
export interface SolicitarViajeCalleRequest {
  origen_lat: number;
  origen_lng: number;
  direccion_origen: string;
  destino_lat: number;
  destino_lng: number;
  direccion_destino: string;
  metodo_pago?: MetodoPagoCalle;
  notas?: string;
  paradas_intermedias?: Record<string, unknown>[] | null;
}

/**
 * Response de solicitar viaje.
 * Ref: SolicitarViajeResponse en viaje_schemas.py.
 *
 * ⚠️ El endpoint `/api/viajes/calle` NO usa este tipo. Devuelve
 * `ViajeEstadoResponse` (que el frontend consume como `ViajeSolicitado`).
 * Este tipo aplica a `/api/viajes/solicitar-broadcast` y `/solicitar`.
 */
export interface SolicitarViajeResponse {
  success: boolean;
  viaje_id: string;
  estado: string;
  mensaje: string;
  tiempo_estimado_segundos: number | null;
  precio_estimado: number | null;
}

/**
 * Request para calcular costo estimado.
 * Ref: CalcularCostoRequest en viaje_schemas.py.
 */
export interface CalcularCostoRequest {
  origen_latitud: number;
  origen_longitud: number;
  destino_latitud: number;
  destino_longitud: number;
  tipo_vehiculo?: string; // default 'standard' en backend
}

/**
 * Response de calcular costo.
 * Ref: CalcularCostoResponse en viaje_schemas.py.
 *
 * ⚠️ El backend NO devuelve `moneda` en este endpoint (confirmado en OpenAPI).
 */
export interface CalcularCostoResponse {
  distancia_metros: number;
  tiempo_estimado_segundos: number;
  precio_estimado: number;
  tarifa_base: number;
  costo_km: number;
  costo_minuto: number;
}

/**
 * Response de reverse geocoding.
 * Ref: ReverseGeocodeResponse en app/routers/viajes/schemas.py.
 *
 * `fuente` indica de dónde vino la dirección:
 *   - "google": se consultó la API de Google (o se consultó y funcionó).
 *   - "cache": se sirvió del cache en memoria del backend (TTL 1h).
 *   - "fallback": Google falló, se devolvieron coordenadas formateadas.
 */
export interface ReverseGeocodeResponse {
  direccion: string;
  lat: number;
  lng: number;
  fuente: 'google' | 'cache' | 'fallback';
}


/**
 * Response del endpoint de mapa estático.
 * Ref: MapaEstaticoResponse en app/routers/viajes/schemas.py.
 *
 * `url` apunta a Google Static Maps con marcadores A (origen) y B (destino)
 * ya configurados. Se consume directo en <Image source={{ uri: url }} />.
 */
export interface MapaEstaticoResponse {
  url: string;
}


/**
 * Destino seleccionado desde Google Places Autocomplete.
 * Reemplaza al mock de coordenadas aleatorias (deuda G21).
 *
 * - `direccion`: formatted_address de Google (ej. "Catamarca 375, San Miguel de Tucumán").
 * - `lat`, `lng`: coordenadas exactas del lugar.
 * - `place_id`: ID estable de Google para el lugar.
 */
export interface DestinoSeleccionado {
  direccion: string;
  lat: number;
  lng: number;
  place_id: string;
}

/**
 * Request para cancelar viaje.
 */
export interface CancelarViajeRequest {
  motivo?: string;
}

/**
 * Request/response para calificar viaje.
 */
export interface CalificarViajeRequest {
  puntaje: number; // 1-5
  comentario?: string;
}

export interface CalificarViajeResponse {
  success: boolean;
  message: string;
}

/**
 * Item del historial de viajes.
 * Ref: HistorialViajeResponse en viaje_schemas.py.
 */
export interface HistorialViajeItem {
  id: string;
  origen: string;
  destino: string | null;
  precio_final: number | null;
  estado: EstadoViaje;
  creado_en: string;
  calificacion_dada: number | null;
}

/**
 * Response de los endpoints de ciclo de vida (aceptar, rechazar, iniciar,
 * finalizar, cancelar).
 * Forma estándar: { success, message }.
 */
export interface AccionViajeResponse {
  success: boolean;
  message: string;
}
// ============================================================
// FINALIZAR VIAJE (M3 - G44)
// ============================================================

/**
 * Respuesta del endpoint POST /api/viajes/{id}/finalizar.
 * Incluye el precio final calculado por el motor unificado
 * y el desglose completo para trazabilidad.
 */
export interface FinalizarViajeResponse {
  success: boolean;
  message: string;
  viaje_id: string;
  precio_final: number;
  moneda: string;
  desglose: Record<string, unknown> | null;
  precio_calculado_con: 'motor_unificado' | 'fallback_estimado';
}