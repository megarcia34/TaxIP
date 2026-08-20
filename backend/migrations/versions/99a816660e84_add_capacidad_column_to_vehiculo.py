"""add capacidad column to vehiculo

Revision ID: 99a816660e84
Revises: 1405916116e3
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa

revision = '99a816660e84'
down_revision = '1405916116e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Agregar columna 'capacidad' a fleet.vehiculo de forma segura"""
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'vehiculo' AND column_name = 'capacidad'
            ) THEN
                ALTER TABLE fleet.vehiculo ADD COLUMN capacidad INTEGER;
                COMMENT ON COLUMN fleet.vehiculo.capacidad IS 'Capacidad de pasajeros del vehículo';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Eliminar columna 'capacidad' de forma segura"""
    op.execute("""
        ALTER TABLE fleet.vehiculo DROP COLUMN IF EXISTS capacidad;
    """)