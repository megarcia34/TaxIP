// D:\ataxip\dashboard\hooks\propietario\usePostulacionChofer.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  postulacionChoferAPI,
  SubirDocumentoData,
} from '@/lib/api/postulacionChofer';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';

const ESTADO_KEY = ['propietario-postulacion-chofer'];
const DOCS_KEY = ['propietario-mis-documentos-chofer'];

export function useEstadoPostulacion(enabled: boolean = true) {
  return useQuery({
    queryKey: ESTADO_KEY,
    queryFn: () => postulacionChoferAPI.getEstado(),
    enabled,
    staleTime: 1000 * 60 * 2,
    refetchOnWindowFocus: false,
  });
}

export function useMisDocumentos(enabled: boolean = true) {
  return useQuery({
    queryKey: DOCS_KEY,
    queryFn: () => postulacionChoferAPI.getMisDocumentos(),
    enabled,
    staleTime: 1000 * 60 * 2,
    refetchOnWindowFocus: false,
  });
}

export function useSolicitarSerChofer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => postulacionChoferAPI.solicitar(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ESTADO_KEY });
      toast.success('Postulacion iniciada. Ya podes cargar tus documentos.');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useCancelarPostulacion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => postulacionChoferAPI.cancelar(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ESTADO_KEY });
      queryClient.invalidateQueries({ queryKey: DOCS_KEY });
      toast.success('Postulacion cancelada');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useSubirDocumentoChofer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SubirDocumentoData) => postulacionChoferAPI.subirDocumento(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ESTADO_KEY });
      queryClient.invalidateQueries({ queryKey: DOCS_KEY });
      toast.success('Documento subido correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useEnviarARevision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => postulacionChoferAPI.enviarARevision(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ESTADO_KEY });
      queryClient.invalidateQueries({ queryKey: DOCS_KEY });
      toast.success('Enviado a revision correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error), { duration: 10000 });
    },
  });
}