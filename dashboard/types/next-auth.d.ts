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
    // ✅ NUEVO: control_base_id para Admin Tenant
    controlBaseId?: string | null
    control_base_id?: string | null
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
      // ✅ NUEVO: control_base_id para Admin Tenant
      controlBaseId?: string | null
      control_base_id?: string | null
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
    // ✅ NUEVO: control_base_id para Admin Tenant
    controlBaseId?: string | null
    control_base_id?: string | null
  }
}