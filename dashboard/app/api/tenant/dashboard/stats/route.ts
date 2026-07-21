import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { query } from '@/lib/db'

export async function GET() {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 })
    }

    const tenantId = session.user.control_base_id
    if (!tenantId) {
      return NextResponse.json({ error: 'Tenant no encontrado' }, { status: 400 })
    }

    // 1. Viajes de hoy (tabla en schema trip)
    const viajesHoy = await query(
      `SELECT COUNT(*) as count
       FROM trip.viaje_solicitado
       WHERE control_base_id = $1
         AND created_at >= CURRENT_DATE
         AND created_at < CURRENT_DATE + INTERVAL '1 day'`,
      [tenantId]
    )

    // 2. Choferes activos (tabla en schema fleet)
    const choferesActivos = await query(
      `SELECT COUNT(*) as count
       FROM fleet.chofer_vehiculo
       WHERE control_base_id = $1
         AND estado_laboral IN ('libre', 'ocupado')
         AND activo = true`,
      [tenantId]
    )

    // 3. Facturación de hoy (tabla en schema trip)
    const facturacionHoy = await query(
      `SELECT COALESCE(SUM(precio_final), 0) as total
       FROM trip.viaje_solicitado
       WHERE control_base_id = $1
         AND created_at >= CURRENT_DATE
         AND created_at < CURRENT_DATE + INTERVAL '1 day'
         AND estado = 'completado'`,
      [tenantId]
    )

    // 4. Calificación promedio (tabla en schema fleet)
    const calificacionPromedio = await query(
      `SELECT COALESCE(AVG(calificacion_promedio), 0) as avg
       FROM fleet.chofer_vehiculo
       WHERE control_base_id = $1
         AND activo = true`,
      [tenantId]
    )

    // 5. Vehículos activos (tabla en schema fleet)
    const vehiculosActivos = await query(
      `SELECT COUNT(*) as count
       FROM fleet.vehiculo
       WHERE control_base_id = $1
         AND activo = true`,
      [tenantId]
    )

    return NextResponse.json({
      viajesHoy: Number(viajesHoy.rows[0]?.count || 0),
      choferesActivos: Number(choferesActivos.rows[0]?.count || 0),
      facturacionHoy: Number(facturacionHoy.rows[0]?.total || 0),
      calificacionPromedio: Number(calificacionPromedio.rows[0]?.avg || 0).toFixed(1),
      vehiculosActivos: Number(vehiculosActivos.rows[0]?.count || 0),
    })
  } catch (error) {
    console.error('Error en dashboard/stats:', error)
    return NextResponse.json(
      { error: 'Error al obtener estadísticas' },
      { status: 500 }
    )
  }
}