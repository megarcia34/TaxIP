
"""add notificacion vencimiento

Revision ID: 2a49bcd3e516
Revises: 6ce12833e2cf
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '2a49bcd3e516'
down_revision = '6ce12833e2cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear tabla notificacion_vencimiento
    op.create_table(
        'notificacion_vencimiento',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('documento_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entidad_tipo', sa.String(20), nullable=False),  # 'propietario', 'vehiculo', 'chofer'
        sa.Column('propietario_id', postgresql.UUID(as_uuid=True), nullable=True),  # nullable para choferes
        sa.Column('tipo_documento', sa.String(50), nullable=False),
        sa.Column('numero', sa.String(50), nullable=False),
        sa.Column('nivel', sa.String(20), nullable=False),  # 'critical', 'warning', 'info'
        sa.Column('dias_restantes', sa.Integer(), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
        sa.Column('email_enviado', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('email_enviado_en', sa.DateTime(), nullable=True),
        sa.Column('sms_enviado', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('sms_enviado_en', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['propietario_id'], ['auth.usuario.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('documento_id', 'nivel', name='uq_notificacion_documento_nivel'),
        sa.CheckConstraint(
            "nivel IN ('critical', 'warning', 'info')",
            name='chk_notificacion_nivel_valido'
        ),
        sa.CheckConstraint(
            "entidad_tipo IN ('propietario', 'vehiculo', 'chofer')",
            name='chk_notificacion_entidad_tipo_valido'
        ),
        schema='fleet'
    )

    # 2. Crear índices para rendimiento
    op.create_index('idx_notificacion_documento', 'notificacion_vencimiento', ['documento_id'], schema='fleet')
    op.create_index('idx_notificacion_propietario', 'notificacion_vencimiento', ['propietario_id'], schema='fleet')
    op.create_index('idx_notificacion_nivel', 'notificacion_vencimiento', ['nivel'], schema='fleet')
    op.create_index('idx_notificacion_fecha_vencimiento', 'notificacion_vencimiento', ['fecha_vencimiento'], schema='fleet')
    op.create_index('idx_notificacion_email_pendiente', 'notificacion_vencimiento',
                    ['email_enviado', 'fecha_vencimiento'],
                    schema='fleet',
                    postgresql_where=sa.text('email_enviado = FALSE'))


def downgrade() -> None:
    op.drop_index('idx_notificacion_email_pendiente', table_name='notificacion_vencimiento', schema='fleet')
    op.drop_index('idx_notificacion_fecha_vencimiento', table_name='notificacion_vencimiento', schema='fleet')
    op.drop_index('idx_notificacion_nivel', table_name='notificacion_vencimiento', schema='fleet')
    op.drop_index('idx_notificacion_propietario', table_name='notificacion_vencimiento', schema='fleet')
    op.drop_index('idx_notificacion_documento', table_name='notificacion_vencimiento', schema='fleet')
    op.drop_table('notificacion_vencimiento', schema='fleet')