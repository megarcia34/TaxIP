'use client'

import { useSession } from 'next-auth/react'
import { useAuthStore } from '@/store/authStore'
import { useEffect } from 'react'

// ✅ Interface extendida para tenantConfig
export interface TenantConfig {
  modo_calculo: string;
  moneda: string;
  tarifa_base: number;
  recargo_nocturno: number;
  hora_inicio_nocturno: string;
  hora_fin_nocturno: string;
  recargo_domingo: number;
}

// ✅ Función para cargar configuración del tenant
async function loadTenantConfig(accessToken: string): Promise<TenantConfig | null> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/tarifas/mi-tenant`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      console.warn('No se pudo cargar configuración del tenant:', response.status);
      return null;
    }
    
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
    console.warn('Error cargando configuración del tenant:', error);
    return null;
  }
}

export function useAuth() {
  const { data: session, status } = useSession()
  const { user, setUser, logout } = useAuthStore()

  useEffect(() => {
    if (session?.user) {
      console.log('🔐 [useAuth] Session user:', session.user)
      console.log('🔐 [useAuth] Role:', session.user.role)
      
      const role = session.user.role?.toLowerCase()
      let empresaNombre = session.user.empresaNombre
      let empresaId = session.user.empresaId

      // ✅ Obtener control_base_id de la sesión (con fallback)
      const controlBaseId = session.user.controlBaseId || session.user.control_base_id || null

      // Si es empleado y no tiene empresa, obtenerla
      if (role === 'empleado' && !empresaNombre) {
        fetch('/api/empresa/mi-empresa', {
          headers: {
            Authorization: `Bearer ${session.user.accessToken}`
          }
        })
          .then(res => {
            if (res.ok) {
              return res.json()
            }
            return null
          })
          .then(async (data) => {
            let tenantConfig = undefined;
            // ✅ Usar controlBaseId en lugar de session.user?.controlBaseId
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
              // ✅ Asignar control_base_id correctamente
              control_base_id: controlBaseId,
              empresaNombre: data?.nombre ?? session.user.empresaNombre ?? undefined,
              empresaId: data?.id ?? session.user.empresaId ?? undefined,
              tenantConfig: tenantConfig,
            })
          })
          .catch(async () => {
            let tenantConfig = undefined;
            // ✅ Usar controlBaseId en lugar de session.user?.controlBaseId
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
              // ✅ Asignar control_base_id correctamente
              control_base_id: controlBaseId,
              empresaNombre: session.user.empresaNombre ?? undefined,
              empresaId: session.user.empresaId ?? undefined,
              tenantConfig: tenantConfig,
            })
          })
      } else {
        // ✅ Si es Admin Tenant, cargar configuración
        const loadConfig = async () => {
          let tenantConfig = undefined;
          // ✅ Usar controlBaseId en lugar de session.user?.controlBaseId
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
            // ✅ Asignar control_base_id correctamente
            control_base_id: controlBaseId,
            empresaNombre: session.user.empresaNombre ?? undefined,
            empresaId: session.user.empresaId ?? undefined,
            tenantConfig: tenantConfig,
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