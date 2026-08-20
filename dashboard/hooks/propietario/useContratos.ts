import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { propietarioAPI } from '@/lib/api';
import { toast } from 'sonner';

// Tipos (copiados de page.tsx o creados en types/)
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

export function useContratos(filterActivo?: boolean | null) {
  return useQuery({
    queryKey: ['contratos', filterActivo],
    queryFn: () => propietarioAPI.getContratos(filterActivo ?? undefined),
    staleTime: 60000, // 1 minuto
    refetchOnWindowFocus: false,
    enabled: true,
  });
}

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