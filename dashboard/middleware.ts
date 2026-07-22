import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token
    const path = req.nextUrl.pathname
    const role = (token?.role as string)?.toLowerCase() || (token?.tipo_usuario as string)?.toLowerCase()

    // Redirigir desde /login si el usuario ya está autenticado
    if (path === '/login' && token) {
      return redirectByRole(role, req.url)
    }

    // Proteger rutas de super-admin: solo super_admin puede acceder
    if (path.startsWith('/super-admin') && role !== 'super_admin') {
      return NextResponse.redirect(new URL('/', req.url))
    }

    // Proteger rutas de empresa/admin tenant
    if (
      path.startsWith('/dashboard-empresa') && 
      role !== 'admin' && 
      role !== 'admin_tenant' && 
      role !== 'admin_empresa'
    ) {
      return redirectByRole(role, req.url)
    }

    // Proteger rutas de propietario
    if (
      path.startsWith('/dashboard-propietario') && 
      role !== 'propietario' && 
      role !== 'admin_propietario'
    ) {
      return redirectByRole(role, req.url)
    }

    // Proteger rutas de operativo (empleados y choferes)
    if (
      path.startsWith('/operativo') && 
      role !== 'empleado' && 
      role !== 'chofer'
    ) {
      return redirectByRole(role, req.url)
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        if (req.nextUrl.pathname === '/login') return true
        return !!token
      },
    },
    pages: {
      signIn: '/login',
    },
  }
)

function redirectByRole(role: string, baseUrl: string) {
  const roleMap: Record<string, string> = {
    super_admin: '/super-admin',
    admin: '/dashboard-empresa',         // Coincide con 'admin' de auth.tipo_usuario
    admin_tenant: '/dashboard-empresa',
    admin_empresa: '/dashboard-empresa',
    admin_propietario: '/dashboard-propietario',
    propietario: '/dashboard-propietario',
    empleado: '/operativo',
    chofer: '/operativo',
  }

  const destination = roleMap[role] || '/login'
  return NextResponse.redirect(new URL(destination, baseUrl))
}

export const config = {
  matcher: [
    '/',
    '/login',
    '/super-admin/:path*',
    '/dashboard-empresa/:path*',
    '/dashboard-propietario/:path*',
    '/operativo/:path*',
    '/choferes/:path*',
    '/clientes/:path*',
    '/configuracion/:path*',
    '/email/:path*',
    '/objetos-olvidados/:path*',
    '/ranking/:path*',
    '/vehiculos/:path*',
    '/viajes/:path*',
  ],
}