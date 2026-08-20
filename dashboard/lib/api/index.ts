// D:\ataxip\dashboard\lib\api\index.ts

// Cliente HTTP
export { apiClient, default } from './client';

// APIs por módulo
export * from './propietario';
export * from './neumaticos';
export * from './tarifaService';

// ============================================================
// EXPORTACIONES PARA MANTENER COMPATIBILIDAD CON lib/api.ts
// ============================================================

// Re-exportar desde propietario.ts
export {
  propietarioReportesAPI,
  propietarioVehiculosAPI,
  propietarioAlertasAPI,
  propietarioFinanzasAPI,
} from './propietario';

// Re-exportar desde neumaticos.ts
export { neumaticosAPI } from './neumaticos';

// Re-exportar desde tarifaService.ts
export { tarifaService } from './tarifaService';

// ============================================================
// TIPOS
// ============================================================

export * from './propietario';
export * from './neumaticos';