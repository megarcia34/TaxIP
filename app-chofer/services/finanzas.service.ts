import api from '@/services/api';

export interface TurnoFinanzas {
  id: string;
  estado: 'ACTIVO' | 'CERRADO' | 'PENDIENTE_CONFIRMACION';
  inicioTurno: string | null;
  finTurno: string | null;
  kmRecorridos: number | null;
  duracionMinutos: number;
  vehiculo: { patente: string; marca: string; modelo: string };
}

export interface ResumenFinanzasTotales {
  totalViajes: number;
  recaudacionTotal: number;
  recaudacionPorMetodo: Record<string, number>;
  gastosTotal: number;
  ingresosManuales: number;
  comisionPropietario: number;
  comisionEstimada: boolean;
  utilidadNeta: number;
}

export interface ViajeFinanzas {
  hora: string | null;
  origen: string;
  destino: string;
  monto: number;
  metodoPago: string;
}

export interface GastoFinanzas {
  hora: string | null;
  tipo: string;
  monto: number;
  descripcion: string;
  urlComprobante: string | null; // <-- AGREGADO para la foto
}

export interface IngresoFinanzas {
  hora: string | null;
  tipo: string;
  monto: number;
  descripcion: string;
}

export interface LiquidacionFinanzas {
  montoBruto: number;
  comisionChofer: number;
  utilidadPropietario: number;
  totalGastos: number;
  estado: string;
}

export interface ResumenFinanzas {
  turno: TurnoFinanzas | null;
  resumen: ResumenFinanzasTotales;
  viajes: ViajeFinanzas[];
  gastos: GastoFinanzas[];
  ingresos: IngresoFinanzas[];
  liquidacion: LiquidacionFinanzas | null;
}

export const finanzasService = {
  async obtenerResumen(): Promise<ResumenFinanzas> {
    const response = await api.get<ResumenFinanzas>('/api/chofer/finanzas/resumen');
    return response.data;
  },
};

// ============================================
// SERVICIO PARA CARGAR GASTOS CON FOTO
// ============================================
export const gastosService = {
  async registrarGasto(
    turnoId: string,
    tipo: string,
    monto: number,
    imagenUri: string | null
  ): Promise<void> {
    const formData = new FormData();
    formData.append('turno_id', turnoId);
    formData.append('tipo_gasto', tipo.toUpperCase());
    formData.append('monto', monto.toString());

    if (imagenUri) {
      const filename = imagenUri.split('/').pop() || 'comprobante.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image/jpeg`;
      
      // @ts-ignore - React Native FormData acepta este formato especial
      formData.append('file', {
        uri: imagenUri,
        name: filename,
        type: type,
      });
    }

    await api.post('/api/choferes/turnos/gasto', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};