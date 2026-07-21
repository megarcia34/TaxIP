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

    // Obtener turno activo
    const turno = await query(
      `SELECT 
         id,
         fecha_inicio,
         viajes_gestionados,
         facturado_total
       FROM auth.turno_empleado
       WHERE empleado_id = $1
         AND estado = 'ACTIVO'
       ORDER BY fecha_inicio DESC
       LIMIT 1`,
      [session.user.id]
    )

    // Si no hay turno activo, devolver datos vacíos
    if (turno.rows.length === 0) {
      return NextResponse.json({
        activo: false,
        mensaje: 'No hay turno activo'
      })
    }

    // KPIs del turno
    const kpis = await query(
      `SELECT 
         COUNT(*) as total_viajes,
         COUNT(CASE WHEN estado = 'completado' THEN 1 END) as completados,
         COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as cancelados,
         COALESCE(SUM(precio_final), 0) as total_facturado,
         COALESCE(AVG(precio_final), 0) as promedio_viaje
       FROM trip.viaje_solicitado
       WHERE control_base_id = $1
         AND created_at >= $2
         AND estado IN ('completado', 'cancelado')`,
      [tenantId, turno.rows[0].fecha_inicio]
    )

    // Viajes del turno
    const viajes = await query(
      `SELECT 
         id,
         nombre_pasajero as pasajero,
         direccion_origen as origen,
         direccion_destino as destino,
         estado,
         precio_final,
         created_at
       FROM trip.viaje_solicitado
       WHERE control_base_id = $1
         AND created_at >= $2
       ORDER BY created_at DESC
       LIMIT 20`,
      [tenantId, turno.rows[0].fecha_inicio]
    )

    return NextResponse.json({
      activo: true,
      turno: {
        id: turno.rows[0].id,
        fecha_inicio: turno.rows[0].fecha_inicio,
        viajes_gestionados: turno.rows[0].viajes_gestionados || 0,
        facturado_total: Number(turno.rows[0].facturado_total || 0),
      },
      kpis: {
        total_viajes: Number(kpis.rows[0]?.total_viajes || 0),
        completados: Number(kpis.rows[0]?.completados || 0),
        cancelados: Number(kpis.rows[0]?.cancelados || 0),
        total_facturado: Number(kpis.rows[0]?.total_facturado || 0),
        promedio_viaje: Number(kpis.rows[0]?.promedio_viaje || 0),
      },
      viajes: viajes.rows.map(row => ({
        id: row.id,
        pasajero: row.pasajero || 'N/A',
        origen: row.origen || 'N/A',
        destino: row.destino || 'N/A',
        estado: row.estado,
        precio: Number(row.precio_final || 0),
        created_at: row.created_at,
      })),
    })
  } catch (error) {
    console.error('Error en cierre-turno:', error)
    return NextResponse.json(
      { error: 'Error al obtener datos del turno' },
      { status: 500 }
    )
  }
}

export async function POST() {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 })
    }

    const tenantId = session.user.control_base_id
    if (!tenantId) {
      return NextResponse.json({ error: 'Tenant no encontrado' }, { status: 400 })
    }

    // Verificar turno activo
    const turno = await query(
      `SELECT id FROM auth.turno_empleado
       WHERE empleado_id = $1 AND estado = 'ACTIVO'
       ORDER BY fecha_inicio DESC LIMIT 1`,
      [session.user.id]
    )

    if (turno.rows.length === 0) {
      return NextResponse.json(
        { error: 'No hay turno activo para cerrar' },
        { status: 400 }
      )
    }

    // Cerrar turno
    await query(
      `UPDATE auth.turno_empleado
       SET estado = 'CERRADO', fecha_fin = NOW()
       WHERE id = $1`,
      [turno.rows[0].id]
    )

    return NextResponse.json({
      success: true,
      message: 'Turno cerrado correctamente'
    })
  } catch (error) {
    console.error('Error cerrando turno:', error)
    return NextResponse.json(
      { error: 'Error al cerrar turno' },
      { status: 500 }
    )
  }
}