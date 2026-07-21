'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Receipt, 
  Search, 
  RefreshCw, 
  Eye, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Download,
  Filter,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Building2
} from 'lucide-react';

interface Factura {
  id: string;
  numero_factura: string;
  periodo: string;
  vehiculos_activos: number;
  canon_total: number;
  porcentaje_plataforma: number;
  total_a_pagar: number;
  estado: 'pendiente' | 'pagado' | 'vencido' | 'anulado';
  fecha_emision: string;
  fecha_vencimiento: string;
  pagada_at: string | null;
  tenant_nombre: string;
  tenant_id: string;
}

interface Tenant {
  id: string;
  nombre: string;
}

export default function FacturacionPage() {
  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [limit] = useState(20);
  const [offset, setOffset] = useState(0);
  
  // Filtros
  const [filtroTenant, setFiltroTenant] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroPeriodo, setFiltroPeriodo] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchFacturas = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filtroTenant) params.append('tenant', filtroTenant);
      if (filtroEstado) params.append('estado', filtroEstado);
      if (filtroPeriodo) params.append('periodo', filtroPeriodo);
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const res = await fetch(`/api/super-admin/facturacion?${params.toString()}`);
      if (!res.ok) throw new Error('Error al obtener facturas');
      const data = await res.json();
      setFacturas(data.facturas);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching facturas:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTenants = async () => {
    try {
      const res = await fetch('/api/super-admin/tenants');
      if (!res.ok) throw new Error('Error al obtener tenants');
      const data = await res.json();
      setTenants(data);
    } catch (error) {
      console.error('Error fetching tenants:', error);
    }
  };

  useEffect(() => {
    fetchFacturas();
  }, [filtroTenant, filtroEstado, filtroPeriodo, offset]);

  useEffect(() => {
    fetchTenants();
  }, []);

  const handlePagar = async (facturaId: string) => {
    if (!confirm('¿Estás seguro de marcar esta factura como pagada?')) return;

    try {
      const res = await fetch('/api/super-admin/facturacion', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ facturaId, action: 'pagar' }),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.error || 'Error al pagar la factura');
        return;
      }

      alert('Factura marcada como pagada');
      fetchFacturas();
    } catch (error) {
      console.error('Error:', error);
      alert('Error al procesar el pago');
    }
  };

  const handleAnular = async (facturaId: string) => {
    if (!confirm('¿Estás seguro de anular esta factura?')) return;

    try {
      const res = await fetch('/api/super-admin/facturacion', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ facturaId, action: 'anular' }),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.error || 'Error al anular la factura');
        return;
      }

      alert('Factura anulada');
      fetchFacturas();
    } catch (error) {
      console.error('Error:', error);
      alert('Error al procesar la anulación');
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

  const totalPages = Math.ceil(total / limit);

  // Filtrar facturas por búsqueda (cliente-side)
  const facturasFiltradas = facturas.filter(f =>
    f.numero_factura.toLowerCase().includes(searchTerm.toLowerCase()) ||
    f.tenant_nombre.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Facturación</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Gestión de facturas de todos los Tenants
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchFacturas}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar factura o tenant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Filtro Tenant */}
          <div className="relative">
            <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={filtroTenant}
              onChange={(e) => setFiltroTenant(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500 appearance-none"
            >
              <option value="">Todos los Tenants</option>
              {tenants.map((t) => (
                <option key={t.id} value={t.id}>{t.nombre}</option>
              ))}
            </select>
          </div>

          {/* Filtro Estado */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500 appearance-none"
            >
              <option value="">Todos los estados</option>
              <option value="pendiente">Pendiente</option>
              <option value="pagado">Pagado</option>
              <option value="vencido">Vencido</option>
              <option value="anulado">Anulado</option>
            </select>
          </div>

          {/* Filtro Periodo */}
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="month"
              value={filtroPeriodo}
              onChange={(e) => setFiltroPeriodo(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Tabla de Facturas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Periodo
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Vehículos
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Canon
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  15%
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
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={10} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    <div className="flex items-center justify-center gap-3">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                      Cargando facturas...
                    </div>
                  </td>
                </tr>
              ) : facturasFiltradas.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    <Receipt className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                    No hay facturas que coincidan con los filtros
                  </td>
                </tr>
              ) : (
                facturasFiltradas.map((factura) => {
                  const estadoColors = {
                    pendiente: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                    pagado: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                    vencido: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
                    anulado: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400',
                  };

                  const estadoLabels = {
                    pendiente: 'Pendiente',
                    pagado: 'Pagado',
                    vencido: 'Vencido',
                    anulado: 'Anulado',
                  };

                  const isVencida = factura.estado === 'pendiente' && new Date(factura.fecha_vencimiento) < new Date();

                  return (
                    <tr key={factura.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                        {factura.numero_factura}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                        {factura.tenant_nombre}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                        {formatDate(factura.periodo)}
                      </td>
                      <td className="px-6 py-4 text-center text-sm text-gray-600 dark:text-gray-300">
                        {factura.vehiculos_activos}
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-gray-600 dark:text-gray-300">
                        {formatCurrency(factura.canon_total)}
                      </td>
                      <td className="px-6 py-4 text-right text-sm text-gray-600 dark:text-gray-300">
                        {formatCurrency(factura.total_a_pagar - factura.canon_total)}
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium text-gray-900 dark:text-white">
                        {formatCurrency(factura.total_a_pagar)}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`
                          inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${isVencida ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : estadoColors[factura.estado]}
                        `}>
                          {isVencida ? 'Vencida' : estadoLabels[factura.estado]}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                        {factura.fecha_vencimiento ? formatDate(factura.fecha_vencimiento) : '-'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            href={`/super-admin/facturacion/${factura.id}`}
                            className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                            title="Ver detalle"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>

                          {factura.estado === 'pendiente' && !isVencida && (
                            <button
                              onClick={() => handlePagar(factura.id)}
                              className="p-1.5 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Marcar como pagada"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}

                          {factura.estado === 'pendiente' && (
                            <button
                              onClick={() => handleAnular(factura.id)}
                              className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Anular factura"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          )}

                          <button
                            className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Descargar PDF"
                            onClick={() => {
                              alert('Función de descarga de PDF en desarrollo');
                            }}
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Paginación */}
      {total > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Mostrando {facturasFiltradas.length} de {total} facturas
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg border border-gray-300 dark:border-gray-600"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Página {Math.floor(offset / limit) + 1} de {totalPages || 1}
            </span>
            <button
              onClick={() => setOffset(Math.min(total - limit, offset + limit))}
              disabled={offset + limit >= total}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg border border-gray-300 dark:border-gray-600"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}