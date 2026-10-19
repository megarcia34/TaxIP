// D:\ataxip\dashboard\hooks\propietario\useMetricasFallbacks.ts
'use client';

import { useQuery } from '@tanstack/react-query';
import { metricasPropietarioAPI } from '@/lib/api/metricasPropietario';

export function useMetricasFallbacks() {
  return useQuery({
    queryKey: ['propietario-metricas-fallbacks'],
    queryFn: () => metricasPropietarioAPI.getFallbacks(),
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: false,
  });
}