'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { toast } from '@/hooks/use-toast';
import { Contrato } from '@/types/propietario';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

async function fetchContratos(activo?: boolean): Promise<Contrato[]> {
  const params = new URLSearchParams();
  if (activo !== undefined) params.append('activo', String(activo));
  const res = await fetch(`/api/propietario/contratos?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar contratos');
  return res.json();
}

async function finalizarContrato(id: string): Promise<void> {
  const res = await fetch(`/api/propietario/contratos/${id}/finalizar`, { method: 'PUT' });
  if (!res.ok) throw new Error('Error al finalizar contrato');
}

export function ContratosList() {
  const [filterActivo, setFilterActivo] = useState<boolean | undefined>(true);
  const [contratoToFinalize, setContratoToFinalize] = useState<Contrato | null>(null);
  const queryClient = useQueryClient();

  const { data: contratos, isLoading } = useQuery({
    queryKey: ['contratos', filterActivo],
    queryFn: () => fetchContratos(filterActivo),
  });

  const finalizeMutation = useMutation({
    mutationFn: finalizarContrato,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast({ title: 'Contrato finalizado', description: 'El contrato ha sido dado de baja correctamente.' });
      setContratoToFinalize(null);
    },
    onError: (error) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  const getBadgeForEstado = (contrato: Contrato) => {
    if (!contrato.activo) return <Badge variant="secondary">Finalizado</Badge>;
    switch (contrato.turno_asignado) {
      case 'DIURNO': return <Badge variant="default" className="bg-blue-500">Activo Diurno</Badge>;
      case 'NOCTURNO': return <Badge variant="default" className="bg-indigo-700">Activo Nocturno</Badge>;
      case 'COMPLETO': return <Badge variant="default" className="bg-green-700">Activo Completo</Badge>;
      default: return <Badge>Activo</Badge>;
    }
  };

  const getTipoContratoLabel = (tipo: string) => {
    switch (tipo) {
      case 'AUTO_GESTION': return 'Auto-gestión';
      case 'PORCENTAJE': return 'Porcentaje';
      case 'CANON_FIJO': return 'Canon fijo';
      default: return tipo;
    }
  };

  if (isLoading) return <div className="p-8 text-center">Cargando contratos...</div>;

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button variant={filterActivo === true ? 'default' : 'outline'} onClick={() => setFilterActivo(true)}>Activos</Button>
        <Button variant={filterActivo === false ? 'default' : 'outline'} onClick={() => setFilterActivo(false)}>Finalizados</Button>
        <Button variant={filterActivo === undefined ? 'default' : 'outline'} onClick={() => setFilterActivo(undefined)}>Todos</Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Vehículo</TableHead>
              <TableHead>Chofer</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Turno</TableHead>
              <TableHead>Detalle económico</TableHead>
              <TableHead>Inicio</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contratos?.map((c) => (
              <TableRow key={c.id}>
                <TableCell className="font-medium">{c.patente} – {c.marca} {c.modelo}</TableCell>
                <TableCell>{c.chofer_nombre} {c.chofer_apellido}</TableCell>
                <TableCell>{getTipoContratoLabel(c.tipo_contrato)}</TableCell>
                <TableCell>{c.turno_asignado}</TableCell>
                <TableCell>
                  {c.tipo_contrato === 'PORCENTAJE' && `${c.porcentaje_chofer}% para chofer`}
                  {c.tipo_contrato === 'CANON_FIJO' && `$${c.monto_diario} / día`}
                  {c.tipo_contrato === 'AUTO_GESTION' && '—'}
                </TableCell>
                <TableCell>{format(new Date(c.fecha_inicio), 'dd/MM/yyyy', { locale: es })}</TableCell>
                <TableCell>{getBadgeForEstado(c)}</TableCell>
                <TableCell>
                  {c.activo && (
                    <Button variant="destructive" size="sm" onClick={() => setContratoToFinalize(c)}>
                      Finalizar
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {contratos?.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="text-center">No hay contratos</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <AlertDialog open={!!contratoToFinalize} onOpenChange={(open) => !open && setContratoToFinalize(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Finalizar contrato?</AlertDialogTitle>
            <AlertDialogDescription>
              El contrato de <strong>{contratoToFinalize?.patente}</strong> con el chofer <strong>{contratoToFinalize?.chofer_nombre} {contratoToFinalize?.chofer_apellido}</strong> será finalizado.
              El chofer quedará desvinculado del vehículo. Esta acción no se puede deshacer.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={() => contratoToFinalize && finalizeMutation.mutate(contratoToFinalize.id)}>
              Sí, finalizar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}