// D:\aTaxip\dashboard\app\(dashboard)\admin\solicitudes-pendientes\page.tsx
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ClipboardList } from 'lucide-react';
import {
  useChoferesPendientes,
  useVehiculosPendientes,
  useVehiculosIncompletos,
} from '@/hooks/admin/useSolicitudesTenant';
import TabChoferes from '@/components/admin/solicitudes/TabChoferes';
import TabVehiculos from '@/components/admin/solicitudes/TabVehiculos';
import TabVehiculosIncompletos from '@/components/admin/solicitudes/TabVehiculosIncompletos';

export default function SolicitudesPendientesPage() {
  const { data: choferes = [] } = useChoferesPendientes();
  const { data: vehiculos = [] } = useVehiculosPendientes();
  const { data: incompletos = [] } = useVehiculosIncompletos();

  const totalChoferes = choferes.length;
  const totalVehiculos = vehiculos.length;
  const totalIncompletos = incompletos.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardList className="h-6 w-6" />
            Solicitudes Pendientes
          </h1>
          <p className="text-muted-foreground">
            Revisa y aprueba las solicitudes de choferes y vehículos
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          {totalChoferes + totalVehiculos} pendientes
        </Badge>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="choferes" className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-md">
          <TabsTrigger value="choferes" className="gap-2">
            Choferes
            {totalChoferes > 0 && (
              <Badge className="bg-red-500 hover:bg-red-600 text-white text-xs px-1.5 py-0 h-5">
                {totalChoferes}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="vehiculos" className="gap-2">
            Vehículos
            {totalVehiculos > 0 && (
              <Badge className="bg-red-500 hover:bg-red-600 text-white text-xs px-1.5 py-0 h-5">
                {totalVehiculos}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="incompletos" className="gap-2">
            Incompletos
            {totalIncompletos > 0 && (
              <Badge variant="secondary" className="text-xs px-1.5 py-0 h-5">
                {totalIncompletos}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="choferes" className="mt-6">
          <TabChoferes />
        </TabsContent>

        <TabsContent value="vehiculos" className="mt-6">
          <TabVehiculos />
        </TabsContent>

        <TabsContent value="incompletos" className="mt-6">
          <TabVehiculosIncompletos />
        </TabsContent>
      </Tabs>
    </div>
  );
}