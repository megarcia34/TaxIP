/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'via.placeholder.com'],
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  
  // ============================================
  // ✅ REWRITES ESPECÍFICOS - Proxy al backend FastAPI
  // EXCLUYE /api/auth/* (NextAuth) y /api/empresa/mi-empresa, /api/empresa/ubicacion
  // que ahora se llaman directo desde el frontend con URL absoluta
  // ============================================
  async rewrites() {
    return [
      // --- EMPRESA (excepto /mi-empresa y /ubicacion que van directo) ---
      {
        source: '/api/empresa/lista',
        destination: 'http://localhost:8000/api/empresa/lista',
      },
      {
        source: '/api/empresa/registro',
        destination: 'http://localhost:8000/api/empresa/registro',
      },
      {
        source: '/api/empresa/public/:path*',
        destination: 'http://localhost:8000/api/empresa/public/:path*',
      },
      {
        source: '/api/empresa/:empresa_id',
        destination: 'http://localhost:8000/api/empresa/:empresa_id',
      },
      {
        source: '/api/empresa/:empresa_id/empleados',
        destination: 'http://localhost:8000/api/empresa/:empresa_id/empleados',
      },
      {
        source: '/api/empresa/:empresa_id/viajes',
        destination: 'http://localhost:8000/api/empresa/:empresa_id/viajes',
      },
      {
        source: '/api/empresa/:empresa_id/estadisticas',
        destination: 'http://localhost:8000/api/empresa/:empresa_id/estadisticas',
      },
      {
        source: '/api/empresa/:empresa_id/facturas',
        destination: 'http://localhost:8000/api/empresa/:empresa_id/facturas',
      },
      
      // --- EMPRESA DASHBOARD ---
      {
        source: '/api/empresa/dashboard/:path*',
        destination: 'http://localhost:8000/api/empresa/dashboard/:path*',
      },
      
      // --- TURNOS ---
      {
        source: '/api/turnos/:path*',
        destination: 'http://localhost:8000/api/turnos/:path*',
      },
      
      // --- RESERVAS ---
      {
        source: '/api/reservas/:path*',
        destination: 'http://localhost:8000/api/reservas/:path*',
      },
      
      // --- CHOFERES ---
      {
        source: '/api/choferes/:path*',
        destination: 'http://localhost:8000/api/choferes/:path*',
      },
      
      // --- VEHÍCULOS ---
      {
        source: '/api/vehiculos/:path*',
        destination: 'http://localhost:8000/api/vehiculos/:path*',
      },
      {
        source: '/api/vehiculo/:path*',
        destination: 'http://localhost:8000/api/vehiculo/:path*',
      },
      
      // --- VIAJES ---
      {
        source: '/api/viajes/:path*',
        destination: 'http://localhost:8000/api/viajes/:path*',
      },
      
      // --- USUARIOS ---
      {
        source: '/api/usuarios/:path*',
        destination: 'http://localhost:8000/api/usuarios/:path*',
      },
      
      // --- PAGOS ---
      {
        source: '/api/pagos/:path*',
        destination: 'http://localhost:8000/api/pagos/:path*',
      },
      
      // --- PROPIETARIO ---
      {
        source: '/api/propietario/:path*',
        destination: 'http://localhost:8000/api/propietario/:path*',
      },
      
      // --- ADMIN ---
      {
        source: '/api/admin/:path*',
        destination: 'http://localhost:8000/api/admin/:path*',
      },
      
      // --- CONTROL BASE ---
      {
        source: '/api/control-base/:path*',
        destination: 'http://localhost:8000/api/control-base/:path*',
      },
      
      // --- AUTH (solo endpoints del backend, NO NextAuth) ---
      {
        source: '/api/auth/login',
        destination: 'http://localhost:8000/api/auth/login',
      },
      {
        source: '/api/auth/registro',
        destination: 'http://localhost:8000/api/auth/registro',
      },
      {
        source: '/api/auth/me',
        destination: 'http://localhost:8000/api/auth/me',
      },
      {
        source: '/api/auth/refresh',
        destination: 'http://localhost:8000/api/auth/refresh',
      },
    ]
  },
}

module.exports = nextConfig