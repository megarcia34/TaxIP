// D:\ataxip\dashboard\hooks\propietario\useVehiculosRevision.ts
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { postulacionChoferAPI } from '@/lib/api/postulacionChofer';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';

export function useEnviarVehiculosARevision() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => postulacionChoferAPI.enviarARevision(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] });
      queryClient.invalidateQueries({ queryKey: ['vehiculo'] });
      queryClient.invalidateQueries({ queryKey: ['vehiculo-estado'] });
      queryClient.invalidateQueries({ queryKey: ['propietario-postulacion-chofer'] });
      toast.success('Vehiculos enviados a revision correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error), { duration: 10000 });
    },
  });
}