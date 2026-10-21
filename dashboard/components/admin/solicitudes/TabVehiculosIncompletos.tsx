// D:\aTaxip\dashboard\components\admin\solicitudes\TabVehiculosIncompletos.tsx
'use client';

import { Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { useVehiculosIncompletos } from '@/hooks/admin/useSolicitudesTenant';
import CardVehiculoIncompleto from './CardVehiculoIncompleto';

export default function TabVehiculosIncompletos() {
  const { data: incompletos = [], isLoading } = useVehiculosIncompletos();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (incompletos.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12 text-muted-foreground">
          <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-green-500/50" />
          <p className="text-lg font-medium">No hay vehículos incompletos</p>
          <p className="text-sm">Todos los vehículos tienen su documentación completa</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-yellow-800">
          Los vehículos con documentación incompleta <strong>no pueden ser aprobados</strong>.
          El propietario debe completarlos antes de enviarlos a revisión.
        </p>
      </div>

      {incompletos.map((vehiculo) => (
        <CardVehiculoIncompleto
          key={vehiculo.vehiculo_id}
          vehiculo={vehiculo}
        />
      ))}
    </div>
  );
}