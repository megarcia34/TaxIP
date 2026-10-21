// D:\aTaxip\dashboard\components\layout\Sidebar.tsx
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'
import { useSolicitudesCount } from '@/hooks/admin/useSolicitudesTenant'
import Image from 'next/image'
import LogoPrincipal from '@/public/logos/logo-principal.png'
import { useState } from 'react'
import {
  LayoutDashboard,
  Car,
  Users,
  Map,
  MapPin,
  Trophy,
  Briefcase,
  Settings,
  Mail,
  Package,
  Store,
  BarChart3,
  DollarSign,
  Wrench,
  FileText,
  Handshake,
  ClipboardList,
  Building2,
  CreditCard,
  Calendar,
  Receipt,
  TrendingUp,
  Wallet,
  AlertTriangle,
  Clock,
  ChevronDown,
  ChevronRight,
  CircleDot,
  Building,
  User,
  CalendarClock,
} from 'lucide-react'

interface SidebarProps {
  open: boolean
  setOpen: (open: boolean) => void
}

// ============================================
// MENU PARA SUPER ADMIN
// ============================================
const menuItemsSuperAdmin = [
  { title: 'Dashboard', href: '/super-admin', icon: LayoutDashboard },
  { title: 'Tenants', href: '/super-admin/tenants', icon: Building },
  { title: 'Facturacion', href: '/super-admin/facturacion', icon: Receipt },
  { title: 'Estadisticas', href: '/super-admin/estadisticas', icon: TrendingUp },
  { title: 'Configuracion', href: '/super-admin/configuracion', icon: Settings },
  { title: 'Pagos Empresas', href: '/admin/pagos', icon: DollarSign },
]

// ============================================
// MENU PARA PROPIETARIO
// ============================================
const menuItemsPropietario = [
  { title: 'Dashboard', href: '/dashboard-propietario', icon: LayoutDashboard },
  { title: 'Vehiculos', href: '/dashboard-propietario/vehiculos', icon: Car },
  {
    title: 'Vehiculos en Tiempo Real',
    href: '/dashboard-propietario/vehiculos-tiempo-real',
    icon: MapPin
  },
  {
    title: 'Viajes',
    href: '/dashboard-propietario/viajes',
    icon: CalendarClock
  },
  { title: 'Documentos', href: '/dashboard-propietario/documentos', icon: FileText },
  { title: 'Contratos', href: '/dashboard-propietario/contratos', icon: Handshake },
  { title: 'Ingresos', href: '/dashboard-propietario/ingresos', icon: DollarSign },
  { title: 'Gastos', href: '/dashboard-propietario/gastos', icon: CreditCard },
  { title: 'Mantenimientos', href: '/dashboard-propietario/mantenimientos', icon: Wrench },
  { title: 'Neumaticos', href: '/dashboard-propietario/neumaticos', icon: CircleDot },
  { title: 'Rentabilidad', href: '/dashboard-propietario/rentabilidad', icon: BarChart3 },
  { title: 'Reportes', href: '/dashboard-propietario/reportes', icon: ClipboardList },
  { title: 'Mi perfil', href: '/dashboard-propietario/perfil', icon: User },
  { title: 'Metricas de fallbacks', href: '/dashboard-propietario/metricas-fallbacks', icon: TrendingUp },
]

// ============================================
// MENU PARA EMPLEADO OPERATIVO
// ============================================
const menuItemsOperativo = [
  { title: 'Dashboard', href: '/operativo', icon: LayoutDashboard },
  { title: 'Nueva Solicitud', href: '/operativo/nueva-solicitud', icon: Car },
  { title: 'Solicitudes Activas', href: '/operativo/solicitudes', icon: ClipboardList },
  { title: 'Reservas', href: '/operativo/reservas', icon: Calendar },
  { title: 'Facturacion', href: '/operativo/facturacion', icon: Wallet },
  { title: 'Contingencias', href: '/operativo/contingencias', icon: AlertTriangle },
  { title: 'Cierre de Turno', href: '/operativo/reportes/cierre-turno', icon: Clock },
]

