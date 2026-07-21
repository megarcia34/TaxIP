import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// GET: Obtener estadísticas avanzadas
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    const { searchParams } = new URL(request.url);
    const periodo = searchParams.get('periodo') || new Date().toISOString().slice(0, 7);

    const client = await pool.connect();
    try {
      // 1. Evolución mensual (últimos 12 meses)
      const evolucionResult = await client.query(`
        SELECT 
          TO_CHAR(periodo, 'YYYY-MM') as mes,
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'pagado'), 0) as pagado,
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'pendiente'), 0) as pendiente,
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'vencido'), 0) as vencido
        FROM tenant.factura
        WHERE periodo >= NOW() - INTERVAL '12 months'
        GROUP BY mes
        ORDER BY mes DESC
      `);

      // 2. Ranking de Tenants por ingresos (últimos 6 meses)
      const rankingResult = await client.query(`
        SELECT 
          c.nombre as tenant,
          COALESCE(SUM(f.total_a_pagar) FILTER (WHERE f.estado = 'pagado'), 0) as total_pagado,
          COALESCE(SUM(f.total_a_pagar) FILTER (WHERE f.estado = 'pendiente'), 0) as total_pendiente,
          COALESCE(SUM(f.total_a_pagar), 0) as total,
          COUNT(f.id) as total_facturas
        FROM tenant.control_base c
        LEFT JOIN tenant.factura f ON c.id = f.control_base_id
        WHERE f.periodo >= NOW() - INTERVAL '6 months'
        GROUP BY c.id, c.nombre
        ORDER BY total DESC
      `);

      // 3. Distribución de vehículos por Tenant
      const vehiculosResult = await client.query(`
        SELECT 
          c.nombre as tenant,
          COUNT(v.id) as total_vehiculos,
          COUNT(v.id) FILTER (WHERE v.activo = true) as vehiculos_activos,
          COUNT(v.id) FILTER (WHERE v.activo = false) as vehiculos_inactivos
        FROM tenant.control_base c
        LEFT JOIN fleet.vehiculo v ON c.id = v.control_base_id
        WHERE c.activo = true
        GROUP BY c.id, c.nombre
        ORDER BY total_vehiculos DESC
      `);

      // 4. Distribución de estado de facturas (último mes)
      const estadoFacturasResult = await client.query(`
        SELECT 
          estado,
          COUNT(*) as cantidad,
          COALESCE(SUM(total_a_pagar), 0) as total
        FROM tenant.factura
        WHERE TO_CHAR(periodo, 'YYYY-MM') = $1
        GROUP BY estado
      `, [periodo]);

      // 5. Top 5 Tenants con mayor deuda
      const deudaResult = await client.query(`
        SELECT 
          c.nombre as tenant,
          COALESCE(SUM(f.total_a_pagar), 0) as deuda,
          COALESCE(SUM(f.total_a_pagar) FILTER (WHERE f.estado = 'vencido'), 0) as deuda_vencida
        FROM tenant.control_base c
        LEFT JOIN tenant.factura f ON c.id = f.control_base_id
        WHERE f.estado IN ('pendiente', 'vencido')
        AND f.periodo >= NOW() - INTERVAL '6 months'
        GROUP BY c.id, c.nombre
        ORDER BY deuda DESC
        LIMIT 5
      `);

      // 6. Resumen general
      const resumenResult = await client.query(`
        SELECT
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'pagado'), 0) as total_pagado,
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'pendiente'), 0) as total_pendiente,
          COALESCE(SUM(total_a_pagar) FILTER (WHERE estado = 'vencido'), 0) as total_vencido,
          COUNT(*) FILTER (WHERE estado = 'pagado') as facturas_pagadas,
          COUNT(*) FILTER (WHERE estado = 'pendiente') as facturas_pendientes,
          COUNT(*) FILTER (WHERE estado = 'vencido') as facturas_vencidas
        FROM tenant.factura
        WHERE TO_CHAR(periodo, 'YYYY-MM') = $1
      `, [periodo]);

      return NextResponse.json({
        evolucion: evolucionResult.rows,
        ranking: rankingResult.rows,
        vehiculos: vehiculosResult.rows,
        estadoFacturas: estadoFacturasResult.rows,
        topDeuda: deudaResult.rows,
        resumen: resumenResult.rows[0] || {
          total_pagado: 0,
          total_pendiente: 0,
          total_vencido: 0,
          facturas_pagadas: 0,
          facturas_pendientes: 0,
          facturas_vencidas: 0,
        },
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error fetching estadisticas:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}