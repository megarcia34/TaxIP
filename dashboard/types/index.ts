// Tipos compartidos para el dashboard

export interface User {
  id: string
  email: string
  nombre: string
  rol: string  // ← CAMBIADO: acepta cualquier string (admin, operador, propietario, empleado, pasajero)
  telefono?: string
  foto?: string
  accessToken?: string
  refreshToken?: string
  totalVehiculos?: number
  vehiculos?: Vehiculo[]
  empresaNombre?: string  // ← NUEVO: para empleados
  empresaId?: string      // ← NUEVO: para empleados
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