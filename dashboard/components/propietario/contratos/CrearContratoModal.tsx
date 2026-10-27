'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { useCrearContrato, useEditarContrato } from '@/hooks/propietario/useContratos';
import { useVerificarDisponibilidad } from '@/hooks/propietario/useVerificarDisponibilidad';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { formatApiError } from '@/lib/utils';
import { DiasContractualesCheckbox } from './DiasContractualesCheckbox';
import { ModalidadComputoRadio } from './ModalidadComputoRadio';
import { TratamientoDiaRadio } from './TratamientoDiaRadio';
import { HorarioSelector } from './HorarioSelector';
import { CompensacionKMSelector } from './CompensacionKMSelector';

interface Vehiculo {
  id: string;
  patente: string;
  marca: string;
  modelo: string;
}

interface Chofer {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  telefono: string;
  calificacion_promedio: number;
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  vehiculoId?: string;
  contratoAEditar?: any | null;
}

const TIPOS_CONTRATO = [
  { value: 'AUTO_GESTION', label: 'Auto-gestionado (dueño maneja)' },
  { value: 'PORCENTAJE', label: 'Chofer a porcentaje' },
  { value: 'ALQUILER', label: 'Alquiler (canon diario)' },
];

export default function CrearContratoModal({
  open,
  onOpenChange,
  onSuccess,
  vehiculoId,
  contratoAEditar,
}: Props) {
  const { user } = useAuth();
  const isEditing = !!contratoAEditar;

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [choferes, setChoferes] = useState<Chofer[]>([]);
  const [loading, setLoading] = useState(false);

  const crearMutation = useCrearContrato();
  const editarMutation = useEditarContrato();
  const isSaving = crearMutation.isPending || editarMutation.isPending;

  const [showConfirmZeroKM, setShowConfirmZeroKM] = useState(false);
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [errores, setErrores] = useState<string[]>([]);

  const [formData, setFormData] = useState({
    vehiculo_id: vehiculoId || '',
    chofer_id: '',
    tipo_contrato: 'ALQUILER',
    porcentaje_chofer: 50,
    hora_inicio: '06:00',
    hora_fin: '14:00',
    duracion_minima_horas: 6,
    permite_extension: false,
    hora_fin_extension: null as string | null,
    dias_contractuales: [] as string[],
    modalidad_computo: 'DIARIO' as 'DIARIO' | 'SEMANAL',
    dia_inicio_semana: 'lunes',
    tratamiento_dia_no_trabajado: 'POR_DISPONIBILIDAD' as 'POR_DISPONIBILIDAD' | 'POR_USO_EFECTIVO',
    canon_diario: 0,
    km_incluidos_dia: 0,
    valor_km_excedente: 0,
    compensacion_km: 'DIARIA' as 'DIARIA' | 'ACUMULADA' | 'COMPENSADA',
    fecha_inicio: new Date().toISOString().split('T')[0],
    fecha_fin: null as string | null,
  });

  const { data: disponibilidad, isLoading: checking, refetch: refetchDisponibilidad } = useVerificarDisponibilidad({
    vehiculo_id: formData.vehiculo_id || undefined,
    chofer_id: formData.chofer_id || undefined,
    hora_inicio: formData.hora_inicio,
    hora_fin: formData.hora_fin,
    dias_contractuales: formData.dias_contractuales,
    fecha_inicio: formData.fecha_inicio,
    fecha_fin: formData.fecha_fin || undefined,
  });

  const tieneConflictos = (disponibilidad?.conflictos?.length ?? 0) > 0;

  useEffect(() => {
    if (vehiculoId && !isEditing) {
      setFormData((prev) => ({ ...prev, vehiculo_id: vehiculoId }));
    }
  }, [vehiculoId, isEditing]);

  useEffect(() => {
    if (open && contratoAEditar) {
      setFormData({
        vehiculo_id: contratoAEditar.vehiculo_id,
        chofer_id: contratoAEditar.chofer_id,
        tipo_contrato: contratoAEditar.tipo_contrato,
        porcentaje_chofer: contratoAEditar.porcentaje_chofer || 50,
        hora_inicio: contratoAEditar.hora_inicio || '06:00',
        hora_fin: contratoAEditar.hora_fin || '14:00',
        duracion_minima_horas: contratoAEditar.duracion_minima_horas || 6,
        permite_extension: contratoAEditar.permite_extension || false,
        hora_fin_extension: contratoAEditar.hora_fin_extension || null,
        dias_contractuales: contratoAEditar.dias_contractuales || [],
        modalidad_computo: contratoAEditar.modalidad_computo || 'DIARIO',
        dia_inicio_semana: contratoAEditar.dia_inicio_semana || 'lunes',
        tratamiento_dia_no_trabajado: contratoAEditar.tratamiento_dia_no_trabajado || 'POR_DISPONIBILIDAD',
        canon_diario: contratoAEditar.canon_diario || 0,
        km_incluidos_dia: contratoAEditar.km_incluidos_dia || 0,
        valor_km_excedente: contratoAEditar.valor_km_excedente || 0,
        compensacion_km: contratoAEditar.compensacion_km || 'DIARIA',
        fecha_inicio: contratoAEditar.fecha_inicio ? contratoAEditar.fecha_inicio.split('T')[0] : new Date().toISOString().split('T')[0],
        fecha_fin: contratoAEditar.fecha_fin ? contratoAEditar.fecha_fin.split('T')[0] : null,
      });
    } else if (open && !contratoAEditar) {
      resetForm();
    }
  }, [open, contratoAEditar]);

  useEffect(() => {
    if (open) cargarDatos();
  }, [open]);

  useEffect(() => {
    if (open && (formData.vehiculo_id || formData.chofer_id)) refetchDisponibilidad();
  }, [formData.vehiculo_id, formData.chofer_id, formData.hora_inicio, formData.hora_fin, formData.dias_contractuales, formData.fecha_inicio, formData.fecha_fin, open, refetchDisponibilidad]);

  const cargarDatos = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const [vehiculosRes, choferesRes] = await Promise.all([
        apiClient.get('/api/propietario/vehiculos'),
        apiClient.get('/api/propietario/choferes/disponibles?hora_inicio=06:00&hora_fin=14:00'),
      ]);
      setVehiculos(vehiculosRes.data || []);
      setChoferes(choferesRes.data || []);
    } catch (error: any) {
      toast.error(formatApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const validarFormulario = (): string[] => {
    const errores: string[] = [];
    if (!formData.vehiculo_id) errores.push('Debes seleccionar un vehículo');
    if (!formData.chofer_id) errores.push('Debes seleccionar un chofer');

    if (formData.tipo_contrato === 'ALQUILER') {
      if (Number(formData.canon_diario) <= 0) errores.push('El Canon Diario debe ser mayor a 0');
      if (Number(formData.km_incluidos_dia) <= 0) errores.push('Los KM Incluidos deben ser mayores a 0');
      if (formData.dias_contractuales.length === 0) errores.push('Debes seleccionar al menos un día contractual');
    }

    if (formData.tipo_contrato !== 'ALQUILER') {
      const [hInicio, mInicio] = formData.hora_inicio.split(':').map(Number);
      const [hFin, mFin] = formData.hora_fin.split(':').map(Number);
      let duracion = ((hFin * 60 + mFin) - (hInicio * 60 + mInicio)) / 60;
      if (duracion < 0) duracion += 24;
      if (duracion < 6) errores.push(`La duración del turno (${duracion.toFixed(1)}h) debe ser de al menos 6 horas`);
      if (duracion > 16) errores.push(`La duración del turno (${duracion.toFixed(1)}h) no puede superar las 16 horas`);
    }

    if (formData.fecha_fin && formData.fecha_fin < formData.fecha_inicio) {
      errores.push('La fecha de finalización no puede ser anterior a la fecha de inicio');
    }
    return errores;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (tieneConflictos) {
      setErrores(disponibilidad?.conflictos || ['Hay conflictos que resolver']);
      setShowErrorDialog(true);
      return;
    }
    const erroresValidacion = validarFormulario();
    if (erroresValidacion.length > 0) {
      setErrores(erroresValidacion);
      setShowErrorDialog(true);
      return;
    }
    if (Number(formData.valor_km_excedente) === 0 && formData.tipo_contrato === 'ALQUILER') {
      setShowConfirmZeroKM(true);
      return;
    }
    await enviarContrato();
  };

  const enviarContrato = async () => {
    setShowConfirmZeroKM(false);
    try {
      const payload: any = {
        vehiculo_id: formData.vehiculo_id,
        chofer_id: formData.chofer_id,
        tipo_contrato: formData.tipo_contrato,
        hora_inicio: formData.hora_inicio,
        hora_fin: formData.hora_fin,
        duracion_minima_horas: Number(formData.duracion_minima_horas) || 6,
        permite_extension: formData.permite_extension,
        hora_fin_extension: formData.permite_extension ? formData.hora_fin_extension : null,
        fecha_inicio: formData.fecha_inicio,
        fecha_fin: formData.fecha_fin || null,
      };

      if (formData.tipo_contrato === 'PORCENTAJE') {
        payload.porcentaje_chofer = Number(formData.porcentaje_chofer) || 0;
      }

      if (formData.tipo_contrato === 'ALQUILER') {
        payload.dias_contractuales = formData.dias_contractuales;
        payload.modalidad_computo = formData.modalidad_computo;
        payload.dia_inicio_semana = formData.modalidad_computo === 'SEMANAL' ? formData.dia_inicio_semana : null;
        payload.tratamiento_dia_no_trabajado = formData.tratamiento_dia_no_trabajado;
        payload.canon_diario = Number(formData.canon_diario) || 0;
        payload.km_incluidos_dia = Number(formData.km_incluidos_dia) || 0;
        payload.valor_km_excedente = Number(formData.valor_km_excedente) || 0;
        payload.compensacion_km = formData.compensacion_km;
      }

      if (isEditing && contratoAEditar) {
        await editarMutation.mutateAsync({ id: contratoAEditar.id, data: payload });
      } else {
        await crearMutation.mutateAsync(payload);
      }

      onSuccess();
      onOpenChange(false);
      resetForm();
    } catch (error: any) {
      const erroresRespuesta: string[] = [];
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) erroresRespuesta.push(...detail.map((d: any) => d.msg || d.message || JSON.stringify(d)));
        else if (typeof detail === 'string') erroresRespuesta.push(detail);
        else erroresRespuesta.push(formatApiError(error));
      } else {
        erroresRespuesta.push(formatApiError(error));
      }
      setErrores(erroresRespuesta);
      setShowErrorDialog(true);
    }
  };

  const resetForm = () => {
    setFormData({
      vehiculo_id: vehiculoId || '',
      chofer_id: '',
      tipo_contrato: 'ALQUILER',
      porcentaje_chofer: 50,
      hora_inicio: '06:00',
      hora_fin: '14:00',
      duracion_minima_horas: 6,
      permite_extension: false,
      hora_fin_extension: null,
      dias_contractuales: [],
      modalidad_computo: 'DIARIO',
      dia_inicio_semana: 'lunes',
      tratamiento_dia_no_trabajado: 'POR_DISPONIBILIDAD',
      canon_diario: 0,
      km_incluidos_dia: 0,
      valor_km_excedente: 0,
      compensacion_km: 'DIARIA',
      fecha_inicio: new Date().toISOString().split('T')[0],
      fecha_fin: null,
    });
  };

  const esAlquiler = formData.tipo_contrato === 'ALQUILER';
  const esPorcentaje = formData.tipo_contrato === 'PORCENTAJE';

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{isEditing ? 'Editar Contrato' : 'Nuevo Contrato'}</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit}>
            <div className="space-y-6 py-4">
              {/* Datos Básicos */}
              <div className="space-y-4 border-b pb-4">
                <h3 className="text-sm font-medium text-muted-foreground">Datos Básicos</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Vehículo *</Label>
                    <Select value={formData.vehiculo_id} onValueChange={(v) => setFormData({ ...formData, vehiculo_id: v })} required disabled={!!vehiculoId || isEditing}>
                      <SelectTrigger><SelectValue placeholder="Seleccionar vehículo" /></SelectTrigger>
                      <SelectContent>
                        {vehiculos.map((v) => <SelectItem key={v.id} value={v.id}>{v.patente} - {v.marca} {v.modelo}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Chofer *</Label>
                    <Select value={formData.chofer_id} onValueChange={(v) => setFormData({ ...formData, chofer_id: v })} required disabled={formData.tipo_contrato === 'AUTO_GESTION' || isEditing}>
                      <SelectTrigger><SelectValue placeholder="Seleccionar chofer" /></SelectTrigger>
                      <SelectContent>
                        {choferes.map((c) => <SelectItem key={c.id} value={c.id}>{c.nombre} {c.apellido}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Tipo de Contrato *</Label>
                    <Select value={formData.tipo_contrato} onValueChange={(v) => setFormData({ ...formData, tipo_contrato: v })} disabled={isEditing}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {TIPOS_CONTRATO.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* PORCENTAJE: Muestra Porcentaje y Horarios */}
              {esPorcentaje && (
                <>
                  <div className="space-y-4 border-b pb-4">
                    <h3 className="text-sm font-medium text-muted-foreground">Configuración de Porcentaje</h3>
                    <div className="space-y-2">
                      <Label>Porcentaje del Chofer (%) *</Label>
                      <Input type="number" min="0" max="100" step="any" value={formData.porcentaje_chofer || ''} onChange={(e) => setFormData({ ...formData, porcentaje_chofer: e.target.value === '' ? 0 : Number(e.target.value) })} required />
                    </div>
                  </div>

                  <div className="space-y-4 border-b pb-4">
                    <h3 className="text-sm font-medium text-muted-foreground">Horario del Turno</h3>
                    <HorarioSelector
                      horaInicio={formData.hora_inicio}
                      horaFin={formData.hora_fin}
                      duracionMinimaHoras={formData.duracion_minima_horas}
                      permiteExtension={formData.permite_extension}
                      horaFinExtension={formData.hora_fin_extension}
                      onChange={(data) => setFormData((prev) => ({ ...prev, hora_inicio: data.horaInicio, hora_fin: data.horaFin, duracion_minima_horas: data.duracionMinimaHoras, permite_extension: data.permiteExtension, hora_fin_extension: data.horaFinExtension }))}
                    />
                  </div>
                </>
              )}

              {/* ALQUILER: Muestra Canon, KM, Días, Modalidad, etc. */}
              {esAlquiler && (
                <>
                  <div className="space-y-4 border-b pb-4">
                    <h3 className="text-sm font-medium text-muted-foreground">Días Contractuales</h3>
                    <DiasContractualesCheckbox value={formData.dias_contractuales} onChange={(dias) => setFormData((prev) => ({ ...prev, dias_contractuales: dias }))} />
                  </div>
                  <div className="space-y-4 border-b pb-4">
                    <h3 className="text-sm font-medium text-muted-foreground">Modalidad y Tratamiento</h3>
                    <ModalidadComputoRadio value={formData.modalidad_computo} onChange={(val) => setFormData((prev) => ({ ...prev, modalidad_computo: val }))} diaInicioSemana={formData.dia_inicio_semana} onDiaInicioChange={(val) => setFormData((prev) => ({ ...prev, dia_inicio_semana: val }))} />
                    <TratamientoDiaRadio value={formData.tratamiento_dia_no_trabajado} onChange={(val) => setFormData((prev) => ({ ...prev, tratamiento_dia_no_trabajado: val }))} />
                  </div>
                  <div className="space-y-4 border-b pb-4">
                    <h3 className="text-sm font-medium text-muted-foreground">Parámetros Económicos</h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Canon Diario ($) *</Label>
                        <Input type="number" min="0" step="any" value={formData.canon_diario || ''} onChange={(e) => setFormData({ ...formData, canon_diario: e.target.value === '' ? 0 : Number(e.target.value) })} required />
                      </div>
                      <div className="space-y-2">
                        <Label>KM Incluidos *</Label>
                        <Input type="number" min="0" step="any" value={formData.km_incluidos_dia || ''} onChange={(e) => setFormData({ ...formData, km_incluidos_dia: e.target.value === '' ? 0 : Number(e.target.value) })} required />
                      </div>
                      <div className="space-y-2">
                        <Label>Valor KM Excedente ($) *</Label>
                        <Input type="number" min="0" step="any" value={formData.valor_km_excedente || ''} onChange={(e) => setFormData({ ...formData, valor_km_excedente: e.target.value === '' ? 0 : Number(e.target.value) })} required />
                      </div>
                    </div>
                    <div className="mt-4">
                      <CompensacionKMSelector value={formData.compensacion_km} onChange={(val) => setFormData({ ...formData, compensacion_km: val })} />
                    </div>
                  </div>
                </>
              )}

              {/* Fechas de Vigencia (siempre visibles) */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-muted-foreground">Vigencia</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Fecha Inicio *</Label>
                    <Input type="date" value={formData.fecha_inicio} onChange={(e) => setFormData({ ...formData, fecha_inicio: e.target.value })} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Fecha Fin (opcional)</Label>
                    <Input type="date" value={formData.fecha_fin || ''} onChange={(e) => setFormData({ ...formData, fecha_fin: e.target.value || null })} />
                  </div>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancelar</Button>
              <Button type="submit" disabled={isSaving || tieneConflictos || checking}>
                {isSaving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                {isEditing ? 'Guardar Cambios' : 'Crear Contrato'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Diálogos de Confirmación */}
      <AlertDialog open={showConfirmZeroKM} onOpenChange={setShowConfirmZeroKM}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Valor KM Excedente</AlertDialogTitle>
            <AlertDialogDescription>El valor de KM excedente está en $0. ¿Estás seguro?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowConfirmZeroKM(false)}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={enviarContrato}>Sí, continuar</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showErrorDialog} onOpenChange={setShowErrorDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-red-600"><AlertCircle className="h-5 w-5" />No se pudo guardar el contrato</AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-3">
                <ul className="list-disc list-inside space-y-1">
                  {errores.map((error, index) => <li key={index} className="text-sm text-red-600">{error}</li>)}
                </ul>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction onClick={() => setShowErrorDialog(false)}>Entendido</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}