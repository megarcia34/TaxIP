import type { DocumentoConfig } from '@/types/documento.types';

export const DOCUMENTOS: DocumentoConfig[] = [
  {
    tipo: 'dni',
    nombre: 'DNI',
    icono: '🪪',
    requiereVencimiento: false,
    bloqueante: false,
  },
  {
    tipo: 'licencia',
    nombre: 'Licencia de Conducir',
    icono: '🚗',
    requiereVencimiento: true,
    bloqueante: true,
  },
  {
    tipo: 'sanidad',
    nombre: 'Carnet de Sanidad',
    icono: '🏥',
    requiereVencimiento: true,
    bloqueante: true,
  },
  {
    tipo: 'buena_conducta',
    nombre: 'Buena Conducta',
    icono: '📜',
    requiereVencimiento: true,
    bloqueante: true,
  },
];