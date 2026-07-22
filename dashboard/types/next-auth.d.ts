import 'next-auth'

declare module 'next-auth' {
  interface User {
    id: string
    email: string
    name: string
    role: string
    accessToken: string
    refreshToken: string
    totalVehiculos?: number
    vehiculos?: any[]
    empresaNombre?: string | null
    empresaId?: string | null
    image?: string | null
    controlBaseId?: string | null
    control_base_id?: string | null
    tipo_usuario?: string // ✅ AGREGADO: Para el Sidebar
  }

  interface Session {
    user: {
      id: string
      email: string
      name: string
      role: string
      accessToken: string
      refreshToken: string
      totalVehiculos?: number
      vehiculos?: any[]
      empresaNombre?: string | null
      empresaId?: string | null
      image?: string | null
      controlBaseId?: string | null
      control_base_id?: string | null
      tipo_usuario?: string // ✅ AGREGADO: Para el Sidebar
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string
    email: string
    name: string
    role: string
    accessToken: string
    refreshToken: string
    totalVehiculos?: number
    vehiculos?: any[]
    empresaNombre?: string | null
    empresaId?: string | null
    image?: string | null
    controlBaseId?: string | null
    control_base_id?: string | null
    tipo_usuario?: string // ✅ AGREGADO: Para el Sidebar
  }
}