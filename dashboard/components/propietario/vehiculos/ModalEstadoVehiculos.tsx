// D:\ataxip\dashboard\components\propietario\vehiculos\ModalEstadoVehiculos.tsx
'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  XCircle,
  Send,
} from 'lucide-react';

type Variante = 'enviado' | 'aprobado' | 'rechazado';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  variante: Variante;
  patentes?: string[];
  motivoRechazo?: string | null;
  onAceptar?: () => void;
  onReintentar?: () => void;
}

const CONFIG: Record<
  Variante,
  { icon: typeof CheckCircle2; color: string; titulo: string; descripcion: string }
> = {
  enviado: {
    icon: Send,
    color: 'text-blue-600',
    titulo: 'Vehiculos enviados',
    descripcion:
      'Tus vehiculos fueron enviados al municipio para su revision. Te avisaremos cuando se aprueben.',
  },
  aprobado: {
    icon: CheckCircle2,
    color: 'text-green-600',
    titulo: 'Vehiculos aprobados!',
    descripcion:
      'El municipio aprobo tus vehiculos. Ya podes comenzar a trabajar.',
  },
  rechazado: {
    icon: XCircle,
    color: 'text-red-600',
    titulo: 'Vehiculos rechazados',
    descripcion:
      'El municipio rechazo algunos de tus vehiculos. Revisa el motivo y reenvia.',
  },
};

export default function ModalEstadoVehiculos({
  open,
  onOpenChange,
  variante,
  patentes = [],
  motivoRechazo,
  onAceptar,
  onReintentar,
}: Props) {
  const config = CONFIG[variante];
  const Icon = config.icon;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Icon className={`h-5 w-5 ${config.color}`} />
            {config.titulo}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">{config.descripcion}</p>

          {patentes.length > 0 && (
            <div className="bg-gray-50 border rounded-md p-3">
              <p className="text-xs font-medium mb-1">Vehiculos:</p>
              <ul className="text-sm space-y-0.5">
                {patentes.map((p) => (
                  <li key={p} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {variante === 'rechazado' && motivoRechazo && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-xs font-medium text-red-800">Motivo:</p>
              <p className="text-sm text-red-700 mt-1">{motivoRechazo}</p>
            </div>
          )}
        </div>

        <DialogFooter>
          {variante === 'rechazado' && (
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cerrar
            </Button>
          )}

          {variante === 'enviado' && (
            <Button onClick={() => onOpenChange(false)}>Entendido</Button>
          )}

          {variante === 'aprobado' && (
            <Button
              onClick={() => {
                onAceptar?.();
                onOpenChange(false);
              }}
            >
              Comenzar a trabajar
            </Button>
          )}

          {variante === 'rechazado' && (
            <Button
              onClick={() => {
                onReintentar?.();
                onOpenChange(false);
              }}
            >
              Reintentar
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}