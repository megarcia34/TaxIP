'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Building2, ArrowLeft, Loader2, MapPin, Lock, Eye, EyeOff, CheckCircle2 } from 'lucide-react';

export default function NuevoTenantPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
    const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
    ciudad_nombre: '',
    codigo_postal: '',
    admin_password: '',
    confirm_password: '',
    timezone: 'America/Argentina/Tucuman',
    moneda_default: 'ARS',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (formData.admin_password.length < 8) {
      newErrors.admin_password = 'La contraseña debe tener al menos 8 caracteres';
    } else if (!/[A-Z]/.test(formData.admin_password)) {
      newErrors.admin_password = 'Debe contener al menos una mayúscula';
    } else if (!/[0-9]/.test(formData.admin_password)) {
      newErrors.admin_password = 'Debe contener al menos un número';
    }
    
    if (formData.admin_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Las contraseñas no coinciden';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);

    try {
      const { confirm_password, ...dataToSend } = formData;
      
      const res = await fetch('/api/super-admin/tenants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || data.error || 'Error al crear el tenant');
        return;
      }

      alert(`✅ Tenant "${data.tenant_nombre}" creado exitosamente.\n\nEl administrador puede iniciar sesión con:\nEmail: ${data.admin_email}\nContraseña: (la definida en el formulario)`);
      router.push('/super-admin/tenants');
    } catch (error) {
      console.error('Error:', error);
      alert('Error al crear el tenant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/super-admin/tenants" className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Nuevo Tenant</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Registra una nueva empresa operadora en la plataforma</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* SECCIÓN 1: DATOS DE LA EMPRESA */}
        <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-700 pb-4 mb-4">
            <Building2 className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Datos de la Empresa</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2 md:col-span-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Nombre del Tenant *</label>
              <input type="text" required value={formData.nombre} onChange={(e) => setFormData({ ...formData, nombre: e.target.value })} placeholder="Ej: Taxis San Miguel S.A." className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email de Contacto *</label>
              <input type="email" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} placeholder="contacto@taxissanmiguel.com" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Teléfono</label>
              <input type="text" value={formData.telefono} onChange={(e) => setFormData({ ...formData, telefono: e.target.value })} placeholder="3811234567" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="space-y-2 md:col-span-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Dirección Comercial</label>
              <input type="text" value={formData.direccion} onChange={(e) => setFormData({ ...formData, direccion: e.target.value })} placeholder="Av. Principal 123" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
        </section>

                {/* SECCIÓN 2: UBICACIÓN */}
        <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-700 pb-4 mb-4">
            <MapPin className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Ubicación y Operación</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Ciudad de Operación *</label>
              <input type="text" required value={formData.ciudad_nombre} onChange={(e) => setFormData({ ...formData, ciudad_nombre: e.target.value })} placeholder="Ej: San Miguel de Tucumán" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Código Postal</label>
              <input type="text" value={formData.codigo_postal} onChange={(e) => setFormData({ ...formData, codigo_postal: e.target.value })} placeholder="Ej: T4000" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          
          <div className="bg-blue-50 text-blue-800 text-sm p-3 rounded-lg flex gap-2 mt-4">
            <MapPin className="w-5 h-5 flex-shrink-0" />
            <p>Las coordenadas geográficas se obtendrán automáticamente al crear el tenant. Asegúrate de que la ciudad esté bien escrita.</p>
          </div>
        </section>

        {/* SECCIÓN 3: SEGURIDAD */}
        <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-700 pb-4 mb-4">
            <Lock className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Seguridad y Acceso</h2>
          </div>
          
          <p className="text-sm text-gray-500 mb-4">Define la contraseña inicial para el Administrador del Tenant. El usuario será: <strong>{formData.email || 'email@del.tenant'}</strong></p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Contraseña *</label>
              <div className="relative">
                <input type={showPassword ? 'text' : 'password'} required value={formData.admin_password} onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })} placeholder="••••••••" className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${errors.admin_password ? 'border-red-500' : 'border-gray-300'}`} />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.admin_password && <p className="text-xs text-red-500">{errors.admin_password}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Confirmar Contraseña *</label>
              <input type="password" required value={formData.confirm_password} onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })} placeholder="••••••••" className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${errors.confirm_password ? 'border-red-500' : 'border-gray-300'}`} />
              {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password}</p>}
            </div>
          </div>
          
          <div className="bg-blue-50 text-blue-800 text-sm p-3 rounded-lg flex gap-2">
            <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
            <p>Mínimo 8 caracteres, al menos una mayúscula y un número. El administrador podrá cambiar esta contraseña luego de su primer inicio de sesión.</p>
          </div>
        </section>

        {/* SECCIÓN 4: CONFIGURACIÓN REGIONAL */}
        <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-700 pb-4 mb-4">Configuración Regional</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Moneda por Defecto</label>
              <select value={formData.moneda_default} onChange={(e) => setFormData({ ...formData, moneda_default: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                <option value="ARS">ARS - Peso Argentino</option>
                <option value="USD">USD - Dólar Estadounidense</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Zona Horaria</label>
              <select value={formData.timezone} onChange={(e) => setFormData({ ...formData, timezone: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                <option value="America/Argentina/Tucuman">Argentina (Tucumán)</option>
                <option value="America/Argentina/Buenos_Aires">Argentina (Buenos Aires)</option>
                <option value="America/Argentina/Cordoba">Argentina (Córdoba)</option>
              </select>
            </div>
          </div>
        </section>

        {/* Botones */}
        <div className="flex items-center justify-end gap-3">
          <Link href="/super-admin/tenants" className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            Cancelar
          </Link>
          <button type="submit" disabled={loading} className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Creando Tenant...</> : 'Crear Tenant'}
          </button>
        </div>
      </form>
    </div>
  );
}