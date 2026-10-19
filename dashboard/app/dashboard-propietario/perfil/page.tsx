// D:\ataxip\dashboard\app\dashboard-propietario\perfil\page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, User, Receipt, Wallet, Car } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PerfilDatosPersonales from '@/components/propietario/perfil/PerfilDatosPersonales';
import PerfilDatosFiscales from '@/components/propietario/perfil/PerfilDatosFiscales';
import PerfilCuentasCobro from '@/components/propietario/perfil/PerfilCuentasCobro';
import PerfilQuieroSerChofer from '@/components/propietario/perfil/PerfilQuieroSerChofer';

export default function PerfilPage() {
  const [propietarioId, setPropietarioId] = useState<string | null>(null);
  const [tab, setTab] = useState('datos-personales');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      setPropietarioId(params.get('propietario_id'));

      // Permite abrir directo una tab: /perfil?tab=cuentas
      const tabParam = params.get('tab');
      if (tabParam) setTab(tabParam);
    }
  }, []);

  const backHref = propietarioId
    ? `/admin/propietarios?propietario_id=${propietarioId}`
    : '/dashboard-propietario';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href={backHref}>
          <Button variant="outline" size="icon" type="button">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Mi perfil</h1>
          <p className="text-muted-foreground">
            Datos personales, fiscales, cuentas de cobro y postulacion como chofer
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={tab} onValueChange={setTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 h-auto">
          <TabsTrigger value="datos-personales" className="gap-2 py-2.5">
            <User className="h-4 w-4" />
            <span className="hidden sm:inline">Datos personales</span>
            <span className="sm:hidden">Personales</span>
          </TabsTrigger>
          <TabsTrigger value="datos-fiscales" className="gap-2 py-2.5">
            <Receipt className="h-4 w-4" />
            <span className="hidden sm:inline">Datos fiscales</span>
            <span className="sm:hidden">Fiscales</span>
          </TabsTrigger>
          <TabsTrigger value="cuentas" className="gap-2 py-2.5">
            <Wallet className="h-4 w-4" />
            <span className="hidden sm:inline">Cuentas de cobro</span>
            <span className="sm:hidden">Cuentas</span>
          </TabsTrigger>
          <TabsTrigger value="chofer" className="gap-2 py-2.5">
            <Car className="h-4 w-4" />
            <span className="hidden sm:inline">Quiero ser chofer</span>
            <span className="sm:hidden">Chofer</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="datos-personales" className="mt-6">
          <PerfilDatosPersonales />
        </TabsContent>

        <TabsContent value="datos-fiscales" className="mt-6">
          <PerfilDatosFiscales />
        </TabsContent>

        <TabsContent value="cuentas" className="mt-6">
          <PerfilCuentasCobro />
        </TabsContent>

        <TabsContent value="chofer" className="mt-6">
          {/* TODO: Fase C */}
          <div className="border rounded-lg p-12 text-center text-muted-foreground">
            <Car className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p>Postulacion como chofer</p>
            <p className="text-sm">Proximamente (Fase C)</p>
          </div>
          <PerfilQuieroSerChofer />
        </TabsContent>
      </Tabs>
    </div>
  );
}