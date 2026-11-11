/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost', 'via.placeholder.com'],
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  
  // ✅ NUEVO: Inyectar la API Key de Google Maps en el bundle del cliente
  env: {
    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
  },
  
  async rewrites() {
    // ✅ USAR LA URL INTERNA DEL BACKEND EN DOCKER
    const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000'
    
    return [
      // ✅ NUEVO: RUTAS DEL ADMIN TENANT (Dashboard del municipio)
      { source: '/admin/tenant/:path*', destination: `${BACKEND_URL}/api/admin/tenant/:path*` },
      
      // --- EMPRESA ---
      { source: '/api/empresa/lista', destination: `${BACKEND_URL}/api/empresa/lista` },
      { source: '/api/empresa/registro', destination: `${BACKEND_URL}/api/empresa/registro` },
      { source: '/api/empresa/public/:path*', destination: `${BACKEND_URL}/api/empresa/public/:path*` },
      { source: '/api/empresa/:empresa_id', destination: `${BACKEND_URL}/api/empresa/:empresa_id` },
      { source: '/api/empresa/:empresa_id/empleados', destination: `${BACKEND_URL}/api/empresa/:empresa_id/empleados` },
      { source: '/api/empresa/:empresa_id/viajes', destination: `${BACKEND_URL}/api/empresa/:empresa_id/viajes` },
      { source: '/api/empresa/:empresa_id/estadisticas', destination: `${BACKEND_URL}/api/empresa/:empresa_id/estadisticas` },
      { source: '/api/empresa/:empresa_id/facturas', destination: `${BACKEND_URL}/api/empresa/:empresa_id/facturas` },
      
      // --- EMPRESA DASHBOARD ---
      { source: '/api/empresa/dashboard/:path*', destination: `${BACKEND_URL}/api/empresa/dashboard/:path*` },
      
      // --- TURNOS ---
      { source: '/api/turnos/:path*', destination: `${BACKEND_URL}/api/turnos/:path*` },
      
      // --- RESERVAS ---
      { source: '/api/reservas/:path*', destination: `${BACKEND_URL}/api/reservas/:path*` },
      
      // --- CHOFERES ---
      { source: '/api/choferes/:path*', destination: `${BACKEND_URL}/api/choferes/:path*` },
      
      // --- VEHÍCULOS ---
      { source: '/api/vehiculos/:path*', destination: `${BACKEND_URL}/api/vehiculos/:path*` },
      { source: '/api/vehiculo/:path*', destination: `${BACKEND_URL}/api/vehiculo/:path*` },
      
      // --- VIAJES ---
      { source: '/api/viajes/:path*', destination: `${BACKEND_URL}/api/viajes/:path*` },
      
      // --- USUARIOS ---
      { source: '/api/usuarios/:path*', destination: `${BACKEND_URL}/api/usuarios/:path*` },
      
      // --- PAGOS ---
      { source: '/api/pagos/:path*', destination: `${BACKEND_URL}/api/pagos/:path*` },
      
      // --- PROPIETARIO ---
      { source: '/api/propietario/:path*', destination: `${BACKEND_URL}/api/propietario/:path*` },
      
      // --- ADMIN ---
      { source: '/api/admin/:path*', destination: `${BACKEND_URL}/api/admin/:path*` },
      
      // --- CONTROL BASE ---
      { source: '/api/control-base/:path*', destination: `${BACKEND_URL}/api/control-base/:path*` },
      
      // --- AUTH (solo endpoints del backend, NO NextAuth) ---
      { source: '/api/auth/login', destination: `${BACKEND_URL}/api/auth/login` },
      { source: '/api/auth/registro', destination: `${BACKEND_URL}/api/auth/registro` },
      { source: '/api/auth/me', destination: `${BACKEND_URL}/api/auth/me` },
      { source: '/api/auth/refresh', destination: `${BACKEND_URL}/api/auth/refresh` },
      
      // --- GEO ---
      { source: '/api/geo/:path*', destination: `${BACKEND_URL}/api/geo/:path*` },
    ]
  },
}

module.exports = nextConfig