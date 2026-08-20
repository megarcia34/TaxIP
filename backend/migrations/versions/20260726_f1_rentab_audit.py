"""rentabilidad y auditoria - fase 1

Revision ID: 20260726_f1_rentab_audit
Revises: c6bc69974304
Create Date: 2026-07-26 19:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260726_f1_rentab_audit'
down_revision = 'c6bc69974304'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Agregar 19 columnas a tenant.configuracion_tenant ──
    op.add_column('configuracion_tenant', sa.Column('canon_mensual_por_vehiculo', sa.Numeric(), server_default='10000', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('porcentaje_taxip_por_viaje', sa.Numeric(), server_default='1.5', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('iva', sa.Numeric(), server_default='21.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('iibb', sa.Numeric(), server_default='5.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('idc', sa.Numeric(), server_default='0.3', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('mix_efectivo', sa.Numeric(), server_default='40.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('mix_transferencia', sa.Numeric(), server_default='20.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('mix_qr', sa.Numeric(), server_default='25.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('mix_debito', sa.Numeric(), server_default='15.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('mix_credito', sa.Numeric(), server_default='0.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('comision_qr', sa.Numeric(), server_default='0.80', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('comision_debito', sa.Numeric(), server_default='1.00', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('comision_credito', sa.Numeric(), server_default='3.50', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('costo_combustible_por_km', sa.Numeric(), server_default='80.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('costo_mantenimiento_por_dia', sa.Numeric(), server_default='500.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('costo_seguro_por_dia', sa.Numeric(), server_default='300.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('costo_impuesto_por_dia', sa.Numeric(), server_default='200.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('depreciacion_vehiculo_por_dia', sa.Numeric(), server_default='400.0', nullable=True), schema='tenant')
    op.add_column('configuracion_tenant', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True), schema='tenant')

    # ── 2. Crear schemas ──
    op.execute("CREATE SCHEMA IF NOT EXISTS rentabilidad")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")

    # ── 3. Tabla rentabilidad.rentabilidad_diaria_vehiculo ──
    op.create_table(
        'rentabilidad_diaria_vehiculo',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('total_viajes', sa.Integer(), server_default='0', nullable=True),
        sa.Column('ingresos_brutos', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('comisiones_bancarias', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('costos_variables', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('costos_fijos', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('canon_taxip', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('porcentaje_taxip', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('utilidad_neta', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('margen', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        schema='rentabilidad'
    )
    op.create_index('idx_rentabilidad_vehiculo_fecha', 'rentabilidad_diaria_vehiculo', ['vehiculo_id', 'fecha'], schema='rentabilidad')
    op.create_index('idx_rentabilidad_fecha', 'rentabilidad_diaria_vehiculo', ['fecha'], schema='rentabilidad')

    # ── 4. Tabla rentabilidad.rentabilidad_mensual_vehiculo ──
    op.create_table(
        'rentabilidad_mensual_vehiculo',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('anio', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('total_viajes', sa.Integer(), server_default='0', nullable=True),
        sa.Column('ingresos_brutos', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('comisiones_bancarias', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('costos_variables', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('costos_fijos', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('canon_taxip', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('porcentaje_taxip', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('utilidad_neta', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('margen', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('vehiculo_id', 'anio', 'mes'),
        sa.CheckConstraint('mes BETWEEN 1 AND 12', name='chk_mes_rango'),
        schema='rentabilidad'
    )
    op.create_index('idx_rentabilidad_mensual_vehiculo', 'rentabilidad_mensual_vehiculo', ['vehiculo_id', 'anio', 'mes'], schema='rentabilidad')
    op.create_index('idx_rentabilidad_mensual_periodo', 'rentabilidad_mensual_vehiculo', ['anio', 'mes'], schema='rentabilidad')

    # ── 5. Tabla rentabilidad.analisis_medios_pago ──
    op.create_table(
        'analisis_medios_pago',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('anio', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('medio_pago', sa.String(20), nullable=False),
        sa.Column('total_viajes', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_ingresos', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('comision_aplicada', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('costo_comisiones', sa.Numeric(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        schema='rentabilidad'
    )
    op.create_index('idx_analisis_vehiculo_periodo', 'analisis_medios_pago', ['vehiculo_id', 'anio', 'mes'], schema='rentabilidad')
    op.create_index('idx_analisis_periodo', 'analisis_medios_pago', ['anio', 'mes'], schema='rentabilidad')

    # ── 6. Tabla audit.log_acciones ──
    op.create_table(
        'log_acciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('accion', sa.String(50), nullable=False),
        sa.Column('tabla_afectada', sa.String(100), nullable=True),
        sa.Column('registro_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('datos_anteriores', postgresql.JSONB(), nullable=True),
        sa.Column('datos_nuevos', postgresql.JSONB(), nullable=True),
        sa.Column('control_base_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['auth.usuario.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['control_base_id'], ['tenant.control_base.id']),
        schema='audit'
    )
    op.create_index('idx_log_acciones_usuario', 'log_acciones', ['usuario_id'], schema='audit')
    op.create_index('idx_log_acciones_tenant', 'log_acciones', ['control_base_id'], schema='audit')
    op.create_index('idx_log_acciones_created', 'log_acciones', ['created_at'], schema='audit')
    op.create_index('idx_log_acciones_accion', 'log_acciones', ['accion'], schema='audit')

    # ── 7. Función y triggers para updated_at ──
    op.execute("""
        CREATE OR REPLACE FUNCTION actualizar_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_rentabilidad_diaria_updated_at
            BEFORE UPDATE ON rentabilidad.rentabilidad_diaria_vehiculo
            FOR EACH ROW
            EXECUTE FUNCTION actualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_rentabilidad_mensual_updated_at
            BEFORE UPDATE ON rentabilidad.rentabilidad_mensual_vehiculo
            FOR EACH ROW
            EXECUTE FUNCTION actualizar_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER trigger_configuracion_tenant_updated_at
            BEFORE UPDATE ON tenant.configuracion_tenant
            FOR EACH ROW
            EXECUTE FUNCTION actualizar_updated_at();
    """)

    # ── 8. Comentarios en columnas de configuracion_tenant ──
    op.execute("""
        COMMENT ON COLUMN tenant.configuracion_tenant.canon_mensual_por_vehiculo IS 'Canon fijo mensual que paga el propietario al Tenant';
        COMMENT ON COLUMN tenant.configuracion_tenant.porcentaje_taxip_por_viaje IS '% que retiene TAXIP por viaje (marketing, premios, etc.)';
        COMMENT ON COLUMN tenant.configuracion_tenant.iva IS 'IVA sobre comisiones de procesadoras';
        COMMENT ON COLUMN tenant.configuracion_tenant.iibb IS 'Ingresos Brutos';
        COMMENT ON COLUMN tenant.configuracion_tenant.idc IS 'Impuesto Débitos y Créditos';
        COMMENT ON COLUMN tenant.configuracion_tenant.mix_efectivo IS '% de viajes en efectivo';
        COMMENT ON COLUMN tenant.configuracion_tenant.mix_transferencia IS '% de viajes por transferencia';
        COMMENT ON COLUMN tenant.configuracion_tenant.mix_qr IS '% de viajes por QR';
        COMMENT ON COLUMN tenant.configuracion_tenant.mix_debito IS '% de viajes por débito';
        COMMENT ON COLUMN tenant.configuracion_tenant.mix_credito IS '% de viajes por crédito';
        COMMENT ON COLUMN tenant.configuracion_tenant.comision_qr IS 'Comisión de procesadora QR (%)';
        COMMENT ON COLUMN tenant.configuracion_tenant.comision_debito IS 'Comisión de procesadora débito (%)';
        COMMENT ON COLUMN tenant.configuracion_tenant.comision_credito IS 'Comisión de procesadora crédito (%)';
        COMMENT ON COLUMN tenant.configuracion_tenant.costo_combustible_por_km IS 'Costo promedio de combustible por km';
        COMMENT ON COLUMN tenant.configuracion_tenant.costo_mantenimiento_por_dia IS 'Mantenimiento prorrateado por día';
        COMMENT ON COLUMN tenant.configuracion_tenant.costo_seguro_por_dia IS 'Seguro prorrateado por día';
        COMMENT ON COLUMN tenant.configuracion_tenant.costo_impuesto_por_dia IS 'Impuestos/patente por día';
        COMMENT ON COLUMN tenant.configuracion_tenant.depreciacion_vehiculo_por_dia IS 'Depreciación del vehículo por día';
    """)


def downgrade() -> None:
    # 1. Eliminar triggers y función
    op.execute("DROP TRIGGER IF EXISTS trigger_rentabilidad_diaria_updated_at ON rentabilidad.rentabilidad_diaria_vehiculo")
    op.execute("DROP TRIGGER IF EXISTS trigger_rentabilidad_mensual_updated_at ON rentabilidad.rentabilidad_mensual_vehiculo")
    op.execute("DROP TRIGGER IF EXISTS trigger_configuracion_tenant_updated_at ON tenant.configuracion_tenant")
    op.execute("DROP FUNCTION IF EXISTS actualizar_updated_at()")

    # 2. Eliminar tablas
    op.drop_table('log_acciones', schema='audit')
    op.drop_table('analisis_medios_pago', schema='rentabilidad')
    op.drop_table('rentabilidad_mensual_vehiculo', schema='rentabilidad')
    op.drop_table('rentabilidad_diaria_vehiculo', schema='rentabilidad')

    # 3. Eliminar schemas
    op.execute("DROP SCHEMA IF EXISTS rentabilidad CASCADE")
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE")

    # 4. Eliminar columnas de configuracion_tenant
    op.drop_column('configuracion_tenant', 'depreciacion_vehiculo_por_dia', schema='tenant')
    op.drop_column('configuracion_tenant', 'costo_impuesto_por_dia', schema='tenant')
    op.drop_column('configuracion_tenant', 'costo_seguro_por_dia', schema='tenant')
    op.drop_column('configuracion_tenant', 'costo_mantenimiento_por_dia', schema='tenant')
    op.drop_column('configuracion_tenant', 'costo_combustible_por_km', schema='tenant')
    op.drop_column('configuracion_tenant', 'comision_credito', schema='tenant')
    op.drop_column('configuracion_tenant', 'comision_debito', schema='tenant')
    op.drop_column('configuracion_tenant', 'comision_qr', schema='tenant')
    op.drop_column('configuracion_tenant', 'mix_credito', schema='tenant')
    op.drop_column('configuracion_tenant', 'mix_debito', schema='tenant')
    op.drop_column('configuracion_tenant', 'mix_qr', schema='tenant')
    op.drop_column('configuracion_tenant', 'mix_transferencia', schema='tenant')
    op.drop_column('configuracion_tenant', 'mix_efectivo', schema='tenant')
    op.drop_column('configuracion_tenant', 'idc', schema='tenant')
    op.drop_column('configuracion_tenant', 'iibb', schema='tenant')
    op.drop_column('configuracion_tenant', 'iva', schema='tenant')
    op.drop_column('configuracion_tenant', 'porcentaje_taxip_por_viaje', schema='tenant')
    op.drop_column('configuracion_tenant', 'canon_mensual_por_vehiculo', schema='tenant')
    op.drop_column('configuracion_tenant', 'updated_at', schema='tenant')