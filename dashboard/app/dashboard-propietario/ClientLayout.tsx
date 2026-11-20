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
  BarChart3,
  ChevronLeft,
  Users,
  Briefcase,
  Loader2,
  LogOut,
  MapPin,
  CalendarClock,
  AlertTriangle,
  CircleDot,
  ClipboardList,
  User,
  TrendingDown,
  Menu, // <-- NUEVO ICONO
  X,    // <-- NUEVO ICONO
} from 'lucide-react'
import { useAlertas } from '@/hooks/useAlertas'

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

  // ✅ NUEVO ESTADO PARA EL MENÚ MÓVIL
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Obtener total de alertas
  const { totalUrgentes } = useAlertas()

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.replace('/login')
      return
    }
  }, [session, status, router])

  // Cerrar el menú móvil al cambiar de ruta
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [pathname])

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
    { title: 'Mi perfil', href: '/dashboard-propietario/perfil', icon: User },
    { title: 'Dashboard', href: '/dashboard-propietario', icon: LayoutDashboard },
    { title: 'Vehículos', href: '/dashboard-propietario/vehiculos', icon: Car },
    { title: 'Vehículos en Tiempo Real', href: '/dashboard-propietario/vehiculos-tiempo-real', icon: MapPin },
    { title: 'Viajes', href: '/dashboard-propietario/viajes', icon: CalendarClock },
    { title: 'Documentos', href: '/dashboard-propietario/documentos', icon: FileText, badge: totalUrgentes },
    { title: 'Neumáticos', href: '/dashboard-propietario/neumaticos', icon: CircleDot },
    { title: 'Contratos', href: '/dashboard-propietario/contratos', icon: Briefcase },
    { title: 'Ingresos', href: '/dashboard-propietario/ingresos', icon: DollarSign },
    { title: 'Conciliaciones', href: '/dashboard-propietario/conciliaciones', icon: ClipboardList },
    { title: 'Gastos', href: '/dashboard-propietario/gastos', icon: CreditCard },
    { title: 'Mantenimientos', href: '/dashboard-propietario/mantenimientos', icon: Wrench },
    { title: 'Rentabilidad', href: '/dashboard-propietario/rentabilidad', icon: BarChart3 },
    { title: 'Reportes', href: '/dashboard-propietario/reportes', icon: ClipboardList },
    { title: 'Metricas de fallbacks', href: '/dashboard-propietario/metricas-fallbacks', icon: TrendingDown },    
  ]

  const handleLogout = async () => {
    await signOut({ callbackUrl: '/login' })
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* HEADER */}
      <header className="bg-white shadow-sm px-4 py-3 flex justify-between items-center border-b relative z-20">
        <div className="flex items-center gap-3">
          {/* BOTÓN HAMBURGUESA (Solo visible en móvil) */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-md"
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>

          <div className="flex items-center gap-3">
            <Briefcase className="h-5 w-5 text-primary hidden sm:block" />
            <div>
              <h1 className="text-base sm:text-lg font-bold truncate max-w-[150px] sm:max-w-none">
                {isAdminView
                  ? `Propietario: ${propietarioNombre}`
                  : user?.role === 'admin'
                  ? 'Módulo Propietarios'
                  : 'Mi Flota'}
              </h1>
              <div className="hidden sm:flex items-center gap-2">
                {isAdminView && propietarioId && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Vista Administrador</span>
                )}
                {user?.role === 'admin' && !propietarioId && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Gestión de Propietarios</span>
                )}
                {user?.role === 'propietario' && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Propietario</span>
                )}
                <span className="text-xs text-muted-foreground truncate">{user?.email}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Botón de Admin (Oculto en móvil) */}
          {user?.role === 'admin' && (
            <Link
              href="/admin/propietarios"
              className="hidden md:flex text-sm bg-primary/10 text-primary px-3 py-1.5 rounded-md hover:bg-primary/20 transition-colors items-center gap-2"
            >
              <Users className="h-4 w-4" />
              Gestionar Propietarios
            </Link>
          )}
          <button
            onClick={handleLogout}
            className="text-sm text-red-600 hover:text-red-800 hover:bg-red-50 px-2 sm:px-3 py-1.5 rounded-md transition-colors flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Salir</span>
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* OVERLAY OSCURO PARA MÓVIL */}
        {isMobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-10 md:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* SIDEBAR */}
        <aside className={`
          fixed md:static inset-y-0 left-0 z-20 w-64 bg-white border-r transform transition-transform duration-200 ease-in-out flex flex-col
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          md:min-h-[calc(100vh-65px)]
        `}>
          <nav className="space-y-1 flex-1 overflow-y-auto p-4 pt-20 md:pt-4">
            {menuItems.map((item) => {
              let href = item.href
              if (isAdminView && propietarioId) {
                href = `${item.href}?propietario_id=${propietarioId}`
              }
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
              const badge = item.badge || 0

              return (
                <Link
                  key={item.href}
                  href={href}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="h-4 w-4" />
                    {item.title}
                  </div>
                  {badge > 0 && (
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      isActive ? 'bg-primary-foreground text-primary' : 'bg-red-500 text-white'
                    }`}>
                      {badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>
          <div className="border-t p-4 mt-auto">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Cerrar Sesión
            </button>
          </div>
        </aside>

        {/* CONTENIDO PRINCIPAL */}
        <main className="flex-1 p-4 md:p-6 overflow-y-auto w-full">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}