"""M3-002: 27 columnas aditivas en trip.viaje_solicitado

Revision ID: m3_002
Revises: m3_001
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_002'
down_revision = 'm3_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    T = 'viaje_solicitado'
    S = 'trip'

    # Pasajero / canal
    op.add_column(T, sa.Column('es_anonimo', sa.Boolean, server_default=sa.false(), nullable=False), schema=S)
    op.add_column(T, sa.Column('pasajero_telefono', sa.String(30)), schema=S)
    op.add_column(T, sa.Column('lugar_subida', sa.String(255)), schema=S)
    op.add_column(T, sa.Column('cantidad_pasajeros', sa.Integer, server_default='1'), schema=S)
    op.add_column(T, sa.Column('origen_tipo', sa.String(20)), schema=S)

    op.create_check_constraint(
        'ck_viaje_origen_tipo', T,
        "origen_tipo IS NULL OR origen_tipo IN ('plataforma','via_publica','qr_comercio','corporativo','despacho_manual')",
        schema=S)

    # Despacho manual
    op.add_column(T, sa.Column('empleado_id', postgresql.UUID(as_uuid=True),
                               sa.ForeignKey('auth.usuario.id', name='fk_viaje_empleado')), schema=S)
    op.add_column(T, sa.Column('turno_empleado_id', postgresql.UUID(as_uuid=True),
                               sa.ForeignKey('auth.turno_empleado.id', name='fk_viaje_turno_emp')), schema=S)
    op.add_column(T, sa.Column('centro_costo', sa.String(100)), schema=S)
    op.add_column(T, sa.Column('paradas_intermedias', postgresql.JSONB, server_default='[]'), schema=S)
    op.add_column(T, sa.Column('subestado_despacho', sa.String(30)), schema=S)
    op.add_column(T, sa.Column('es_programado', sa.Boolean, server_default=sa.false()), schema=S)

    op.create_check_constraint(
        'ck_viaje_subestado_despacho', T,
        "subestado_despacho IS NULL OR subestado_despacho IN ('reservado','despachado','vehiculo_llego','pasajero_a_bordo','completado')",
        schema=S)

    # Filtros opt-in
    op.add_column(T, sa.Column('requiere_baul_grande', sa.Boolean, server_default=sa.false()), schema=S)
    op.add_column(T, sa.Column('cantidad_valijas', sa.Integer, server_default='0'), schema=S)
    op.add_column(T, sa.Column('calidad_minima_vehiculo', sa.String(20)), schema=S)
    op.add_column(T, sa.Column('tipo_vehiculo_solicitado', sa.String(50)), schema=S)

    op.create_check_constraint(
        'ck_viaje_calidad_min', T,
        "calidad_minima_vehiculo IS NULL OR calidad_minima_vehiculo IN ('regular','bueno','excelente')",
        schema=S)

    # Broadcast
    op.add_column(T, sa.Column('intentos_broadcast', sa.Integer, server_default='0'), schema=S)
    op.add_column(T, sa.Column('radio_broadcast_metros', sa.Integer, server_default='2000'), schema=S)
    op.add_column(T, sa.Column('fecha_publicacion', sa.DateTime), schema=S)
    op.add_column(T, sa.Column('fecha_expiracion', sa.DateTime), schema=S)

    # QR cobro
    op.add_column(T, sa.Column('qr_cobro_token', sa.String(120)), schema=S)
    op.add_column(T, sa.Column('qr_cobro_expira', sa.DateTime), schema=S)

    # Cuenta corriente
    op.add_column(T, sa.Column('cuenta_corriente_id', postgresql.UUID(as_uuid=True),
                               sa.ForeignKey('corporate.cuenta_corriente.id', name='fk_viaje_cc')), schema=S)
    op.add_column(T, sa.Column('cargado_a_cuenta', sa.Boolean, server_default=sa.false()), schema=S)
    op.add_column(T, sa.Column('responsable_cobro', sa.String(20)), schema=S)
    op.add_column(T, sa.Column('estado_cobro', sa.String(20)), schema=S)
    op.add_column(T, sa.Column('fecha_cobro', sa.DateTime), schema=S)
    op.add_column(T, sa.Column('movimiento_cc_id', postgresql.UUID(as_uuid=True),
                               sa.ForeignKey('corporate.movimiento_cuenta.id', name='fk_viaje_mov_cc')), schema=S)

    op.create_check_constraint(
        'ck_viaje_responsable_cobro', T,
        "responsable_cobro IS NULL OR responsable_cobro IN ('chofer','propietario','tenant','comercio','empresa')",
        schema=S)
    op.create_check_constraint(
        'ck_viaje_estado_cobro', T,
        "estado_cobro IS NULL OR estado_cobro IN ('pendiente','cobrado','facturado','pagado')",
        schema=S)
    op.create_check_constraint(
        'ck_viaje_cc_obligatoria', T,
        "(cargado_a_cuenta = false) OR (cuenta_corriente_id IS NOT NULL)",
        schema=S)
    op.create_check_constraint(
        'ck_viaje_centro_costo_despacho', T,
        "(origen_tipo IS NULL OR origen_tipo <> 'despacho_manual') OR (centro_costo IS NOT NULL)",
        schema=S)

    # Metodo pago unificado
    op.add_column(T, sa.Column('metodo_pago', sa.String(30)), schema=S)

    # Indices
    op.create_index('ix_viaje_estado', T, ['estado'], schema=S)
    op.create_index('ix_viaje_cuenta_corriente_id', T, ['cuenta_corriente_id'], schema=S)
    op.create_index('ix_viaje_empleado_id', T, ['empleado_id'], schema=S)
    op.create_index('ix_viaje_empresa_id', T, ['empresa_id'], schema=S)
    op.create_index('ix_viaje_centro_costo', T, ['centro_costo'], schema=S)
    op.create_index('ix_viaje_qr_cobro_token', T, ['qr_cobro_token'], schema=S)
    op.create_index(
        'ix_viaje_fecha_expiracion_publicado', T, ['fecha_expiracion'],
        schema=S, postgresql_where=sa.text("estado = 'publicado'"))


def downgrade() -> None:
    T, S = 'viaje_solicitado', 'trip'
    for idx in ['ix_viaje_fecha_expiracion_publicado','ix_viaje_qr_cobro_token','ix_viaje_centro_costo',
                'ix_viaje_empresa_id','ix_viaje_empleado_id','ix_viaje_cuenta_corriente_id','ix_viaje_estado']:
        op.drop_index(idx, table_name=T, schema=S)
    for ck in ['ck_viaje_centro_costo_despacho','ck_viaje_cc_obligatoria','ck_viaje_estado_cobro',
               'ck_viaje_responsable_cobro','ck_viaje_calidad_min','ck_viaje_subestado_despacho','ck_viaje_origen_tipo']:
        op.drop_constraint(ck, T, schema=S)
    for col in ['metodo_pago','movimiento_cc_id','fecha_cobro','estado_cobro','responsable_cobro','cargado_a_cuenta',
                'cuenta_corriente_id','qr_cobro_expira','qr_cobro_token','fecha_expiracion','fecha_publicacion',
                'radio_broadcast_metros','intentos_broadcast','tipo_vehiculo_solicitado','calidad_minima_vehiculo',
                'cantidad_valijas','requiere_baul_grande','es_programado','subestado_despacho','paradas_intermedias',
                'centro_costo','turno_empleado_id','empleado_id','origen_tipo','cantidad_pasajeros','lugar_subida',
                'pasajero_telefono','es_anonimo']:
        op.drop_column(T, col, schema=S)
