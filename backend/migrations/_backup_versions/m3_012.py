"""Rename CHECK gasto_turno_monto_check a nombre canonico

Revision ID: m3_012
Revises: m3_011
Create Date: 2026-10-06

La DB tiene el CHECK de fleet.gasto_turno como 'gasto_turno_monto_check'
(nombre sin convention). El ORM lo declara con name='monto_check', que
la naming_convention expande a 'ck_gasto_turno_monto_check'.

Se renombra el CHECK en DB al nombre canonico del ORM para que
matcheen.

Deuda orm.naming_convention_check_divergente (parcial).
Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_012'
down_revision = 'm3_011'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        RENAME CONSTRAINT gasto_turno_monto_check
        TO ck_gasto_turno_monto_check
    """)


def downgrade():
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        RENAME CONSTRAINT ck_gasto_turno_monto_check
        TO gasto_turno_monto_check
    """)