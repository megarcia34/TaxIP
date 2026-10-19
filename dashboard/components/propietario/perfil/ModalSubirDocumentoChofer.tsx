// D:\aTaxip\dashboard\components\propietario\perfil\ModalSubirDocumentoChofer.tsx
'use client';

import { useState, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, Upload, FileCheck, X, AlertCircle } from 'lucide-react';
import { useSubirDocumentoChofer } from '@/hooks/propietario/usePostulacionChofer';
import {
  TIPOS_CON_VENCIMIENTO,
  type TipoDocumentoChofer,
} from '@/lib/api/postulacionChofer';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tipoDocumento: TipoDocumentoChofer;
}

const LABELS: Record<TipoDocumentoChofer, string> = {
  dni: 'DNI',
  licencia: 'Licencia de conducir',
  buena_conducta: 'Certificado de buena conducta',
  antecedentes: 'Certificado de antecedentes',
  sanidad: 'Certificado de sanidad',
};

// Configuracion de numero por tipo
// - null: no se muestra input (el backend lo toma del perfil)
// - obligatorio: true/false
// - label: etiqueta del input
// - placeholder: placeholder del input
const NUMERO_CONFIG: Record<
  TipoDocumentoChofer,
  { label: string; obligatorio: boolean; placeholder: string } | null
> = {
  dni: null, // No mostrar (viene del perfil)
  licencia: {
    label: 'Numero de licencia',
    obligatorio: true,
    placeholder: 'Ej: LIC-123456',
  },
  buena_conducta: {
    label: 'Numero de certificado',
    obligatorio: true,
    placeholder: 'Ej: 1234/2026',
  },
  antecedentes: {
    label: 'Numero de certificado',
    obligatorio: true,
    placeholder: 'Ej: 5678/2026',
  },
  sanidad: {
    label: 'Numero de certificado (opcional)',
    obligatorio: false,
    placeholder: 'Ej: 9012/2026',
  },
};

function todayISO(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${dd}`;
}

export default function ModalSubirDocumentoChofer({
  open,
  onOpenChange,
  tipoDocumento,
}: Props) {
  const subirMutation = useSubirDocumentoChofer();
  const [archivo, setArchivo] = useState<File | null>(null);
  const [numero, setNumero] = useState('');
  const [fechaVencimiento, setFechaVencimiento] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const requiereVencimiento = TIPOS_CON_VENCIMIENTO.includes(tipoDocumento);
  const numeroConfig = NUMERO_CONFIG[tipoDocumento];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setArchivo(file);
    setErrorLocal(null);
  };

  const handleQuitarArchivo = () => {
    setArchivo(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorLocal(null);

    if (!archivo) {
      setErrorLocal('Debes seleccionar un archivo.');
      return;
    }

    if (requiereVencimiento) {
      if (!fechaVencimiento) {
        setErrorLocal('La fecha de vencimiento es obligatoria para este documento.');
        return;
      }
      if (fechaVencimiento < todayISO()) {
        setErrorLocal('La fecha de vencimiento no puede ser anterior a hoy.');
        return;
      }
    }

    if (numeroConfig?.obligatorio && !numero.trim()) {
      setErrorLocal(`El ${numeroConfig.label.toLowerCase()} es obligatorio.`);
      return;
    }

    try {
      await subirMutation.mutateAsync({
        tipo_documento: tipoDocumento,
        numero: numero.trim() || null,
        fecha_vencimiento: fechaVencimiento || null,
        archivo,
      });
      onOpenChange(false);
      setArchivo(null);
      setNumero('');
      setFechaVencimiento('');
      if (inputRef.current) inputRef.current.value = '';
    } catch {
      // El hook muestra el toast de error
    }
  };

  const handleClose = () => {
    if (subirMutation.isPending) return;
    onOpenChange(false);
    setArchivo(null);
    setNumero('');
    setFechaVencimiento('');
    setErrorLocal(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Subir {LABELS[tipoDocumento]}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Archivo */}
          <div className="space-y-2">
            <Label>Archivo *</Label>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={handleFileChange}
              className="hidden"
              id={`file-input-${tipoDocumento}`}
            />
            {archivo ? (
              <div className="border rounded-md p-3 bg-green-50 border-green-200 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-sm text-green-800 min-w-0">
                  <FileCheck className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">{archivo.name}</span>
                  <span className="text-xs text-green-600 flex-shrink-0">
                    ({(archivo.size / 1024).toFixed(0)} KB)
                  </span>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleQuitarArchivo}
                  disabled={subirMutation.isPending}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <label
                htmlFor={`file-input-${tipoDocumento}`}
                className="block border-2 border-dashed rounded-md p-6 hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer text-center"
              >
                <div className="flex flex-col items-center gap-2 text-muted-foreground">
                  <Upload className="h-6 w-6" />
                  <span className="text-sm font-medium">
                    Click para seleccionar archivo
                  </span>
                  <span className="text-xs">PDF, JPG o PNG (max 10MB)</span>
                </div>
              </label>
            )}
          </div>

          {/* Numero (condicional segun tipo) */}
          {numeroConfig && (
            <div className="space-y-2">
              <Label htmlFor="numero">
                {numeroConfig.label} {numeroConfig.obligatorio && '*'}
              </Label>
              <Input
                id="numero"
                value={numero}
                onChange={(e) => setNumero(e.target.value)}
                placeholder={numeroConfig.placeholder}
                maxLength={50}
                required={numeroConfig.obligatorio}
              />
              {!numeroConfig.obligatorio && (
                <p className="text-xs text-muted-foreground">
                  Si el documento no tiene numero, deja vacio.
                </p>
              )}
            </div>
          )}

          {/* Aviso para DNI */}
          {tipoDocumento === 'dni' && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3 text-xs text-blue-800">
              El numero del DNI se toma automaticamente de tu perfil.
            </div>
          )}

          {/* Fecha de vencimiento */}
          {requiereVencimiento && (
            <div className="space-y-2">
              <Label htmlFor="fecha_vencimiento">Fecha de vencimiento *</Label>
              <Input
                id="fecha_vencimiento"
                type="date"
                value={fechaVencimiento}
                onChange={(e) => setFechaVencimiento(e.target.value)}
                min={todayISO()}
                required
              />
              <p className="text-xs text-muted-foreground">
                Debe ser posterior a la fecha actual.
              </p>
            </div>
          )}

          {/* Error local */}
          {errorLocal && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700">{errorLocal}</p>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={subirMutation.isPending}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={!archivo || subirMutation.isPending}>
              {subirMutation.isPending && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              Subir documento
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}