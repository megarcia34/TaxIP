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
         u.id,
         COALESCE(pg.nombre, 'Sin nombre') as nombre,
         COALESCE(pg.apellido, '') as apellido,
         cv.calificacion_promedio as calificacion,
         cv.total_viajes,
         cv.estado_laboral,
         pg.foto_perfil_url
       FROM fleet.chofer_vehiculo cv
       JOIN auth.usuario u ON cv.usuario_id = u.id
       LEFT JOIN auth.perfil_general pg ON u.id = pg.usuario_id
       WHERE cv.control_base_id = $1
         AND cv.activo = true
         AND cv.total_viajes > 0
       ORDER BY cv.calificacion_promedio DESC, cv.total_viajes DESC
       LIMIT 10`,
      [tenantId]
    )

    return NextResponse.json(
      result.rows.map(row => ({
        id: row.id,
        nombre: row.nombre,
        apellido: row.apellido,
        calificacion: Number(row.calificacion),
        total_viajes: Number(row.total_viajes),
        estado_laboral: row.estado_laboral || 'inactivo',
        foto_perfil_url: row.foto_perfil_url || null,
      }))
    )
  } catch (error) {
    console.error('Error en dashboard/ranking:', error)
    return NextResponse.json(
      { error: 'Error al obtener ranking' },
      { status: 500 }
    )
  }
}