
"""fase3_modelos_corporativos_manual

Revision ID: 3109ac9ef826
Revises: 605c45669a36
Create Date: 2026-08-24 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '3109ac9ef826'
down_revision: Union[str, Sequence[str], None] = '605c45669a36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FASE 3 - MODELOS CORPORATIVOS
    SOLO AGREGA - NO ELIMINA NADA
    """
    
    # ============================================================
    # 1. CREAR SCHEMA CORPORATE SI NO EXISTE
    # ============================================================
    
    op.execute("CREATE SCHEMA IF NOT EXISTS corporate")
    
    # ============================================================
    # 2. CREAR TABLA CUENTA_CORRIENTE
    # ============================================================
    
    op.create_table(
        'cuenta_corriente',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(as_uuid=True), nullable=False),
        sa.Column('saldo_actual', sa.DECIMAL(12, 2), server_default='0', nullable=False),
        sa.Column('saldo_disponible', sa.DECIMAL(12, 2), server_default='0', nullable=False),
        sa.Column('limite_credito', sa.DECIMAL(12, 2), server_default='0', nullable=False),
        sa.Column('moneda', sa.String(10), server_default='ARS', nullable=False),
        sa.Column('ultima_actualizacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['tenant.empresa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id'),
        schema='corporate'
    )
    
    # ============================================================
    # 3. CREAR TABLA MOVIMIENTO_CUENTA
    # ============================================================
    
    op.create_table(
        'movimiento_cuenta',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('cuenta_id', UUID(as_uuid=True), nullable=False),
        sa.Column('viaje_id', UUID(as_uuid=True), nullable=True),
        sa.Column('tipo_movimiento', sa.String(20), nullable=False),
        sa.Column('concepto', sa.String(200), nullable=False),
        sa.Column('monto', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('saldo_anterior', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('saldo_nuevo', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('referencia', sa.String(100), nullable=True),
        sa.Column('meta_data', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cuenta_id'], ['corporate.cuenta_corriente.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['viaje_id'], ['trip.viaje_solicitado.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='corporate'
    )
    
    # ============================================================
    # 4. CREAR TABLA FACTURA_CORPORATIVA
    # ============================================================
    
    op.create_table(
        'factura_corporativa',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(as_uuid=True), nullable=False),
        sa.Column('numero_factura', sa.String(50), nullable=False),
        sa.Column('periodo_desde', sa.Date(), nullable=False),
        sa.Column('periodo_hasta', sa.Date(), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True),
        sa.Column('subtotal', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('descuento', sa.DECIMAL(12, 2), server_default='0', nullable=False),
        sa.Column('iva', sa.DECIMAL(12, 2), server_default='0', nullable=False),
        sa.Column('total', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('estado', sa.String(20), server_default='pendiente', nullable=False),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['tenant.empresa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_factura'),
        schema='corporate'
    )
    
    # ============================================================
    # 5. CREAR TABLA PAGO_CORPORATIVO
    # ============================================================
    
    op.create_table(
        'pago_corporativo',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(as_uuid=True), nullable=False),
        sa.Column('factura_id', UUID(as_uuid=True), nullable=True),
        sa.Column('monto', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('metodo_pago', sa.String(50), nullable=False),
        sa.Column('referencia', sa.String(100), nullable=True),
        sa.Column('comprobante_url', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(20), server_default='pendiente', nullable=False),
        sa.Column('fecha_pago', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('confirmado_por', UUID(as_uuid=True), nullable=True),
        sa.Column('confirmado_en', sa.DateTime(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['tenant.empresa.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['factura_id'], ['corporate.factura_corporativa.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['confirmado_por'], ['auth.usuario.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='corporate'
    )
    
    # ============================================================
    # 6. CREAR ÍNDICES
    # ============================================================
    
    op.create_index('idx_cuenta_corriente_empresa', 'cuenta_corriente', ['empresa_id'], schema='corporate')
    op.create_index('idx_movimiento_cuenta_cuenta', 'movimiento_cuenta', ['cuenta_id'], schema='corporate')
    op.create_index('idx_movimiento_cuenta_fecha', 'movimiento_cuenta', ['created_at'], schema='corporate')
    op.create_index('idx_factura_corporativa_empresa', 'factura_corporativa', ['empresa_id'], schema='corporate')
    op.create_index('idx_factura_corporativa_estado', 'factura_corporativa', ['estado'], schema='corporate')
    op.create_index('idx_factura_corporativa_fecha', 'factura_corporativa', ['fecha_emision'], schema='corporate')
    op.create_index('idx_pago_corporativo_factura', 'pago_corporativo', ['factura_id'], schema='corporate')
    op.create_index('idx_pago_corporativo_fecha', 'pago_corporativo', ['fecha_pago'], schema='corporate')


def downgrade() -> None:
    """
    REVERTIR CAMBIOS DE LA FASE 3
    """
    
    # Eliminar índices
    op.drop_index('idx_pago_corporativo_fecha', table_name='pago_corporativo', schema='corporate')
    op.drop_index('idx_pago_corporativo_factura', table_name='pago_corporativo', schema='corporate')
    op.drop_index('idx_factura_corporativa_fecha', table_name='factura_corporativa', schema='corporate')
    op.drop_index('idx_factura_corporativa_estado', table_name='factura_corporativa', schema='corporate')
    op.drop_index('idx_factura_corporativa_empresa', table_name='factura_corporativa', schema='corporate')
    op.drop_index('idx_movimiento_cuenta_fecha', table_name='movimiento_cuenta', schema='corporate')
    op.drop_index('idx_movimiento_cuenta_cuenta', table_name='movimiento_cuenta', schema='corporate')
    op.drop_index('idx_cuenta_corriente_empresa', table_name='cuenta_corriente', schema='corporate')
    
    # Eliminar tablas
    op.drop_table('pago_corporativo', schema='corporate')
    op.drop_table('factura_corporativa', schema='corporate')
    op.drop_table('movimiento_cuenta', schema='corporate')
    op.drop_table('cuenta_corriente', schema='corporate')
    
    # Eliminar schema
    op.execute("DROP SCHEMA IF EXISTS corporate CASCADE")