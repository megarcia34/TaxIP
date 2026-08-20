// lib/formatters.ts

/**
 * Formatea un número como moneda ARS
 * Ejemplo: 903849.50 → $ 903.849,50
 */
export function formatCurrency(value: number): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '$ 0,00'
  }
  
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Formatea un número como porcentaje
 * Ejemplo: 34.78 → 34,78%
 */
export function formatPercentage(value: number): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '0,00%'
  }
  
  return new Intl.NumberFormat('es-AR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100)
}

/**
 * Formatea un número con separador de miles
 * Ejemplo: 903849 → 903.849
 */
export function formatNumber(value: number): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '0'
  }
  
  return new Intl.NumberFormat('es-AR').format(value)
}

/**
 * Formatea una fecha
 * Ejemplo: 2026-07-26 → 26/07/2026
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('es-AR')
  } catch {
    return dateStr
  }
}