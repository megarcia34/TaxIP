'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

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

    // Verificar que el usuario es admin
    if (status === 'authenticated') {
      const role = session?.user?.role?.toLowerCase()
      if (role !== 'admin') {
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

  if (!session || session?.user?.role?.toLowerCase() !== 'admin') {
    return null
  }

  return <>{children}</>
}