'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Car, 
  Users, 
  DollarSign, 
  Clock, 
  Loader2,
  TrendingUp,
  Calendar,
  Wallet,
  FileText
} from 'lucide-react'
import Link from 'next/link'

interface EmpresaKPI {
  total_viajes: number
  viajes_hoy: number
  viajes_mes: number
  viajes_pendientes: number
  viajes_en_curso: number
  viajes_completados: number
  viajes_cancelados: number
  total_gastado: number
  gasto_hoy: number
  gasto_mes: number
  empleados_activos: number
  promedio_viaje: number
}

const formatMoneda = (monto: number | undefined | null) => {
  if (monto === undefined || monto === null) return '$0'
  return `$${monto.toFixed(2)}`
}

export default function DashboardEmpresaPage() {
  const { data: kpis, isLoading } = useQuery<EmpresaKPI>({
    queryKey: ['empresa-kpis'],
    queryFn: async () => {
      const response = await apiClient.get('/api/empresa/dashboard/kpis')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Building2 className="h-6 w-6" />
          Dashboard Empresa
        </h1>
        <p className="text-muted-foreground">
          Panel de gestión para clientes corporativos
        </p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Viajes</p>
                <p className="text-2xl font-bold">{kpis?.total_viajes || 0}</p>
              </div>
              <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                <Car className="h-5 w-5 text-blue-600 dark:text-blue-300" />
              </div>
            </div>
            <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
              <span>Hoy: {kpis?.viajes_hoy || 0}</span>
              <span>Mes: {kpis?.viajes_mes || 0}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Gastado</p>
                <p className="text-2xl font-bold">{formatMoneda(kpis?.total_gastado)}</p>
              </div>
              <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
                <DollarSign className="h-5 w-5 text-green-600 dark:text-green-300" />
              </div>
            </div>
            <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
              <span>Hoy: {formatMoneda(kpis?.gasto_hoy)}</span>
              <span>Mes: {formatMoneda(kpis?.gasto_mes)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Empleados Activos</p>
                <p className="text-2xl font-bold">{kpis?.empleados_activos || 0}</p>
              </div>
              <div className="rounded-full bg-purple-100 p-3 dark:bg-purple-900">
                <Users className="h-5 w-5 text-purple-600 dark:text-purple-300" />
              </div>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              <span>Promedio por viaje: {formatMoneda(kpis?.promedio_viaje)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pendientes</p>
                <p className="text-2xl font-bold">{kpis?.viajes_pendientes || 0}</p>
              </div>
              <div className="rounded-full bg-orange-100 p-3 dark:bg-orange-900">
                <Clock className="h-5 w-5 text-orange-600 dark:text-orange-300" />
              </div>
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <Badge className="bg-green-500">Completados: {kpis?.viajes_completados || 0}</Badge>
              <Badge variant="outline">Cancelados: {kpis?.viajes_cancelados || 0}</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Acciones rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Link href="/dashboard-empresa/viajes/nuevo">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-full bg-blue-100 p-2 dark:bg-blue-900">
                <Car className="h-5 w-5 text-blue-600 dark:text-blue-300" />
              </div>
              <div>
                <p className="font-medium">Solicitar Viaje</p>
                <p className="text-xs text-muted-foreground">Nuevo viaje corporativo</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-empresa/viajes">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-full bg-green-100 p-2 dark:bg-green-900">
                <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-300" />
              </div>
              <div>
                <p className="font-medium">Ver Viajes</p>
                <p className="text-xs text-muted-foreground">Historial de viajes</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-empresa/empleados">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-full bg-purple-100 p-2 dark:bg-purple-900">
                <Users className="h-5 w-5 text-purple-600 dark:text-purple-300" />
              </div>
              <div>
                <p className="font-medium">Empleados</p>
                <p className="text-xs text-muted-foreground">Gestionar empleados</p>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard-empresa/facturacion">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-full bg-yellow-100 p-2 dark:bg-yellow-900">
                <FileText className="h-5 w-5 text-yellow-600 dark:text-yellow-300" />
              </div>
              <div>
                <p className="font-medium">Facturación</p>
                <p className="text-xs text-muted-foreground">Facturas y pagos</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Resumen del Mes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between border-b py-2">
                <span className="text-muted-foreground">Viajes realizados</span>
                <span className="font-medium">{kpis?.viajes_mes || 0}</span>
              </div>
              <div className="flex justify-between border-b py-2">
                <span className="text-muted-foreground">Gasto total</span>
                <span className="font-medium">{formatMoneda(kpis?.gasto_mes)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Completados / Cancelados</span>
                <span className="font-medium">
                  {kpis?.viajes_completados || 0} / {kpis?.viajes_cancelados || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Wallet className="h-4 w-4" />
              Actividad Reciente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between border-b py-2">
                <span className="text-muted-foreground">Viajes hoy</span>
                <span className="font-medium">{kpis?.viajes_hoy || 0}</span>
              </div>
              <div className="flex justify-between border-b py-2">
                <span className="text-muted-foreground">Gasto hoy</span>
                <span className="font-medium">{formatMoneda(kpis?.gasto_hoy)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">En curso</span>
                <span className="font-medium">{kpis?.viajes_en_curso || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}