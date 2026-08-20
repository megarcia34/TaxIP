

"""fleet desgaste neumaticos

Revision ID: f4149e326a1a
Revises: 20260726_f1_rentab_audit
Create Date: 2026-07-28
"""
from alembic import op
import sqlalchemy as sa

revision = 'f4149e326a1a'
down_revision = '20260726_f1_rentab_audit'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'vehiculo',
        sa.Column('desgaste_neumaticos', sa.Integer(), server_default='0', nullable=True),
        schema='fleet'
    )
    op.add_column(
        'vehiculo',
        sa.Column('desgaste_manual', sa.Integer(), server_default='0', nullable=True,
                  comment='% ingresado por propietario'),
        schema='fleet'
    )
    op.add_column(
        'vehiculo',
        sa.Column('fecha_ultimo_cambio_neumaticos', sa.Date(), nullable=True,
                  comment='fecha del último cambio'),
        schema='fleet'
    )
    op.add_column(
        'vehiculo',
        sa.Column('km_ultimo_cambio_neumaticos', sa.Integer(), nullable=True,
                  comment='km al último cambio'),
        schema='fleet'
    )
    op.add_column(
        'vehiculo',
        sa.Column('parches_neumaticos', sa.Integer(), server_default='0', nullable=True,
                  comment='cantidad de parches'),
        schema='fleet'
    )


def downgrade() -> None:
    op.drop_column('vehiculo', 'parches_neumaticos', schema='fleet')
    op.drop_column('vehiculo', 'km_ultimo_cambio_neumaticos', schema='fleet')
    op.drop_column('vehiculo', 'fecha_ultimo_cambio_neumaticos', schema='fleet')
    op.drop_column('vehiculo', 'desgaste_manual', schema='fleet')
    op.drop_column('vehiculo', 'desgaste_neumaticos', schema='fleet')