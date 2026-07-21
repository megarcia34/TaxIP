'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  Car, 
  ClipboardList, 
  Calendar, 
  Wallet, 
  AlertTriangle, 
  FileText,
  LogOut,
  Menu,
  X,
  User,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { signOut } from 'next-auth/react'

const menuItems = [
  { title: 'Dashboard', href: '/operativo', icon: LayoutDashboard },
  { title: 'Nueva Solicitud', href: '/operativo/nueva-solicitud', icon: Car },
  { title: 'Solicitudes Activas', href: '/operativo/solicitudes', icon: ClipboardList },
  { title: 'Reservas', href: '/operativo/reservas', icon: Calendar },
  { title: 'Facturación', href: '/operativo/facturacion', icon: Wallet },
  { title: 'Contingencias', href: '/operativo/contingencias', icon: AlertTriangle },
  { title: 'Cierre de Turno', href: '/operativo/reportes/cierre-turno', icon: FileText },
]

export default function OperativoLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
      return
    }

    if (status === 'authenticated') {
      const role = session?.user?.role?.toLowerCase()
      // Verificar que el usuario es empleado
      if (role !== 'empleado') {
        router.push('/dashboard-empresa')
      }
    }
  }, [status, session, router])

  if (status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!session || session?.user?.role?.toLowerCase() !== 'empleado') {
    return null
  }

  const userInitial = session?.user?.name?.charAt(0) || session?.user?.email?.charAt(0) || 'U'

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform bg-background border-r transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center border-b px-4">
            <Link href="/operativo" className="flex items-center space-x-2">
              <Car className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">TaxIP Operativo</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-2">
              {menuItems.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.title}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="border-t p-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                <AvatarImage src={session?.user?.image || ''} />
                <AvatarFallback className="bg-primary/10 text-primary">
                  {userInitial}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {session?.user?.name || session?.user?.email}
                </p>
                <p className="text-xs text-muted-foreground capitalize">
                  {session?.user?.role || 'Operativo'}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              className="w-full mt-2 justify-start text-muted-foreground hover:text-foreground"
              onClick={() => signOut()}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Cerrar Sesión
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <h1 className="text-lg font-semibold">
            {menuItems.find(item => pathname === item.href || pathname?.startsWith(item.href + '/'))?.title || 'Dashboard'}
          </h1>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground hidden md:inline">
              Turno activo
            </span>
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          </div>
          <Avatar className="h-8 w-8">
            <AvatarImage src={session?.user?.image || ''} />
            <AvatarFallback className="bg-primary/10 text-primary">
              {userInitial}
            </AvatarFallback>
          </Avatar>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}