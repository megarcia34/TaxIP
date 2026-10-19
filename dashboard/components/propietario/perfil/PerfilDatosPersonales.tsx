// D:\ataxip\dashboard\components\propietario\perfil\PerfilDatosPersonales.tsx
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
import { Loader2, Save, User } from 'lucide-react';
import { usePerfil, useUpdatePerfil, useCiudadesOperativas } from '@/hooks/propietario/usePerfil';
import { useAuth } from '@/hooks/useAuth';

export default function PerfilDatosPersonales() {
  const { user } = useAuth();
  const { data: perfil, isLoading } = usePerfil();
  const { data: ciudades = [] } = useCiudadesOperativas();
  const updateMutation = useUpdatePerfil();

  const [form, setForm] = useState({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    documento: '',
    direccion: '',
    ciudad_id: '',
    codigo_postal: '',
    fecha_nacimiento: '',
  });

  // Precarga 1: datos que ya conocemos desde useAuth
  useEffect(() => {
    if (user) {
      setForm((prev) => ({
        ...prev,
        nombre: prev.nombre || (user as any).nombre || '',
        email: prev.email || user.email || '',
      }));
    }
  }, [user]);

  // Precarga 2: cuando llega el perfil completo, sobreescribe
  useEffect(() => {
    if (perfil) {
      setForm({
        nombre: perfil.nombre || '',
        apellido: perfil.apellido || '',
        email: perfil.email || '',
        telefono: perfil.telefono || '',
        documento: perfil.documento || '',
        direccion: perfil.direccion || '',
        ciudad_id: perfil.ciudad_id || '',
        codigo_postal: perfil.codigo_postal || '',
        fecha_nacimiento: perfil.fecha_nacimiento || '',
      });
    }
  }, [perfil]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      nombre: form.nombre,
      apellido: form.apellido,
      telefono: form.telefono || null,
      documento: form.documento || null,
      direccion: form.direccion || null,
      ciudad_id: form.ciudad_id || null,
      codigo_postal: form.codigo_postal || null,
      fecha_nacimiento: form.fecha_nacimiento || null,
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
          <User className="h-5 w-5" />
          Datos personales
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nombre">Nombre</Label>
              <Input
                id="nombre"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="apellido">Apellido</Label>
              <Input
                id="apellido"
                value={form.apellido}
                onChange={(e) => setForm({ ...form, apellido: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                value={form.email}
                disabled
                className="bg-muted cursor-not-allowed"
              />
              <p className="text-xs text-muted-foreground">
                El email no se puede modificar
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="telefono">Telefono</Label>
              <Input
                id="telefono"
                value={form.telefono}
                onChange={(e) => setForm({ ...form, telefono: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="documento">Documento</Label>
              <Input
                id="documento"
                value={form.documento}
                onChange={(e) => setForm({ ...form, documento: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="fecha_nacimiento">Fecha de nacimiento</Label>
              <Input
                id="fecha_nacimiento"
                type="date"
                value={form.fecha_nacimiento}
                onChange={(e) => setForm({ ...form, fecha_nacimiento: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="direccion">Direccion</Label>
              <Input
                id="direccion"
                value={form.direccion}
                onChange={(e) => setForm({ ...form, direccion: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="codigo_postal">Codigo postal</Label>
              <Input
                id="codigo_postal"
                value={form.codigo_postal}
                onChange={(e) => setForm({ ...form, codigo_postal: e.target.value })}
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="ciudad">Ciudad</Label>
              <Select
                value={form.ciudad_id || 'sin-seleccionar'}
                onValueChange={(v) => setForm({ ...form, ciudad_id: v === 'sin-seleccionar' ? '' : v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar ciudad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sin-seleccionar">Sin seleccionar</SelectItem>
                  {ciudades.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.nombre}
                      {c.provincia ? ` - ${c.provincia}` : ''}
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