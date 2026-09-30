/**
 * Servicio de registro progresivo de choferes.
 */
import api from './api';

interface IniciarRegistroResponse {
  success: boolean;
  message: string;
  user_id: string;
  requiere_validacion_email: boolean;
  es_reanudacion?: boolean;
}

interface ValidarEmailResponse {
  success: boolean;
  access_token: string;
  user_id: string;
  message: string;
}

interface ActualizarDatosResponse {
  success: boolean;
  tenant_nombre: string;
  pasos_completados: {
    email: boolean;
    datos: boolean;
  };
}

interface SubirDocumentoResponse {
  success: boolean;
  tipo_documento: string;
  url: string;
  documentos_pendientes: string[];
}

interface VerificarDniResponse {
  existe: boolean;
  estado_aprobacion?: string;
  bloqueante?: boolean;
}

interface SubirSelfieResponse {
  success: boolean;
  estado_aprobacion: string;
  mensaje: string;
}

export const registroService = {
  /**
   * PASO 1: Iniciar registro (crear cuenta o reanudar).
   * POST /api/chofer/registro-progresivo/iniciar
   */
  async iniciarRegistro(
    email: string,
    password: string
  ): Promise<IniciarRegistroResponse> {
    const response = await api.post<IniciarRegistroResponse>(
      '/api/chofer/registro-progresivo/iniciar',
      { email, password }
    );
    return response.data;
  },

  /**
   * PASO 2: Validar email con código OTP.
   * POST /api/chofer/registro-progresivo/validar-email
   */
  async validarEmail(
    email: string,
    codigo: string
  ): Promise<ValidarEmailResponse> {
    const response = await api.post<ValidarEmailResponse>(
      '/api/chofer/registro-progresivo/validar-email',
      { email, codigo }
    );
    return response.data;
  },

  /**
   * PASO 3: Actualizar datos personales.
   * PUT /api/chofer/registro-progresivo/datos-personales
   */
  async actualizarDatos(datos: {
    nombre: string;
    apellido: string;
    dni: string;
    telefono: string;
    prestadora_id: string;
    direccion: string;
    ciudad_id: string;
    codigo_postal: string;
  }): Promise<ActualizarDatosResponse> {
    const response = await api.put<ActualizarDatosResponse>(
      '/api/chofer/registro-progresivo/datos-personales',
      datos
    );
    return response.data;
  },

  /**
   * PASO 3: Verificar si un DNI ya está registrado en un tenant.
   * GET /api/chofer/registro-progresivo/verificar-dni?dni=X&ciudad_id=Y
   */
  async verificarDni(
    dni: string,
    ciudadId: string
  ): Promise<VerificarDniResponse> {
    const params = new URLSearchParams();
    params.append('dni', dni);
    params.append('ciudad_id', ciudadId);

    const response = await api.get<VerificarDniResponse>(
      `/api/chofer/registro-progresivo/verificar-dni?${params.toString()}`
    );
    return response.data;
  },

  /**
   * PASO 4: Subir un documento al backend.
   * El backend lo sube a Cloudinary y guarda la URL.
   * POST /api/chofer/registro-progresivo/documento?tipo_documento=X&fecha_vencimiento=Y
   */
  async subirDocumento(
    uriLocal: string,
    tipoDocumento: string,
    fechaVencimiento?: string
  ): Promise<SubirDocumentoResponse> {
    const formData = new FormData();

    const filename = uriLocal.split('/').pop() || 'documento.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';

    // @ts-ignore - FormData en React Native
    formData.append('file', {
      uri: uriLocal,
      name: filename,
      type,
    });

    const params = new URLSearchParams();
    params.append('tipo_documento', tipoDocumento);
    if (fechaVencimiento) {
      const [dia, mes, anio] = fechaVencimiento.split('/');
      params.append('fecha_vencimiento', `${anio}-${mes}-${dia}`);
    }

    const response = await api.post<SubirDocumentoResponse>(
      `/api/chofer/registro-progresivo/documento?${params.toString()}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * PASO 5: Subir selfie (solo la URL, ya subida a Cloudinary desde el frontend).
   * POST /api/chofer/registro-progresivo/selfie
   */
  async subirSelfie(fotoUrl: string): Promise<SubirSelfieResponse> {
    const response = await api.post<SubirSelfieResponse>(
      '/api/chofer/registro-progresivo/selfie',
      { foto_url: fotoUrl }
    );
    return response.data;
  },
};