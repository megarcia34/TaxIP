"""Add numero column to fleet.documentos_chofer

Revision ID: m3_024
Revises: m3_023
Create Date: 2026-10-17
"""

from alembic import op

# revision identifiers
revision = 'm3_024'
down_revision = 'm3_023'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega columna 'numero' a fleet.documentos_chofer.
    Nullable, para no romper los registros existentes que no la tienen.
    """
    op.execute("""
        ALTER TABLE fleet.documentos_chofer
        ADD COLUMN numero VARCHAR(50) NULL
    """)

    op.execute("""
        COMMENT ON COLUMN fleet.documentos_chofer.numero
        IS 'Numero del documento (DNI, licencia, etc). Opcional.'
    """)


def downgrade() -> None:
    """Elimina la columna 'numero' de fleet.documentos_chofer."""
    op.execute("""
        ALTER TABLE fleet.documentos_chofer
        DROP COLUMN numero
    """)