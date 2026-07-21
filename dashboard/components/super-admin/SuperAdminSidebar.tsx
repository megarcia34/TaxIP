'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Building2,
  Receipt,
  BarChart3,
  Settings,
  LogOut,
} from 'lucide-react'
import { signOut } from 'next-auth/react'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/super-admin' },
  { icon: Building2, label: 'Tenants', href: '/super-admin/tenants' },
  { icon: Receipt, label: 'Facturación', href: '/super-admin/facturacion' },
  { icon: BarChart3, label: 'Estadísticas', href: '/super-admin/estadisticas' },
  { icon: Settings, label: 'Configuración', href: '/super-admin/configuracion' },
]

export default function SuperAdminSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col min-h-screen">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-800 dark:text-white">TaxIP</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400">Super Admin</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                ${isActive
                  ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  )
}