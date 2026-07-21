import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// GET: Listar facturas con filtros
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
    const tenantId = searchParams.get('tenant');
    const estado = searchParams.get('estado');
    const periodo = searchParams.get('periodo');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');

    const client = await pool.connect();
    try {
      let query = `
        SELECT 
          f.id,
          f.numero_factura,
          f.periodo,
          f.vehiculos_activos,
          f.canon_total,
          f.porcentaje_plataforma,
          f.total_a_pagar,
          f.estado,
          f.fecha_emision,
          f.fecha_vencimiento,
          f.pagada_at,
          c.nombre as tenant_nombre,
          c.id as tenant_id
        FROM tenant.factura f
        JOIN tenant.control_base c ON f.control_base_id = c.id
        WHERE 1=1
      `;

      const params: any[] = [];
      let paramIndex = 1;

      if (tenantId) {
        query += ` AND f.control_base_id = $${paramIndex}`;
        params.push(tenantId);
        paramIndex++;
      }

      if (estado) {
        query += ` AND f.estado = $${paramIndex}`;
        params.push(estado);
        paramIndex++;
      }

      if (periodo) {
        query += ` AND TO_CHAR(f.periodo, 'YYYY-MM') = $${paramIndex}`;
        params.push(periodo);
        paramIndex++;
      }

      query += ` ORDER BY f.created_at DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
      params.push(limit, offset);

      const result = await client.query(query, params);

      // Total de registros para paginación
      let countQuery = `
        SELECT COUNT(*) as total
        FROM tenant.factura f
        JOIN tenant.control_base c ON f.control_base_id = c.id
        WHERE 1=1
      `;

      const countParams: any[] = [];
      let countIndex = 1;

      if (tenantId) {
        countQuery += ` AND f.control_base_id = $${countIndex}`;
        countParams.push(tenantId);
        countIndex++;
      }

      if (estado) {
        countQuery += ` AND f.estado = $${countIndex}`;
        countParams.push(estado);
        countIndex++;
      }

      if (periodo) {
        countQuery += ` AND TO_CHAR(f.periodo, 'YYYY-MM') = $${countIndex}`;
        countParams.push(periodo);
        countIndex++;
      }

      const countResult = await client.query(countQuery, countParams);
      const total = parseInt(countResult.rows[0]?.total) || 0;

      return NextResponse.json({
        facturas: result.rows,
        total,
        limit,
        offset,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error fetching facturas:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// PUT: Actualizar estado de una factura (pagar)
export async function PUT(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    const body = await request.json();
    const { facturaId, action } = body; // action: 'pagar' | 'anular'

    if (!facturaId) {
      return NextResponse.json({ error: 'ID de factura requerido' }, { status: 400 });
    }

    const client = await pool.connect();
    try {
      if (action === 'pagar') {
        await client.query(
          `UPDATE tenant.factura 
           SET estado = 'pagado', pagada_at = NOW(), pagada_por = $1
           WHERE id = $2 AND estado = 'pendiente'`,
          [user.id, facturaId]
        );
      } else if (action === 'anular') {
        await client.query(
          `UPDATE tenant.factura 
           SET estado = 'anulado'
           WHERE id = $1 AND estado = 'pendiente'`,
          [facturaId]
        );
      } else {
        return NextResponse.json({ error: 'Acción no válida' }, { status: 400 });
      }

      return NextResponse.json({ success: true });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error updating factura:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}