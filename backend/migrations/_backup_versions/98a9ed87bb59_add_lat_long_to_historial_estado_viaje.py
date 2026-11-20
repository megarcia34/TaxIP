

"""add lat long to historial estado viaje

Revision ID: 98a9ed87bb59
Revises: 4fa1ae56e7e7
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa

revision = '98a9ed87bb59'
down_revision = '4fa1ae56e7e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Agregar columnas faltantes a trip.historial_estado_viaje de forma segura"""
    op.execute("""
        DO $$
        BEGIN
            -- 1. Agregar latitud si no existe
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'historial_estado_viaje' AND column_name = 'latitud'
            ) THEN
                ALTER TABLE trip.historial_estado_viaje ADD COLUMN latitud DECIMAL(10, 8);
            END IF;

            -- 2. Agregar longitud si no existe
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'historial_estado_viaje' AND column_name = 'longitud'
            ) THEN
                ALTER TABLE trip.historial_estado_viaje ADD COLUMN longitud DECIMAL(11, 8);
            END IF;

            -- 3. Agregar observacion si no existe (ya existe según el diagnóstico, pero por seguridad)
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'historial_estado_viaje' AND column_name = 'observacion'
            ) THEN
                ALTER TABLE trip.historial_estado_viaje ADD COLUMN observacion TEXT;
            END IF;

            -- 4. Agregar created_at si no existe (ya existe según el diagnóstico, pero por seguridad)
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'historial_estado_viaje' AND column_name = 'created_at'
            ) THEN
                ALTER TABLE trip.historial_estado_viaje ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
            END IF;
        END $$;
    """)

    # Agregar comentarios descriptivos
    op.execute("""
        COMMENT ON COLUMN trip.historial_estado_viaje.latitud IS 'Latitud del vehículo al momento del cambio de estado';
        COMMENT ON COLUMN trip.historial_estado_viaje.longitud IS 'Longitud del vehículo al momento del cambio de estado';
    """)


def downgrade() -> None:
    """Revertir cambios de forma segura"""
    op.execute("""
        ALTER TABLE trip.historial_estado_viaje DROP COLUMN IF EXISTS created_at;
        ALTER TABLE trip.historial_estado_viaje DROP COLUMN IF EXISTS observacion;
        ALTER TABLE trip.historial_estado_viaje DROP COLUMN IF EXISTS longitud;
        ALTER TABLE trip.historial_estado_viaje DROP COLUMN IF EXISTS latitud;
    """)