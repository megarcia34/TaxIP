'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    // Redirigir según rol cuando está autenticado
    if (status === 'authenticated' && session?.user) {
      const role = session.user.role?.toLowerCase()
      console.log('🔐 [AuthLayout] Usuario autenticado, redirigiendo por rol:', role)
      
      if (role === 'admin') {
        router.push('/')
      } else if (role === 'propietario') {
        router.push('/dashboard-propietario')
      } else if (role === 'empleado') {
        router.push('/empresa')
      } else {
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

  // Si está autenticado, no renderizar el login (la redirección ocurre en el useEffect)
  if (status === 'authenticated') {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50 p-4">
      {children}
    </div>
  )
}