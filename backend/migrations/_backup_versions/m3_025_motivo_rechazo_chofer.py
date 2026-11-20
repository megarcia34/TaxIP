"""Add motivo_rechazo, rechazado_en, rechazado_por to fleet.chofer_vehiculo

Revision ID: m3_025
Revises: m3_024
Create Date: 2026-10-20
"""
from alembic import op

# revision identifiers
revision = 'm3_025'
down_revision = 'm3_024'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega columnas para registrar el rechazo de un chofer.
    Alineado con la estructura de fleet.vehiculo.
    """
    op.execute("""
        ALTER TABLE fleet.chofer_vehiculo
        ADD COLUMN motivo_rechazo TEXT NULL
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.chofer_vehiculo.motivo_rechazo
        IS 'Motivo del rechazo de la postulacion del chofer'
    """)

    op.execute("""
        ALTER TABLE fleet.chofer_vehiculo
        ADD COLUMN rechazado_en TIMESTAMP NULL
    """)

    op.execute("""
        ALTER TABLE fleet.chofer_vehiculo
        ADD COLUMN rechazado_por UUID NULL
    """)
    op.execute("""
        ALTER TABLE fleet.chofer_vehiculo
        ADD CONSTRAINT fk_chofer_vehiculo_rechazado_por
        FOREIGN KEY (rechazado_por) REFERENCES auth.usuario(id) ON DELETE SET NULL
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.chofer_vehiculo
        DROP CONSTRAINT IF EXISTS fk_chofer_vehiculo_rechazado_por
    """)
    op.execute("ALTER TABLE fleet.chofer_vehiculo DROP COLUMN rechazado_por")
    op.execute("ALTER TABLE fleet.chofer_vehiculo DROP COLUMN rechazado_en")
    op.execute("ALTER TABLE fleet.chofer_vehiculo DROP COLUMN motivo_rechazo")