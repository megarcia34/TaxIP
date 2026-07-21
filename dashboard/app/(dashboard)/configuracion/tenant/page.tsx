// D:\ataxip\dashboard\app\(dashboard)\configuracion\tenant\page.tsx
'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'

export default function ConfiguracionTenantPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Datos del Municipio</h1>

      <Card>
        <CardHeader>
          <CardTitle>Información del Tenant</CardTitle>
          <CardDescription>
            Configuración general de {user?.tenantConfig?.nombre || 'tu municipio'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Nombre del Municipio</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {user?.tenantConfig?.nombre || 'No configurado'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">ID del Tenant</label>
                <p className="text-sm text-muted-foreground font-mono mt-1">
                  {user?.control_base_id || 'No asignado'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Modo de Cálculo</label>
                <p className="text-sm text-muted-foreground mt-1 capitalize">
                  {user?.tenantConfig?.modo_calculo || 'No configurado'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Moneda</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {user?.tenantConfig?.moneda || 'ARS'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Tarifa Base</label>
                <p className="text-sm text-muted-foreground mt-1">
                  ${user?.tenantConfig?.tarifa_base?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Recargo Nocturno</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {user?.tenantConfig?.recargo_nocturno || '1.0'}x
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Horario Nocturno</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {user?.tenantConfig?.hora_inicio_nocturno || '22:00'} -{' '}
                  {user?.tenantConfig?.hora_fin_nocturno || '06:00'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Recargo Domingo</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {user?.tenantConfig?.recargo_domingo || '1.0'}x
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}