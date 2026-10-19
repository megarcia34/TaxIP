// D:\ataxip\dashboard\lib\api\index.ts

// Cliente HTTP
export { apiClient, default } from './client';

// APIs por módulo
export * from './propietario';
export * from './neumaticos';
export * from './tarifaService';
export * from './perfil';
export * from './cuentasCobro';
export * from './postulacionChofer';
export * from './contratosAcciones';
export * from './metricasPropietario';

// ============================================================
// EXPORTACIONES PARA MANTENER COMPATIBILIDAD CON lib/api.ts
// ============================================================

export {
  propietarioReportesAPI,
  propietarioVehiculosAPI,
  propietarioAlertasAPI,
  propietarioFinanzasAPI,
} from './propietario';

export { neumaticosAPI } from './neumaticos';
export { tarifaService } from './tarifaService';

// ============================================================
// TIPOS
// ============================================================

export * from './propietario';
export * from './neumaticos';
export * from './perfil';
export * from './cuentasCobro';
export * from './postulacionChofer';
export * from './contratosAcciones';
export * from './metricasPropietario';