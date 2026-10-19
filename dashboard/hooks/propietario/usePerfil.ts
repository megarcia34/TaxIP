// D:\ataxip\dashboard\hooks\propietario\usePerfil.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { perfilAPI, PerfilUpdate } from '@/lib/api/perfil';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';

export function usePerfil() {
  return useQuery({
    queryKey: ['propietario-perfil'],
    queryFn: () => perfilAPI.get(),
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: false,
  });
}

export function useUpdatePerfil() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PerfilUpdate) => perfilAPI.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['propietario-perfil'] });
      toast.success('Perfil actualizado correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useCiudadesOperativas() {
  return useQuery({
    queryKey: ['ciudades-operativas'],
    queryFn: () => perfilAPI.getCiudadesOperativas(),
    staleTime: 1000 * 60 * 60,
    refetchOnWindowFocus: false,
  });
}