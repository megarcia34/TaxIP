"""M3-001: Extender fleet.vehiculo con capacidad_baul, estado_vehiculo, equipamiento

Revision ID: m3_001
Revises: b25539ad0e3e
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_001'
down_revision = 'b25539ad0e3e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('vehiculo',
        sa.Column('capacidad_baul', sa.String(20), nullable=False, server_default='sin_baul'),
        schema='fleet')
    op.add_column('vehiculo',
        sa.Column('estado_vehiculo', sa.String(20), nullable=False, server_default='bueno'),
        schema='fleet')
    op.add_column('vehiculo',
        sa.Column('equipamiento', postgresql.JSONB, nullable=False, server_default='[]'),
        schema='fleet')

    op.create_check_constraint(
        'ck_vehiculo_capacidad_baul', 'vehiculo',
        "capacidad_baul IN ('sin_baul','baul_chico','baul_mediano','baul_grande','van_carga')",
        schema='fleet')
    op.create_check_constraint(
        'ck_vehiculo_estado_vehiculo', 'vehiculo',
        "estado_vehiculo IN ('regular','bueno','excelente')",
        schema='fleet')

    op.create_index('ix_vehiculo_capacidad_baul', 'vehiculo', ['capacidad_baul'], schema='fleet')
    op.create_index('ix_vehiculo_estado_vehiculo', 'vehiculo', ['estado_vehiculo'], schema='fleet')


def downgrade() -> None:
    op.drop_index('ix_vehiculo_estado_vehiculo', table_name='vehiculo', schema='fleet')
    op.drop_index('ix_vehiculo_capacidad_baul', table_name='vehiculo', schema='fleet')
    op.drop_constraint('ck_vehiculo_estado_vehiculo', 'vehiculo', schema='fleet')
    op.drop_constraint('ck_vehiculo_capacidad_baul', 'vehiculo', schema='fleet')
    op.drop_column('vehiculo', 'equipamiento', schema='fleet')
    op.drop_column('vehiculo', 'estado_vehiculo', schema='fleet')
    op.drop_column('vehiculo', 'capacidad_baul', schema='fleet')
