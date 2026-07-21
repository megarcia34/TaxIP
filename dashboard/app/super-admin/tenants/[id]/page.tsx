'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Building2, 
  Car, 
  Users, 
  Briefcase, 
  DollarSign, 
  MapPin, 
  Mail, 
  Phone,
  Calendar,
  CheckCircle,
  Ban,
  Edit,
  AlertTriangle,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

interface TenantDetail {
  tenant: {
    id: string;
    nombre: string;
    email: string;
    telefono: string;
    direccion: string;
    latitud: string;
    longitud: string;
    activo: boolean;
    created_at: string;
    fecha_suspension: string;
    motivo_suspension: string;
  };
  stats: {
    total_vehiculos: number;
    vehiculos_inactivos: number;
    total_propietarios: number;
    total_empresas: number;
    total_choferes: number;
    total_viajes: number;
  };
  vehiculos: any[];
  empresas: any[];
  propietarios: any[];
  finanzas: {
    deuda_pendiente: number;
    total_pagado: number;
    facturas_pendientes: number;
    facturas_pagadas: number;
    facturas_vencidas: number;
  };
  facturas: any[];
}

export default function TenantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<TenantDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchTenantDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/super-admin/tenants/${id}`);
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Error al obtener detalles');
      }
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error('Error fetching tenant:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchTenantDetail();
    }
  }, [id]);

  const handleAction = async (action: 'suspend' | 'activate' | 'delete') => {
    const actionLabels = {
      suspend: 'suspender',
      activate: 'activar',
      delete: 'eliminar'
    };

    if (!confirm(`¿Estás seguro de ${actionLabels[action]} este tenant?`)) {
      return;
    }

    setActionLoading(true);
    try {
      const res = await fetch(`/api/super-admin/tenants/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.error || `Error al ${actionLabels[action]}`);
        return;
      }

      if (action === 'delete') {
        router.push('/super-admin/tenants');
      } else {
        fetchTenantDetail();
        alert(`Tenant ${actionLabels[action]} con éxito`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al procesar la acción');
    } finally {
      setActionLoading(false);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error || 'No se encontró el tenant'}</p>
        <button
          onClick={fetchTenantDetail}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const { tenant, stats, vehiculos, empresas, propietarios, finanzas, facturas } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <Link
            href="/super-admin/tenants"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {tenant.nombre}
              </h1>
              <span className={`
                inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                ${tenant.activo 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                }
              `}>
                {tenant.activo ? 'Activo' : 'Suspendido'}
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Creado el {formatDate(tenant.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => handleAction(tenant.activo ? 'suspend' : 'activate')}
            disabled={actionLoading}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
              ${tenant.activo 
                ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400' 
                : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400'
              }
            `}
          >
            {tenant.activo ? (
              <Ban className="w-4 h-4" />
            ) : (
              <CheckCircle className="w-4 h-4" />
            )}
            {tenant.activo ? 'Suspender' : 'Activar'}
          </button>
          <Link
            href={`/super-admin/tenants/${id}/editar`}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Edit className="w-4 h-4" />
            Editar
          </Link>
          <button
            onClick={fetchTenantDetail}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Información General */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Información General</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">{tenant.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <Phone className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">{tenant.telefono || 'No disponible'}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {tenant.direccion || 'Sin dirección'}
              {tenant.latitud && tenant.longitud && ` (${tenant.latitud}, ${tenant.longitud})`}
            </span>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          icon={Car}
          label="Vehículos"
          value={stats.total_vehiculos}
          subtitle={`${stats.vehiculos_inactivos} inactivos`}
          color="blue"
        />
        <StatCard
          icon={Users}
          label="Propietarios"
          value={stats.total_propietarios}
          color="purple"
        />
        <StatCard
          icon={Users}
          label="Choferes"
          value={stats.total_choferes}
          color="green"
        />
        <StatCard
          icon={Briefcase}
          label="Empresas"
          value={stats.total_empresas}
          color="indigo"
        />
        <StatCard
          icon={DollarSign}
          label="Deuda"
          value={formatCurrency(finanzas.deuda_pendiente)}
          color="red"
        />
        <StatCard
          icon={Calendar}
          label="Viajes Totales"
          value={stats.total_viajes}
          color="orange"
        />
      </div>

      {/* Finanzas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Resumen Financiero</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Deuda Pendiente</p>
            <p className="text-xl font-bold text-red-600 dark:text-red-400">
              {formatCurrency(finanzas.deuda_pendiente)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Pagado</p>
            <p className="text-xl font-bold text-green-600 dark:text-green-400">
              {formatCurrency(finanzas.total_pagado)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Facturas Pendientes</p>
            <p className="text-xl font-bold text-yellow-600 dark:text-yellow-400">
              {finanzas.facturas_pendientes}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Facturas Vencidas</p>
            <p className="text-xl font-bold text-red-600 dark:text-red-400">
              {finanzas.facturas_vencidas}
            </p>
          </div>
        </div>
      </div>

      {/* Últimas Facturas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Últimas Facturas</h2>
          <Link
            href={`/super-admin/facturacion?tenant=${tenant.id}`}
            className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 flex items-center gap-1"
          >
            Ver todas <ExternalLink className="w-3 h-3" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  N° Factura
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Periodo
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Vehículos
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Vencimiento
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {facturas.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No hay facturas registradas
                  </td>
                </tr>
              ) : (
                facturas.map((factura) => (
                  <tr key={factura.numero_factura} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {factura.numero_factura}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {formatDate(factura.periodo)}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                      {factura.vehiculos_activos}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium text-gray-900 dark:text-white">
                      {formatCurrency(factura.total_a_pagar)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${factura.estado === 'pagado' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : ''}
                        ${factura.estado === 'pendiente' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' : ''}
                        ${factura.estado === 'vencido' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : ''}
                      `}>
                        {factura.estado === 'pagado' ? 'Pagado' : ''}
                        {factura.estado === 'pendiente' ? 'Pendiente' : ''}
                        {factura.estado === 'vencido' ? 'Vencido' : ''}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {factura.fecha_vencimiento ? formatDate(factura.fecha_vencimiento) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Vehículos */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Vehículos</h2>
          <span className="text-sm text-gray-500 dark:text-gray-400">{stats.total_vehiculos} vehículos</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Patente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Marca / Modelo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Propietario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Chofer
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {vehiculos.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No hay vehículos registrados
                  </td>
                </tr>
              ) : (
                vehiculos.map((vehiculo) => (
                  <tr key={vehiculo.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {vehiculo.patente}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {vehiculo.propietario_nombre || 'Sin asignar'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {vehiculo.chofer_email || 'Sin asignar'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${vehiculo.activo 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        }
                      `}>
                        {vehiculo.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empresas Corporativas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Empresas Corporativas</h2>
          <span className="text-sm text-gray-500 dark:text-gray-400">{stats.total_empresas} empresas</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Email Facturación
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Empleados
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {empresas.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No hay empresas corporativas registradas
                  </td>
                </tr>
              ) : (
                empresas.map((empresa) => (
                  <tr key={empresa.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {empresa.nombre}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {empresa.tipo || 'No especificado'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                      {empresa.email_facturacion || '-'}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                      {empresa.total_empleados}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${empresa.activo 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        }
                      `}>
                        {empresa.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ============================================
// COMPONENTES AUXILIARES
// ============================================

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  subtitle?: string;
  color: 'blue' | 'green' | 'red' | 'purple' | 'indigo' | 'orange';
}

function StatCard({ icon: Icon, label, value, subtitle, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
    indigo: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
    orange: 'bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-400 dark:text-gray-500">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
}