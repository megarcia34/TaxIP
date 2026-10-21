// D:\aTaxip\dashboard\components\admin\solicitudes\ModalRechazo.tsx
'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Loader2, AlertTriangle } from 'lucide-react';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  titulo: string;
  descripcion?: string;
  requiereMotivo?: boolean;
  onConfirm: (motivo: string) => Promise<void> | void;
  isPending?: boolean;
}

export default function ModalRechazo({
  open,
  onOpenChange,
  titulo,
  descripcion,
  requiereMotivo = true,
  onConfirm,
  isPending = false,
}: Props) {
  const [motivo, setMotivo] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);

  // Reset al abrir/cerrar
  useEffect(() => {
    if (!open) {
      setMotivo('');
      setErrorLocal(null);
    }
  }, [open]);

  const handleConfirm = async () => {
    if (requiereMotivo && motivo.trim().length < 15) {
      setErrorLocal('El motivo debe tener al menos 15 caracteres.');
      return;
    }

    try {
      await onConfirm(motivo.trim());
      onOpenChange(false);
    } catch {
      // El error ya lo maneja el hook
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            {titulo}
          </DialogTitle>
          {descripcion && (
            <DialogDescription>{descripcion}</DialogDescription>
          )}
        </DialogHeader>

        <div className="space-y-4">
          {requiereMotivo && (
            <div className="space-y-2">
              <Label htmlFor="motivo">Motivo del rechazo *</Label>
              <Textarea
                id="motivo"
                value={motivo}
                onChange={(e) => {
                  setMotivo(e.target.value);
                  setErrorLocal(null);
                }}
                placeholder="Explica el motivo del rechazo (mínimo 15 caracteres)..."
                rows={4}
                maxLength={500}
                disabled={isPending}
              />
              <div className="flex justify-between items-center text-xs text-muted-foreground">
                <span>Mínimo 15 caracteres</span>
                <span>{motivo.length} / 500</span>
              </div>
            </div>
          )}

          {errorLocal && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
              {errorLocal}
            </div>
          )}

          {!requiereMotivo && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-sm text-yellow-800">
              Esta acción no se puede deshacer. El chofer no podrá iniciar turnos hasta que se vuelva a aprobar.
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isPending}
          >
            Cancelar
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={isPending || (requiereMotivo && motivo.trim().length < 15)}
          >
            {isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
            Rechazar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}