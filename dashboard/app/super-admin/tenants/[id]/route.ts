import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// GET: Obtener detalle de un Tenant específico
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    const { id } = params;

    if (!id) {
      return NextResponse.json({ error: 'ID de tenant requerido' }, { status: 400 });
    }

    const client = await pool.connect();
    try {
      // 1. Información general del Tenant
      const tenantResult = await client.query(
        `SELECT 
          id, nombre, email, telefono, direccion, latitud, longitud, 
          activo, created_at, updated_at,
          fecha_suspension, motivo_suspension
        FROM tenant.control_base
        WHERE id = $1`,
        [id]
      );

      if (tenantResult.rows.length === 0) {
        return NextResponse.json({ error: 'Tenant no encontrado' }, { status: 404 });
      }

      const tenant = tenantResult.rows[0];

      // 2. Estadísticas del Tenant
      const statsResult = await client.query(
        `SELECT
          COALESCE((SELECT COUNT(*) FROM fleet.vehiculo WHERE control_base_id = $1 AND activo = true), 0) as total_vehiculos,
          COALESCE((SELECT COUNT(*) FROM fleet.vehiculo WHERE control_base_id = $1 AND activo = false), 0) as vehiculos_inactivos,
          COALESCE((SELECT COUNT(*) FROM auth.usuario WHERE control_base_id = $1 AND tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario')), 0) as total_propietarios,
          COALESCE((SELECT COUNT(*) FROM tenant.empresa WHERE control_base_id = $1), 0) as total_empresas,
          COALESCE((SELECT COUNT(*) FROM auth.usuario WHERE control_base_id = $1 AND tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer')), 0) as total_choferes,
          COALESCE((SELECT COUNT(*) FROM trip.viaje_solicitado WHERE control_base_id = $1), 0) as total_viajes
        FROM tenant.control_base WHERE id = $1`,
        [id]
      );

      const stats = statsResult.rows[0];

      // 3. Vehículos del Tenant
      const vehiculosResult = await client.query(
        `SELECT 
          v.id, v.patente, v.marca, v.modelo, v.anio, v.activo, v.created_at,
          COALESCE(u.email, 'Sin chofer') as chofer_email,
          COALESCE(p.nombre, 'Sin propietario') as propietario_nombre
        FROM fleet.vehiculo v
        LEFT JOIN fleet.chofer_vehiculo cv ON v.id = cv.vehiculo_id
        LEFT JOIN auth.usuario u ON cv.usuario_id = u.id
        LEFT JOIN fleet.propietario_vehiculo pv ON v.id = pv.vehiculo_id AND pv.activo = true
        LEFT JOIN auth.usuario p ON pv.propietario_id = p.id
        WHERE v.control_base_id = $1
        ORDER BY v.created_at DESC
        LIMIT 10`,
        [id]
      );

      // 4. Empresas Corporativas del Tenant
      const empresasResult = await client.query(
        `SELECT 
          e.id, e.nombre, e.tipo, e.email_facturacion, e.telefono, e.activo,
          e.created_at,
          COALESCE((SELECT COUNT(*) FROM auth.usuario_empresa ue WHERE ue.empresa_id = e.id), 0) as total_empleados
        FROM tenant.empresa e
        WHERE e.control_base_id = $1
        ORDER BY e.created_at DESC
        LIMIT 10`,
        [id]
      );

      // 5. Propietarios del Tenant
      const propietariosResult = await client.query(
        `SELECT 
          u.id, u.email, u.activo, u.created_at,
          pg.nombre, pg.apellido, pg.telefono,
          COALESCE((SELECT COUNT(*) FROM fleet.propietario_vehiculo pv WHERE pv.propietario_id = u.id AND pv.activo = true), 0) as total_vehiculos
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general pg ON u.id = pg.usuario_id
        WHERE u.control_base_id = $1 
        AND u.tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario')
        ORDER BY u.created_at DESC
        LIMIT 10`,
        [id]
      );

      // 6. Finanzas del Tenant
      const finanzasResult = await client.query(
        `SELECT
          COALESCE((SELECT SUM(total_a_pagar) FROM tenant.factura WHERE control_base_id = $1 AND estado = 'pendiente'), 0) as deuda_pendiente,
          COALESCE((SELECT SUM(total_a_pagar) FROM tenant.factura WHERE control_base_id = $1 AND estado = 'pagado'), 0) as total_pagado,
          COALESCE((SELECT COUNT(*) FROM tenant.factura WHERE control_base_id = $1 AND estado = 'pendiente'), 0) as facturas_pendientes,
          COALESCE((SELECT COUNT(*) FROM tenant.factura WHERE control_base_id = $1 AND estado = 'pagado'), 0) as facturas_pagadas,
          COALESCE((SELECT COUNT(*) FROM tenant.factura WHERE control_base_id = $1 AND estado = 'pendiente' AND fecha_vencimiento < NOW()), 0) as facturas_vencidas
        FROM tenant.control_base WHERE id = $1`,
        [id]
      );

      const finanzas = finanzasResult.rows[0];

      // 7. Últimas facturas
      const facturasResult = await client.query(
        `SELECT 
          numero_factura, periodo, vehiculos_activos, canon_total, 
          porcentaje_plataforma, total_a_pagar, estado, fecha_emision, fecha_vencimiento
        FROM tenant.factura
        WHERE control_base_id = $1
        ORDER BY created_at DESC
        LIMIT 5`,
        [id]
      );

      return NextResponse.json({
        tenant,
        stats,
        vehiculos: vehiculosResult.rows,
        empresas: empresasResult.rows,
        propietarios: propietariosResult.rows,
        finanzas: finanzas,
        facturas: facturasResult.rows,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error fetching tenant detail:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// PUT: Actualizar un Tenant
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    const { id } = params;
    const body = await request.json();
    const { nombre, email, telefono, direccion, latitud, longitud, activo } = body;

    const client = await pool.connect();
    try {
      const result = await client.query(
        `UPDATE tenant.control_base 
        SET nombre = COALESCE($1, nombre),
            email = COALESCE($2, email),
            telefono = COALESCE($3, telefono),
            direccion = COALESCE($4, direccion),
            latitud = COALESCE($5, latitud),
            longitud = COALESCE($6, longitud),
            activo = COALESCE($7, activo),
            updated_at = NOW()
        WHERE id = $8
        RETURNING id, nombre, email, telefono, activo`,
        [nombre, email, telefono, direccion, latitud, longitud, activo, id]
      );

      if (result.rows.length === 0) {
        return NextResponse.json({ error: 'Tenant no encontrado' }, { status: 404 });
      }

      return NextResponse.json({
        success: true,
        tenant: result.rows[0],
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error updating tenant:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// DELETE: Eliminar un Tenant (o suspenderlo)
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    const { id } = params;
    const body = await request.json();
    const { action } = body; // 'suspend', 'activate', 'delete'

    const client = await pool.connect();
    try {
      let query = '';
      let params = [id];

      switch (action) {
        case 'suspend':
          query = `UPDATE tenant.control_base SET activo = false, fecha_suspension = NOW(), suspendido_por = $1 WHERE id = $2`;
          params = [user.id, id];
          break;
        case 'activate':
          query = `UPDATE tenant.control_base SET activo = true, fecha_suspension = NULL, suspendido_por = NULL WHERE id = $1`;
          break;
        case 'delete':
          query = `DELETE FROM tenant.control_base WHERE id = $1`;
          break;
        default:
          return NextResponse.json({ error: 'Acción no válida' }, { status: 400 });
      }

      await client.query(query, params);

      return NextResponse.json({ success: true });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error managing tenant:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}