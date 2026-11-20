"""m3_020 vocabulario metodo_pago liquidacion propietario + CHECK

Revision ID: m3_020
Revises: m3_019
Create Date: 2026-10-12

R18 - Flujo propietario.

Agrega CHECK a fleet.liquidacion.metodo_pago con el vocabulario
canonico de liquidaciones propietario -> chofer:

    EFECTIVO, TRANSFERENCIA

Antes: el campo no tenia restriccion. Se validaba solo en Python
(liquidacion.py:329).

El campo es nullable: la liquidacion puede estar en BORRADOR, APROBADA,
etc. sin metodo_pago asignado. El CHECK contempla ese caso (IS NULL OR ...).
"""
from alembic import op

revision = 'm3_020'
down_revision = 'm3_019'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD CONSTRAINT ck_liquidacion_metodo_pago
        CHECK (metodo_pago IS NULL OR metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA'))
    """)


def downgrade():
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP CONSTRAINT ck_liquidacion_metodo_pago
    """)