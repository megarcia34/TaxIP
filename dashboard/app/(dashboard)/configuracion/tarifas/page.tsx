'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { tarifaService, ConfiguracionTarifa } from '@/lib/api/tarifaService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { Loader2, Save } from 'lucide-react';

export default function ConfiguracionTarifasPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<ConfiguracionTarifa | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [esNueva, setEsNueva] = useState(false);

  const [formData, setFormData] = useState({
    nombre: 'Tarifa Base',           // ✅ NUEVO
    modo_calculo: 'por_km',
    tarifa_base: 0,
    precio_por_km: 0,
    precio_por_minuto: 0,
    distancia_por_ficha: 100,
    precio_por_ficha: 0,
    precio_por_minuto_espera: 0,
    recargo_nocturno: 1.2,
    recargo_feriado: 1.0,            // ✅ NUEVO
    recargo_domingo: 1.0,
    hora_inicio_nocturno: '22:00',
    hora_fin_nocturno: '06:00',
    moneda: 'ARS',
    descripcion: '',
    activo: true,
  });

  useEffect(() => {
    const loadConfig = async () => {
      if (authLoading) return;

      if (!user) {
        router.push('/login');
        return;
      }

      if (user.rol === 'admin' && user.control_base_id) {
        setIsAdmin(true);
        try {
          setLoading(true);
          const data = await tarifaService.getMiTenant();
          setConfig(data);
          setEsNueva(false);
          setFormData({
            nombre: data.nombre || 'Tarifa Base',
            modo_calculo: data.modo_calculo || 'por_km',
            tarifa_base: data.tarifa_base || 0,
            precio_por_km: data.precio_por_km || 0,
            precio_por_minuto: data.precio_por_minuto || 0,
            distancia_por_ficha: data.distancia_por_ficha || 100,
            precio_por_ficha: data.precio_por_ficha || 0,
            precio_por_minuto_espera: data.precio_por_minuto_espera || 0,
            recargo_nocturno: data.recargo_nocturno || 1.2,
            recargo_feriado: data.recargo_feriado || 1.0,
            recargo_domingo: data.recargo_domingo || 1.0,
            hora_inicio_nocturno: data.hora_inicio_nocturno || '22:00',
            hora_fin_nocturno: data.hora_fin_nocturno || '06:00',
            moneda: data.moneda || 'ARS',
            descripcion: data.descripcion || '',
            activo: data.activo !== undefined ? data.activo : true,
          });
        } catch (error: any) {
          if (error?.response?.status === 404) {
            console.log('ℹ️ No hay tarifa configurada. Se creará una nueva.');
            setEsNueva(true);
            setConfig({ id: '' } as ConfiguracionTarifa);
            toast.info('No hay tarifa configurada. Completá los datos para crearla.');
          } else {
            console.error('Error cargando configuración:', error);
            toast.error('No se pudo cargar la configuración de tarifas');
          }
        } finally {
          setLoading(false);
        }
      } else {
        setIsAdmin(false);
        setLoading(false);
      }
    };

    loadConfig();
  }, [user, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;

    setSaving(true);
    try {
      const horaInicio = formData.hora_inicio_nocturno?.slice(0, 5) || '22:00';
      const horaFin = formData.hora_fin_nocturno?.slice(0, 5) || '06:00';

      const updateData = {
        control_base_id: user?.control_base_id || '',  // ✅ NUEVO
        nombre: formData.nombre || 'Tarifa Base',      // ✅ NUEVO
        modo_calculo: formData.modo_calculo,
        tarifa_base: formData.tarifa_base,
        precio_por_km: formData.precio_por_km,
        precio_por_minuto: formData.precio_por_minuto,
        distancia_por_ficha: formData.distancia_por_ficha,
        precio_por_ficha: formData.precio_por_ficha,
        precio_por_minuto_espera: formData.precio_por_minuto_espera,
        recargo_nocturno: formData.recargo_nocturno,
        recargo_feriado: formData.recargo_feriado,      // ✅ NUEVO
        recargo_domingo: formData.recargo_domingo,
        hora_inicio_nocturno: horaInicio,
        hora_fin_nocturno: horaFin,
        moneda: formData.moneda,
        descripcion: formData.descripcion,
        activo: formData.activo,
      };

      console.log('📤 Enviando:', updateData);

      if (esNueva) {
        await tarifaService.create(updateData);
        toast.success('Tarifa creada correctamente');
      } else {
        await tarifaService.update(config.id, updateData);
        toast.success('Configuración actualizada correctamente');
      }
      
      const data = await tarifaService.getMiTenant();
      setConfig(data);
      setEsNueva(false);
    } catch (error: any) {
      console.error('❌ Error:', error);
      console.error('❌ Response:', error.response?.data);
      toast.error(`Error: ${error.response?.data?.detail || 'Error al guardar'}`);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No tienes permisos para acceder a esta página.
              <br />
              Se requiere ser Administrador de Tenant.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Configuración de Tarifas</h1>
          <p className="text-sm text-muted-foreground">
            {esNueva 
              ? 'Crea la configuración inicial de tarifas para tu municipio' 
              : `Gestiona las tarifas para ${config?.tenant_nombre || 'tu municipio'}`}
          </p>
        </div>
        <div className="text-sm">
          <span className={config?.activo || esNueva ? 'text-green-600' : 'text-red-600'}>
            {esNueva ? '🆕 Nueva Configuración' : (config?.activo ? '✅ Activo' : '❌ Inactivo')}
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Configuración de Tarifa</CardTitle>
            <CardDescription>
              Define los parámetros de cálculo de tarifa para tu municipio.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Nombre de la tarifa */}
              <div className="space-y-2 md:col-span-2">
                <Label>Nombre de la Tarifa</Label>
                <Input
                  type="text"
                  value={formData.nombre}
                  onChange={(e) => handleChange('nombre', e.target.value)}
                  placeholder="Ej: Tarifa Base 2026"
                />
              </div>

              {/* Modo de cálculo */}
              <div className="space-y-2">
                <Label>Modo de Cálculo</Label>
                <Select
                  value={formData.modo_calculo || 'por_km'}
                  onValueChange={(value) => handleChange('modo_calculo', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar modo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ficha_argentina">Ficha Argentina</SelectItem>
                    <SelectItem value="por_km">Por Kilómetro</SelectItem>
                    <SelectItem value="por_minuto">Por Minuto</SelectItem>
                    <SelectItem value="mixto">Mixto</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Moneda</Label>
                <Select
                  value={formData.moneda || 'ARS'}
                  onValueChange={(value) => handleChange('moneda', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar moneda" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ARS">ARS ($)</SelectItem>
                    <SelectItem value="USD">USD (US$)</SelectItem>
                    <SelectItem value="EUR">EUR (€)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Tarifa Base (Bajada)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.tarifa_base}
                  onChange={(e) => handleChange('tarifa_base', parseFloat(e.target.value) || 0)}
                />
              </div>

              {(formData.modo_calculo === 'por_km' || formData.modo_calculo === 'mixto') && (
                <div className="space-y-2">
                  <Label>Precio por KM</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.precio_por_km}
                    onChange={(e) => handleChange('precio_por_km', parseFloat(e.target.value) || 0)}
                  />
                </div>
              )}

              {(formData.modo_calculo === 'por_km' || formData.modo_calculo === 'por_minuto') && (
                <div className="space-y-2">
                  <Label>Precio por Minuto</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.precio_por_minuto}
                    onChange={(e) => handleChange('precio_por_minuto', parseFloat(e.target.value) || 0)}
                  />
                </div>
              )}

              {formData.modo_calculo === 'ficha_argentina' && (
                <>
                  <div className="space-y-2">
                    <Label>Distancia por Ficha (metros)</Label>
                    <Input
                      type="number"
                      step="1"
                      value={formData.distancia_por_ficha}
                      onChange={(e) => handleChange('distancia_por_ficha', parseFloat(e.target.value) || 100)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Precio por Ficha</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={formData.precio_por_ficha}
                      onChange={(e) => handleChange('precio_por_ficha', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label>Precio por Minuto de Espera</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.precio_por_minuto_espera}
                  onChange={(e) => handleChange('precio_por_minuto_espera', parseFloat(e.target.value) || 0)}
                />
              </div>

              <div className="space-y-2">
                <Label>Recargo Nocturno (factor)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="1"
                  value={formData.recargo_nocturno}
                  onChange={(e) => handleChange('recargo_nocturno', parseFloat(e.target.value) || 1.0)}
                />
                <p className="text-xs text-muted-foreground">Ej: 1.2 = 20% de recargo</p>
              </div>

              {/* ✅ NUEVO: Recargo Feriado */}
              <div className="space-y-2">
                <Label>Recargo Feriado (factor)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="1"
                  value={formData.recargo_feriado}
                  onChange={(e) => handleChange('recargo_feriado', parseFloat(e.target.value) || 1.0)}
                />
                <p className="text-xs text-muted-foreground">Ej: 1.5 = 50% de recargo</p>
              </div>

              <div className="space-y-2">
                <Label>Recargo Domingo (factor)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="1"
                  value={formData.recargo_domingo}
                  onChange={(e) => handleChange('recargo_domingo', parseFloat(e.target.value) || 1.0)}
                />
                <p className="text-xs text-muted-foreground">Ej: 1.1 = 10% de recargo</p>
              </div>

              <div className="space-y-2">
                <Label>Hora Inicio Nocturno</Label>
                <Input
                  type="time"
                  value={formData.hora_inicio_nocturno}
                  onChange={(e) => handleChange('hora_inicio_nocturno', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Hora Fin Nocturno</Label>
                <Input
                  type="time"
                  value={formData.hora_fin_nocturno}
                  onChange={(e) => handleChange('hora_fin_nocturno', e.target.value)}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label>Descripción</Label>
                <Input
                  placeholder="Descripción adicional de la configuración"
                  value={formData.descripcion}
                  onChange={(e) => handleChange('descripcion', e.target.value)}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="activo"
                    checked={formData.activo}
                    onCheckedChange={(checked) => handleChange('activo', checked)}
                  />
                  <Label htmlFor="activo">Configuración activa</Label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end mt-6">
          <Button type="submit" disabled={saving} className="min-w-[150px]">
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Guardando...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                {esNueva ? 'Crear Tarifa' : 'Guardar Configuración'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}// BUILD 1794086645
