import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { propietarioAPI } from '@/lib/api';
import { toast } from 'sonner';

// Tipos
interface Contrato {
  id: string;
  vehiculo_id: string;
  patente: string;
  // ... todos los campos
}

interface CrearContratoData {
  vehiculo_id: string;
  chofer_id: string;
  tipo_contrato: string;
  // ... todos los campos del formulario
}

// ============================================================
// LISTAR CONTRATOS
// ============================================================
export function useContratos(filterActivo?: boolean | null) {
  return useQuery({
    queryKey: ['contratos', filterActivo],
    queryFn: () => propietarioAPI.getContratos(filterActivo ?? undefined),
    staleTime: 60000,
    refetchOnWindowFocus: false,
    enabled: true,
  });
}

// ============================================================
// CREAR CONTRATO
// ============================================================
export function useCrearContrato() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CrearContratoData) => propietarioAPI.createContrato(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast.success('Contrato creado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al crear contrato');
    },
  });
}

// ============================================================
// EDITAR CONTRATO (NUEVO - CORREGIDO)
// ============================================================
export function useEditarContrato() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      // Usamos la misma estructura de propietarioAPI o hacemos la llamada directa
      const response = await propietarioAPI.editarContrato(id, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast.success('Contrato actualizado correctamente');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al actualizar contrato');
    },
  });
}

// ============================================================
// FINALIZAR CONTRATO
// ============================================================
export function useFinalizarContrato() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (contratoId: string) => propietarioAPI.finalizarContrato(contratoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast.success('Contrato finalizado');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al finalizar contrato');
    },
  });
}

// ============================================================
// CONFIGURAR CONTRATO PENDIENTE
// ============================================================
export function useConfigurarContrato() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ contratoId, data }: { contratoId: string; data: any }) =>
      propietarioAPI.configurarContrato(contratoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast.success('Contrato configurado exitosamente');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al configurar contrato');
    },
  });
}

// ============================================================
// GENERAR CÓDIGO DE INICIO DE TURNO
// ============================================================
import { contratosAccionesAPI } from '@/lib/api/contratosAcciones';

export function useGenerarCodigo() {
  return useMutation({
    mutationFn: ({ contratoId, diasValidez }: { contratoId: string; diasValidez?: number }) =>
      contratosAccionesAPI.generarCodigo(contratoId, diasValidez),
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Error al generar el codigo');
    },
  });
}