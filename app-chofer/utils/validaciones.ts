/**
 * Utilidades de validación para M3.
 *
 * Funciones puras, sin dependencias.
 */

/**
 * Valida un email con regex simple.
 * No hace verificación MX/SMTP: eso lo hace el backend.
 */
export function esEmailValido(email: string): boolean {
  if (!email) return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email.trim());
}

/**
 * Valida una patente argentina.
 * Acepta formato viejo (AAA123) y nuevo (AB123CD).
 * Case-insensitive. Ignora espacios y guiones.
 */
export function esPatenteValida(patente: string): boolean {
  if (!patente) return false;
  const limpia = patente.replace(/[\s-]/g, '').toUpperCase();
  // Viejo: 3 letras + 3 dígitos (AAA123)
  const reViejo = /^[A-Z]{3}\d{3}$/;
  // Nuevo: 2 letras + 3 dígitos + 2 letras (AB123CD)
  const reNuevo = /^[A-Z]{2}\d{3}[A-Z]{2}$/;
  return reViejo.test(limpia) || reNuevo.test(limpia);
}

/**
 * Valida que una coordenada esté dentro de rangos válidos WGS84.
 */
export function esCoordenadaValida(
  lat: number | null | undefined,
  lng: number | null | undefined
): boolean {
  if (lat == null || lng == null) return false;
  if (!isFinite(lat) || !isFinite(lng)) return false;
  return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}