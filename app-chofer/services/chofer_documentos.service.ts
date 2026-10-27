import api from './api';

export interface DocumentoChofer {
  id: string;
  tipo_documento: string;
  url: string;
  numero: string | null;
  fecha_vencimiento: string | null;
  subido_en: string | null;
}

export interface MisDocumentosResponse {
  success: boolean;
  documentos: DocumentoChofer[];
}

export interface SubirDocumentoParams {
  tipo_documento: string;
  fecha_vencimiento?: string; // Formato YYYY-MM-DD
  numero?: string;
  imagenUri: string;
}

export const choferDocumentosService = {
  async obtenerMisDocumentos(): Promise<DocumentoChofer[]> {
    const response = await api.get<MisDocumentosResponse>('/api/chofer/mis-documentos');
    return response.data.documentos;
  },

  async subirDocumento(params: SubirDocumentoParams): Promise<void> {
    const formData = new FormData();
    
    // El endpoint usa Query Params para tipo, fecha y numero, y FormData para el archivo.
    // Armamos la URL con los query params
    const queryParams = new URLSearchParams();
    queryParams.append('tipo_documento', params.tipo_documento.toLowerCase());
    if (params.fecha_vencimiento) queryParams.append('fecha_vencimiento', params.fecha_vencimiento);
    if (params.numero) queryParams.append('numero', params.numero);

    // Adjuntar el archivo (la foto)
    const filename = params.imagenUri.split('/').pop() || 'documento.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : `image/jpeg`;
    
    // @ts-ignore
    formData.append('file', {
      uri: params.imagenUri,
      name: filename,
      type: type,
    });

    await api.post(`/api/chofer/subir-documento?${queryParams.toString()}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};