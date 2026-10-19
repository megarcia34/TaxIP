// D:\ataxip\dashboard\components\propietario\perfil\ModalCuentaCobro.tsx
'use client';

import { useEffect, useState } from 'react';
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
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Loader2 } from 'lucide-react';
import type { CuentaCobro, TipoCuenta } from '@/lib/api/cuentasCobro';
import {
  useCrearCuenta,
  useActualizarCuenta,
} from '@/hooks/propietario/useCuentasCobro';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  cuenta?: CuentaCobro | null;
}

export default function ModalCuentaCobro({ open, onOpenChange, cuenta }: Props) {
  const crearMutation = useCrearCuenta();
  const updateMutation = useActualizarCuenta();
  const isEdit = !!cuenta;

  const [tipo, setTipo] = useState<TipoCuenta>('cbu');
  const [numero, setNumero] = useState('');
  const [alias, setAlias] = useState('');
  const [banco, setBanco] = useState('');
  const [titular, setTitular] = useState('');

  useEffect(() => {
    if (open) {
      if (cuenta) {
        setTipo(cuenta.tipo);
        setNumero(cuenta.numero);
        setAlias(cuenta.alias || '');
        setBanco(cuenta.banco);
        setTitular(cuenta.titular || '');
      } else {
        setTipo('cbu');
        setNumero('');
        setAlias('');
        setBanco('');
        setTitular('');
      }
    }
  }, [open, cuenta]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      tipo,
      numero,
      alias: alias || null,
      banco,
      titular: titular || null,
    };
    try {
      if (isEdit && cuenta) {
        await updateMutation.mutateAsync({ id: cuenta.id, data: payload });
      } else {
        await crearMutation.mutateAsync(payload);
      }
      onOpenChange(false);
    } catch {
      // el hook ya muestra el toast de error
    }
  };

  const isPending = crearMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Editar cuenta' : 'Nueva cuenta de cobro'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Tipo</Label>
            <RadioGroup value={tipo} onValueChange={(v) => setTipo(v as TipoCuenta)}>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="cbu" id="cbu" />
                  <Label htmlFor="cbu" className="cursor-pointer">CBU</Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="cvu" id="cvu" />
                  <Label htmlFor="cvu" className="cursor-pointer">CVU</Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="numero">Numero (22 digitos)</Label>
            <Input
              id="numero"
              value={numero}
              onChange={(e) => setNumero(e.target.value.replace(/\D/g, '').slice(0, 22))}
              maxLength={22}
              inputMode="numeric"
              placeholder="0000000000000000000000"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="alias">Alias (opcional)</Label>
            <Input
              id="alias"
              value={alias}
              onChange={(e) => setAlias(e.target.value)}
              placeholder="mi.alias.banco"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="banco">Banco</Label>
            <Input
              id="banco"
              value={banco}
              onChange={(e) => setBanco(e.target.value)}
              placeholder="Banco Nacion"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="titular">Titular (opcional)</Label>
            <Input
              id="titular"
              value={titular}
              onChange={(e) => setTitular(e.target.value)}
              placeholder="Juan Perez"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {isEdit ? 'Guardar cambios' : 'Crear cuenta'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}