import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Pool } from 'pg';

// Configurar conexión a PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function GET(request: NextRequest) {
  console.log('========================================');
  console.log('🔍 [Dashboard API] INICIO DE SOLICITUD');
  console.log('========================================');

  try {
    // 1. Obtener la sesión
    console.log('🔍 [Dashboard API] Obteniendo sesión...');
    const session = await getServerSession(authOptions);
    
    console.log('🔍 [Dashboard API] Session completa:', JSON.stringify(session, null, 2));

    // 2. Verificar autenticación
    if (!session) {
      console.log('❌ [Dashboard API] No hay sesión - 401');
      return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
    }

    console.log('✅ [Dashboard API] Sesión encontrada');

    // 3. Verificar el usuario
    const user = session.user as any;
    console.log('🔍 [Dashboard API] User object:', user);
    console.log('🔍 [Dashboard API] user.tipo_usuario:', user?.tipo_usuario);
    console.log('🔍 [Dashboard API] user.role:', user?.role);
    console.log('🔍 [Dashboard API] user.email:', user?.email);

    // 4. Verificar que sea Super Admin (con fallback a role)
    const tipoUsuario = user?.tipo_usuario || user?.role || '';
    console.log('🔍 [Dashboard API] tipoUsuario detectado (fallback):', tipoUsuario);

    if (tipoUsuario !== 'super_admin') {
      console.log(`❌ [Dashboard API] Acceso denegado. Esperado: super_admin, Recibido: ${tipoUsuario}`);
      return NextResponse.json({ 
        error: 'Acceso denegado', 
        detalle: `Se esperaba super_admin, se recibió: ${tipoUsuario}` 
      }, { status: 403 });
    }

    console.log('✅ [Dashboard API] Usuario autorizado como Super Admin');

    // 5. Obtener parámetros
    const { searchParams } = new URL(request.url);
    const periodo = searchParams.get('periodo') || new Date().toISOString().slice(0, 7);
    console.log('🔍 [Dashboard API] Periodo solicitado:', periodo);

    // 6. Conectar a la base de datos
    console.log('🔍 [Dashboard API] Conectando a PostgreSQL...');
    const client = await pool.connect();
    console.log('✅ [Dashboard API] Conectado a PostgreSQL');

    try {
      // 7. Consultas
      console.log('🔍 [Dashboard API] Ejecutando consultas...');

      // 7.1 Total Tenants activos
      const tenantsResult = await client.query(
        `SELECT COUNT(*) as total FROM tenant.control_base WHERE activo = true`
      );
      console.log('✅ [Dashboard API] Tenants:', tenantsResult.rows[0]?.total);

      // 7.2 Total Vehículos activos
      const vehiculosResult = await client.query(
        `SELECT COUNT(*) as total FROM fleet.vehiculo WHERE activo = true`
      );
      console.log('✅ [Dashboard API] Vehículos:', vehiculosResult.rows[0]?.total);

      // 7.3 Deuda Total
      const deudaResult = await client.query(
        `SELECT COALESCE(SUM(total_a_pagar), 0) as total 
         FROM tenant.factura 
         WHERE estado = 'pendiente'`
      );
      console.log('✅ [Dashboard API] Deuda:', deudaResult.rows[0]?.total);

      // 7.4 Ingresos del Mes
      const ingresosResult = await client.query(
        `SELECT COALESCE(SUM(total_a_pagar), 0) as total 
         FROM tenant.factura 
         WHERE estado = 'pagado' 
         AND TO_CHAR(periodo, 'YYYY-MM') = $1`,
        [periodo]
      );
      console.log('✅ [Dashboard API] Ingresos mes:', ingresosResult.rows[0]?.total);

      // 7.5 Facturas recientes
      const facturasResult = await client.query(
        `SELECT 
          f.id,
          f.numero_factura,
          c.nombre as tenant,
          f.total_a_pagar as total,
          f.estado,
          f.fecha_emision
        FROM tenant.factura f
        JOIN tenant.control_base c ON f.control_base_id = c.id
        ORDER BY f.created_at DESC
        LIMIT 5`
      );
      console.log('✅ [Dashboard API] Facturas recientes:', facturasResult.rowCount);

      // 7.6 Ingresos por Tenant
      const ingresosPorTenantResult = await client.query(
        `SELECT 
          c.nombre as tenant,
          COALESCE(SUM(f.total_a_pagar) FILTER (WHERE f.estado = 'pagado'), 0) as pagado,
          COALESCE(SUM(f.total_a_pagar) FILTER (WHERE f.estado = 'pendiente'), 0) as pendiente
        FROM tenant.control_base c
        LEFT JOIN tenant.factura f ON c.id = f.control_base_id
        WHERE c.activo = true
        GROUP BY c.id, c.nombre`
      );
      console.log('✅ [Dashboard API] Ingresos por tenant:', ingresosPorTenantResult.rowCount);

      // 7.7 Alertas
      const alertas: any[] = [];

      // Facturas vencidas
      const vencidasResult = await client.query(
        `SELECT 
          f.numero_factura,
          c.nombre as tenant,
          f.total_a_pagar
        FROM tenant.factura f
        JOIN tenant.control_base c ON f.control_base_id = c.id
        WHERE f.estado = 'pendiente' 
        AND f.fecha_vencimiento < NOW()`
      );

      if (vencidasResult.rows.length > 0) {
        const v = vencidasResult.rows[0];
        alertas.push({
          tipo: 'critica',
          mensaje: `${vencidasResult.rowCount} factura(s) vencida(s) - ${v.tenant} - ${formatCurrency(Number(v.total_a_pagar))}`,
          link: '/super-admin/facturacion'
        });
        console.log('⚠️ [Dashboard API] Alertas: Facturas vencidas encontradas');
      }

      // Tenants sin vehículos activos
      const tenantsSinVehiculos = await client.query(
        `SELECT c.nombre
        FROM tenant.control_base c
        LEFT JOIN fleet.vehiculo v ON c.id = v.control_base_id AND v.activo = true
        WHERE c.activo = true
        GROUP BY c.id
        HAVING COUNT(v.id) = 0`
      );

      if (tenantsSinVehiculos.rows.length > 0) {
        alertas.push({
          tipo: 'advertencia',
          mensaje: `${tenantsSinVehiculos.rows.length} Tenant(s) sin vehículos activos: ${tenantsSinVehiculos.rows.map(r => r.nombre).join(', ')}`,
          link: '/super-admin/tenants'
        });
        console.log('⚠️ [Dashboard API] Alertas: Tenants sin vehículos');
      }

      // 8. Construir respuesta
      const responseData = {
        totalTenants: Number(tenantsResult.rows[0]?.total) || 0,
        totalVehiculos: Number(vehiculosResult.rows[0]?.total) || 0,
        deudaTotal: Number(deudaResult.rows[0]?.total) || 0,
        ingresosMes: Number(ingresosResult.rows[0]?.total) || 0,
        facturasRecientes: facturasResult.rows.map((row: any) => ({
          id: row.id,
          numero_factura: row.numero_factura,
          tenant: row.tenant,
          total: Number(row.total),
          estado: row.estado,
          fecha_emision: row.fecha_emision,
        })),
        ingresosPorTenant: ingresosPorTenantResult.rows.map((row: any) => ({
          tenant: row.tenant,
          pagado: Number(row.pagado) || 0,
          pendiente: Number(row.pendiente) || 0,
        })),
        alertas,
      };

      console.log('✅ [Dashboard API] Respuesta generada exitosamente');
      console.log('========================================');
      return NextResponse.json(responseData);

    } finally {
      client.release();
      console.log('🔍 [Dashboard API] Conexión a PostgreSQL liberada');
    }

  } catch (error) {
    console.error('❌ [Dashboard API] Error:', error);
    console.log('========================================');
    return NextResponse.json({ 
      error: 'Error interno del servidor',
      detalle: error instanceof Error ? error.message : 'Error desconocido'
    }, { status: 500 });
  }
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}