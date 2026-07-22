'use client'
import { useSession } from 'next-auth/react'
import { useAuthStore } from '@/store/authStore'
import { useEffect } from 'react'

export interface TenantConfig {
  modo_calculo: string;
  moneda: string;
  tarifa_base: number;
  recargo_nocturno: number;
  hora_inicio_nocturno: string;
  hora_fin_nocturno: string;
  recargo_domingo: number;
}

async function loadTenantConfig(accessToken: string): Promise<TenantConfig | null> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/tarifas/mi-tenant`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) return null;
    const data = await response.json();
    return {
      modo_calculo: data.modo_calculo,
      moneda: data.moneda,
      tarifa_base: data.tarifa_base,
      recargo_nocturno: data.recargo_nocturno,
      hora_inicio_nocturno: data.hora_inicio_nocturno,
      hora_fin_nocturno: data.hora_fin_nocturno,
      recargo_domingo: data.recargo_domingo,
    };
  } catch (error) {
    return null;
  }
}

export function useAuth() {
  const { data: session, status } = useSession()
  const { user, setUser, logout } = useAuthStore()

  useEffect(() => {
    if (session?.user) {
      const role = session.user.role?.toLowerCase()
      const controlBaseId = session.user.controlBaseId || session.user.control_base_id || null

      if (role === 'empleado' && !session.user.empresaNombre) {
        fetch('/api/empresa/mi-empresa', {
          headers: { Authorization: `Bearer ${session.user.accessToken}` }
        })
          .then(res => res.ok ? res.json() : null)
          .then(async (data) => {
            let tenantConfig = undefined;
            if (controlBaseId) tenantConfig = await loadTenantConfig(session.user.accessToken);
            
            setUser({
              id: session.user.id,
              email: session.user.email || '',
              nombre: session.user.name || '',
              rol: session.user.role as string,
              accessToken: session.user.accessToken,
              refreshToken: session.user.refreshToken,
              totalVehiculos: session.user.totalVehiculos,
              vehiculos: session.user.vehiculos,
              control_base_id: controlBaseId,
              empresaNombre: data?.nombre ?? session.user.empresaNombre ?? undefined,
              empresaId: data?.id ?? session.user.empresaId ?? undefined,
              tenantConfig: tenantConfig ?? undefined, // ✅ CORREGIDO
            })
          })
          .catch(async () => {
            let tenantConfig = undefined;
            if (controlBaseId) tenantConfig = await loadTenantConfig(session.user.accessToken);
            
            setUser({
              id: session.user.id,
              email: session.user.email || '',
              nombre: session.user.name || '',
              rol: session.user.role as string,
              accessToken: session.user.accessToken,
              refreshToken: session.user.refreshToken,
              totalVehiculos: session.user.totalVehiculos,
              vehiculos: session.user.vehiculos,
              control_base_id: controlBaseId,
              empresaNombre: session.user.empresaNombre ?? undefined,
              empresaId: session.user.empresaId ?? undefined,
              tenantConfig: tenantConfig ?? undefined, // ✅ CORREGIDO
            })
          })
      } else {
        const loadConfig = async () => {
          let tenantConfig = undefined;
          if (role === 'admin' && controlBaseId) {
            tenantConfig = await loadTenantConfig(session.user.accessToken);
          }
          setUser({
            id: session.user.id,
            email: session.user.email || '',
            nombre: session.user.name || '',
            rol: session.user.role as string,
            accessToken: session.user.accessToken,
            refreshToken: session.user.refreshToken,
            totalVehiculos: session.user.totalVehiculos,
            vehiculos: session.user.vehiculos,
            control_base_id: controlBaseId,
            empresaNombre: session.user.empresaNombre ?? undefined,
            empresaId: session.user.empresaId ?? undefined,
            tenantConfig: tenantConfig ?? undefined, // ✅ CORREGIDO
          })
        };
        loadConfig();
      }
    } else if (status === 'unauthenticated') {
      logout()
    }
  }, [session, status, setUser, logout])

  return {
    user,
    isAuthenticated: !!user,
    isLoading: status === 'loading',
    logout,
  }
}