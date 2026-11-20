import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============================================================
// FUNCIÓN AUXILIAR PARA REFRESCAR EL TOKEN
// ============================================================
async function refreshAccessToken(token: any) {
  try {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: token.refreshToken,
      }),
    })

    const refreshedTokens = await response.json()

    if (!response.ok) {
      throw refreshedTokens
    }

    return {
      ...token,
      accessToken: refreshedTokens.access_token,
      // Si el backend devuelve un nuevo refresh token, lo guardamos
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken,
      // Calculamos la nueva expiración (asumimos 30 minutos = 1800 segundos)
      accessTokenExpires: Date.now() + 30 * 60 * 1000,
    }
  } catch (error) {
    console.error('❌ Error refrescando token:', error)
    return {
      ...token,
      error: 'RefreshAccessTokenError',
    }
  }
}

// ============================================================
// CONFIGURACIÓN DE NEXTAUTH
// ============================================================
const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // ... (tu código de authorize igual)
        if (!credentials?.email || !credentials?.password) return null

        try {
          const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({
              email: credentials.email.trim(),
              password: credentials.password
            }),
          })

          const data = await response.json()

          if (!response.ok || !data.success || !data.access_token) return null

          const tipoUsuario = data.tipo || data.tipo_usuario || 'pasajero'
          const controlBaseId = data.control_base_id || null

          return {
            id: data.user_id,
            email: data.email,
            name: data.nombre_completo || data.email,
            role: tipoUsuario,
            tipo_usuario: tipoUsuario,
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            controlBaseId: controlBaseId,
            control_base_id: controlBaseId,
            // Guardamos cuándo expira (asumimos 30 min)
            accessTokenExpires: Date.now() + 30 * 60 * 1000,
          }
        } catch (error) {
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      // 1. Login inicial
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.role = user.role
        token.tipo_usuario = user.tipo_usuario
        token.accessToken = user.accessToken
        token.refreshToken = user.refreshToken
        token.controlBaseId = user.controlBaseId
        token.control_base_id = user.control_base_id
        token.accessTokenExpires = user.accessTokenExpires
        return token
      }

      // 2. Token aún válido
      if (Date.now() < (token.accessTokenExpires as number)) {
        return token
      }

      // 3. Token expirado -> Refrescar
      console.log('🔄 Token expirado, refrescando...')
      return refreshAccessToken(token)
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.email = token.email as string
        session.user.name = token.name as string
        session.user.role = token.role as string
        session.user.tipo_usuario = token.tipo_usuario as string
        session.user.accessToken = token.accessToken as string
        session.user.refreshToken = token.refreshToken as string
        session.user.controlBaseId = token.controlBaseId as string | null
        session.user.control_base_id = token.control_base_id as string | null
      }
      return session
    },
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
    maxAge: 7 * 24 * 60 * 60,
  },
  secret: process.env.NEXTAUTH_SECRET || 'secret-for-development',
})

export { handler as GET, handler as POST }