// ============================================
// MENU PARA ADMIN EMPRESA
// ============================================
const menuItemsAdminEmpresa = [
  { title: 'Dashboard', href: '/dashboard-empresa', icon: LayoutDashboard },
  { title: 'Viajes', href: '/dashboard-empresa/viajes', icon: Map },
  { title: 'Empleados', href: '/dashboard-empresa/empleados', icon: Users },
  { title: 'Facturacion', href: '/dashboard-empresa/facturacion', icon: Receipt },
  { title: 'Estadisticas', href: '/dashboard-empresa/estadisticas', icon: TrendingUp },
  { title: 'Cuenta Corriente', href: '/dashboard-empresa/cuenta-corriente', icon: Wallet },
]

// ============================================
// MENU PARA ADMIN TENANT
// ============================================
const menuItemsAdminTenant = [
  // SECCION PRINCIPAL
  { title: 'Dashboard', href: '/', icon: LayoutDashboard },

  // SECCION GESTION
  { title: 'Solicitudes Pendientes', href: '/admin/solicitudes-pendientes', icon: ClipboardList, badge: 'solicitudes' },
  { title: 'Viajes', href: '/viajes', icon: Map },
  { title: 'Choferes', href: '/choferes', icon: Car },
  { title: 'Vehiculos', href: '/vehiculos', icon: Car },
  { title: 'Pasajeros', href: '/clientes', icon: User },
  { title: 'Ranking', href: '/ranking', icon: Trophy },

  // SECCION ADMIN
  { title: 'Propietarios', href: '/admin/propietarios', icon: Briefcase },
  { title: 'Empresas', href: '/admin/empresas', icon: Building2 },
  { title: 'Comercios QR', href: '/admin/comercios', icon: Store },
  { title: 'Estadisticas', href: '/admin/estadisticas', icon: BarChart3 },
  { title: 'Facturacion', href: '/admin/facturacion', icon: Receipt },
  { title: 'Cierre de Turno', href: '/admin/cierre-turno', icon: Clock },
  { title: 'Pagos Empresas', href: '/admin/pagos', icon: DollarSign },

  // SECCION UTILIDADES
  { title: 'Objetos Olvidados', href: '/objetos-olvidados', icon: Package },
  { title: 'Email', href: '/email', icon: Mail },
  {
    title: 'Configuracion',
    icon: Settings,
    subItems: [
      { title: 'Tarifas', href: '/configuracion/tarifas' },
      { title: 'Datos del Tenant', href: '/configuracion/tenant' },
    ],
  },
]

