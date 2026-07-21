// ============================================
// AUTH TYPES
// ============================================

export interface User {
  id: string;
  email: string;
  tipo_usuario: string;
  nombre_completo?: string;
  control_base_id?: string | null;
  accessToken?: string;
  refreshToken?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  access_token: string;
  refresh_token: string;
  user_id: string;
  email: string;
  tipo_usuario: string;
  nombre_completo: string;
  control_base_id?: string | null;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  apellido: string;
  telefono?: string;
  tipo: "pasajero" | "chofer" | "propietario";
}

export interface RegisterResponse {
  success: boolean;
  user_id: string;
  email: string;
  message: string;
}

// ============================================
// BOOKING TYPES
// ============================================

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface Address {
  address: string;
  coordinates: Coordinates;
}

export interface Waypoint {
  address: string;
  coordinates?: Coordinates;
}

export interface BookingRequest {
  empresa_id?: string;
  pasajero_nombre: string;
  pasajero_telefono?: string;
  direccion_origen: string;
  latitud_origen: number;
  longitud_origen: number;
  direccion_destino: string;
  latitud_destino: number;
  longitud_destino: number;
  paradas_intermedias: Waypoint[];
  tipo_vehiculo: string;
  nota_conductor?: string;
  metodo_pago: string;
  cantidad_pasajeros: number;
  cantidad_equipaje: number;
  es_programado?: boolean;
  fecha_programada?: string;
}

export interface BookingResponse {
  id: string;
  estado: string;
  precio_estimado: number;
  created_at: string;
}

export interface PriceEstimateRequest {
  direccion_origen: string;
  latitud_origen: number;
  longitud_origen: number;
  direccion_destino: string;
  latitud_destino: number;
  longitud_destino: number;
  paradas_intermedias?: Waypoint[];
  tipo_vehiculo?: string;
}

export interface PriceEstimateResponse {
  precio_estimado: number;
  distancia_km: number;
  tiempo_minutos: number;
  desglose?: {
    tarifa_base: number;
    precio_por_km: number;
    precio_por_minuto: number;
    recargo_nocturno?: number;
  };
}

export interface BookingStatus {
  id: string;
  estado: "reservado" | "despachado" | "vehiculo_llego" | "pasajero_a_bordo" | "completado" | "cancelado";
  precio_estimado: number;
  precio_final?: number;
  chofer?: {
    nombre: string;
    telefono: string;
    vehiculo: string;
    patente: string;
  };
  created_at: string;
  updated_at: string;
}

// ============================================
// DRIVER TYPES
// ============================================

export interface Driver {
  id: string;
  nombre: string;
  apellido: string;
  telefono: string;
  estado_laboral: "libre" | "ocupado" | "fuera_de_servicio";
  latitud: number;
  longitud: number;
  calificacion_promedio: number;
  vehiculo: {
    patente: string;
    marca: string;
    modelo: string;
  };
}

// ============================================
// COMPANY TYPES
// ============================================

export interface Company {
  id: string;
  nombre: string;
  tipo: "hotel" | "empresa" | "institucion";
  direccion: string;
  latitud: number;
  longitud: number;
  telefono: string;
  email_facturacion: string;
}