'use client'
import { useEffect, useState } from 'react'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useSession, signOut } from 'next-auth/react'
import { propietarioAPI } from '@/lib/api'
import {
  LayoutDashboard,
  Car,
  FileText,
  DollarSign,
  CreditCard,
  Wrench,
  BarChart,
  ChevronLeft,
  Users,
  Briefcase,
  Loader2,
  LogOut,
} from 'lucide-react'

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const { data: session, status } = useSession()
  const [propietarioNombre, setPropietarioNombre] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [isAdminView, setIsAdminView] = useState(false)
  const propietarioId = searchParams?.get('propietario_id')
  const user = session?.user

  // Manejar redirección al login
  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.replace('/login')
      return
    }
  }, [session, status, router])

  useEffect(() => {
    const loadPropietario = async () => {
      if (!user) return

      try {
        if (user?.role === 'admin' && propietarioId) {
          setIsAdminView(true)
          const data = await propietarioAPI.getOne(propietarioId)
          setPropietarioNombre(data.nombre)
        } else if (user?.role === 'admin') {
          setIsAdminView(true)
          setPropietarioNombre('Selecciona un propietario')
        } else if (user?.role === 'propietario') {
          setPropietarioNombre(user.name || 'Propietario')
        }
      } catch (error) {
        console.error('Error cargando propietario:', error)
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      loadPropietario()
    } else if (status !== 'loading') {
      setLoading(false)
    }
  }, [user, propietarioId, status])

  if (status === 'loading' || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!session || !user) {
    return null
  }

  if (user.role !== 'admin' && user.role !== 'propietario') {
    router.replace('/')
    return null
  }

  const menuItems = [
    { title: 'Dashboard', href: '/dashboard-propietario', icon: LayoutDashboard },
    { title: 'Vehículos', href: '/dashboard-propietario/vehiculos', icon: Car },
    { title: 'Contratos', href: '/dashboard-propietario/contratos', icon: FileText },
    { title: 'Ingresos', href: '/dashboard-propietario/ingresos', icon: DollarSign },
    { title: 'Gastos', href: '/dashboard-propietario/gastos', icon: CreditCard },
    { title: 'Mantenimientos', href: '/dashboard-propietario/mantenimientos', icon: Wrench },
    { title: 'Rentabilidad', href: '/dashboard-propietario/rentabilidad', icon: BarChart },
    { title: 'Reportes', href: '/dashboard-propietario/reportes', icon: FileText },
  ]

  const handleLogout = async () => {
    await signOut({ callbackUrl: '/login' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm px-6 py-3 flex justify-between items-center border-b">
        <div className="flex items-center gap-4">
          {isAdminView && (
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
              Dashboard Principal
            </button>
          )}
          <div className="flex items-center gap-3">
            <Briefcase className="h-5 w-5 text-primary" />
            <div>
              <h1 className="text-lg font-bold">
                {isAdminView
                  ? `Propietario: ${propietarioNombre}`
                  : user?.role === 'admin'
                  ? 'Módulo Propietarios'
                  : 'Mi Flota'}
              </h1>
              <div className="flex items-center gap-2">
                {isAdminView && propietarioId && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                    Vista Administrador
                  </span>
                )}
                {user?.role === 'admin' && !propietarioId && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                    Gestión de Propietarios
                  </span>
                )}
                {user?.role === 'propietario' && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                    Propietario
                  </span>
                )}
                <span className="text-xs text-muted-foreground">
                  {user?.email}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {user?.role === 'admin' && (
            <Link
              href="/admin/propietarios"
              className="text-sm bg-primary/10 text-primary px-3 py-1.5 rounded-md hover:bg-primary/20 transition-colors flex items-center gap-2"
            >
              <Users className="h-4 w-4" />
              Gestionar Propietarios
            </Link>
          )}
          <button
            onClick={handleLogout}
            className="text-sm text-red-600 hover:text-red-800 hover:bg-red-50 px-3 py-1.5 rounded-md transition-colors flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            Salir
          </button>
        </div>
      </header>

      <div className="flex">
        <aside className="w-64 bg-white border-r min-h-[calc(100vh-65px)] p-4 flex flex-col">
          <nav className="space-y-1 flex-1">
            {menuItems.map((item) => {
              let href = item.href
              if (isAdminView && propietarioId) {
                href = `${item.href}?propietario_id=${propietarioId}`
              } else if (user?.role === 'admin' && !propietarioId) {
                href = item.href
              } else if (user?.role === 'propietario') {
                href = item.href
              }
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
              return (
                <Link
                  key={item.href}
                  href={href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.title}
                </Link>
              )
            })}
          </nav>
          <div className="border-t pt-4 mt-4">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Cerrar Sesión
            </button>
          </div>
        </aside>
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}