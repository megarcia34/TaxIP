'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

interface Props {
  horaInicio: string;
  horaFin: string;
  duracionMinimaHoras: number;
  permiteExtension: boolean;
  horaFinExtension: string | null;
  onChange: (data: {
    horaInicio: string;
    horaFin: string;
    duracionMinimaHoras: number;
    permiteExtension: boolean;
    horaFinExtension: string | null;
  }) => void;
  disabled?: boolean;
}

export function HorarioSelector({
  horaInicio,
  horaFin,
  duracionMinimaHoras,
  permiteExtension,
  horaFinExtension,
  onChange,
  disabled,
}: Props) {
  const handleChange = (field: string, value: any) => {
    onChange({
      horaInicio,
      horaFin,
      duracionMinimaHoras,
      permiteExtension,
      horaFinExtension,
      [field]: value,
    });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label>Hora Inicio *</Label>
          <Input
            type="time"
            value={horaInicio}
            onChange={(e) => handleChange('horaInicio', e.target.value)}
            disabled={disabled}
            required
          />
        </div>
        <div className="space-y-2">
          <Label>Hora Fin *</Label>
          <Input
            type="time"
            value={horaFin}
            onChange={(e) => handleChange('horaFin', e.target.value)}
            disabled={disabled}
            required
          />
        </div>
        <div className="space-y-2">
          <Label>Duración Mínima (horas) *</Label>
          <Input
            type="number"
            min={1}
            max={24}
            value={duracionMinimaHoras}
            onChange={(e) => handleChange('duracionMinimaHoras', Number(e.target.value))}
            disabled={disabled}
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="permite-extension"
            checked={permiteExtension}
            onCheckedChange={(checked) => handleChange('permiteExtension', checked === true)}
            disabled={disabled}
          />
          <Label htmlFor="permite-extension" className="cursor-pointer">
            Permite extensión horaria
          </Label>
        </div>
        {permiteExtension && (
          <div className="pl-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Hora límite de extensión *</Label>
                <Input
                  type="time"
                  value={horaFinExtension || ''}
                  onChange={(e) => handleChange('horaFinExtension', e.target.value || null)}
                  disabled={disabled}
                  required={permiteExtension}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}