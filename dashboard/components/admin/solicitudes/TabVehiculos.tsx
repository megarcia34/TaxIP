// D:\aTaxip\dashboard\components\admin\solicitudes\TabVehiculos.tsx
'use client';

import { Loader2, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { useVehiculosPendientes } from '@/hooks/admin/useSolicitudesTenant';
import CardVehiculo from './CardVehiculo';

export default function TabVehiculos() {
  const { data: vehiculos = [], isLoading } = useVehiculosPendientes();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (vehiculos.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12 text-muted-foreground">
          <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-green-500/50" />
          <p className="text-lg font-medium">No hay vehículos pendientes</p>
          <p className="text-sm">Todos los vehículos han sido revisados</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {vehiculos.map((vehiculo) => (
        <CardVehiculo key={vehiculo.vehiculo_id} vehiculo={vehiculo} />
      ))}
    </div>
  );
}