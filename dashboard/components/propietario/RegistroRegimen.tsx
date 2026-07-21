'use client'

import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'

interface Props {
  data: any
  updateData: (data: any) => void
}

export default function RegistroRegimen({ data, updateData }: Props) {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <Label>Tipo de Propietario *</Label>
        <RadioGroup
          value={data.tipo_propietario}
          onValueChange={(value) => updateData({ tipo_propietario: value })}
          className="flex flex-col space-y-2"
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="individual" id="individual" />
            <Label htmlFor="individual" className="font-normal">
              Propietario Individual
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="empresa" id="empresa" />
            <Label htmlFor="empresa" className="font-normal">
              Empresa / Persona Jurídica
            </Label>
          </div>
        </RadioGroup>
      </div>

      {data.tipo_propietario === 'empresa' && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="razon_social">Razón Social</Label>
            <Input
              id="razon_social"
              placeholder="Razón Social de la empresa"
              value={data.razon_social}
              onChange={(e) => updateData({ razon_social: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="cuit_empresa">CUIT de la Empresa</Label>
            <Input
              id="cuit_empresa"
              placeholder="30-12345678-9"
              value={data.cuit_empresa}
              onChange={(e) => updateData({ cuit_empresa: e.target.value })}
            />
          </div>
        </div>
      )}

      <Card className="bg-muted/50">
        <CardContent className="p-4 text-sm text-muted-foreground">
          <p>📋 Información importante:</p>
          <ul className="list-disc list-inside text-xs mt-2 space-y-1">
            <li>Los propietarios individuales pueden registrar hasta 5 vehículos</li>
            <li>Las empresas pueden registrar cantidad ilimitada de vehículos</li>
            <li>Los datos fiscales serán verificados</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}