'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Building2, DollarSign } from 'lucide-react'
import DatosEmpresaPage from './empresa/page'
import TarifasPage from './tarifas/page'

export default function ConfiguracionPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Configuración</h1>
        <p className="text-muted-foreground">
          Gestión de datos de la empresa y configuración de tarifas
        </p>
      </div>

      <Tabs defaultValue="empresa" className="space-y-4">
        <TabsList>
          <TabsTrigger value="empresa" className="gap-2">
            <Building2 className="h-4 w-4" />
            Datos de la Empresa
          </TabsTrigger>
          <TabsTrigger value="tarifas" className="gap-2">
            <DollarSign className="h-4 w-4" />
            Tarifas
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="empresa">
          <DatosEmpresaPage />
        </TabsContent>
        
        <TabsContent value="tarifas">
          <TarifasPage />
        </TabsContent>
      </Tabs>
    </div>
  )
}