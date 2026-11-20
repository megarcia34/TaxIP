

"""crear documento propietario

Revision ID: 'd1e5496783df'
Revises: 390dc56c9bea
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd1e5496783df'
down_revision = '390dc56c9bea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear la tabla documento_propietario
    op.create_table(
        'documento_propietario',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('propietario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_documento', sa.String(50), nullable=False),
        sa.Column('numero', sa.String(50), nullable=False),
        sa.Column('fecha_emision', sa.Date(), nullable=True),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('url_archivo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['propietario_id'], ['auth.usuario.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('propietario_id', 'tipo_documento', name='uq_documento_propietario_tipo'),
        schema='fleet'
    )
    
    # 2. Crear índice para búsquedas rápidas
    op.create_index('idx_documento_propietario_propietario_id', 'documento_propietario', ['propietario_id'], schema='fleet')


def downgrade() -> None:
    op.drop_index('idx_documento_propietario_propietario_id', table_name='documento_propietario', schema='fleet')
    op.drop_table('documento_propietario', schema='fleet')