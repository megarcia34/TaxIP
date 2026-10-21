// D:\aTaxip\dashboard\components\admin\solicitudes\TabChoferes.tsx
'use client';

import { useMemo } from 'react';
import { Loader2, UserCheck, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { useChoferesPendientes } from '@/hooks/admin/useSolicitudesTenant';
import CardChofer from './CardChofer';

export default function TabChoferes() {
  const { data: choferes = [], isLoading } = useChoferesPendientes();

  // ORDENAMIENTO: propietarios-choferes primero, despues por fecha (mas viejos primero)
  const ordenados = useMemo(() => {
    return [...choferes].sort((a, b) => {
      // Propietarios primero
      if (a.es_propietario !== b.es_propietario) {
        return a.es_propietario ? -1 : 1;
      }
      // Dentro del mismo grupo, por fecha de registro (mas viejo primero)
      return new Date(a.fecha_registro).getTime() - new Date(b.fecha_registro).getTime();
    });
  }, [choferes]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (ordenados.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12 text-muted-foreground">
          <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-green-500/50" />
          <p className="text-lg font-medium">No hay choferes pendientes</p>
          <p className="text-sm">Todos los choferes han sido revisados</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {ordenados.map((chofer) => (
        <CardChofer key={chofer.chofer_vehiculo_id} chofer={chofer} />
      ))}
    </div>
  );
}