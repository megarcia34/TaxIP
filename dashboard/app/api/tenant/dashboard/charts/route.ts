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
      `WITH dias AS (
         SELECT generate_series(
           CURRENT_DATE - INTERVAL '6 days',
           CURRENT_DATE,
           INTERVAL '1 day'
         )::date AS dia
       )
       SELECT 
         dias.dia::text,
         COALESCE(COUNT(v.id), 0) as viajes,
         COALESCE(SUM(v.precio_final), 0) as facturado
       FROM dias
       LEFT JOIN trip.viaje_solicitado v 
         ON DATE(v.created_at) = dias.dia
         AND v.control_base_id = $1
         AND v.estado = 'completado'
       GROUP BY dias.dia
       ORDER BY dias.dia ASC`,
      [tenantId]
    )

    return NextResponse.json(
      result.rows.map(row => ({
        dia: row.dia,
        viajes: Number(row.viajes),
        facturado: Number(row.facturado),
      }))
    )
  } catch (error) {
    console.error('Error en dashboard/charts:', error)
    return NextResponse.json(
      { error: 'Error al obtener datos del gráfico' },
      { status: 500 }
    )
  }
}