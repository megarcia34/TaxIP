'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle2, Car } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

function ExitoContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get('email') || '';

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push(`/login?email=${encodeURIComponent(email)}&role=propietario`);
    }, 5000);

    return () => clearTimeout(timer);
  }, [router, email]);

  return (
    <div className="text-center space-y-6 max-w-md">
      <div className="flex justify-center">
        <div className="p-4 bg-green-100 rounded-full">
          <CheckCircle2 className="h-16 w-16 text-green-600" />
        </div>
      </div>
      
      <h1 className="text-2xl font-bold text-gray-900">✅ ¡Registro completado!</h1>
      
      <p className="text-gray-600">
        Ya sos parte de TaxIP. Te redirigiremos para que inicies sesión
        y registres tu primer vehículo.
      </p>

      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <p className="font-medium">Credenciales</p>
        <p className="mt-1">📧 <span className="font-mono">{email || 'tu email'}</span></p>
        <p className="text-xs text-gray-400 mt-2">Usá estas credenciales para iniciar sesión</p>
      </div>

      <div className="flex flex-col gap-3">
        <Button
          onClick={() => router.push(`/login?email=${encodeURIComponent(email)}&role=propietario`)}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          Iniciar sesión ahora
        </Button>
        
        <p className="text-sm text-gray-400">
          Serás redirigido automáticamente en 5 segundos...
        </p>
      </div>

      <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
        <Car className="h-3 w-3" />
        <span>TaxIP 2.0</span>
      </div>
    </div>
  );
}

export default function RegistroExitoPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Suspense fallback={
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      }>
        <ExitoContent />
      </Suspense>
    </div>
  );
}