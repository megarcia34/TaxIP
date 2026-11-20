
"""add timestamps to vehiculo

Revision ID: 3d211643101a
Revises: 99a816660e84
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa

revision = '3d211643101a'
down_revision = '99a816660e84'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega las columnas de timestamp a fleet.vehiculo de forma segura.
    Usa bloques DO para evitar errores si las columnas ya existen.
    """
    op.execute("""
        DO $$
        BEGIN
            -- 1. Agregar created_at si no existe
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'vehiculo' AND column_name = 'created_at'
            ) THEN
                ALTER TABLE fleet.vehiculo ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
            END IF;

            -- 2. Agregar updated_at si no existe
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'vehiculo' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE fleet.vehiculo ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
            END IF;
        END $$;
    """)

    # Agregar comentarios descriptivos
    op.execute("""
        COMMENT ON COLUMN fleet.vehiculo.created_at IS 'Fecha y hora de creación del registro del vehículo';
        COMMENT ON COLUMN fleet.vehiculo.updated_at IS 'Fecha y hora de la última actualización del registro del vehículo';
    """)


def downgrade() -> None:
    """
    Elimina las columnas de timestamp de forma segura.
    """
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'vehiculo' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE fleet.vehiculo DROP COLUMN updated_at;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'vehiculo' AND column_name = 'created_at'
            ) THEN
                ALTER TABLE fleet.vehiculo DROP COLUMN created_at;
            END IF;
        END $$;
    """)