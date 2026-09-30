/**
 * Utilidades de formato para M3.
 *
 * Funciones puras, sin dependencias del store ni del backend.
 * Formato de números y fechas en convención argentina.
 */

/**
 * Formatea un número como moneda argentina.
 * Ej: 1234.56 → "$ 1.234,56"
 */
export function formatearMoneda(valor: number, moneda: string = 'ARS'): string {
  if (!isFinite(valor)) return '$ 0,00';
  const formateado = new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(valor);
  return `$ ${formateado}`;
}

/**
 * Formatea una distancia en metros.
 * - Menos de 1 km: entero en metros. Ej: 850 → "850 m"
 * - 1 km o más: kilómetros con 1 decimal. Ej: 1250 → "1,3 km"
 */
export function formatearDistancia(metros: number | null | undefined): string {
  if (metros == null || !isFinite(metros)) return '—';
  if (metros < 1000) {
    return `${Math.round(metros)} m`;
  }
  const km = metros / 1000;
  const formateado = new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(km);
  return `${formateado} km`;
}

/**
 * Formatea una duración en segundos.
 * - Menos de 60s: "45s"
 * - Menos de 1h: "15m"
 * - 1h o más: "1h 15m"
 */
export function formatearDuracion(
  segundos: number | null | undefined
): string {
  if (segundos == null || !isFinite(segundos) || segundos < 0) return '—';
  if (segundos < 60) {
    return `${Math.round(segundos)}s`;
  }
  const minutos = Math.floor(segundos / 60);
  if (minutos < 60) {
    return `${minutos}m`;
  }
  const horas = Math.floor(minutos / 60);
  const minutosRestantes = minutos % 60;
  return minutosRestantes > 0 ? `${horas}h ${minutosRestantes}m` : `${horas}h`;
}

/**
 * Formatea un timestamp ISO a hora local HH:MM.
 * Ej: "2026-09-17T14:35:00.000Z" → "14:35" (según zona local del device)
 */
export function formatearHora(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    const fecha = new Date(iso);
    if (isNaN(fecha.getTime())) return '—';
    return new Intl.DateTimeFormat('es-AR', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(fecha);
  } catch {
    return '—';
  }
}