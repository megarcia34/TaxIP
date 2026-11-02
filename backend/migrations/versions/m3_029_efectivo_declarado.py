"""conciliacion: agregar efectivo_declarado a turno_chofer

Revision ID: m3_029
Revises: m3_028
Create Date: 2026-11-01

Agrega:
- Columna efectivo_declarado NUMERIC a fleet.turno_chofer
- Comment de la columna
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'm3_029'
down_revision: Union[str, None] = 'm3_028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS efectivo_declarado NUMERIC
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.efectivo_declarado
        IS 'Efectivo que el chofer declara haber entregado al propietario al cerrar el turno'
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP COLUMN IF EXISTS efectivo_declarado
    """)