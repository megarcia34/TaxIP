"""fix viaje solicitado missing columns

Revision ID: 4fa1ae56e7e7
Revises: 3d211643101a
Create Date: 2026-08-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '4fa1ae56e7e7'
down_revision: Union[str, Sequence[str], None] = '3d211643101a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar columnas faltantes a viaje_solicitado de forma segura"""
    
    # 1. Agregar solicitado_en (si no existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'viaje_solicitado' AND column_name = 'solicitado_en'
            ) THEN
                ALTER TABLE trip.viaje_solicitado ADD COLUMN solicitado_en TIMESTAMP DEFAULT NOW();
            END IF;
        END $$;
    """)
    
    # 2. Agregar chofer_vehiculo_id (si no existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'viaje_solicitado' AND column_name = 'chofer_vehiculo_id'
            ) THEN
                ALTER TABLE trip.viaje_solicitado ADD COLUMN chofer_vehiculo_id UUID;
            END IF;
        END $$;
    """)
    
    # 3. Agregar updated_at (si no existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'viaje_solicitado' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE trip.viaje_solicitado ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
            END IF;
        END $$;
    """)
    
    # 4. Crear índice para chofer_vehiculo_id (si no existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'trip' AND tablename = 'viaje_solicitado' AND indexname = 'idx_viaje_solicitado_chofer_vehiculo'
            ) THEN
                CREATE INDEX idx_viaje_solicitado_chofer_vehiculo ON trip.viaje_solicitado(chofer_vehiculo_id);
            END IF;
        END $$;
    """)
    
    # 5. Agregar FK a chofer_vehiculo (si no existe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_viaje_solicitado_chofer_vehiculo' 
                  AND table_schema = 'trip' AND table_name = 'viaje_solicitado'
            ) THEN
                ALTER TABLE trip.viaje_solicitado 
                ADD CONSTRAINT fk_viaje_solicitado_chofer_vehiculo 
                FOREIGN KEY (chofer_vehiculo_id) 
                REFERENCES fleet.chofer_vehiculo(id) 
                ON DELETE SET NULL;
            END IF;
        END $$;
    """)
    
    # 6. Poblar solicitado_en con created_at para registros existentes
    op.execute("""
        UPDATE trip.viaje_solicitado 
        SET solicitado_en = created_at 
        WHERE solicitado_en IS NULL AND created_at IS NOT NULL
    """)
    
    # 7. Comentarios descriptivos
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.solicitado_en IS 
        'Fecha y hora en que se solicitó el viaje (snapshot del momento de la solicitud)';
    """)
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.chofer_vehiculo_id IS 
        'Asignación específica chofer-vehículo al momento del viaje (snapshot inmutable)';
    """)
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.updated_at IS 
        'Fecha y hora de la última actualización del viaje';
    """)


def downgrade() -> None:
    """Revertir cambios de forma segura"""
    
    # 1. Eliminar FK
    op.execute("""
        ALTER TABLE trip.viaje_solicitado 
        DROP CONSTRAINT IF EXISTS fk_viaje_solicitado_chofer_vehiculo
    """)
    
    # 2. Eliminar índice
    op.execute("""
        DROP INDEX IF EXISTS trip.idx_viaje_solicitado_chofer_vehiculo
    """)
    
    # 3. Eliminar columnas (orden inverso)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado DROP COLUMN IF EXISTS updated_at
    """)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado DROP COLUMN IF EXISTS chofer_vehiculo_id
    """)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado DROP COLUMN IF EXISTS solicitado_en
    """)