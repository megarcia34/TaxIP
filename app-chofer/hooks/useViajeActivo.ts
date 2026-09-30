/**
 * Hook para leer el viaje activo del store.
 *
 * Opción A (Fase 9.2): devuelve solo el estado. El consumidor maneja
 * loading/error localmente si los necesita. Si en Fase 9.3 o Etapas 11+
 * se necesitan en el store, se agregan ahí y este hook los expone.
 */
import { useViajeStore } from '@/stores/viaje.store';

export function useViajeActivo() {
  const viajeActivo = useViajeStore((s) => s.viajeActivo);
  return { viajeActivo };
}