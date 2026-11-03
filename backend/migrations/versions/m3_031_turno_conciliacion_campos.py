"""conciliacion: agregar campos de conciliacion a turno_chofer

Revision ID: m3_031
Revises: m3_030
Create Date: 2026-11-02

Agrega a fleet.turno_chofer:
- conciliado_por UUID
- conciliado_en TIMESTAMP
- tipo_conciliacion VARCHAR(20) DEFAULT 'MANUAL'
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'm3_031'
down_revision: Union[str, None] = 'm3_030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS conciliado_por UUID REFERENCES auth.usuario(id)
    """)
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS conciliado_en TIMESTAMP
    """)
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS tipo_conciliacion VARCHAR(20) DEFAULT 'MANUAL'
    """)

def downgrade() -> None:
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS tipo_conciliacion")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS conciliado_en")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS conciliado_por")