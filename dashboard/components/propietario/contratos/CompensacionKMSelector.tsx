'use client';

import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface Props {
  value: 'DIARIA' | 'ACUMULADA' | 'COMPENSADA';
  onChange: (value: 'DIARIA' | 'ACUMULADA' | 'COMPENSADA') => void;
  disabled?: boolean;
}

const OPCIONES = [
  {
    value: 'DIARIA' as const,
    label: 'Diaria',
    descripcion: 'Excedente calculado por día. Se cobra cada día individualmente.',
    ejemplo: 'Lunes: +50km → se cobran 50km',
  },
  {
    value: 'ACUMULADA' as const,
    label: 'Acumulada',
    descripcion: 'Excedente calculado sobre el total del período.',
    ejemplo: 'Lunes: +50km, Martes: -30km → Total: +20km → se cobran 20km',
  },
  {
    value: 'COMPENSADA' as const,
    label: 'Compensada',
    descripcion: 'Compensación entre días. Los excedentes se compensan con sobrantes.',
    ejemplo: 'Lunes: +50km, Martes: -50km → Total: 0km → NO se cobra',
  },
];

export function CompensacionKMSelector({ value, onChange, disabled }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Compensación de KM Excedentes</span>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Info className="h-4 w-4 text-muted-foreground cursor-help" />
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              <p className="text-xs">
                Define cómo se calcularán los kilómetros excedentes cuando hay múltiples días en el contrato.
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <RadioGroup
        value={value}
        onValueChange={(val) => onChange(val as 'DIARIA' | 'ACUMULADA' | 'COMPENSADA')}
        className="space-y-2"
        disabled={disabled}
      >
        {OPCIONES.map((opcion) => (
          <div
            key={opcion.value}
            className={`flex items-start space-x-3 rounded-lg border p-3 ${
              value === opcion.value ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20' : ''
            }`}
          >
            <RadioGroupItem value={opcion.value} id={opcion.value} className="mt-1" />
            <div className="flex-1">
              <Label htmlFor={opcion.value} className="font-medium cursor-pointer">
                {opcion.label}
              </Label>
              <p className="text-xs text-muted-foreground">{opcion.descripcion}</p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1 font-mono">
                {opcion.ejemplo}
              </p>
            </div>
          </div>
        ))}
      </RadioGroup>
    </div>
  );
}