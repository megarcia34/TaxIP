import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ============================================
// FORMATO DE ERRORES DE API
// ============================================

/**
 * Formatea errores de la API para mostrarlos en el frontend
 * Maneja errores de Pydantic (422), errores de string y errores genéricos
 */
export function formatApiError(error: any): string {
  // Si no hay error, mensaje genérico
  if (!error) return 'Error desconocido'
  
  // Si ya es un string, devolverlo directamente
  if (typeof error === 'string') return error
  
  // Si tiene response.data.detail (estructura de FastAPI)
  const detail = error?.response?.data?.detail
  
  if (!detail) {
    // Intentar obtener mensaje del error
    return error?.message || 'Error desconocido'
  }
  
  // Si detail es un array de errores de validación de Pydantic
  if (Array.isArray(detail)) {
    // Extraer los mensajes de cada error
    const mensajes = detail
      .map((err: any) => err.msg || err.message || JSON.stringify(err))
      .filter(Boolean) // Filtrar vacíos
    return mensajes.length > 0 ? mensajes.join('. ') : 'Error de validación'
  }
  
  // Si detail es un string
  if (typeof detail === 'string') {
    return detail
  }
  
  // Si detail es un objeto con mensaje
  if (typeof detail === 'object' && detail.message) {
    return detail.message
  }
  
  // Si detail es un objeto pero no tiene mensaje, convertirlo a string
  if (typeof detail === 'object') {
    try {
      return JSON.stringify(detail)
    } catch {
      return 'Error desconocido'
    }
  }
  
  return 'Error desconocido'
}

/**
 * Versión más simple para casos donde solo se quiere extraer el mensaje principal
 */
export function getApiErrorMessage(error: any): string {
  if (!error) return 'Error desconocido'
  if (typeof error === 'string') return error
  
  const detail = error?.response?.data?.detail
  if (!detail) return error?.message || 'Error desconocido'
  
  if (Array.isArray(detail)) {
    // Tomar solo el primer mensaje de error
    const firstError = detail[0]
    return firstError?.msg || firstError?.message || 'Error de validación'
  }
  
  if (typeof detail === 'string') return detail
  if (typeof detail === 'object' && detail.message) return detail.message
  
  return 'Error desconocido'
}