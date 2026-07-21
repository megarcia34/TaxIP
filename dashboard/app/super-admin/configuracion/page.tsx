'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Settings, 
  Save, 
  Loader2, 
  AlertTriangle, 
  CheckCircle,
  DollarSign,
  Calendar,
  Clock,
  Globe,
  CreditCard,
  Percent,
  Building2,
  RefreshCw,
  Users,
  Plus,
  Trash2
} from 'lucide-react';

interface Configuracion {
  canon_por_vehiculo: number;
  porcentaje_plataforma: number;
  dia_facturacion: number;
  dias_vencimiento: number;
  moneda_default: string;
  timezone: string;
  idioma: string;
  habilitar_fidelizacion: boolean;
  habilitar_pagos_online: boolean;
}

interface SuperAdmin {
  id: string;
  email: string;
  activo: boolean;
  created_at: string;
  nombre: string;
  apellido: string;
}

export default function ConfiguracionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  // Configuración
  const [config, setConfig] = useState<Configuracion>({
    canon_por_vehiculo: 10000,
    porcentaje_plataforma: 15,
    dia_facturacion: 1,
    dias_vencimiento: 10,
    moneda_default: 'ARS',
    timezone: 'America/Argentina/Tucuman',
    idioma: 'es',
    habilitar_fidelizacion: false,
    habilitar_pagos_online: true,
  });

  // Super Admins
  const [superAdmins, setSuperAdmins] = useState<SuperAdmin[]>([]);
  const [isMaster, setIsMaster] = useState(false);
  const [nuevoSuperAdminEmail, setNuevoSuperAdminEmail] = useState('');

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/super-admin/configuracion');
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Error al cargar configuración');
      }
      const data = await res.json();
      setConfig(prev => ({
        ...prev,
        ...data.config,
      }));
      setSuperAdmins(data.superAdmins || []);
      setIsMaster(data.isMaster || false);
    } catch (err) {
      console.error('Error fetching config:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const res = await fetch('/api/super-admin/configuracion', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Error al guardar configuración');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      console.error('Error saving config:', err);
      setError(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: checked,
    }));
  };

  // ============================================
  // FUNCIONES PARA SUPER ADMINS
  // ============================================

  const handleCrearSuperAdmin = async () => {
    if (!nuevoSuperAdminEmail) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch('/api/super-admin/configuracion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: nuevoSuperAdminEmail,
          action: 'crear_super_admin',
        }),
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.error || 'Error al crear Super Admin');
      }
      const data = await res.json();
      alert(`✅ Super Admin creado con éxito.\n\n📧 Email: ${nuevoSuperAdminEmail}\n🔑 Contraseña temporal: ${data.tempPassword}`);
      setNuevoSuperAdminEmail('');
      fetchConfig();
    } catch (err) {
      console.error('Error creating super admin:', err);
      setError(err instanceof Error ? err.message : 'Error al crear');
    } finally {
      setSaving(false);
    }
  };

  const handleEliminarSuperAdmin = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este Super Admin?')) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`/api/super-admin/configuracion?id=${id}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.error || 'Error al eliminar Super Admin');
      }
      alert('✅ Super Admin eliminado con éxito');
      fetchConfig();
    } catch (err) {
      console.error('Error deleting super admin:', err);
      setError(err instanceof Error ? err.message : 'Error al eliminar');
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Settings className="w-6 h-6 text-indigo-600" />
            Configuración Global
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Parámetros que afectan a todos los Tenants de la plataforma
          </p>
        </div>
        <button
          onClick={fetchConfig}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Mensajes */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
          <span className="text-red-700 dark:text-red-300">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
          <span className="text-green-700 dark:text-green-300">
            Configuración guardada exitosamente
          </span>
        </div>
      )}

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Parámetros de Facturación */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-indigo-600" />
            Parámetros de Facturación
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Canon por Vehículo ($)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                <input
                  type="number"
                  name="canon_por_vehiculo"
                  value={config.canon_por_vehiculo}
                  onChange={handleChange}
                  min="0"
                  step="100"
                  className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Monto fijo que paga el propietario al Tenant por vehículo
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                % Plataforma
              </label>
              <div className="relative">
                <input
                  type="number"
                  name="porcentaje_plataforma"
                  value={config.porcentaje_plataforma}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  step="0.5"
                  className="w-full pr-8 pl-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">%</span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Porcentaje que el Tenant paga a la Plataforma sobre el canon
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Día de Facturación
              </label>
              <input
                type="number"
                name="dia_facturacion"
                value={config.dia_facturacion}
                onChange={handleChange}
                min="1"
                max="28"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Día del mes en que se generan las facturas automáticamente
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Días de Vencimiento
              </label>
              <input
                type="number"
                name="dias_vencimiento"
                value={config.dias_vencimiento}
                onChange={handleChange}
                min="1"
                max="60"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Días para pagar después de la emisión de la factura
              </p>
            </div>
          </div>
        </div>

        {/* Configuración Regional */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-indigo-600" />
            Configuración Regional
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Moneda por Defecto
              </label>
              <select
                name="moneda_default"
                value={config.moneda_default}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="ARS">ARS - Peso Argentino</option>
                <option value="USD">USD - Dólar Americano</option>
                <option value="EUR">EUR - Euro</option>
                <option value="BRL">BRL - Real Brasileño</option>
                <option value="CLP">CLP - Peso Chileno</option>
                <option value="UYU">UYU - Peso Uruguayo</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Zona Horaria
              </label>
              <select
                name="timezone"
                value={config.timezone}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="America/Argentina/Tucuman">Argentina (Tucumán)</option>
                <option value="America/Argentina/Buenos_Aires">Argentina (Buenos Aires)</option>
                <option value="America/Sao_Paulo">Brasil (Sao Paulo)</option>
                <option value="America/Santiago">Chile (Santiago)</option>
                <option value="America/Montevideo">Uruguay (Montevideo)</option>
                <option value="America/New_York">Estados Unidos (New York)</option>
                <option value="Europe/Madrid">España (Madrid)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Idioma
              </label>
              <select
                name="idioma"
                value={config.idioma}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="es">Español</option>
                <option value="en">English</option>
                <option value="pt">Português</option>
                <option value="it">Italiano</option>
                <option value="fr">Français</option>
              </select>
            </div>
          </div>
        </div>

        {/* Funcionalidades */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-indigo-600" />
            Funcionalidades
          </h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="habilitar_pagos_online"
                name="habilitar_pagos_online"
                checked={config.habilitar_pagos_online}
                onChange={handleCheckboxChange}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <div>
                <label htmlFor="habilitar_pagos_online" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Habilitar Pagos Online
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Permite a los Tenants pagar facturas a través de la plataforma
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="habilitar_fidelizacion"
                name="habilitar_fidelizacion"
                checked={config.habilitar_fidelizacion}
                onChange={handleCheckboxChange}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <div>
                <label htmlFor="habilitar_fidelizacion" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Habilitar Programa de Fidelización
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Sistema de puntos y recompensas para pasajeros
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 🔴 GESTIÓN DE SUPER ADMINS (SOLO MAESTRO) */}
        {isMaster && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-indigo-600" />
              Gestión de Super Admins
              <span className="ml-2 text-xs bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400 px-2 py-0.5 rounded-full">
                Solo Maestro
              </span>
            </h2>
            
            {/* Listado de Super Admins */}
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Super Admins existentes
              </h3>
              <div className="space-y-2">
                {superAdmins.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No hay Super Admins registrados</p>
                ) : (
                  superAdmins.map((admin) => (
                    <div key={admin.id} className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {admin.email}
                          {admin.email === 'super@taxip.com' && (
                            <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 px-2 py-0.5 rounded-full">
                              Maestro
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Creado: {new Date(admin.created_at).toLocaleDateString('es-AR')}
                        </p>
                      </div>
                      {admin.email !== 'super@taxip.com' && (
                        <button
                          onClick={() => handleEliminarSuperAdmin(admin.id)}
                          className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Formulario para crear Super Admin */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Email del nuevo Super Admin *
                </label>
                <input
                  type="email"
                  value={nuevoSuperAdminEmail}
                  onChange={(e) => setNuevoSuperAdminEmail(e.target.value)}
                  placeholder="admin@taxip.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  El nuevo Super Admin recibirá una contraseña temporal: <strong>super123</strong>
                </p>
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleCrearSuperAdmin}
                  disabled={!nuevoSuperAdminEmail || saving}
                  className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  <Plus className="w-4 h-4 inline mr-2" />
                  Crear Super Admin
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Resumen y Botón Guardar */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Resumen de Configuración</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Canon: {formatCurrency(config.canon_por_vehiculo)} • 
                % Plataforma: {config.porcentaje_plataforma}% • 
                Facturación: Día {config.dia_facturacion} • 
                Vencimiento: {config.dias_vencimiento} días
              </p>
            </div>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Guardar Configuración
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}