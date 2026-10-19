// D:\ataxip\dashboard\hooks\propietario\useCuentasCobro.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  cuentasCobroAPI,
  CuentaCobroCreate,
  CuentaCobroUpdate,
} from '@/lib/api/cuentasCobro';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';

const QUERY_KEY = ['propietario-cuentas-cobro'];

export function useCuentasCobro() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: () => cuentasCobroAPI.list(),
    staleTime: 1000 * 60 * 2,
    refetchOnWindowFocus: false,
  });
}

export function useCrearCuenta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CuentaCobroCreate) => cuentasCobroAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('Cuenta creada correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useActualizarCuenta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CuentaCobroUpdate }) =>
      cuentasCobroAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('Cuenta actualizada');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useEliminarCuenta() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => cuentasCobroAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('Cuenta eliminada');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useMarcarPredeterminada() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => cuentasCobroAPI.marcarPredeterminada(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('Cuenta marcada como predeterminada');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}