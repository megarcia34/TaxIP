'use client'

import { useState, useEffect } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Car, Loader2, AlertCircle } from 'lucide-react'

// Roles válidos que pueden venir desde la landing
const ROLES_VALIDOS = ['conductor', 'propietario', 'empresa', 'empleado']

// Mapeo de roles a nombres amigables para mostrar
const ROLES_DISPLAY: Record<string, string> = {
  conductor: 'Conductor',
  propietario: 'Propietario',
  empresa: 'Empresa',
  empleado: 'Empleado',
}

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  // Leer el parámetro `?role=` de la URL
  const roleParam = searchParams.get('role')
  const isValidRole = roleParam && ROLES_VALIDOS.includes(roleParam.toLowerCase())
  const displayRole = isValidRole ? ROLES_DISPLAY[roleParam.toLowerCase()] : null

  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [loginError, setLoginError] = useState<string | null>(null)

  // Limpiar error cuando el usuario escribe
  useEffect(() => {
    if (loginError) setLoginError(null)
  }, [formData.email, formData.password])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setLoginError(null)

    try {
      // 1. Intentar login con NextAuth
      const result = await signIn('credentials', {
        email: formData.email,
        password: formData.password,
        redirect: false,
      })

      if (result?.error) {
        toast.error('Credenciales inválidas')
        setLoginError('Email o contraseña incorrectos')
        setIsLoading(false)
        return
      }

      // 2. Obtener sesión para conocer el rol real del usuario
      const sessionRes = await fetch('/api/auth/session')
      const session = await sessionRes.json()

      const tipoUsuario = (session?.user?.tipo_usuario || session?.user?.role || '').toLowerCase()
      const userName = session?.user?.name || session?.user?.email

      console.log('🔐 [Login] tipo_usuario detectado:', tipoUsuario)
      console.log('🔐 [Login] role solicitado:', roleParam)

      // 3. VALIDACIÓN DE ROL: Si se solicitó un rol, verificar que coincida
      if (isValidRole && tipoUsuario !== roleParam.toLowerCase()) {
        const errorMsg = `No tienes permisos para acceder como ${displayRole}. Tu rol es: ${tipoUsuario}`
        toast.error(errorMsg)
        setLoginError(errorMsg)
        setIsLoading(false)
        return
      }

      // 4. Si hay un rol solicitado y es válido, guardarlo para redirección
      const targetRole = isValidRole ? roleParam.toLowerCase() : tipoUsuario

      // 5. Mapeo de roles a rutas del dashboard
      const roleMap: Record<string, string> = {
        super_admin: '/super-admin',
        admin: '/admin',
        admin_tenant: '/admin',
        admin_empresa: '/dashboard-empresa',
        admin_propietario: '/dashboard-propietario',
        propietario: '/dashboard-propietario',
        empleado: '/operativo',
        chofer: '/operativo',
      }

      // Determinar la ruta de redirección
      let redirectPath = '/'
      
      if (targetRole === 'admin' || targetRole === 'admin_tenant') {
        redirectPath = '/admin'
      } else {
        redirectPath = roleMap[targetRole] || '/'
      }

      console.log('🔄 [Login] Redirigiendo a:', redirectPath)

      toast.success(`Bienvenido de nuevo, ${userName || ''}`)

      // 6. Redirigir
      router.push(redirectPath)
      router.refresh()

    } catch (error) {
      console.error('❌ [Login] Error general:', error)
      toast.error('Error al iniciar sesión')
      setLoginError('Ocurrió un error inesperado')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-primary/10 rounded-full">
              <Car className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl">TaxIP 2.0</CardTitle>
          <CardDescription>
            Ingresa tus credenciales para acceder al dashboard
          </CardDescription>
          
          {/* Indicador de rol solicitado */}
          {isValidRole && displayRole && (
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 bg-yellow-50 border border-yellow-200 rounded-full text-sm text-yellow-700">
              <span className="text-xs font-medium uppercase tracking-wider">Accediendo como:</span>
              <span className="font-semibold">{displayRole}</span>
            </div>
          )}

          {!isValidRole && roleParam && (
            <div className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 bg-red-50 border border-red-200 rounded-full text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>Rol "{roleParam}" no válido</span>
            </div>
          )}
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {/* Mensaje de error de validación de rol */}
            {loginError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600 flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@taxip.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                disabled={isLoading}
              />
            </div>

            {/* Mensaje informativo sobre el rol solicitado */}
            {isValidRole && displayRole && (
              <div className="p-2 bg-blue-50 border border-blue-100 rounded-lg text-xs text-blue-600 text-center">
                Estás iniciando sesión como <strong>{displayRole}</strong>. 
                Tu cuenta debe tener este rol para continuar.
              </div>
            )}
          </CardContent>

          <CardFooter>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Ingresando...
                </>
              ) : (
                'Ingresar'
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}