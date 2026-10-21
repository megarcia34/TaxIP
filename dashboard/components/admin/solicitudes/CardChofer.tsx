// D:\aTaxip\dashboard\components\admin\solicitudes\CardChofer.tsx
'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  User,
  Car,
  Phone,
  CheckCircle2,
  XCircle,
  Loader2,
  Calendar,
  Building2,
  FileText,
} from 'lucide-react';
import { useAprobarChofer, useRechazarChofer } from '@/hooks/admin/useSolicitudesTenant';
import type { ChoferPendiente } from '@/lib/api/solicitudesTenant';
import ModalRechazo from './ModalRechazo';
import ModalVerDocumentos from './ModalVerDocumentos';

interface Props {
  chofer: ChoferPendiente;
}

const TIPOS_DOCS_CHOFER = [
  { tipo: 'dni', label: 'DNI' },
  { tipo: 'licencia', label: 'Licencia' },
  { tipo: 'buena_conducta', label: 'Buena Conducta' },
  { tipo: 'antecedentes', label: 'Antecedentes' },
  { tipo: 'sanidad', label: 'Sanidad' },
];

export default function CardChofer({ chofer }: Props) {
  const aprobarMutation = useAprobarChofer();
  const rechazarMutation = useRechazarChofer();
  const [showRechazar, setShowRechazar] = useState(false);
  const [showDocs, setShowDocs] = useState(false);

  const handleAprobar = async () => {
    if (!confirm(`Aprobar a ${chofer.nombre} ${chofer.apellido}?`)) return;
    try {
      await aprobarMutation.mutateAsync(chofer.chofer_vehiculo_id);
    } catch {
      // El hook ya muestra el toast
    }
  };

  const handleRechazar = async (motivo: string) => {
    // AHORA pasa { id, motivo }
    await rechazarMutation.mutateAsync({ id: chofer.chofer_vehiculo_id, motivo });
  };

  const nombreCompleto = `${chofer.nombre || ''} ${chofer.apellido || ''}`.trim() || chofer.email;

  return (
    <>
      <Card className="hover:shadow-sm transition-shadow">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            {/* Datos del chofer */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="font-semibold text-base">{nombreCompleto}</span>

                {chofer.es_propietario && (
                  <Badge className="bg-purple-100 text-purple-800 border-purple-200 gap-1">
                    <Building2 className="h-3 w-3" />
                    Propietario
                  </Badge>
                )}

                {chofer.es_propietario && chofer.cantidad_vehiculos > 0 && (
                  <Badge variant="outline" className="gap-1">
                    <Car className="h-3 w-3" />
                    {chofer.cantidad_vehiculos} {chofer.cantidad_vehiculos === 1 ? 'vehículo' : 'vehículos'}
                  </Badge>
                )}
              </div>

              <div className="text-sm text-muted-foreground space-y-1">
                <p>📧 {chofer.email}</p>
                {chofer.telefono && (
                  <p className="flex items-center gap-1">
                    <Phone className="h-3 w-3" />
                    {chofer.telefono}
                  </p>
                )}

                {chofer.vehiculo && (
                  <p className="flex items-center gap-1">
                    <Car className="h-3 w-3" />
                    {chofer.vehiculo.patente} — {chofer.vehiculo.marca} {chofer.vehiculo.modelo} ({chofer.vehiculo.anio})
                  </p>
                )}

                <p className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  Registrado: {new Date(chofer.fecha_registro).toLocaleDateString('es-AR')}
                </p>
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
        titulo={`Rechazar a ${nombreCompleto}`}
        descripcion="El chofer no podrá iniciar turnos hasta que se vuelva a aprobar."
        requiereMotivo={true}
        onConfirm={handleRechazar}
        isPending={rechazarMutation.isPending}
      />

      <ModalVerDocumentos
        open={showDocs}
        onOpenChange={setShowDocs}
        titulo={`Documentos de ${nombreCompleto}`}
        documentos={chofer.documentos}
        tiposRequeridos={TIPOS_DOCS_CHOFER}
      />
    </>
  );
}