"""m3_036: agregar tipo_conciliacion a turno_chofer

Revision ID: m3_036
Revises: m3_035
"""
from alembic import op

revision = 'm3_036'
down_revision = 'm3_035'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS tipo_conciliacion VARCHAR(30) DEFAULT 'AUTOMATICA';
    """)

def downgrade():
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP COLUMN IF EXISTS tipo_conciliacion;
    """)