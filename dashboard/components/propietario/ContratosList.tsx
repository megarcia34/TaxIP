'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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

// Helper para formatear días
function formatDias(dias: string[]): string {
  const abreviaturas: Record<string, string> = {
    lunes: 'Lun',
    martes: 'Mar',
    miercoles: 'Mié',
    jueves: 'Jue',
    viernes: 'Vie',
    sabado: 'Sáb',
    domingo: 'Dom',
  };
  return dias.map((d) => abreviaturas[d] || d).join(', ');
}

// Helper para badge de estado
function EstadoBadge({ estado, activo }: { estado: string; activo: boolean }) {
  if (!activo) {
    return <Badge variant="secondary">Finalizado</Badge>;
  }
  switch (estado) {
    case 'ACTIVO':
      return <Badge className="bg-green-500 hover:bg-green-600">Activo</Badge>;
    case 'PROGRAMADO':
      return <Badge className="bg-yellow-500 hover:bg-yellow-600">Programado</Badge>;
    case 'PENDIENTE_CONFIGURACION':
      return <Badge className="bg-orange-500 hover:bg-orange-600">Pendiente Config.</Badge>;
    default:
      return <Badge>Activo</Badge>;
  }
}

export function ContratosList() {
  const [filterActivo, setFilterActivo] = useState<boolean | undefined>(true);
  const [contratoToFinalize, setContratoToFinalize] = useState<Contrato | null>(null);
  const queryClient = useQueryClient();

  const { data: contratos, isLoading } = useQuery({
    queryKey: ['contratos', filterActivo],
    queryFn: () => fetchContratos(filterActivo),
    staleTime: 60000, // ✅ 1 minuto de stale time
    refetchOnWindowFocus: false, // ✅ No recargar al enfocar
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

  const getTipoContratoLabel = (tipo: string) => {
    switch (tipo) {
      case 'AUTO_GESTION': return 'Auto-gestión';
      case 'PORCENTAJE': return 'Porcentaje';
      case 'ALQUILER': return 'Alquiler';
      default: return tipo;
    }
  };


 

  const getDetalleContrato = (c: Contrato) => {
    if (c.tipo_contrato === 'PORCENTAJE') {
      return `${c.porcentaje_chofer}% chofer`;
    }
    if (c.tipo_contrato === 'ALQUILER') {
      let detalle = `$${c.canon_diario?.toLocaleString() || 0}/día`;
      if (c.km_incluidos_dia) {
        detalle += ` | ${c.km_incluidos_dia} km`;
      }
      if (c.modalidad_computo === 'SEMANAL') {
        detalle += ' | Semanal';
      }
      return detalle;
    }
    return 'Dueño conduce';
  };

  if (isLoading) return <div className="p-8 text-center">Cargando contratos...</div>;

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button variant={filterActivo === true ? 'default' : 'outline'} onClick={() => setFilterActivo(true)}>
          Activos
        </Button>
        <Button variant={filterActivo === false ? 'default' : 'outline'} onClick={() => setFilterActivo(false)}>
          Finalizados
        </Button>
        <Button variant={filterActivo === undefined ? 'default' : 'outline'} onClick={() => setFilterActivo(undefined)}>
          Todos
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Vehículo</TableHead>
              <TableHead>Chofer</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Horario</TableHead>
              <TableHead>Días</TableHead>
              <TableHead>Detalle</TableHead>
              <TableHead>Vigencia</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contratos?.map((c) => (
              <TableRow key={c.id}>
                <TableCell className="font-medium">
                  {c.patente} – {c.marca} {c.modelo}
                </TableCell>
                <TableCell>
                  {c.tipo_contrato === 'AUTO_GESTION' ? (
                    <span className="text-muted-foreground text-xs">(dueño)</span>
                  ) : (
                    `${c.chofer_nombre} ${c.chofer_apellido || ''}`
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{getTipoContratoLabel(c.tipo_contrato)}</Badge>
                </TableCell>
                <TableCell className="text-sm">
                  {c.hora_inicio && c.hora_fin ? `${c.hora_inicio} - ${c.hora_fin}` : '—'}
                </TableCell>
                <TableCell className="text-sm">
                  {c.dias_contractuales?.length ? formatDias(c.dias_contractuales) : '—'}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {getDetalleContrato(c)}
                </TableCell>
                <TableCell className="text-xs">
                  {format(new Date(c.fecha_inicio), 'dd/MM/yy', { locale: es })}
                  {c.fecha_fin && ` → ${format(new Date(c.fecha_fin), 'dd/MM/yy', { locale: es })}`}
                </TableCell>
                <TableCell>
                  <EstadoBadge estado={c.estado_contrato || 'ACTIVO'} activo={c.activo} />
                </TableCell>
                <TableCell>
                  {c.activo && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => setContratoToFinalize(c)}
                    >
                      Finalizar
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {contratos?.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} className="text-center">No hay contratos</TableCell>
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
              El contrato de <strong>{contratoToFinalize?.patente}</strong> con el chofer{' '}
              <strong>{contratoToFinalize?.chofer_nombre} {contratoToFinalize?.chofer_apellido}</strong> será finalizado.
              Esta acción no se puede deshacer.
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