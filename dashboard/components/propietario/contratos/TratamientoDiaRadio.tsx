'use client';

import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';

interface Props {
  value: 'POR_DISPONIBILIDAD' | 'POR_USO_EFECTIVO';
  onChange: (value: 'POR_DISPONIBILIDAD' | 'POR_USO_EFECTIVO') => void;
  disabled?: boolean;
}

export function TratamientoDiaRadio({ value, onChange, disabled }: Props) {
  return (
    <div className="space-y-2">
      <span className="text-sm font-medium">Tratamiento de Día No Trabajado</span>
      <RadioGroup
        value={value}
        onValueChange={(val) => onChange(val as 'POR_DISPONIBILIDAD' | 'POR_USO_EFECTIVO')}
        className="flex space-x-4 mt-2"
        disabled={disabled}
      >
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="POR_DISPONIBILIDAD" id="disponibilidad" />
          <Label htmlFor="disponibilidad" className="cursor-pointer">
            Disponibilidad
          </Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="POR_USO_EFECTIVO" id="uso-efectivo" />
          <Label htmlFor="uso-efectivo" className="cursor-pointer">
            Uso Efectivo
          </Label>
        </div>
      </RadioGroup>
    </div>
  );
}