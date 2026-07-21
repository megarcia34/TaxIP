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
         f.id,
         e.nombre as empresa_nombre,
         f.periodo,
         f.total,
         f.descuento,
         f.total_final,
         f.estado,
         f.created_at,
         f.pagada_at,
         CASE 
           WHEN f.estado = 'pendiente' AND f.created_at < NOW() - INTERVAL '30 days' 
           THEN 'vencida'
           WHEN f.estado = 'pendiente' AND f.created_at < NOW() - INTERVAL '15 days'
           THEN 'proximo_vencimiento'
           WHEN f.estado = 'pagada'
           THEN 'pagada'
           ELSE 'al_dia'
         END as estado_deuda
       FROM payment.factura_empresa f
       JOIN tenant.empresa e ON f.empresa_id = e.id
       WHERE e.control_base_id = $1
       ORDER BY f.estado = 'pendiente' DESC, f.created_at DESC`,
      [tenantId]
    )

    return NextResponse.json(
      result.rows.map(row => ({
        id: row.id,
        empresa_nombre: row.empresa_nombre,
        periodo: row.periodo,
        total: Number(row.total),
        descuento: Number(row.descuento || 0),
        total_final: Number(row.total_final),
        estado: row.estado,
        created_at: row.created_at,
        pagada_at: row.pagada_at,
        estado_deuda: row.estado_deuda,
      }))
    )
  } catch (error) {
    console.error('Error en facturacion:', error)
    return NextResponse.json(
      { error: 'Error al obtener facturas' },
      { status: 500 }
    )
  }
}

export async function PUT(request: Request) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 })
    }

    const tenantId = session.user.control_base_id
    if (!tenantId) {
      return NextResponse.json({ error: 'Tenant no encontrado' }, { status: 400 })
    }

    const body = await request.json()
    const { factura_id, estado } = body

    if (!factura_id || !estado) {
      return NextResponse.json(
        { error: 'factura_id y estado son requeridos' },
        { status: 400 }
      )
    }

    // Verificar que la factura pertenece al tenant
    const check = await query(
      `SELECT f.id 
       FROM payment.factura_empresa f
       JOIN tenant.empresa e ON f.empresa_id = e.id
       WHERE f.id = $1 AND e.control_base_id = $2`,
      [factura_id, tenantId]
    )

    if (check.rows.length === 0) {
      return NextResponse.json(
        { error: 'Factura no encontrada' },
        { status: 404 }
      )
    }

    const updateQuery = estado === 'pagada'
      ? `UPDATE payment.factura_empresa 
         SET estado = $1, pagada_at = NOW() 
         WHERE id = $2`
      : `UPDATE payment.factura_empresa 
         SET estado = $1, pagada_at = NULL 
         WHERE id = $2`

    await query(updateQuery, [estado, factura_id])

    return NextResponse.json({
      success: true,
      message: `Factura ${estado === 'pagada' ? 'pagada' : 'actualizada'} correctamente`
    })
  } catch (error) {
    console.error('Error actualizando factura:', error)
    return NextResponse.json(
      { error: 'Error al actualizar factura' },
      { status: 500 }
    )
  }
}