"""M3-004: Extender corporate.* y auth.direccion_frecuente con campos faltantes

Revision ID: m3_004
Revises: m3_003
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_004'
down_revision = 'm3_003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # corporate.cuenta_corriente - solo los que NO existen
    CC = 'cuenta_corriente'
    for col, tipo, default in [
        ('titular_tipo', sa.String(20), None),
        ('estado', sa.String(20), 'activa'),
        ('periodo_facturacion', sa.String(20), 'mensual'),
        ('dia_cierre', sa.Integer, '1'),
        ('responsable_cobro', sa.String(20), None),
    ]:
        op.add_column(CC, sa.Column(col, tipo, server_default=default), schema='corporate')

    op.add_column(CC, sa.Column('titular_id', postgresql.UUID(as_uuid=True)), schema='corporate')
    op.add_column(CC, sa.Column('propietario_id', postgresql.UUID(as_uuid=True),
                                sa.ForeignKey('auth.usuario.id')), schema='corporate')
    op.add_column(CC, sa.Column('fecha_apertura', sa.DateTime, server_default=sa.func.now()), schema='corporate')
    op.add_column(CC, sa.Column('fecha_ultimo_pago', sa.DateTime), schema='corporate')
    op.add_column(CC, sa.Column('fecha_proximo_vencimiento', sa.DateTime), schema='corporate')

    op.create_check_constraint('ck_cc_estado', CC,
        "estado IN ('activa','suspendida','cerrada')", schema='corporate')

    # corporate.movimiento_cuenta - solo faltantes
    MC = 'movimiento_cuenta'
    op.add_column(MC, sa.Column('tipo', sa.String(20)), schema='corporate')
    op.add_column(MC, sa.Column('fecha_vencimiento', sa.DateTime), schema='corporate')
    op.add_column(MC, sa.Column('estado', sa.String(20), server_default='pendiente'), schema='corporate')
    op.add_column(MC, sa.Column('metodo_pago', sa.String(30)), schema='corporate')
    op.add_column(MC, sa.Column('referencia_pago', sa.String(120)), schema='corporate')
    op.add_column(MC, sa.Column('created_by', postgresql.UUID(as_uuid=True),
                                sa.ForeignKey('auth.usuario.id')), schema='corporate')

    op.create_check_constraint('ck_mc_estado', MC,
        "estado IS NULL OR estado IN ('pendiente','pagado','vencido','anulado')", schema='corporate')

    # corporate.factura_corporativa
    FC = 'factura_corporativa'
    for col in ['saldo_anterior','saldo_final','total_cargos','total_pagos']:
        op.add_column(FC, sa.Column(col, sa.Numeric(12,2), server_default='0'), schema='corporate')

    # corporate.pago_corporativo
    op.add_column('pago_corporativo',
        sa.Column('movimiento_cc_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('corporate.movimiento_cuenta.id')),
        schema='corporate')

    # auth.direccion_frecuente
    op.add_column('direccion_frecuente', sa.Column('telefono', sa.String(30)), schema='auth')
    op.add_column('direccion_frecuente', sa.Column('email', sa.String(120)), schema='auth')


def downgrade() -> None:
    op.drop_column('direccion_frecuente', 'email', schema='auth')
    op.drop_column('direccion_frecuente', 'telefono', schema='auth')
    op.drop_column('pago_corporativo', 'movimiento_cc_id', schema='corporate')
    for col in ['total_pagos','total_cargos','saldo_final','saldo_anterior']:
        op.drop_column('factura_corporativa', col, schema='corporate')
    op.drop_constraint('ck_mc_estado', 'movimiento_cuenta', schema='corporate')
    for col in ['created_by','referencia_pago','metodo_pago','estado','fecha_vencimiento','tipo']:
        op.drop_column('movimiento_cuenta', col, schema='corporate')
    op.drop_constraint('ck_cc_estado', 'cuenta_corriente', schema='corporate')
    for col in ['fecha_proximo_vencimiento','fecha_ultimo_pago','fecha_apertura','propietario_id','titular_id',
                'responsable_cobro','dia_cierre','periodo_facturacion','estado','titular_tipo']:
        op.drop_column('cuenta_corriente', col, schema='corporate')
