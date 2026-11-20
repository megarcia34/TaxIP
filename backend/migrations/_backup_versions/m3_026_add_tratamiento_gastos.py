"""add tratamiento_gastos to contrato_vehiculo

Revision ID: m3_026
Revises: m3_025
Create Date: 2026-10-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'm3_026'
down_revision = 'm3_025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'contrato_vehiculo',
        sa.Column('tratamiento_gastos', sa.String(50), nullable=True, server_default='DESPUES'),
        schema='fleet'
    )


def downgrade() -> None:
    op.drop_column('contrato_vehiculo', 'tratamiento_gastos', schema='fleet')