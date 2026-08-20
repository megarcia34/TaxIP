'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

// ✅ Roles que pueden acceder a /admin
const ROLES_ADMIN = ['admin', 'admin_tenant', 'super_admin']

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    // Verificar que el usuario está autenticado
    if (status === 'unauthenticated') {
      router.push('/login')
      return
    }

    // Verificar que el usuario tiene rol admin
    if (status === 'authenticated') {
      const role = session?.user?.role?.toLowerCase()
      // ✅ Permitir admin, admin_tenant y super_admin
      if (!role || !ROLES_ADMIN.includes(role)) {
        router.push('/')
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

  // ✅ Permitir acceso si el rol es admin, admin_tenant o super_admin
  const role = session?.user?.role?.toLowerCase()
  if (!session || !role || !ROLES_ADMIN.includes(role)) {
    return null
  }

  return <>{children}</>
}