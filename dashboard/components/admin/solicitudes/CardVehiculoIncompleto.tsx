// D:\aTaxip\dashboard\components\admin\solicitudes\CardVehiculoIncompleto.tsx
'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Car,
  User,
  Phone,
  AlertTriangle,
  FileText,
  Lock,
} from 'lucide-react';
import type { VehiculoIncompleto } from '@/lib/api/solicitudesTenant';

interface Props {
  vehiculo: VehiculoIncompleto;
}

const DOCS_LABELS: Record<string, string> = {
  SEGURO: 'Seguro',
  VTV: 'VTV',
  CEDULA_VERDE: 'Cédula Verde',
  HABILITACION: 'Habilitación',
};

export default function CardVehiculoIncompleto({ vehiculo }: Props) {
  const propietarioNombre = `${vehiculo.propietario.nombre} ${vehiculo.propietario.apellido}`.trim() || vehiculo.propietario.email;

  return (
    <Card className="border-yellow-200 bg-yellow-50/30">
      <CardContent className="p-4">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          {/* Datos del vehículo */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <Car className="h-4 w-4 text-muted-foreground" />
              <span className="font-semibold text-base">{vehiculo.patente}</span>
              <span className="text-sm text-muted-foreground">
                {vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})
              </span>

              <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300 gap-1">
                <AlertTriangle className="h-3 w-3" />
                {vehiculo.estado_aprobacion === 'rechazado' ? 'Rechazado' : 'Incompleto'}
              </Badge>
            </div>

            <div className="text-sm text-muted-foreground space-y-1">
              <p className="flex items-center gap-1">
                <User className="h-3 w-3" />
                Propietario: {propietarioNombre}
                <span className="text-xs">({vehiculo.propietario.email})</span>
              </p>
              {vehiculo.propietario.telefono && (
                <p className="flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  {vehiculo.propietario.telefono}
                </p>
              )}
            </div>

            {/* Documentos faltantes */}
            <div className="mt-3">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="h-3 w-3 text-red-500" />
                <span className="text-sm font-medium text-red-700">
                  Documentos faltantes:
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {vehiculo.documentos_faltantes.map((tipo) => (
                  <Badge
                    key={tipo}
                    variant="outline"
                    className="bg-red-50 text-red-700 border-red-300"
                  >
                    ❌ {DOCS_LABELS[tipo] || tipo}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Sin acciones - solo lectura */}
          <div className="flex-shrink-0">
            <div className="text-xs text-yellow-700 bg-yellow-100 border border-yellow-300 rounded-md px-3 py-2 flex items-center gap-2">
              <Lock className="h-3 w-3" />
              Solo lectura
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}