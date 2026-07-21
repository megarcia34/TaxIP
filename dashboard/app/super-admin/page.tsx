'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { 
  Building2, 
  Car, 
  DollarSign, 
  CheckCircle,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import Link from 'next/link';

// ============================================
// TIPOS DE DATOS
// ============================================

interface DashboardData {
  totalTenants: number;
  totalVehiculos: number;
  deudaTotal: number;
  ingresosMes: number;
  facturasRecientes: Factura[];
  ingresosPorTenant: IngresoPorTenant[];
  alertas: Alerta[];
}

interface Factura {
  id: string;
  numero_factura: string;
  tenant: string;
  total: number;
  estado: 'pagado' | 'pendiente' | 'vencido';
  fecha_emision: string;
}

interface IngresoPorTenant {
  tenant: string;
  pagado: number;
  pendiente: number;
}

interface Alerta {
  tipo: 'critica' | 'advertencia' | 'informativa';
  mensaje: string;
  link?: string;
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export default function SuperAdminDashboard() {
  const { data: session } = useSession();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodo, setPeriodo] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  // Log de sesión
  console.log('========================================');
  console.log('🔍 [Dashboard Frontend] INICIO');
  console.log('========================================');
  console.log('🔍 [Dashboard Frontend] Session:', session);
  console.log('🔍 [Dashboard Frontend] user:', session?.user);
  console.log('🔍 [Dashboard Frontend] tipo_usuario:', session?.user?.tipo_usuario);
  console.log('🔍 [Dashboard Frontend] role:', session?.user?.role);
  console.log('🔍 [Dashboard Frontend] email:', session?.user?.email);

  useEffect(() => {
    console.log('🔍 [Dashboard Frontend] useEffect - periodo cambiado a:', periodo);
    fetchDashboardData();
  }, [periodo]);

  const fetchDashboardData = async () => {
    console.log('🔍 [Dashboard Frontend] fetchDashboardData - INICIO');
    setLoading(true);
    setError(null);
    
    try {
      const url = `/api/super-admin/dashboard?periodo=${periodo}`;
      console.log(`🔍 [Dashboard Frontend] Fetching: ${url}`);
      
      const res = await fetch(url);
      console.log(`🔍 [Dashboard Frontend] Response status: ${res.status}`);
      console.log(`🔍 [Dashboard Frontend] Response ok: ${res.ok}`);
      
      if (!res.ok) {
        let errorText = '';
        try {
          const errorJson = await res.json();
          errorText = JSON.stringify(errorJson, null, 2);
          console.error('❌ [Dashboard Frontend] Error response:', errorJson);
        } catch {
          errorText = await res.text();
          console.error('❌ [Dashboard Frontend] Error response (text):', errorText);
        }
        throw new Error(`Error ${res.status}: ${errorText}`);
      }
      
      const result = await res.json();
      console.log('✅ [Dashboard Frontend] Datos recibidos:', result);
      setData(result);
      
    } catch (error) {
      console.error('❌ [Dashboard Frontend] Error fetching dashboard:', error);
      setError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setLoading(false);
      console.log('🔍 [Dashboard Frontend] fetchDashboardData - FIN');
    }
  };

  // ============================================
  // RENDERIZADO
  // ============================================

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="ml-4 text-gray-500">Cargando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 font-medium">Error al cargar los datos</p>
        <p className="text-sm text-gray-500 mt-2">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No se pudieron cargar los datos</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Resumen financiero de todos los Tenants
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          />
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Actualizar
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          icon={Building2}
          label="Tenants Activos"
          value={data.totalTenants}
          color="blue"
        />
        <KpiCard
          icon={Car}
          label="Vehículos Activos"
          value={data.totalVehiculos}
          color="green"
        />
        <KpiCard
          icon={DollarSign}
          label="Deuda Total"
          value={formatCurrency(data.deudaTotal)}
          color="red"
        />
        <KpiCard
          icon={CheckCircle}
          label="Ingresos del Mes"
          value={formatCurrency(data.ingresosMes)}
          color="green"
        />
      </div>

      {/* Alertas */}
      {data.alertas.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Alertas</h3>
          {data.alertas.map((alerta, index) => (
            <div
              key={index}
              className={`
                flex items-center justify-between p-4 rounded-lg border
                ${alerta.tipo === 'critica' ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800' : ''}
                ${alerta.tipo === 'advertencia' ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800' : ''}
                ${alerta.tipo === 'informativa' ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800' : ''}
              `}
            >
              <div className="flex items-center gap-3">
                <AlertCircle className={`
                  w-5 h-5
                  ${alerta.tipo === 'critica' ? 'text-red-600' : ''}
                  ${alerta.tipo === 'advertencia' ? 'text-yellow-600' : ''}
                  ${alerta.tipo === 'informativa' ? 'text-blue-600' : ''}
                `} />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {alerta.mensaje}
                </span>
              </div>
              {alerta.link && (
                <Link
                  href={alerta.link}
                  className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium flex items-center gap-1"
                >
                  Ver <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ingresos por Tenant */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
            Ingresos por Tenant
          </h3>
          <div className="space-y-3">
            {data.ingresosPorTenant.map((item, index) => {
              const total = item.pagado + item.pendiente;
              return (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 dark:text-gray-300">{item.tenant}</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(total)}
                    </span>
                  </div>
                  <div className="flex h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                    {item.pagado > 0 && (
                      <div
                        className="bg-green-500 h-full"
                        style={{ width: `${(item.pagado / total) * 100}%` }}
                      />
                    )}
                    {item.pendiente > 0 && (
                      <div
                        className="bg-yellow-500 h-full"
                        style={{ width: `${(item.pendiente / total) * 100}%` }}
                      />
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>Pagado: {formatCurrency(item.pagado)}</span>
                    <span>Pendiente: {formatCurrency(item.pendiente)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Estado de Facturas */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
            Estado de Facturas
          </h3>
          <div className="flex items-center justify-center h-48">
            <div className="relative w-40 h-40">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="60"
                  stroke="#e5e7eb"
                  strokeWidth="20"
                  fill="none"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="60"
                  stroke="#22c55e"
                  strokeWidth="20"
                  fill="none"
                  strokeDasharray="377"
                  strokeDashoffset="0"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="60"
                  stroke="#eab308"
                  strokeWidth="20"
                  fill="none"
                  strokeDasharray="377"
                  strokeDashoffset="-79"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {data.facturasRecientes.length} facturas
                </span>
              </div>
            </div>
          </div>
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Pagado</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Pendiente</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Vencido</span>
            </div>
          </div>
        </div>
      </div>

      {/* Últimas Facturas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Últimas Facturas Emitidas
          </h3>
          <Link
            href="/super-admin/facturacion"
            className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 flex items-center gap-1"
          >
            Ver todas <ArrowRight className="w-4 h-4" />
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
                  Tenant
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.facturasRecientes.map((factura) => (
                <tr key={factura.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                    {factura.numero_factura}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                    {factura.tenant}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white text-right">
                    {formatCurrency(factura.total)}
                  </td>
                  <td className="px-6 py-4">
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
                    {formatDate(factura.fecha_emision)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/super-admin/facturacion/${factura.id}`}
                      className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
                    >
                      Ver
                    </Link>
                  </td>
                </tr>
              ))}
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

interface KpiCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: 'blue' | 'green' | 'red' | 'purple';
}

function KpiCard({ icon: Icon, label, value, color }: KpiCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });
}