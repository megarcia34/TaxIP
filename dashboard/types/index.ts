// Tipos compartidos para el dashboard

export interface User {
  id: string
  email: string
  nombre: string
  rol: string  // admin, operador, propietario, empleado, pasajero
  telefono?: string
  foto?: string
  accessToken?: string
  refreshToken?: string
  totalVehiculos?: number
  vehiculos?: Vehiculo[]
  empresaNombre?: string
  empresaId?: string
  
  // ✅ Propiedades de NextAuth (por compatibilidad)
  name?: string
  role?: string
  image?: string | null
  
  // ✅ Propiedades faltantes que causaron los errores
  control_base_id?: string | null
  controlBaseId?: string | null
  tipo_usuario?: string
  
  // ✅ CORREGIDO: Acepta cualquier estructura de configuración del backend (incluyendo null o undefined)
  tenantConfig?: any
}

export interface Chofer {
  id: string
  nombre: string
  email: string
  telefono: string
  estado_laboral: 'activo' | 'inactivo' | 'vacaciones'
  calificacion_promedio: number
  total_viajes: number
  vehiculo_id?: string
  foto?: string
  latitud?: number
  longitud?: number
}

export interface Vehiculo {
  id: string
  patente: string
  marca: string | null
  modelo: string | null
  año: number | null
  color?: string
  licencia?: string
  capacidad?: number
  propietario_id: string
  chofer_id?: string
  foto?: string
  porcentaje_participacion?: number
  fecha_inicio?: string
}

export interface Viaje {
  id: string
  estado: 'pendiente' | 'asignado' | 'en_curso' | 'completado' | 'cancelado'
  origen: string
  destino: string
  origen_lat: number
  origen_lng: number
  destino_lat: number
  destino_lng: number
  precio_estimado: number
  precio_final?: number
  distancia_km?: number
  duracion_min?: number
  pasajero_id: string
  pasajero_nombre: string
  chofer_id?: string
  chofer_nombre?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface SolicitudViaje {
  id: string
  estado: 'pendiente' | 'aceptada' | 'cancelada'
  origen: string
  destino: string
  pasajero_id: string
  pasajero_nombre: string
  created_at: string
}

export interface ChoferOnline {
  id: string
  nombre: string
  patente: string
  latitud: number
  longitud: number
  estado: 'libre' | 'ocupado'
  calificacion: number
  foto?: string
}

export interface Estadisticas {
  total_choferes_activos: number
  viajes_hoy: number
  ingresos_dia: number
  calificacion_promedio: number
  viajes_semana: number[]
  ingresos_semana: number[]
}

export interface RankingChofer {
  id: string
  nombre: string
  foto?: string
  total_viajes: number
  calificacion_promedio: number
  ingresos_totales: number
}

export interface ObjetoOlvidado {
  id: string
  viaje_id: string
  descripcion: string
  estado: 'reportado' | 'encontrado' | 'entregado'
  reportado_por: string
  fecha_reporte: string
  fecha_entrega?: string
}

export interface GastoVehiculo {
  id: string
  vehiculo_id: string
  tipo: 'combustible' | 'mantenimiento' | 'seguro' | 'impuesto' | 'otro'
  monto: number
  descripcion: string
  fecha: string
  kilometraje?: number
}

export interface MantenimientoVehiculo {
  id: string
  vehiculo_id: string
  tipo: 'reparacion' | 'service' | 'neumaticos' | 'otros'
  descripcion: string
  costo: number
  taller: string
  fecha: string
  proximo_servicio_km?: number
}

export interface ConfiguracionTarifas {
  tarifa_base: number
  precio_por_km: number
  precio_por_minuto: number
  recargo_nocturno: number
  recargo_feriado: number
  tarifa_minima: number
}

// ========== NUEVOS TIPOS PARA PROPIETARIOS ==========
export interface Propietario {
  id: string
  usuario_id: string
  nombre: string
  email: string
  telefono: string
  estado: 'activo' | 'inactivo'
  total_vehiculos: number
  total_contratos: number
  fecha_registro: string
  vehiculos?: Array<{
    id: string
    patente: string
    marca: string
    modelo: string
  }>
}

export interface PropietarioVehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  año: number
  color: string
  chofer_id?: string
  chofer_nombre?: string
  contrato_activo: boolean
  porcentaje_participacion: number
}

export interface PropietarioContrato {
  id: string
  vehiculo_id: string
  patente: string
  marca: string
  modelo: string
  chofer_id: string
  chofer_nombre: string
  chofer_apellido: string
  tipo_contrato: 'AUTO_GESTION' | 'PORCENTAJE' | 'CANON_FIJO'
  turno_asignado: 'DIURNO' | 'NOCTURNO' | 'COMPLETO'
  porcentaje_chofer?: number
  monto_diario?: number
  fecha_inicio: string
  fecha_fin?: string
  activo: boolean
}

export interface PropietarioGasto {
  id: string
  vehiculo_id: string
  patente: string
  categoria: 'combustible' | 'lubricantes' | 'seguros' | 'impuestos' | 'reparaciones' | 'mantenimiento' | 'lavado' | 'peajes' | 'neumaticos' | 'otros'
  monto: number
  descripcion: string
  fecha: string
  kilometraje?: number
  comprobante?: string
}

export interface PropietarioMantenimiento {
  id: string
  vehiculo_id: string
  patente: string
  tipo: 'service_menor' | 'service_mayor' | 'neumaticos' | 'frenos' | 'distribucion' | 'cambio_aceite' | 'otros'
  descripcion: string
  costo: number
  taller: string
  fecha: string
  kilometraje: number
  proximo_servicio_km?: number
  comprobante?: string
}

