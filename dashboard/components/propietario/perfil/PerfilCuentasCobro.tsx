// D:\ataxip\dashboard\components\propietario\perfil\PerfilCuentasCobro.tsx
'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Wallet, Plus, Pencil, Trash2, Star, Loader2 } from 'lucide-react';
import type { CuentaCobro } from '@/lib/api/cuentasCobro';
import {
  useCuentasCobro,
  useEliminarCuenta,
  useMarcarPredeterminada,
} from '@/hooks/propietario/useCuentasCobro';
import ModalCuentaCobro from './ModalCuentaCobro';

export default function PerfilCuentasCobro() {
  const { data: cuentas = [], isLoading } = useCuentasCobro();
  const eliminarMutation = useEliminarCuenta();
  const predeterminadaMutation = useMarcarPredeterminada();

  const [modalOpen, setModalOpen] = useState(false);
  const [cuentaEditando, setCuentaEditando] = useState<CuentaCobro | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleNueva = () => {
    setCuentaEditando(null);
    setModalOpen(true);
  };

  const handleEditar = (cuenta: CuentaCobro) => {
    setCuentaEditando(cuenta);
    setModalOpen(true);
  };

  const handleEliminar = async () => {
    if (deleteId) {
      await eliminarMutation.mutateAsync(deleteId);
      setDeleteId(null);
    }
  };

  const activas = cuentas.filter((c) => c.activo);

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Cuentas de cobro
          </CardTitle>
          <Button
            onClick={handleNueva}
            size="sm"
            className="gap-2"
            disabled={activas.length >= 5}
          >
            <Plus className="h-4 w-4" />
            Nueva cuenta
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Maximo 5 cuentas activas. La marcada como predeterminada es la que se usa por defecto.
        </p>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : activas.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Wallet className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
            <p>No hay cuentas registradas</p>
            <p className="text-sm">Agrega una cuenta para recibir los pagos</p>
          </div>
        ) : (
          <div className="space-y-3">
            {activas.map((cuenta) => (
              <div
                key={cuenta.id}
                className="border rounded-lg p-4 flex flex-col sm:flex-row justify-between gap-3"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className="uppercase">
                      {cuenta.tipo}
                    </Badge>
                    <span className="font-mono text-sm">
                      {cuenta.numero.slice(0, 4)}...{cuenta.numero.slice(-4)}
                    </span>
                    {cuenta.predeterminada && (
                      <Badge className="bg-yellow-500 hover:bg-yellow-600 gap-1">
                        <Star className="h-3 w-3" />
                        Predeterminada
                      </Badge>
                    )}
                  </div>
                  <div className="mt-1 text-sm">
                    <span className="font-medium">{cuenta.banco}</span>
                    {cuenta.titular && (
                      <span className="text-muted-foreground"> - {cuenta.titular}</span>
                    )}
                  </div>
                  {cuenta.alias && (
                    <div className="text-xs text-muted-foreground mt-0.5">
                      Alias: {cuenta.alias}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {!cuenta.predeterminada && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => predeterminadaMutation.mutate(cuenta.id)}
                      disabled={predeterminadaMutation.isPending}
                      title="Marcar como predeterminada"
                    >
                      <Star className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditar(cuenta)}
                    title="Editar"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDeleteId(cuenta.id)}
                    title="Eliminar"
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      <ModalCuentaCobro
        open={modalOpen}
        onOpenChange={setModalOpen}
        cuenta={cuentaEditando}
      />

      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eliminar cuenta?</AlertDialogTitle>
            <AlertDialogDescription>
              La cuenta se desactivara. Si era la predeterminada, se promovera otra.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleEliminar}
              className="bg-red-500 hover:bg-red-600"
              disabled={eliminarMutation.isPending}
            >
              {eliminarMutation.isPending ? 'Eliminando...' : 'Eliminar'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}