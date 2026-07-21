'use client'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'

interface Props {
  data: any
  updateData: (data: any) => void
}

export default function RegistroIdentificacion({ data, updateData }: Props) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="cuil">CUIL/CUIT *</Label>
          <Input
            id="cuil"
            placeholder="20-12345678-9"
            value={data.cuil}
            onChange={(e) => updateData({ cuil: e.target.value })}
            required
          />
          <p className="text-xs text-muted-foreground">Formato: 20-12345678-9</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="fecha_nacimiento">Fecha de Nacimiento *</Label>
          <Input
            id="fecha_nacimiento"
            type="date"
            value={data.fecha_nacimiento}
            onChange={(e) => updateData({ fecha_nacimiento: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="nombre">Nombre *</Label>
          <Input
            id="nombre"
            placeholder="Nombre"
            value={data.nombre}
            onChange={(e) => updateData({ nombre: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="apellido">Apellido *</Label>
          <Input
            id="apellido"
            placeholder="Apellido"
            value={data.apellido}
            onChange={(e) => updateData({ apellido: e.target.value })}
            required
          />
        </div>
      </div>

      <Card className="bg-muted/50">
        <CardContent className="p-4 text-sm text-muted-foreground">
          <p>⚠️ Los datos de identificación no podrán ser modificados después del registro.</p>
          <p className="text-xs mt-1">Verifique que la información sea correcta.</p>
        </CardContent>
      </Card>
    </div>
  )
}