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

    const alertas = []

    // 1. Choferes sin vehículo asignado
    const sinVehiculo = await query(
      `SELECT COUNT(*) as count
       FROM fleet.chofer_vehiculo
       WHERE control_base_id = $1
         AND vehiculo_id IS NULL
         AND activo = true`,
      [tenantId]
    )

    if (Number(sinVehiculo.rows[0]?.count || 0) > 0) {
      alertas.push({
        id: 'choferes-sin-vehiculo',
        tipo: 'warning',
        titulo: 'Choferes sin vehículo',
        descripcion: `${sinVehiculo.rows[0].count} choferes activos no tienen vehículo asignado`,
        accion: { texto: 'Asignar vehículos', url: '/choferes' },
      })
    }

    // 2. Vehículos sin chofer
    const sinChofer = await query(
      `SELECT COUNT(*) as count
       FROM fleet.vehiculo
       WHERE control_base_id = $1
         AND activo = true
         AND id NOT IN (
           SELECT vehiculo_id FROM fleet.chofer_vehiculo 
           WHERE control_base_id = $1 AND activo = true AND vehiculo_id IS NOT NULL
         )`,
      [tenantId]
    )

    if (Number(sinChofer.rows[0]?.count || 0) > 0) {
      alertas.push({
        id: 'vehiculos-sin-chofer',
        tipo: 'warning',
        titulo: 'Vehículos sin chofer',
        descripcion: `${sinChofer.rows[0].count} vehículos activos no tienen chofer asignado`,
        accion: { texto: 'Asignar choferes', url: '/vehiculos' },
      })
    }

    // 3. Facturas vencidas (si hay empresas)
    const facturasVencidas = await query(
      `SELECT COUNT(*) as count
       FROM payment.factura_empresa
       WHERE empresa_id IN (
         SELECT id FROM tenant.empresa WHERE control_base_id = $1 AND activo = true
       )
         AND estado = 'pendiente'
         AND created_at < NOW() - INTERVAL '30 days'`,
      [tenantId]
    )

    if (Number(facturasVencidas.rows[0]?.count || 0) > 0) {
      alertas.push({
        id: 'facturas-vencidas',
        tipo: 'danger',
        titulo: 'Facturas vencidas',
        descripcion: `${facturasVencidas.rows[0].count} facturas tienen más de 30 días sin pagar`,
        accion: { texto: 'Ver facturas', url: '/admin/facturacion' },
      })
    }

    // 4. Empresas con límite de crédito excedido
    const creditoExcedido = await query(
      `SELECT COUNT(*) as count
       FROM tenant.empresa
       WHERE control_base_id = $1
         AND activo = true
         AND limite_credito > 0
         AND (
           SELECT COALESCE(SUM(total_final), 0) 
           FROM payment.factura_empresa 
           WHERE empresa_id = tenant.empresa.id 
             AND estado = 'pendiente'
         ) > limite_credito`,
      [tenantId]
    )

    if (Number(creditoExcedido.rows[0]?.count || 0) > 0) {
      alertas.push({
        id: 'credito-excedido',
        tipo: 'danger',
        titulo: 'Empresas con crédito excedido',
        descripcion: `${creditoExcedido.rows[0].count} empresas han superado su límite de crédito`,
        accion: { texto: 'Ver empresas', url: '/admin/empresas' },
      })
    }

    // 5. Choferes con baja calificación (menos de 3.0)
    const bajaCalificacion = await query(
      `SELECT 
         u.id,
         COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre,
         cv.calificacion_promedio
       FROM fleet.chofer_vehiculo cv
       JOIN auth.usuario u ON u.id = cv.usuario_id
       LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
       WHERE cv.control_base_id = $1
         AND cv.activo = true
         AND cv.calificacion_promedio < 3.0
         AND cv.total_calificaciones > 3
       LIMIT 5`,
      [tenantId]
    )

    if (bajaCalificacion.rows.length > 0) {
      const nombres = bajaCalificacion.rows.map(r => r.nombre).join(', ')
      alertas.push({
        id: 'baja-calificacion',
        tipo: 'warning',
        titulo: 'Choferes con baja calificación',
        descripcion: `${bajaCalificacion.rows.length} choferes tienen calificación menor a 3.0: ${nombres}`,
        accion: { texto: 'Ver choferes', url: '/choferes' },
      })
    }

    return NextResponse.json(alertas)
  } catch (error) {
    console.error('Error en dashboard/alertas:', error)
    return NextResponse.json(
      { error: 'Error al obtener alertas' },
      { status: 500 }
    )
  }
}