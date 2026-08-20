'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

const DIAS = [
  { key: 'lunes', label: 'Lun' },
  { key: 'martes', label: 'Mar' },
  { key: 'miercoles', label: 'Mié' },
  { key: 'jueves', label: 'Jue' },
  { key: 'viernes', label: 'Vie' },
  { key: 'sabado', label: 'Sáb' },
  { key: 'domingo', label: 'Dom' },
];

interface Props {
  value: string[];
  onChange: (dias: string[]) => void;
  disabled?: boolean;
}

export function DiasContractualesCheckbox({ value, onChange, disabled }: Props) {
  const toggleDia = (dia: string) => {
    const nuevos = value.includes(dia)
      ? value.filter((d) => d !== dia)
      : [...value, dia];
    onChange(nuevos);
  };

  const toggleAll = () => {
    if (value.length === DIAS.length) {
      onChange([]);
    } else {
      onChange(DIAS.map((d) => d.key));
    }
  };

  const todosSeleccionados = value.length === DIAS.length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Días Contractuales</span>
        <button
          type="button"
          onClick={toggleAll}
          className="text-xs text-blue-600 hover:underline"
          disabled={disabled}
        >
          {todosSeleccionados ? 'Deseleccionar todos' : 'Seleccionar todos'}
        </button>
      </div>
      <div className="flex flex-wrap gap-4">
        {DIAS.map((dia) => (
          <div key={dia.key} className="flex items-center space-x-2">
            <Checkbox
              id={`dia-${dia.key}`}
              checked={value.includes(dia.key)}
              onCheckedChange={() => toggleDia(dia.key)}
              disabled={disabled}
            />
            <Label htmlFor={`dia-${dia.key}`} className="text-sm cursor-pointer">
              {dia.label}
            </Label>
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground">
        {value.length} de {DIAS.length} días seleccionados
      </p>
    </div>
  );
}