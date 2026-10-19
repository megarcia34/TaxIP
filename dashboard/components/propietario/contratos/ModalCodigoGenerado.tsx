'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Copy, MessageCircle, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  codigo: string;
  expiraEn: string;
  choferNombre: string;
  choferTelefono: string | null;
  patente: string;
}

export default function ModalCodigoGenerado({
  open,
  onOpenChange,
  codigo,
  expiraEn,
  choferNombre,
  choferTelefono,
  patente,
}: Props) {
  const [copiado, setCopiado] = useState(false);

  const handleCopiar = async () => {
    try {
      await navigator.clipboard.writeText(codigo);
      setCopiado(true);
      toast.success('Codigo copiado al portapapeles');
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      toast.error('No se pudo copiar el codigo');
    }
  };

  const handleWhatsApp = () => {
    if (!choferTelefono) {
      toast.error('El chofer no tiene telefono registrado en su perfil');
      return;
    }
    const telefono = choferTelefono.replace(/\D/g, '');
    const fecha = new Date(expiraEn).toLocaleDateString('es-AR');
    const mensaje = `Hola ${choferNombre}, tu codigo de inicio de turno para el vehiculo ${patente} es: ${codigo}. Valido hasta el ${fecha}.`;
    const url = `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`;
    window.open(url, '_blank');
  };

  const fechaExpiracion = new Date(expiraEn).toLocaleString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Codigo generado
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 text-center">
            <p className="text-xs text-blue-700 font-medium uppercase tracking-wide">
              Codigo de inicio de turno
            </p>
            <p className="text-4xl font-mono font-bold text-blue-900 tracking-widest mt-2">
              {codigo}
            </p>
            <p className="text-xs text-blue-600 mt-2">
              Valido hasta {fechaExpiracion}
            </p>
          </div>

          <div className="bg-gray-50 rounded-md p-3 text-sm space-y-1">
            <p><span className="font-medium">Vehiculo:</span> {patente}</p>
            <p><span className="font-medium">Chofer:</span> {choferNombre}</p>
            {choferTelefono && (
              <p><span className="font-medium">Telefono:</span> {choferTelefono}</p>
            )}
          </div>

          <p className="text-xs text-muted-foreground text-center">
            Comparti este codigo con el chofer. Lo va a necesitar para iniciar su turno en la app.
          </p>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            onClick={handleCopiar}
            className="gap-2 flex-1"
          >
            <Copy className="h-4 w-4" />
            {copiado ? 'Copiado' : 'Copiar codigo'}
          </Button>
          <Button
            onClick={handleWhatsApp}
            disabled={!choferTelefono}
            className="gap-2 flex-1 bg-green-600 hover:bg-green-700"
          >
            <MessageCircle className="h-4 w-4" />
            Enviar por WhatsApp
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}