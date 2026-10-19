// D:\ataxip\dashboard\lib\api\postulacionChofer.ts
import { apiClient } from './client';

export type EstadoAprobacion =
  | 'pendiente'
  | 'en_revision'
  | 'aprobado'
  | 'rechazado';

export type TipoDocumentoChofer =
  | 'dni'
  | 'licencia'
  | 'buena_conducta'
  | 'antecedentes'
  | 'sanidad';

export interface DocumentoChofer {
  id: string;
  tipo_documento: TipoDocumentoChofer;
  url: string | null;
  numero: string | null;
  fecha_vencimiento: string | null;
  subido_en: string | null;
}

export interface EstadoPostulacion {
  estado_aprobacion: EstadoAprobacion;
  mensaje: string;
  documentos_subidos: number;
  documentos_requeridos: number;
  puede_manejar: boolean;
  motivo_rechazo?: string | null;
}

export interface MisDocumentosResponse {
  success: boolean;
  documentos: DocumentoChofer[];
}

export interface SubirDocumentoData {
  tipo_documento: TipoDocumentoChofer;
  numero?: string | null;
  fecha_vencimiento?: string | null;
  archivo: File;
}

export interface SubirDocumentoResponse {
  success: boolean;
  tipo_documento: string;
  url: string;
  message: string;
}

export const TIPOS_DOCUMENTO_REQUERIDOS: TipoDocumentoChofer[] = [
  'dni',
  'licencia',
  'buena_conducta',
  'antecedentes',
  'sanidad',
];

export const TIPOS_CON_VENCIMIENTO: TipoDocumentoChofer[] = [
  'licencia',
  'sanidad',
  'buena_conducta',
  'antecedentes',
];

export const postulacionChoferAPI = {
  getEstado: async (): Promise<EstadoPostulacion> => {
    const response = await apiClient.get('/chofer/estado-aprobacion');
    return response.data;
  },

  getMisDocumentos: async (): Promise<MisDocumentosResponse> => {
    const response = await apiClient.get('/chofer/mis-documentos');
    return response.data;
  },

  solicitar: async (): Promise<{ success: boolean; mensaje: string }> => {
    const response = await apiClient.post('/propietario/perfil/solicitar-ser-chofer');
    return response.data;
  },

  cancelar: async (): Promise<{ success: boolean; mensaje: string }> => {
    const response = await apiClient.post('/propietario/perfil/cancelar-postulacion-chofer');
    return response.data;
  },

  enviarARevision: async (): Promise<{ success: boolean; mensaje: string }> => {
    const response = await apiClient.post('/propietario/perfil/enviar-a-revision');
    return response.data;
  },

  subirDocumento: async (data: SubirDocumentoData): Promise<SubirDocumentoResponse> => {
    const formData = new FormData();
    formData.append('file', data.archivo);

    const params = new URLSearchParams();
    params.append('tipo_documento', data.tipo_documento);
    if (data.numero) params.append('numero', data.numero);
    if (data.fecha_vencimiento) params.append('fecha_vencimiento', data.fecha_vencimiento);

    const response = await apiClient.post(
      `/chofer/subir-documento?${params.toString()}`,
      formData
    );
    return response.data;
  },
};