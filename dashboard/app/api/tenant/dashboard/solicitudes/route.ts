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

    const result = await query(
      `SELECT 
         v.id,
         COALESCE(v.nombre_pasajero, 'Pasajero') as pasajero,
         v.direccion_origen as origen,
         v.direccion_destino as destino,
         v.estado,
         EXTRACT(EPOCH FROM (NOW() - v.created_at)) / 3600 as horas_espera,
         TO_CHAR(v.created_at, 'DD/MM/YYYY HH24:MI') as creado_en
       FROM trip.viaje_solicitado v
       WHERE v.control_base_id = $1
         AND v.estado NOT IN ('completado', 'cancelado')
       ORDER BY v.created_at ASC
       LIMIT 10`,
      [tenantId]
    )

    return NextResponse.json(
      result.rows.map(row => ({
        id: row.id,
        pasajero: row.pasajero,
        origen: row.origen || 'Sin origen',
        destino: row.destino || 'Sin destino',
        estado: row.estado || 'pendiente',
        horasEspera: Math.round(row.horas_espera || 0),
        creadoEn: row.creado_en,
      }))
    )
  } catch (error) {
    console.error('Error en dashboard/solicitudes:', error)
    return NextResponse.json(
      { error: 'Error al obtener solicitudes' },
      { status: 500 }
    )
  }
}