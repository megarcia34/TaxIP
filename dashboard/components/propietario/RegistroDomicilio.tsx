'use client'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface Props {
  data: any
  updateData: (data: any) => void
}

export default function RegistroDomicilio({ data, updateData }: Props) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="domicilio">Domicilio *</Label>
          <Input
            id="domicilio"
            placeholder="Calle y número"
            value={data.domicilio}
            onChange={(e) => updateData({ domicilio: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="numero">Número/Sector</Label>
          <Input
            id="numero"
            placeholder="Número"
            value={data.numero}
            onChange={(e) => updateData({ numero: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="piso">Piso/Manzana</Label>
          <Input
            id="piso"
            placeholder="Piso"
            value={data.piso}
            onChange={(e) => updateData({ piso: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="depto">Departamento/Casa</Label>
          <Input
            id="depto"
            placeholder="Depto"
            value={data.depto}
            onChange={(e) => updateData({ depto: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="barrio">Barrio</Label>
          <Input
            id="barrio"
            placeholder="Barrio"
            value={data.barrio}
            onChange={(e) => updateData({ barrio: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="localidad">Localidad *</Label>
          <Input
            id="localidad"
            placeholder="Localidad"
            value={data.localidad}
            onChange={(e) => updateData({ localidad: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="codigo_postal">Código Postal</Label>
          <Input
            id="codigo_postal"
            placeholder="Código Postal"
            value={data.codigo_postal}
            onChange={(e) => updateData({ codigo_postal: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="telefono">Teléfono *</Label>
          <Input
            id="telefono"
            type="tel"
            placeholder="3812345678"
            value={data.telefono}
            onChange={(e) => updateData({ telefono: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            placeholder="correo@ejemplo.com"
            value={data.email}
            onChange={(e) => updateData({ email: e.target.value })}
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="domicilio_constitucion">Domicilio Constituido</Label>
        <Input
          id="domicilio_constitucion"
          placeholder="Domicilio para notificaciones"
          value={data.domicilio_constitucion}
          onChange={(e) => updateData({ domicilio_constitucion: e.target.value })}
        />
        <p className="text-xs text-muted-foreground">Opcional. Domicilio legal para notificaciones.</p>
      </div>
    </div>
  )
}