'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/hooks/use-toast';
import { ChoferDisponible } from '@/types/propietario';

const contratoSchema = z.object({
  vehiculo_id: z.string().uuid('Seleccione un vehículo'),
  chofer_id: z.string().uuid('Seleccione un chofer'),
  tipo_contrato: z.enum(['AUTO_GESTION', 'PORCENTAJE', 'CANON_FIJO']),
  turno_asignado: z.enum(['DIURNO', 'NOCTURNO', 'COMPLETO']),
  porcentaje_chofer: z.number().min(0).max(100).optional(),
  monto_diario: z.number().positive().optional(),
}).superRefine((data, ctx) => {
  if (data.tipo_contrato === 'PORCENTAJE' && (data.porcentaje_chofer === undefined || data.porcentaje_chofer <= 0)) {
    ctx.addIssue({ code: 'custom', path: ['porcentaje_chofer'], message: 'Porcentaje requerido' });
  }
  if (data.tipo_contrato === 'CANON_FIJO' && (data.monto_diario === undefined || data.monto_diario <= 0)) {
    ctx.addIssue({ code: 'custom', path: ['monto_diario'], message: 'Monto diario requerido' });
  }
});

type FormData = z.infer<typeof contratoSchema>;

interface VehiculoOption {
  id: string;
  patente: string;
  marca: string;
  modelo: string;
}

async function fetchVehiculos(): Promise<VehiculoOption[]> {
  const res = await fetch('/api/propietario/vehiculos');
  if (!res.ok) throw new Error('Error al cargar vehículos');
  return res.json();
}

async function fetchChoferesDisponibles(turno: string): Promise<ChoferDisponible[]> {
  const res = await fetch(`/api/propietario/choferes/disponibles?turno=${turno}`);
  if (!res.ok) throw new Error('Error al cargar choferes disponibles');
  return res.json();
}

async function createContrato(data: FormData) {
  const res = await fetch('/api/propietario/contratos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Error al crear contrato');
  }
  return res.json();
}

export function CrearContratoModal() {
  const [open, setOpen] = useState(false);
  const [selectedTurno, setSelectedTurno] = useState<'DIURNO' | 'NOCTURNO' | 'COMPLETO'>('DIURNO');
  const queryClient = useQueryClient();

  const { data: vehiculos, isLoading: loadingVehiculos } = useQuery({
    queryKey: ['vehiculos-propietario'],
    queryFn: fetchVehiculos,
  });

  const { data: choferesDisponibles, refetch: refetchChoferes } = useQuery({
    queryKey: ['choferes-disponibles', selectedTurno],
    queryFn: () => fetchChoferesDisponibles(selectedTurno),
    enabled: open,
  });

  const form = useForm<FormData>({
    resolver: zodResolver(contratoSchema),
    defaultValues: {
      tipo_contrato: 'PORCENTAJE',
      turno_asignado: 'DIURNO',
      porcentaje_chofer: 40,
      monto_diario: 5000,
    },
  });

  const tipoContrato = form.watch('tipo_contrato');

  useEffect(() => {
    const subscription = form.watch((value, { name }) => {
      if (name === 'turno_asignado' && value.turno_asignado) {
        setSelectedTurno(value.turno_asignado as any);
        refetchChoferes();
        form.setValue('chofer_id', '');
      }
    });
    return () => subscription.unsubscribe();
  }, [form, refetchChoferes]);

  const mutation = useMutation({
    mutationFn: createContrato,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contratos'] });
      toast({ title: 'Contrato creado', description: 'El contrato se ha registrado exitosamente.' });
      setOpen(false);
      form.reset();
    },
    onError: (error: Error) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  const onSubmit = (data: FormData) => mutation.mutate(data);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Nuevo Contrato</Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Crear nuevo contrato</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="vehiculo_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Vehículo</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar vehículo" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {vehiculos?.map(v => (
                        <SelectItem key={v.id} value={v.id}>{v.patente} - {v.marca} {v.modelo}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="turno_asignado"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Turno</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="DIURNO">Diurno</SelectItem>
                      <SelectItem value="NOCTURNO">Nocturno</SelectItem>
                      <SelectItem value="COMPLETO">Completo</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="chofer_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Chofer</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar chofer disponible" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {choferesDisponibles?.map(c => (
                        <SelectItem key={c.id} value={c.id}>
                          {c.nombre} {c.apellido} - ⭐ {c.calificacion_promedio?.toFixed(1) || 'N/A'}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="tipo_contrato"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Modelo de negocio</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="AUTO_GESTION">Auto‑gestionado (dueño conduce)</SelectItem>
                      <SelectItem value="PORCENTAJE">Chofer a porcentaje</SelectItem>
                      <SelectItem value="CANON_FIJO">Alquiler fijo (canon diario)</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {tipoContrato === 'PORCENTAJE' && (
              <FormField
                control={form.control}
                name="porcentaje_chofer"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Porcentaje para el chofer: {field.value}%</FormLabel>
                    <FormControl>
                      <Slider min={0} max={100} step={1} value={[field.value || 40]} onValueChange={(vals) => field.onChange(vals[0])} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {tipoContrato === 'CANON_FIJO' && (
              <FormField
                control={form.control}
                name="monto_diario"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Monto diario (canon)</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="Ej: 5000" {...field} value={field.value || ''} onChange={e => field.onChange(Number(e.target.value))} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <div className="flex justify-end space-x-2 pt-4">
              <Button variant="outline" type="button" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creando...' : 'Crear contrato'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}