// D:\ataxip\dashboard\components\propietario\perfil\PerfilDatosFiscales.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Save, Receipt } from 'lucide-react';
import { usePerfil, useUpdatePerfil } from '@/hooks/propietario/usePerfil';
import type { CondicionImpositiva } from '@/lib/api/perfil';

const CONDICIONES: { value: CondicionImpositiva; label: string }[] = [
  { value: 'responsable_inscripto', label: 'Responsable Inscripto' },
  { value: 'monotributo', label: 'Monotributo' },
  { value: 'exento', label: 'Exento' },
  { value: 'consumidor_final', label: 'Consumidor Final' },
  { value: 'no_categorizado', label: 'No Categorizado' },
];

export default function PerfilDatosFiscales() {
  const { data: perfil, isLoading } = usePerfil();
  const updateMutation = useUpdatePerfil();

  const [cuit, setCuit] = useState('');
  const [condicion, setCondicion] = useState<CondicionImpositiva | ''>('');

  useEffect(() => {
    if (perfil) {
      setCuit(perfil.cuit_cuil || '');
      setCondicion(perfil.condicion_impositiva || '');
    }
  }, [perfil]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Validacion suave: solo UX. El backend rechaza si esta mal.
    if (cuit && !/^\d{11}$/.test(cuit)) {
      // dejamos pasar igual, el backend valida
    }
    updateMutation.mutate({
      cuit_cuil: cuit || null,
      condicion_impositiva: (condicion as CondicionImpositiva) || null,
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Receipt className="h-5 w-5" />
          Datos fiscales
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cuit">CUIT / CUIL</Label>
              <Input
                id="cuit"
                value={cuit}
                onChange={(e) => setCuit(e.target.value.replace(/\D/g, '').slice(0, 11))}
                placeholder="11 digitos sin guiones"
                maxLength={11}
                inputMode="numeric"
              />
              <p className="text-xs text-muted-foreground">
                11 digitos numericos
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="condicion">Condicion impositiva</Label>
              <Select
                value={condicion || 'sin-seleccionar'}
                onValueChange={(v) =>
                  setCondicion(v === 'sin-seleccionar' ? '' : (v as CondicionImpositiva))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sin-seleccionar">Sin seleccionar</SelectItem>
                  {CONDICIONES.map((c) => (
                    <SelectItem key={c.value} value={c.value}>
                      {c.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t">
            <Button type="submit" disabled={updateMutation.isPending} className="gap-2">
              {updateMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Guardar cambios
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}