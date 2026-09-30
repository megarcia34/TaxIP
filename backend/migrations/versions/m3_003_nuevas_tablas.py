"""M3-003: trip.broadcast_log, payment.qr_cobro, payment.configuracion_pasarela, auth.plantilla_viaje

Revision ID: m3_003
Revises: m3_002
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_003'
down_revision = 'm3_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # trip.broadcast_log
    op.create_table('broadcast_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trip.viaje_solicitado.id'), nullable=False),
        sa.Column('chofer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.usuario.id'), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fleet.vehiculo.id')),
        sa.Column('distancia_metros', sa.Integer),
        sa.Column('emitido_en', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('respondido_en', sa.DateTime),
        sa.Column('respuesta', sa.String(20)),
        sa.Column('motivo_exclusion', sa.String(60)),
        sa.Column('tiempo_respuesta_segundos', sa.Integer),
        sa.Column('control_base_id', postgresql.UUID(as_uuid=True), nullable=False),
        schema='trip')
    op.create_index('ix_bcl_viaje', 'broadcast_log', ['viaje_id'], schema='trip')
    op.create_index('ix_bcl_chofer_fecha', 'broadcast_log', ['chofer_id','emitido_en'], schema='trip')
    op.create_index('ix_bcl_cb_fecha', 'broadcast_log', ['control_base_id','emitido_en'], schema='trip')
    op.create_index('ix_bcl_respuesta', 'broadcast_log', ['respuesta'], schema='trip')
    op.create_index('ix_bcl_motivo', 'broadcast_log', ['motivo_exclusion'], schema='trip')

    # payment.qr_cobro
    op.create_table('qr_cobro',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trip.viaje_solicitado.id'), nullable=False),
        sa.Column('token', sa.String(120), unique=True, nullable=False),
        sa.Column('monto', sa.Numeric(12,2), nullable=False),
        sa.Column('pasarela', sa.String(30)),
        sa.Column('estado', sa.String(20), server_default='pendiente', nullable=False),
        sa.Column('url_pago', sa.Text),
        sa.Column('id_transaccion_externa', sa.String(120)),
        sa.Column('creado_en', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('expira_en', sa.DateTime, nullable=False),
        sa.Column('pagado_en', sa.DateTime),
        sa.Column('control_base_id', postgresql.UUID(as_uuid=True), nullable=False),
        schema='payment')
    op.create_index('ix_qr_cobro_token', 'qr_cobro', ['token'], schema='payment', unique=True)
    op.create_index('ix_qr_cobro_viaje', 'qr_cobro', ['viaje_id'], schema='payment')
    op.create_check_constraint('ck_qr_estado', 'qr_cobro',
        "estado IN ('pendiente','pagado','expirado','cancelado')", schema='payment')

    # payment.configuracion_pasarela
    op.create_table('configuracion_pasarela',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pasarela', sa.String(30), nullable=False),
        sa.Column('activa', sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column('credenciales', postgresql.JSONB, server_default='{}', nullable=False),
        sa.Column('comision_porcentaje', sa.Numeric(5,2), server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('control_base_id','pasarela', name='uq_cb_pasarela'),
        schema='payment')

    # auth.plantilla_viaje
    op.create_table('plantilla_viaje',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('auth.usuario.id'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenant.empresa.id')),
        sa.Column('nombre', sa.String(80), nullable=False),
        sa.Column('direccion_origen', sa.Text),
        sa.Column('latitud_origen', sa.Numeric(10,7)),
        sa.Column('longitud_origen', sa.Numeric(10,7)),
        sa.Column('direccion_destino', sa.Text),
        sa.Column('latitud_destino', sa.Numeric(10,7)),
        sa.Column('longitud_destino', sa.Numeric(10,7)),
        sa.Column('paradas_intermedias', postgresql.JSONB, server_default='[]'),
        sa.Column('tipo_vehiculo', sa.String(50)),
        sa.Column('metodo_pago', sa.String(30)),
        sa.Column('cantidad_pasajeros', sa.Integer, server_default='1'),
        sa.Column('cantidad_equipaje', sa.Integer, server_default='0'),
        sa.Column('nota_conductor', sa.Text),
        sa.Column('activo', sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        schema='auth')
    op.create_index('ix_plantilla_usuario', 'plantilla_viaje', ['usuario_id'], schema='auth')
    op.create_index('ix_plantilla_empresa', 'plantilla_viaje', ['empresa_id'], schema='auth')


def downgrade() -> None:
    op.drop_table('plantilla_viaje', schema='auth')
    op.drop_table('configuracion_pasarela', schema='payment')
    op.drop_table('qr_cobro', schema='payment')
    op.drop_table('broadcast_log', schema='trip')
