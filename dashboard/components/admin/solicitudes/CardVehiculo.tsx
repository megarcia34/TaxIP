// D:\aTaxip\dashboard\components\admin\solicitudes\CardVehiculo.tsx
'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Car,
  User,
  Phone,
  CheckCircle2,
  XCircle,
  Loader2,
  Calendar,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import { useAprobarVehiculo, useRechazarVehiculo } from '@/hooks/admin/useSolicitudesTenant';
import type { VehiculoPendiente } from '@/lib/api/solicitudesTenant';
import ModalRechazo from './ModalRechazo';
import ModalVerDocumentos from './ModalVerDocumentos';

interface Props {
  vehiculo: VehiculoPendiente;
}

const TIPOS_DOCS = ['SEGURO', 'VTV', 'CEDULA_VERDE', 'HABILITACION'] as const;

const DOCS_LABELS: Record<string, string> = {
  SEGURO: 'Seguro',
  VTV: 'VTV',
  CEDULA_VERDE: 'Cédula Verde',
  HABILITACION: 'Habilitación',
};

const TIPOS_DOCS_VEHICULO = TIPOS_DOCS.map((tipo) => ({
  tipo,
  label: DOCS_LABELS[tipo] || tipo,
}));

export default function CardVehiculo({ vehiculo }: Props) {
  const aprobarMutation = useAprobarVehiculo();
  const rechazarMutation = useRechazarVehiculo();
  const [showRechazar, setShowRechazar] = useState(false);
  const [showDocs, setShowDocs] = useState(false);

  const handleAprobar = async () => {
    if (!confirm(`Aprobar el vehículo ${vehiculo.patente}?`)) return;
    try {
      await aprobarMutation.mutateAsync(vehiculo.vehiculo_id);
    } catch {
      // El hook ya muestra el toast
    }
  };

  const handleRechazar = async (motivo: string) => {
    await rechazarMutation.mutateAsync({ id: vehiculo.vehiculo_id, motivo });
  };

  const propietarioNombre = `${vehiculo.propietario.nombre} ${vehiculo.propietario.apellido}`.trim() || vehiculo.propietario.email;

  // Verificar si el vencimiento del taxi es proximo
  const fechaVenceTaxi = vehiculo.fecha_vencimiento_taxi
    ? new Date(vehiculo.fecha_vencimiento_taxi)
    : null;
  const diasParaVencerTaxi = fechaVenceTaxi
    ? Math.ceil((fechaVenceTaxi.getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;
  const taxiPorVencer = diasParaVencerTaxi !== null && diasParaVencerTaxi <= 90;

  return (
    <>
      <Card className="hover:shadow-sm transition-shadow">
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

                {taxiPorVencer && (
                  <Badge className="bg-orange-100 text-orange-800 border-orange-200 gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    Vence en {diasParaVencerTaxi}d
                  </Badge>
                )}
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
                {vehiculo.fecha_vencimiento_taxi && (
                  <p className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Vence taxi: {new Date(vehiculo.fecha_vencimiento_taxi).toLocaleDateString('es-AR')}
                  </p>
                )}
              </div>

              {/* Documentos */}
              <div className="mt-2 flex items-center gap-2 flex-wrap">
                <FileText className="h-3 w-3 text-muted-foreground" />
                {TIPOS_DOCS.map((tipo) => {
                  const doc = vehiculo.documentos[tipo];
                  const presente = !!doc;
                  return (
                    <Badge
                      key={tipo}
                      variant="outline"
                      className={
                        presente
                          ? 'bg-green-50 text-green-700 border-green-300'
                          : 'bg-red-50 text-red-700 border-red-300'
                      }
                    >
                      {presente ? '✅' : '❌'} {DOCS_LABELS[tipo]}
                    </Badge>
                  );
                })}
              </div>
            </div>

            {/* Acciones */}
            <div className="flex gap-2 flex-shrink-0 flex-wrap">
              <Button
                variant="outline"
                onClick={() => setShowDocs(true)}
                className="gap-2"
              >
                <FileText className="h-4 w-4" />
                Ver documentos
              </Button>
              <Button
                onClick={handleAprobar}
                disabled={aprobarMutation.isPending}
                className="bg-green-600 hover:bg-green-700 gap-2"
              >
                {aprobarMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="h-4 w-4" />
                )}
                Aprobar
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowRechazar(true)}
                disabled={rechazarMutation.isPending}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200 gap-2"
              >
                <XCircle className="h-4 w-4" />
                Rechazar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <ModalRechazo
        open={showRechazar}
        onOpenChange={setShowRechazar}
        titulo={`Rechazar vehículo ${vehiculo.patente}`}
        descripcion="El vehículo no podrá operar hasta que se vuelva a aprobar."
        requiereMotivo={true}
        onConfirm={handleRechazar}
        isPending={rechazarMutation.isPending}
      />

      <ModalVerDocumentos
        open={showDocs}
        onOpenChange={setShowDocs}
        titulo={`Documentos de ${vehiculo.patente}`}
        documentos={vehiculo.documentos}
        tiposRequeridos={TIPOS_DOCS_VEHICULO}
      />
    </>
  );
}