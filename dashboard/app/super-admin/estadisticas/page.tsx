'use client';

import { useEffect, useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  Building2,
  Car,
  Receipt,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Calendar,
  RefreshCw,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

interface EstadisticasData {
  evolucion: Array<{
    mes: string;
    pagado: number;
    pendiente: number;
    vencido: number;
  }>;
  ranking: Array<{
    tenant: string;
    total_pagado: number;
    total_pendiente: number;
    total: number;
    total_facturas: number;
  }>;
  vehiculos: Array<{
    tenant: string;
    total_vehiculos: number;
    vehiculos_activos: number;
    vehiculos_inactivos: number;
  }>;
  estadoFacturas: Array<{
    estado: string;
    cantidad: number;
    total: number;
  }>;
  topDeuda: Array<{
    tenant: string;
    deuda: number;
    deuda_vencida: number;
  }>;
  resumen: {
    total_pagado: number;
    total_pendiente: number;
    total_vencido: number;
    facturas_pagadas: number;
    facturas_pendientes: number;
    facturas_vencidas: number;
  };
}

export default function EstadisticasPage() {
  const [data, setData] = useState<EstadisticasData | null>(null);
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/super-admin/estadisticas?periodo=${periodo}`);
      if (!res.ok) throw new Error('Error al obtener estadísticas');
      const result = await res.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching estadisticas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [periodo]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number, total: number) => {
    if (total === 0) return '0%';
    return `${((value / total) * 100).toFixed(1)}%`;
  };

  // Calcular el máximo para los gráficos de barras
  const maxEvolucion = data?.evolucion?.reduce((max, item) => {
    const total = item.pagado + item.pendiente + item.vencido;
    return Math.max(max, total);
  }, 0) || 1;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No se pudieron cargar las estadísticas</p>
        <button
          onClick={fetchData}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const totalFacturas = data.resumen.facturas_pagadas + data.resumen.facturas_pendientes + data.resumen.facturas_vencidas;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-indigo-600" />
            Estadísticas Globales
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Análisis detallado de viajes, ingresos y rendimiento de la plataforma
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Resumen General */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
            <CheckCircle className="w-4 h-4" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Pagado</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">{formatCurrency(data.resumen.total_pagado)}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.resumen.facturas_pagadas} facturas</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Pendiente</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">{formatCurrency(data.resumen.total_pendiente)}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.resumen.facturas_pendientes} facturas</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
            <XCircle className="w-4 h-4" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Vencido</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">{formatCurrency(data.resumen.total_vencido)}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.resumen.facturas_vencidas} facturas</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
            <Receipt className="w-4 h-4" />
            <span className="text-xs text-gray-500 dark:text-gray-400">Total Facturas</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">{totalFacturas}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">en el período</p>
        </div>
      </div>

      {/* Evolución Mensual */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-indigo-600" />
          Evolución Mensual
        </h2>
        <div className="space-y-3">
          {data.evolucion.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No hay datos para mostrar</p>
          ) : (
            data.evolucion.map((item) => {
              const total = item.pagado + item.pendiente + item.vencido;
              const porcentaje = maxEvolucion > 0 ? (total / maxEvolucion) * 100 : 0;

              return (
                <div key={item.mes}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 dark:text-gray-300">
                      {new Date(item.mes + '-01').toLocaleDateString('es-AR', { month: 'long', year: 'numeric' })}
                    </span>
                    <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(total)}</span>
                  </div>
                  <div className="flex h-4 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                    {item.pagado > 0 && (
                      <div
                        className="bg-green-500 h-full"
                        style={{ width: `${(item.pagado / total) * 100}%` }}
                        title={`Pagado: ${formatCurrency(item.pagado)}`}
                      />
                    )}
                    {item.pendiente > 0 && (
                      <div
                        className="bg-yellow-500 h-full"
                        style={{ width: `${(item.pendiente / total) * 100}%` }}
                        title={`Pendiente: ${formatCurrency(item.pendiente)}`}
                      />
                    )}
                    {item.vencido > 0 && (
                      <div
                        className="bg-red-500 h-full"
                        style={{ width: `${(item.vencido / total) * 100}%` }}
                        title={`Vencido: ${formatCurrency(item.vencido)}`}
                      />
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>Pagado: {formatCurrency(item.pagado)}</span>
                    <span>Pendiente: {formatCurrency(item.pendiente)}</span>
                    <span>Vencido: {formatCurrency(item.vencido)}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Ranking y Vehículos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ranking de Tenants */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-600" />
            Ranking de Tenants
          </h2>
          <div className="space-y-3">
            {data.ranking.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No hay datos para mostrar</p>
            ) : (
              data.ranking.map((item, index) => {
                const maxTotal = data.ranking[0]?.total || 1;
                const porcentaje = (item.total / maxTotal) * 100;

                return (
                  <div key={item.tenant}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`
                          inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold
                          ${index === 0 ? 'bg-yellow-100 text-yellow-800' : ''}
                          ${index === 1 ? 'bg-gray-100 text-gray-600' : ''}
                          ${index === 2 ? 'bg-orange-100 text-orange-800' : ''}
                          ${index > 2 ? 'bg-gray-50 text-gray-400' : ''}
                        `}>
                          {index + 1}
                        </span>
                        <span className="text-gray-600 dark:text-gray-300">{item.tenant}</span>
                      </div>
                      <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(item.total)}</span>
                    </div>
                    <div className="flex h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                      <div
                        className={`h-full ${index === 0 ? 'bg-yellow-500' : 'bg-indigo-500'}`}
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>{item.total_facturas} facturas</span>
                      <span>Pagado: {formatCurrency(item.total_pagado)}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Distribución de Vehículos */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Car className="w-5 h-5 text-indigo-600" />
            Vehículos por Tenant
          </h2>
          <div className="space-y-3">
            {data.vehiculos.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No hay vehículos registrados</p>
            ) : (
              data.vehiculos.map((item) => {
                const total = item.total_vehiculos;
                const maxTotal = data.vehiculos[0]?.total_vehiculos || 1;
                const porcentaje = (total / maxTotal) * 100;

                return (
                  <div key={item.tenant}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600 dark:text-gray-300">{item.tenant}</span>
                      <span className="font-medium text-gray-900 dark:text-white">{total} vehículos</span>
                    </div>
                    <div className="flex h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                      <div
                        className="bg-indigo-500 h-full"
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>Activos: {item.vehiculos_activos}</span>
                      <span>Inactivos: {item.vehiculos_inactivos}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Top Deuda y Estado Facturas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Deuda */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-red-600" />
            Tenants con Mayor Deuda
          </h2>
          <div className="space-y-3">
            {data.topDeuda.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No hay deudas registradas</p>
            ) : (
              data.topDeuda.map((item, index) => {
                const maxDeuda = data.topDeuda[0]?.deuda || 1;
                const porcentaje = (item.deuda / maxDeuda) * 100;

                return (
                  <div key={item.tenant}>
                    <div className="flex justify-between text-sm mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`
                          inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold
                          ${index === 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}
                        `}>
                          {index + 1}
                        </span>
                        <span className="text-gray-600 dark:text-gray-300">{item.tenant}</span>
                      </div>
                      <span className="font-medium text-red-600 dark:text-red-400">{formatCurrency(item.deuda)}</span>
                    </div>
                    <div className="flex h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                      <div
                        className="bg-red-500 h-full"
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>Total deuda: {formatCurrency(item.deuda)}</span>
                      <span>Vencida: {formatCurrency(item.deuda_vencida)}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Estado de Facturas */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Receipt className="w-5 h-5 text-indigo-600" />
            Distribución de Estados
          </h2>
          <div className="space-y-3">
            {data.estadoFacturas.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No hay facturas en el período</p>
            ) : (
              data.estadoFacturas.map((item) => {
                const total = data.estadoFacturas.reduce((sum, i) => sum + i.cantidad, 0);
                const porcentaje = total > 0 ? (item.cantidad / total) * 100 : 0;

                const colors = {
                  pagado: 'bg-green-500',
                  pendiente: 'bg-yellow-500',
                  vencido: 'bg-red-500',
                  anulado: 'bg-gray-500',
                };

                const labels = {
                  pagado: 'Pagado',
                  pendiente: 'Pendiente',
                  vencido: 'Vencido',
                  anulado: 'Anulado',
                };

                const color = colors[item.estado as keyof typeof colors] || 'bg-gray-500';
                const label = labels[item.estado as keyof typeof labels] || item.estado;

                return (
                  <div key={item.estado}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600 dark:text-gray-300">{label}</span>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white">{item.cantidad}</span>
                        <span className="text-xs text-gray-400">{formatPercentage(item.cantidad, total)}</span>
                      </div>
                    </div>
                    <div className="flex h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                      <div
                        className={color}
                        style={{ width: `${porcentaje}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
          {data.estadoFacturas.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">Total facturas: {data.estadoFacturas.reduce((sum, i) => sum + i.cantidad, 0)}</span>
              <span className="text-gray-500 dark:text-gray-400">Total: {formatCurrency(data.estadoFacturas.reduce((sum, i) => sum + i.total, 0))}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}