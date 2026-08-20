'use client';

import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';

const DIAS_SEMANA = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];

interface Props {
  value: 'DIARIO' | 'SEMANAL';
  onChange: (value: 'DIARIO' | 'SEMANAL') => void;
  diaInicioSemana: string;
  onDiaInicioChange: (value: string) => void;
  disabled?: boolean;
}

export function ModalidadComputoRadio({
  value,
  onChange,
  diaInicioSemana,
  onDiaInicioChange,
  disabled,
}: Props) {
  return (
    <div className="space-y-4">
      <div>
        <span className="text-sm font-medium">Modalidad de Cómputo</span>
        <RadioGroup
          value={value}
          onValueChange={(val) => onChange(val as 'DIARIO' | 'SEMANAL')}
          className="flex space-x-4 mt-2"
          disabled={disabled}
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="DIARIO" id="diario" />
            <Label htmlFor="diario" className="cursor-pointer">DIARIO</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="SEMANAL" id="semanal" />
            <Label htmlFor="semanal" className="cursor-pointer">SEMANAL</Label>
          </div>
        </RadioGroup>
      </div>

      {value === 'SEMANAL' && (
        <div className="pl-4 border-l-2 border-blue-200">
          <span className="text-sm font-medium">Día de inicio de semana</span>
          <RadioGroup
            value={diaInicioSemana}
            onValueChange={onDiaInicioChange}
            className="grid grid-cols-4 gap-2 mt-2"
            disabled={disabled}
          >
            {DIAS_SEMANA.map((dia) => (
              <div key={dia} className="flex items-center space-x-2">
                <RadioGroupItem value={dia} id={`inicio-${dia}`} />
                <Label htmlFor={`inicio-${dia}`} className="text-sm capitalize cursor-pointer">
                  {dia.slice(0, 3)}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      )}
    </div>
  );
}