/**
 * Hook que sincroniza el estado laboral del chofer con el viaje activo.
 *
 * Reglas:
 * - Si hay viaje activo en estado 'aceptado' → estadoLaboral = 'ocupado'.
 * - Si hay viaje activo en estado 'en_curso' → estadoLaboral = 'ocupado'.
 * - Si no hay viaje activo, o está finalizado/cancelado → estadoLaboral = 'libre'.
 * - Si el chofer está fuera de servicio, no se toca.
 *
 * Se monta una sola vez en el layout de (app).
 * No acopla los stores entre sí: la sincronización vive acá.
 */
import { useEffect } from 'react';
import { useViajeStore } from '@/stores/viaje.store';
import { useTurnoStore } from '@/stores/turno.store';
import type { EstadoViaje } from '@/types/viaje.types';

const ESTADOS_VIAJE_ACTIVO: EstadoViaje[] = ['aceptado', 'en_curso'];
const turnoActivo = useTurnoStore((s) => s.turnoActivo);
const cargarTurnoActivo = useTurnoStore((s) => s.cargarTurnoActivo);

export function useSincronizacionEstadoLaboral(): void {
  const estadoViaje = useViajeStore((s) => s.viajeActivo?.estado);
  const estadoLaboralActual = useTurnoStore((s) => s.estadoLaboral);
  const setEstadoLaboral = useTurnoStore((s) => s.setEstadoLaboral);

  useEffect(() => {
    // No pisar 'fuera_servicio': el chofer puede estar logueado pero no operando.
    if (estadoLaboralActual === 'fuera_servicio') return;

    const debeEstarOcupado =
      estadoViaje != null && ESTADOS_VIAJE_ACTIVO.includes(estadoViaje);

    const esperado = debeEstarOcupado ? 'ocupado' : 'libre';

    if (estadoLaboralActual !== esperado) {
      setEstadoLaboral(esperado);
    }
  }, [estadoViaje, estadoLaboralActual, setEstadoLaboral]);
}