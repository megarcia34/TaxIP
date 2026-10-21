// D:\aTaxip\dashboard\hooks\admin\useSolicitudesTenant.ts
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { solicitudesTenantAPI } from '@/lib/api/solicitudesTenant';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';

const KEY_CHOFERES = ['tenant-choferes-pendientes'];
const KEY_VEHICULOS = ['tenant-vehiculos-pendientes'];
const KEY_INCOMPLETOS = ['tenant-vehiculos-incompletos'];

// ============================================
// QUERIES (GET)
// ============================================

export function useChoferesPendientes(enabled: boolean = true) {
  return useQuery({
    queryKey: KEY_CHOFERES,
    queryFn: () => solicitudesTenantAPI.getChoferesPendientes(),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
    enabled,
  });
}

export function useVehiculosPendientes(enabled: boolean = true) {
  return useQuery({
    queryKey: KEY_VEHICULOS,
    queryFn: () => solicitudesTenantAPI.getVehiculosPendientes(),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
    enabled,
  });
}

export function useVehiculosIncompletos(enabled: boolean = true) {
  return useQuery({
    queryKey: KEY_INCOMPLETOS,
    queryFn: () => solicitudesTenantAPI.getVehiculosIncompletos(),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
    enabled,
  });
}

// ============================================
// HOOK DE CONTEO (para el badge del Sidebar)
// ============================================

/**
 * Hook especial para el sidebar: devuelve el total de solicitudes pendientes
 * (choferes + vehiculos, NO incluye incompletos).
 * 
 * Se activa solo si `enabled` es true (para no disparar queries en otros roles).
 */
export function useSolicitudesCount(enabled: boolean = false) {
  const choferes = useChoferesPendientes(enabled);
  const vehiculos = useVehiculosPendientes(enabled);

  const totalChoferes = choferes.data?.length ?? 0;
  const totalVehiculos = vehiculos.data?.length ?? 0;

  return {
    total: totalChoferes + totalVehiculos,
    choferes: totalChoferes,
    vehiculos: totalVehiculos,
    isLoading: choferes.isLoading || vehiculos.isLoading,
  };
}

// ============================================
// MUTATIONS (POST/PUT)
// ============================================

export function useAprobarChofer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => solicitudesTenantAPI.aprobarChofer(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY_CHOFERES });
      toast.success('Chofer aprobado correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useRechazarChofer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: string; motivo: string }) =>
       solicitudesTenantAPI.rechazarChofer(id, motivo),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY_CHOFERES });
      toast.success('Chofer rechazado');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useAprobarVehiculo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => solicitudesTenantAPI.aprobarVehiculo(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY_VEHICULOS });
      qc.invalidateQueries({ queryKey: KEY_INCOMPLETOS });
      toast.success('Vehiculo aprobado correctamente');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}

export function useRechazarVehiculo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: string; motivo: string }) =>
      solicitudesTenantAPI.rechazarVehiculo(id, motivo),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEY_VEHICULOS });
      qc.invalidateQueries({ queryKey: KEY_INCOMPLETOS });
      toast.success('Vehiculo rechazado');
    },
    onError: (error: any) => {
      toast.error(formatApiError(error));
    },
  });
}