'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Building2, 
  Plus, 
  Eye, 
  Edit, 
  Ban, 
  CheckCircle,
  Search,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';

interface Tenant {
  id: string;
  nombre: string;
  email: string;
  telefono: string;
  activo: boolean;
  created_at: string;
  total_vehiculos: number;
  total_propietarios: number;
  total_empresas: number;
  deuda: number;
}

export default function TenantsPage() {
  const router = useRouter();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchTenants = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/super-admin/tenants');
      if (!res.ok) throw new Error('Error al obtener tenants');
      const data = await res.json();
      setTenants(data);
    } catch (error) {
      console.error('Error fetching tenants:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenants();
  }, []);

  const filteredTenants = tenants.filter(tenant =>
    tenant.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tenant.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tenants</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Gestión de todas las empresas de taxis registradas en la plataforma
          </p>
        </div>
        <Link
          href="/super-admin/tenants/nuevo"
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nuevo Tenant
        </Link>
      </div>

      {/* Filtros */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nombre o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <button
          onClick={fetchTenants}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {/* Tabla de Tenants */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Tenant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Contacto
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Vehículos
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Propietarios
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Empresas
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Deuda
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredTenants.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No hay tenants registrados
                  </td>
                </tr>
              ) : (
                filteredTenants.map((tenant) => (
                  <tr key={tenant.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/30">
                          <Building2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {tenant.nombre}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Creado: {new Date(tenant.created_at).toLocaleDateString('es-AR')}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600 dark:text-gray-300">{tenant.email}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">{tenant.telefono || 'Sin teléfono'}</p>
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                      {tenant.total_vehiculos}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                      {tenant.total_propietarios}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                      {tenant.total_empresas}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`text-sm font-medium ${
                        tenant.deuda > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'
                      }`}>
                        {formatCurrency(tenant.deuda)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${tenant.activo 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        }
                      `}>
                        {tenant.activo ? 'Activo' : 'Suspendido'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/super-admin/tenants/${tenant.id}`}
                          className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          title="Ver detalle"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        <Link
                          href={`/super-admin/tenants/${tenant.id}/editar`}
                          className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <button
                          className={`p-1.5 rounded-lg transition-colors ${
                            tenant.activo 
                              ? 'text-gray-500 hover:text-red-600 hover:bg-red-50' 
                              : 'text-gray-500 hover:text-green-600 hover:bg-green-50'
                          }`}
                          title={tenant.activo ? 'Suspender' : 'Activar'}
                          onClick={() => {
                            if (confirm(`¿Estás seguro de ${tenant.activo ? 'suspender' : 'activar'} el tenant "${tenant.nombre}"?`)) {
                              // Aquí llamar a la API para suspender/activar
                            }
                          }}
                        >
                          {tenant.activo ? (
                            <Ban className="w-4 h-4" />
                          ) : (
                            <CheckCircle className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Tenants</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{tenants.length}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Activos</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {tenants.filter(t => t.activo).length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Suspendidos</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {tenants.filter(t => !t.activo).length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Deuda Total</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {formatCurrency(tenants.reduce((sum, t) => sum + t.deuda, 0))}
          </p>
        </div>
      </div>
    </div>
  );
}