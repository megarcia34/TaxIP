// D:\ataxip\dashboard\components\operativo\WaypointList.tsx

'use client';

import { Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AddressAutocomplete } from './AddressAutocomplete';
import { cn } from '@/lib/utils';

interface Waypoint {
  address: string;
  lat?: number;
  lng?: number;
}

interface WaypointListProps {
  /** Lista de paradas */
  waypoints: Waypoint[];
  /** Callback cuando cambia la lista */
  onChange: (waypoints: Waypoint[]) => void;
  /** Número máximo de paradas */
  maxWaypoints?: number;
  /** Deshabilitado */
  disabled?: boolean;
  /** Clases adicionales */
  className?: string;
}

/**
 * Lista dinámica de paradas intermedias
 * 
 * Características:
 * - Agregar hasta N paradas (máx 5)
 * - Eliminar paradas
 * - Cada parada tiene autocompletado de direcciones
 * - Muestra número de orden
 */
export function WaypointList({
  waypoints = [],
  onChange,
  maxWaypoints = 5,
  disabled = false,
  className = '',
}: WaypointListProps) {
  const canAdd = waypoints.length < maxWaypoints;

  const handleAdd = () => {
    if (!canAdd) return;
    onChange([...waypoints, { address: '', lat: undefined, lng: undefined }]);
  };

  const handleRemove = (index: number) => {
    const newWaypoints = [...waypoints];
    newWaypoints.splice(index, 1);
    onChange(newWaypoints);
  };

  const handleWaypointChange = (index: number, address: string, lat: number, lng: number) => {
    const newWaypoints = [...waypoints];
    newWaypoints[index] = { address, lat, lng };
    onChange(newWaypoints);
  };

  if (waypoints.length === 0) {
    return (
      <div className={className}>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAdd}
          disabled={disabled || !canAdd}
          className="w-full border-dashed text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <Plus className="h-4 w-4 mr-2" />
          Agregar parada
        </Button>
        <p className="text-xs text-gray-400 mt-1.5">
          Puedes agregar hasta {maxWaypoints} paradas intermedias
        </p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Lista de paradas */}
      {waypoints.map((waypoint, index) => (
        <div key={index} className="flex items-start gap-2">
          {/* Indicador de orden */}
          <div className="flex items-center justify-center w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-700 text-xs font-medium text-gray-500 dark:text-gray-400 flex-shrink-0 mt-1">
            {index + 1}
          </div>

          {/* Input de dirección */}
          <div className="flex-1">
            <AddressAutocomplete
              placeholder={`Parada ${index + 1}`}
              defaultValue={waypoint.address}
              initialLat={waypoint.lat}
              initialLng={waypoint.lng}
              onSelect={(address, lat, lng) => {
                handleWaypointChange(index, address, lat, lng);
              }}
              disabled={disabled}
            />
          </div>

          {/* Botón eliminar */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-7 w-7 flex-shrink-0 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
            onClick={() => handleRemove(index)}
            disabled={disabled || waypoints.length <= 1}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}

      {/* Botón agregar */}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleAdd}
        disabled={disabled || !canAdd}
        className="w-full border-dashed text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <Plus className="h-4 w-4 mr-2" />
        Agregar parada {waypoints.length >= maxWaypoints && '(máximo alcanzado)'}
      </Button>

      <p className="text-xs text-gray-400">
        {waypoints.length} de {maxWaypoints} paradas {waypoints.length >= maxWaypoints && '(máximo alcanzado)'}
      </p>
    </div>
  );
}

export default WaypointList;