export interface PropietarioIngreso {
  id: string
  vehiculo_id: string
  patente: string
  tipo: 'viaje' | 'recaudacion_manual' | 'canon'
  monto: number
  descripcion: string
  fecha: string
  metodo_pago?: 'efectivo' | 'tarjeta' | 'transferencia'
  referencia?: string
}

export interface PropietarioResumenFinanciero {
  ingresos_totales: number
  gastos_totales: number
  ganancia_neta: number
  margen_ganancia: number
  ingreso_promedio_vehiculo: number
  flujo_efectivo: {
    electronico: number
    manual: number
  }
  periodo: {
    desde: string
    hasta: string
  }
}

export interface PropietarioRentabilidad {
  vehiculo_id: string
  patente: string
  marca: string
  modelo: string
  ingresos: number
  gastos: number
  ganancia: number
  margen: number
  viajes: number
  calificacion_promedio: number
}

export interface PropietarioAlerta {
  id: string
  tipo: 'mantenimiento' | 'documento' | 'contrato'
  vehiculo_id: string
  patente: string
  mensaje: string
  urgencia: 'alta' | 'media' | 'baja'
  fecha_limite: string
  leida: boolean
}

// ============================================================
// NEUMÁTICOS
// ============================================================

export interface Neumatico {
  id: string
  codigo_interno: string
  marca: string
  modelo_dibujo: string | null
  medida: string | null
  tipo_neumatico: 'RADIAL' | 'BIAS' | 'TUBELESS' | 'RUN_FLAT' | 'TODO_TERRENO'
  estado: 'ACTIVO' | 'BAJA' | 'DESECHADO'
  vehiculo_id: string
  patente: string
  posicion_actual: 'DI' | 'DD' | 'TI' | 'TD' | 'REPUESTO' | null
  km_totales_acumulados: number
  km_en_posicion_actual: number | null
  fecha_alta: string
  fecha_baja: string | null
  ultima_profundidad_mm: number | null
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO'
  ultima_medicion_fecha: string | null
  observaciones?: string | null
  
  // ✅ HISTORIAL DE POSICIONES - Agregado para DetalleNeumaticoModal
  historial_posiciones?: {
    eje: string
    km_montaje: number
    km_desmontaje: number | null
    fecha_montaje: string
    fecha_desmontaje: string | null
  }[]
  
  // ✅ MEDICIONES - Agregado para DetalleNeumaticoModal
  mediciones?: {
    id: string
    fecha: string
    profundidad_mm: number
    estado_color: 'VERDE' | 'AMARILLO' | 'ROJO'
    medido_por: string | null
    observaciones: string | null
  }[]
  
  // ✅ OPERACIONES - Agregado para DetalleNeumaticoModal
  operaciones?: {
    tipo: string
    fecha: string
    km_vehiculo: number
    descripcion: string | null
  }[]
}

export interface NeumaticoActivo {
  id: string
  codigo_interno: string
  marca: string
  modelo_dibujo: string | null
  medida: string | null
  km_montaje: number
  km_recorridos: number
  ultima_profundidad_mm: number | null
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO'
  sugerencia: string | null
}

export interface NeumaticosActivosResponse {
  vehiculo_id: string
  patente: string
  vehiculo_marca: string
  vehiculo_modelo: string
  neumaticos: {
    DI: NeumaticoActivo
    DD: NeumaticoActivo
    TI: NeumaticoActivo
    TD: NeumaticoActivo
  }
  resumen: {
    verde: number
    amarillo: number
    rojo: number
  }
}

export interface MedicionRequest {
  profundidad_mm: number
  observaciones?: string
}

export interface MedicionResponse {
  mensaje: string
  medicion_id: string
  profundidad_mm: number
  estado_color: 'VERDE' | 'AMARILLO' | 'ROJO'
  interpretacion: string
  sugerencia_generada: string | null
}

export interface OperacionNeumatico {
  id: string
  tipo: string
  fecha: string
  km_vehiculo: number
  descripcion: string
  neumaticos_afectados: string[]
}

export interface SugerenciaNeumatico {
  id: string
  tipo: string
  mensaje: string
  prioridad: 'ALTA' | 'MEDIA' | 'BAJA'
  color: 'ROJO' | 'AMARILLO' | 'VERDE'
  km_actual: number
  km_umbral: number
  estado: 'PENDIENTE' | 'VISTA' | 'ACCIONADA' | 'DESESTIMADA'
  fecha_generacion: string
  fecha_atendida: string | null
  neumatico: string | null
  posicion: string | null
  dias_activa: number
}

export interface ConfiguracionNeumaticos {
  control_base_id: string
  vida_util_km: number
  umbral_rotacion_km: number
  umbral_cambio_km: number
  profundidad_minima_mm: number
  factor_desgaste_delantero: number
  colores: {
    verde: { desde_mm: number; estado: string }
    amarillo: { desde_mm: number; hasta_mm: number; estado: string }
    rojo: { hasta_mm: number; estado: string }
  }
  ultima_actualizacion: string
}

export interface NeumaticoImagen {
  id: string
  url: string
  secure_url: string
  tipo_imagen: 'NEUMATICO' | 'OPERACION' | 'DANO' | 'MEDICION' | 'INVENTARIO' | 'OTRO'
  descripcion: string | null
  peso_bytes: number
  dimensiones: string | null
  fecha_subida: string
  subido_por: string | null
}