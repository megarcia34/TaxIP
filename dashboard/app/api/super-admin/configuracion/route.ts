import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';
import bcrypt from 'bcryptjs';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// GET: Obtener configuración global y Super Admins
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
      // 1. Obtener configuración
      const configResult = await client.query(`
        SELECT 
          moneda_default,
          timezone,
          idioma,
          habilitar_fidelizacion,
          habilitar_pagos_online
        FROM tenant.configuracion_tenant
        LIMIT 1
      `);

      const config = {
        canon_por_vehiculo: 10000,
        porcentaje_plataforma: 15,
        dia_facturacion: 1,
        dias_vencimiento: 10,
        moneda_default: 'ARS',
        timezone: 'America/Argentina/Tucuman',
        idioma: 'es',
        habilitar_fidelizacion: false,
        habilitar_pagos_online: true,
      };

      if (configResult.rows.length > 0) {
        Object.assign(config, configResult.rows[0]);
      }

      // 2. Obtener lista de Super Admins
      const superAdminsResult = await client.query(`
        SELECT 
          u.id,
          u.email,
          u.activo,
          u.created_at,
          pg.nombre,
          pg.apellido
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general pg ON u.id = pg.usuario_id
        WHERE u.tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'super_admin')
        ORDER BY u.created_at DESC
      `);

      // 3. Identificar si el usuario actual es el MAESTRO (super@taxip.com)
      const isMaster = user.email === 'super@taxip.com';

      return NextResponse.json({
        config,
        superAdmins: superAdminsResult.rows,
        isMaster, // ← Flag para saber si puede crear
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error fetching config:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// POST: Crear nuevo Super Admin (SOLO MAESTRO)
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

    // 🔴 VERIFICACIÓN: Solo el MAESTRO puede crear Super Admins
    if (user.email !== 'super@taxip.com') {
      return NextResponse.json({ 
        error: 'No tienes permisos para crear Super Admins. Solo el usuario maestro puede hacerlo.' 
      }, { status: 403 });
    }

    const body = await request.json();
    const { email, action } = body;

    if (action !== 'crear_super_admin') {
      return NextResponse.json({ error: 'Acción no válida' }, { status: 400 });
    }

    if (!email) {
      return NextResponse.json({ error: 'Email requerido' }, { status: 400 });
    }

    const client = await pool.connect();
    try {
      // Verificar que el email no existe
      const checkResult = await client.query(
        'SELECT id FROM auth.usuario WHERE email = $1',
        [email]
      );
      if (checkResult.rows.length > 0) {
        return NextResponse.json({ error: 'El email ya está registrado' }, { status: 400 });
      }

      // Generar hash de la contraseña temporal
      const tempPassword = 'super123';
      const hashedPassword = await bcrypt.hash(tempPassword, 10);

      // Crear el usuario con tipo super_admin
      const result = await client.query(
        `INSERT INTO auth.usuario (
          id, email, password_hash, tipo_usuario_id, activo, created_at, updated_at
        ) VALUES (
          gen_random_uuid(), $1, $2, 
          (SELECT id FROM auth.tipo_usuario WHERE nombre = 'super_admin'),
          true, NOW(), NOW()
        ) RETURNING id, email`,
        [email, hashedPassword]
      );

      return NextResponse.json({
        success: true,
        user: result.rows[0],
        tempPassword,
        message: `Super Admin creado con éxito. Contraseña temporal: ${tempPassword}`,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error creating super admin:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}

// DELETE: Eliminar Super Admin (SOLO MAESTRO)
export async function DELETE(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    const user = session.user as any;
    if (user.tipo_usuario !== 'super_admin') {
      return NextResponse.json({ error: 'Acceso denegado' }, { status: 403 });
    }

    // 🔴 VERIFICACIÓN: Solo el MAESTRO puede eliminar Super Admins
    if (user.email !== 'super@taxip.com') {
      return NextResponse.json({ 
        error: 'No tienes permisos para eliminar Super Admins. Solo el usuario maestro puede hacerlo.' 
      }, { status: 403 });
    }

    const url = new URL(request.url);
    const id = url.searchParams.get('id');

    if (!id) {
      return NextResponse.json({ error: 'ID requerido' }, { status: 400 });
    }

    const client = await pool.connect();
    try {
      // Verificar que no sea el maestro
      const checkResult = await client.query(
        'SELECT email FROM auth.usuario WHERE id = $1',
        [id]
      );
      if (checkResult.rows.length === 0) {
        return NextResponse.json({ error: 'Usuario no encontrado' }, { status: 404 });
      }
      if (checkResult.rows[0].email === 'super@taxip.com') {
        return NextResponse.json({ error: 'No puedes eliminar al usuario maestro' }, { status: 400 });
      }

      await client.query(
        'DELETE FROM auth.usuario WHERE id = $1',
        [id]
      );

      return NextResponse.json({ success: true });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Error deleting super admin:', error);
    return NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 });
  }
}