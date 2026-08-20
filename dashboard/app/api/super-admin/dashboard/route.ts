import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { Pool } from 'pg'

// Configurar conexión a PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

export async function GET(request: NextRequest) {
  console.log('========================================')
  console.log('🔍 [Dashboard API] INICIO DE SOLICITUD')
  console.log('========================================')

  try {
    // 1. Obtener la sesión
    console.log('🔍 [Dashboard API] Obteniendo sesión...')
    const session = await getServerSession(authOptions)
    console.log('🔍 [Dashboard API] Session:', session?.user?.email)

    if (!session) {
      console.log('❌ [Dashboard API] No hay sesión - 401')
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 })
    }

    // 2. Verificar que sea Super Admin
    const user = session.user as any
    const tipoUsuario = user?.tipo_usuario || user?.role || ''
    console.log('🔍 [Dashboard API] tipoUsuario:', tipoUsuario)

    if (tipoUsuario !== 'super_admin') {
      console.log(`❌ [Dashboard API] Acceso denegado. Recibido: ${tipoUsuario}`)
      return NextResponse.json({ 
        error: 'Acceso denegado', 
        detalle: `Se esperaba super_admin, se recibió: ${tipoUsuario}` 
      }, { status: 403 })
    }

    console.log('✅ [Dashboard API] Usuario autorizado como Super Admin')

    // 3. Obtener parámetros
    const { searchParams } = new URL(request.url)
    const periodo = searchParams.get('periodo') || 'mes'
    const fechaDesde = searchParams.get('fecha_desde')
    const fechaHasta = searchParams.get('fecha_hasta')

    console.log('🔍 [Dashboard API] Periodo:', periodo)
    console.log('🔍 [Dashboard API] Fechas:', { fechaDesde, fechaHasta })

    // 4. Conectar a la base de datos
    const client = await pool.connect()
    console.log('✅ [Dashboard API] Conectado a PostgreSQL')

    try {
      // ============================================
      // 1. RESUMEN GLOBAL
      // ============================================
      
      const resumenResult = await client.query(`
        SELECT 
          (SELECT COUNT(*) FROM tenant.control_base WHERE activo = true) as total_tenants,
          (SELECT COUNT(*) FROM fleet.vehiculo WHERE activo = true) as total_vehiculos,
          COALESCE((
            SELECT COUNT(*) 
            FROM trip.viaje_solicitado 
            WHERE estado = 'finalizado'
          ), 0) as total_viajes,
          COALESCE((
            SELECT COALESCE(SUM(precio_final), 0) 
            FROM trip.viaje_solicitado 
            WHERE estado = 'finalizado'
          ), 0) as total_recaudacion
      `)
      const resumen = resumenResult.rows[0]
      console.log('✅ [Dashboard API] Resumen global obtenido')

      // ============================================
      // 2. DESGLOSE POR TENANT
      // ============================================
      
      const tenantsResult = await client.query(`
        SELECT 
          cb.id as tenant_id,
          cb.nombre as tenant_nombre,
          COUNT(DISTINCT v.id) as total_vehiculos,
          COALESCE(COUNT(vs.id), 0) as total_viajes,
          COALESCE(SUM(vs.precio_final), 0) as total_recaudacion,
          COALESCE(AVG(vs.precio_final), 0) as promedio_por_viaje,
          COALESCE(SUM(g.monto), 0) as total_gastos
        FROM tenant.control_base cb
        LEFT JOIN fleet.vehiculo v ON v.control_base_id = cb.id AND v.activo = true
        LEFT JOIN trip.viaje_solicitado vs ON vs.control_base_id = cb.id 
          AND vs.estado = 'finalizado'
        LEFT JOIN fleet.gasto_vehiculo g ON g.vehiculo_id = v.id
        WHERE cb.activo = true
        GROUP BY cb.id, cb.nombre
        ORDER BY total_recaudacion DESC
      `)
      const tenants = tenantsResult.rows
      console.log(`✅ [Dashboard API] ${tenants.length} tenants procesados`)

      // ============================================
      // 3. MEDIOS DE PAGO
      // ============================================
      
      const mediosResult = await client.query(`
        SELECT 
          COALESCE(mp.nombre, 'efectivo') as medio_pago,
          COUNT(vs.id) as total_viajes,
          COALESCE(SUM(vs.precio_final), 0) as total_ingresos
        FROM trip.viaje_solicitado vs
        LEFT JOIN payment.transaccion t ON t.viaje_id = vs.id
        LEFT JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id
        WHERE vs.estado = 'finalizado'
        GROUP BY medio_pago
        ORDER BY total_ingresos DESC
      `)
      const medios = mediosResult.rows
      const totalIngresosMedios = medios.reduce((sum, m) => sum + Number(m.total_ingresos), 0)
      console.log(`✅ [Dashboard API] ${medios.length} medios de pago procesados`)

      // ============================================
      // 4. GASTOS OPERATIVOS
      // ============================================
      
      const gastosResult = await client.query(`
        SELECT 
          tipo_gasto,
          COALESCE(SUM(monto), 0) as total
        FROM fleet.gasto_vehiculo
        GROUP BY tipo_gasto
        ORDER BY total DESC
      `)
      const gastos = gastosResult.rows
      console.log(`✅ [Dashboard API] ${gastos.length} tipos de gasto procesados`)

      // ============================================
      // 5. EVOLUCIÓN MENSUAL (últimos 6 meses)
      // ============================================
      
      const evolucionResult = await client.query(`
        SELECT 
          TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') as mes,
          COUNT(*) as total_viajes,
          COALESCE(SUM(precio_final), 0) as total_recaudacion
        FROM trip.viaje_solicitado
        WHERE estado = 'finalizado'
          AND created_at >= NOW() - INTERVAL '6 months'
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY mes ASC
      `)
      const evolucion = evolucionResult.rows
      console.log(`✅ [Dashboard API] ${evolucion.length} meses de evolución`)

      // ============================================
      // 6. CONSTRUIR RESPUESTA
      // ============================================

      const responseData = {
        totalTenants: Number(resumen.total_tenants) || 0,
        totalVehiculos: Number(resumen.total_vehiculos) || 0,
        totalViajes: Number(resumen.total_viajes) || 0,
        totalRecaudacion: Number(resumen.total_recaudacion) || 0,
        tenants: tenants.map((t: any) => ({
          tenant_id: t.tenant_id,
          tenant_nombre: t.tenant_nombre,
          total_vehiculos: Number(t.total_vehiculos) || 0,
          total_viajes: Number(t.total_viajes) || 0,
          total_recaudacion: Number(t.total_recaudacion) || 0,
          promedio_por_viaje: Number(t.promedio_por_viaje) || 0,
          total_gastos: Number(t.total_gastos) || 0,
          utilidad_neta: Number(t.total_recaudacion) - Number(t.total_gastos),
          margen: Number(t.total_recaudacion) > 0 
            ? ((Number(t.total_recaudacion) - Number(t.total_gastos)) / Number(t.total_recaudacion)) * 100 
            : 0
        })),
        mediosPago: medios.map((m: any) => ({
          medio_pago: m.medio_pago,
          total_viajes: Number(m.total_viajes) || 0,
          total_ingresos: Number(m.total_ingresos) || 0,
          porcentaje: totalIngresosMedios > 0 
            ? (Number(m.total_ingresos) / totalIngresosMedios) * 100 
            : 0
        })),
        gastosOperativos: gastos.map((g: any) => ({
          tipo_gasto: g.tipo_gasto || 'otros',
          total: Number(g.total) || 0
        })),
        evolucionMensual: evolucion.map((e: any) => ({
          mes: e.mes,
          total_viajes: Number(e.total_viajes) || 0,
          total_recaudacion: Number(e.total_recaudacion) || 0
        })),
        periodo: {
          tipo: periodo,
          desde: fechaDesde || 'N/A',
          hasta: fechaHasta || 'N/A'
        }
      }

      console.log('✅ [Dashboard API] Respuesta generada exitosamente')
      console.log('========================================')
      return NextResponse.json(responseData)

    } finally {
      client.release()
      console.log('🔍 [Dashboard API] Conexión a PostgreSQL liberada')
    }

  } catch (error) {
    console.error('❌ [Dashboard API] Error:', error)
    console.log('========================================')
    return NextResponse.json({ 
      error: 'Error interno del servidor',
      detalle: error instanceof Error ? error.message : 'Error desconocido'
    }, { status: 500 })
  }
}