export function Sidebar({ open, setOpen }: SidebarProps) {
  const pathname = usePathname()
  const { user, isLoading } = useAuth()
  const [openSubMenus, setOpenSubMenus] = useState<Record<string, boolean>>({})

  const toggleSubMenu = (title: string) => {
    setOpenSubMenus(prev => ({
      ...prev,
      [title]: !prev[title],
    }))
  }

  // Detectar si el usuario es admin tenant para contar solicitudes
  const tipoUsuario = user?.tipo_usuario?.toLowerCase() || ''
  const esAdminTenant = tipoUsuario === 'admin_tenant' || (tipoUsuario === 'admin' && !!user?.control_base_id)

  // Hook de conteo de solicitudes (solo se ejecuta si es admin tenant)
  // NOTA: el hook usa enabled para no disparar queries en otros roles
  const { total: totalSolicitudes } = useSolicitudesCount(esAdminTenant)

  if (isLoading) {
    return (
      <>
        <div
          className={cn(
            'fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden',
            open ? 'block' : 'hidden'
          )}
          onClick={() => setOpen(false)}
        />
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-50 w-64 transform bg-background border-r transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0',
            open ? 'translate-x-0' : '-translate-x-full'
          )}
        >
          <div className="flex h-full flex-col">
            <div className="flex h-16 items-center border-b px-4">
              <div className="flex items-center space-x-2">
                <Car className="h-6 w-6 text-primary" />
                <span className="font-bold text-lg">TaxIP 2.0</span>
              </div>
            </div>
            <div className="flex-1 flex items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          </div>
        </aside>
      </>
    )
  }

  // ============================================
  // DETECCION DE ROL
  // ============================================
  const getMenuItems = () => {
    if (tipoUsuario === 'super_admin') {
      return menuItemsSuperAdmin
    }

    if (tipoUsuario === 'propietario' || tipoUsuario === 'admin_propietario') {
      return menuItemsPropietario
    }

    if (tipoUsuario === 'empleado' || tipoUsuario === 'chofer') {
      return menuItemsOperativo
    }

    if (tipoUsuario === 'admin_empresa') {
      return menuItemsAdminEmpresa
    }

    if (esAdminTenant) {
      return menuItemsAdminTenant
    }

    return menuItemsAdminTenant
  }

  const menuItems = getMenuItems()

  const getHomeHref = () => {
    if (tipoUsuario === 'super_admin') return '/super-admin'
    if (tipoUsuario === 'propietario' || tipoUsuario === 'admin_propietario') return '/dashboard-propietario'
    if (tipoUsuario === 'empleado' || tipoUsuario === 'chofer') return '/operativo'
    if (tipoUsuario === 'admin_empresa') return '/dashboard-empresa'
    return '/'
  }

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden',
          open ? 'block' : 'hidden'
        )}
        onClick={() => setOpen(false)}
      />

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-background border-r transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center border-b px-4">
            <Link href={getHomeHref()} className="flex items-center space-x-2">
              <Image
                src={LogoPrincipal}
                alt="TaxIP"
                width={120}
                height={26}
                className="h-8 w-auto"
                priority
              />
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-2">
              {menuItems.map((item: any) => {
                // Items con submenu
                if (item.subItems) {
                  const isOpen = openSubMenus[item.title] || false
                  const isActive = item.subItems.some(
                    (sub: any) => pathname === sub.href || pathname?.startsWith(sub.href + '/')
                  )

                  return (
                    <li key={item.title}>
                      <button
                        onClick={() => toggleSubMenu(item.title)}
                        className={cn(
                          'flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-muted',
                          isActive && 'bg-primary/10 text-primary'
                        )}
                      >
                        <span className="flex items-center gap-3">
                          <item.icon className="h-4 w-4" />
                          {item.title}
                        </span>
                        {isOpen ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </button>
                      {isOpen && (
                        <ul className="ml-4 mt-1 space-y-1 border-l border-muted pl-2">
                          {item.subItems.map((subItem: any) => {
                            const isSubActive =
                              pathname === subItem.href || pathname?.startsWith(subItem.href + '/')
                            return (
                              <li key={subItem.href}>
                                <Link
                                  href={subItem.href}
                                  className={cn(
                                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                    isSubActive
                                      ? 'bg-primary/10 text-primary'
                                      : 'hover:bg-muted'
                                  )}
                                >
                                  {subItem.title}
                                </Link>
                              </li>
                            )
                          })}
                        </ul>
                      )}
                    </li>
                  )
                }

                // Items sin submenu
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
                const showBadge = item.badge === 'solicitudes' && totalSolicitudes > 0

                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      <span className="flex-1">{item.title}</span>
                      {showBadge && (
                        <span
                          className={cn(
                            'ml-auto text-xs rounded-full px-2 py-0.5 font-semibold',
                            isActive
                              ? 'bg-primary-foreground text-primary'
                              : 'bg-red-500 text-white'
                          )}
                        >
                          {totalSolicitudes}
                        </span>
                      )}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="border-t p-4">
            {user && (
              <div className="mb-2 text-xs">
                <p className="font-medium">{user.nombre || user.email}</p>
                <p className="text-muted-foreground">{user.email}</p>
                <p className="text-muted-foreground capitalize mt-1">
                  Rol: {user.tipo_usuario || user.rol}
                  {user.rol === 'propietario' && user.totalVehiculos !== undefined && (
                    <span className="ml-2 text-primary">({user.totalVehiculos} vehiculos)</span>
                  )}
                  {user.rol === 'empleado' && user.empresaNombre && (
                    <span className="ml-2 text-primary block">Empresa: {user.empresaNombre}</span>
                  )}
                </p>
              </div>
            )}

            <p className="text-xs text-muted-foreground text-center mt-3">TaxIP 2.0 2024</p>
          </div>
        </div>
      </aside>
    </>
  )
}