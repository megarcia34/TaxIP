'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Car, Loader2, MapPin, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';

interface CiudadOperativa {
  id: string;
  nombre: string;
  codigo_postal: string | null;
  tenant_id: string;
  tenant_nombre: string;
}

export default function RegistroPropietarioPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [cargandoCiudades, setCargandoCiudades] = useState(true);
  const [ciudades, setCiudades] = useState<CiudadOperativa[]>([]);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    password: '',
    confirmPassword: '',
    ciudad_id: '',
    acepta_terminos: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Cargar ciudades operativas
  useEffect(() => {
    const cargarCiudades = async () => {
      try {
        const res = await fetch('/api/geo/ciudades-operativas');
        if (!res.ok) throw new Error('Error al cargar ciudades');
        const data = await res.json();
        setCiudades(data);
        if (data.length === 0) {
          toast.error('No hay ciudades disponibles. Contacta al administrador.');
        }
      } catch (error) {
        console.error('Error cargando ciudades:', error);
        toast.error('Error al cargar las ciudades disponibles');
      } finally {
        setCargandoCiudades(false);
      }
    };
    cargarCiudades();
  }, []);

  const validarFormulario = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) newErrors.nombre = 'El nombre es obligatorio';
    if (!formData.apellido.trim()) newErrors.apellido = 'El apellido es obligatorio';
    if (!formData.email.trim()) {
      newErrors.email = 'El email es obligatorio';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    if (!formData.password) {
      newErrors.password = 'La contraseña es obligatoria';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }
    if (!formData.ciudad_id) {
      newErrors.ciudad_id = 'Selecciona una ciudad';
    }
    if (!formData.acepta_terminos) {
      newErrors.acepta_terminos = 'Debes aceptar los términos y condiciones';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validarFormulario()) {
      toast.error('Corrige los errores del formulario');
      return;
    }

    setLoading(true);

    try {
      await apiClient.post('/api/auth/registro/propietario',{
        nombre: formData.nombre,
        apellido: formData.apellido,
        email: formData.email,
        password: formData.password,
        telefono: formData.telefono,
        ciudad_id: formData.ciudad_id,
        acepta_terminos: formData.acepta_terminos,
      });

      toast.success('¡Registro completado! Redirigiendo...');
      router.push(`/registro/propietario/exito?email=${encodeURIComponent(formData.email)}`);
    } catch (error: any) {
      console.error('Error en registro:', error);
      toast.error(error.response?.data?.detail || 'Error al procesar el registro');
    } finally {
      setLoading(false);
    }
  };

  if (cargandoCiudades) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <div className="p-3 bg-indigo-100 rounded-full">
              <Car className="h-8 w-8 text-indigo-600" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Crear cuenta de Propietario</h1>
          <p className="text-sm text-gray-500 mt-1">
            Completá tus datos para empezar a gestionar tu flota
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          {/* Nombre y Apellido */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-700">Nombre *</label>
              <input
                type="text"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                placeholder="Juan"
                className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 ${
                  errors.nombre ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.nombre && <p className="text-xs text-red-500">{errors.nombre}</p>}
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-700">Apellido *</label>
              <input
                type="text"
                value={formData.apellido}
                onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                placeholder="Pérez"
                className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 ${
                  errors.apellido ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.apellido && <p className="text-xs text-red-500">{errors.apellido}</p>}
            </div>
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Email *</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="juan@email.com"
              className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
          </div>

          {/* Teléfono */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Teléfono</label>
            <input
              type="text"
              value={formData.telefono}
              onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              placeholder="3511234567"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Contraseña */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Contraseña *</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Mínimo 6 caracteres"
                className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.password && <p className="text-xs text-red-500">{errors.password}</p>}
          </div>

          {/* Confirmar Contraseña */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Confirmar Contraseña *</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Repetí tu contraseña"
                className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.confirmPassword && <p className="text-xs text-red-500">{errors.confirmPassword}</p>}
          </div>

          {/* Ciudad */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-gray-700">Ciudad de operación *</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={formData.ciudad_id}
                onChange={(e) => setFormData({ ...formData, ciudad_id: e.target.value })}
                className={`w-full pl-10 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 appearance-none ${
                  errors.ciudad_id ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Seleccioná una ciudad</option>
                {ciudades.map((ciudad) => (
                  <option key={ciudad.id} value={ciudad.id}>
                    {ciudad.nombre} {ciudad.codigo_postal ? `(${ciudad.codigo_postal})` : ''}
                  </option>
                ))}
              </select>
            </div>
            {ciudades.length === 0 && (
              <p className="text-xs text-amber-600">
                No hay ciudades disponibles. Contactá al administrador.
              </p>
            )}
            {errors.ciudad_id && <p className="text-xs text-red-500">{errors.ciudad_id}</p>}
          </div>

          {/* Términos */}
          <div className="flex items-start gap-2 pt-1">
            <input
              type="checkbox"
              id="terminos"
              checked={formData.acepta_terminos}
              onChange={(e) => setFormData({ ...formData, acepta_terminos: e.target.checked })}
              className="mt-0.5 h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <label htmlFor="terminos" className="text-sm text-gray-600">
              Acepto los{' '}
              <Link href="/terminos" className="text-indigo-600 hover:underline">
                términos y condiciones
              </Link>
              {' '}de la plataforma
            </label>
          </div>
          {errors.acepta_terminos && <p className="text-xs text-red-500">{errors.acepta_terminos}</p>}

          {/* Botón */}
          <button
            type="submit"
            disabled={loading || ciudades.length === 0}
            className="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 text-sm font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Registrando...
              </>
            ) : (
              'Registrarme'
            )}
          </button>

          {/* Link a login */}
          <p className="text-center text-sm text-gray-500 mt-2">
            ¿Ya tenés cuenta?{' '}
            <Link href="/login?role=propietario" className="text-indigo-600 hover:underline">
              Iniciar sesión
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}