export type TipoDocumento = 'dni' | 'licencia' | 'sanidad' | 'buena_conducta';

export type EstadoDocumento = 'pendiente' | 'cargado' | 'subiendo' | 'rechazado';

export interface DocumentoConfig {
  tipo: TipoDocumento;
  nombre: string;
  icono: string;
  requiereVencimiento: boolean;
  bloqueante: boolean;
}

export interface DocumentoSubido {
  tipo: TipoDocumento;
  url: string;
  fechaVencimiento?: string;
  estado: EstadoDocumento;
}