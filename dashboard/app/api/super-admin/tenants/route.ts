import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// GET: Listar todos los Tenants
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

    const client = await pool.connect();
    try {
      const result = await client.query(`
        SELECT 
          c.id,
          c.nombre,
          c.email,
          c.telefono,
          c.activo,
          c.created_at,
          c.latitud,
          c.longitud,
          COALESCE((
            SELECT COUNT(*) FROM fleet.vehiculo v 
            WHERE v.control_base_id = c.id AND v.activo = true
          ), 0) as total_vehiculos,
          COALESCE((
            SELECT COUNT(*) FROM auth.usuario u 
            WHERE u.control_base_id = c.id 
            AND u.tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario')
          ), 0) as total_propietarios,
          COALESCE((
            SELECT COUNT(*) FROM tenant.empresa e 
            WHERE e.control_base_id = c.id
          ), 0) as total_empresas,
          COALESCE((
            SELECT SUM(total_a_pagar) FROM tenant.factura f 
            WHERE f.control_base_id = c.id AND f.estado = 'pendiente'
          ), 0) as deuda
        FROM tenant.control_base c
        ORDER BY c.created_at DESC
      `);

      return NextResponse.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error fetching tenants:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// POST: Crear un nuevo Tenant
export async function POST(request: NextRequest) {
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
    const { nombre, email, telefono, direccion, latitud, longitud } = body;

    if (!nombre || !email) {
      return NextResponse.json({ error: 'Nombre y email son requeridos' }, { status: 400 });
    }

    const client = await pool.connect();
    try {
      const result = await client.query(
        `INSERT INTO tenant.control_base (
          id, nombre, email, telefono, direccion, latitud, longitud, activo, created_at, updated_at
        ) VALUES (
          gen_random_uuid(), $1, $2, $3, $4, $5, $6, true, NOW(), NOW()
        ) RETURNING id, nombre, email, telefono, activo`,
        [nombre, email, telefono, direccion, latitud, longitud]
      );

      // Crear usuario Admin Tenant automáticamente
      const adminEmail = `admin@${email.split('@')[1] || 'tenant.com'}`;
      // Nota: En producción, deberías generar un hash de contraseña y enviarla por email
      const tempPassword = 'tenant123';
      
      await client.query(
        `INSERT INTO auth.usuario (
          id, email, password_hash, tipo_usuario_id, control_base_id, activo, created_at, updated_at
        ) VALUES (
          gen_random_uuid(), $1, $2, 
          (SELECT id FROM auth.tipo_usuario WHERE nombre = 'admin_tenant'), 
          $3, true, NOW(), NOW()
        )`,
        [adminEmail, `$2a$10$temp_hash_para_demo`, result.rows[0].id]
      );

      return NextResponse.json({
        success: true,
        tenant: result.rows[0],
        adminEmail,
        tempPassword
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error creating tenant:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}