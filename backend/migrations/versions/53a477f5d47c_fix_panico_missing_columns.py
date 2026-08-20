
"""fix panico missing columns

Revision ID: 53a477f5d47c
Revises: 98a9ed87bb59
Create Date: 2026-08-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '53a477f5d47c'
down_revision: Union[str, Sequence[str], None] = '98a9ed87bb59' # Head actual
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar columnas faltantes a trip.panico de forma segura"""
    
    # ========================================
    # 1. trip.panico: Agregar usuario_id y resuelto_en
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'panico' AND column_name = 'usuario_id'
            ) THEN
                ALTER TABLE trip.panico ADD COLUMN usuario_id UUID;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'trip' AND table_name = 'panico' AND column_name = 'resuelto_en'
            ) THEN
                ALTER TABLE trip.panico ADD COLUMN resuelto_en TIMESTAMP;
            END IF;
        END $$;
    """)

    # ========================================
    # 2. FK para usuario_id (auth.usuario)
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_panico_usuario' 
                  AND table_schema = 'trip' AND table_name = 'panico'
            ) THEN
                ALTER TABLE trip.panico 
                ADD CONSTRAINT fk_panico_usuario 
                FOREIGN KEY (usuario_id) 
                REFERENCES auth.usuario(id) 
                ON DELETE CASCADE;
            END IF;
        END $$;
    """)

    # Comentarios
    op.execute("COMMENT ON COLUMN trip.panico.usuario_id IS 'Usuario (chofer/pasajero) que activó el pánico'")
    op.execute("COMMENT ON COLUMN trip.panico.resuelto_en IS 'Fecha y hora en que se resolvió la alerta de pánico'")


def downgrade() -> None:
    """Revertir cambios"""
    op.execute("ALTER TABLE trip.panico DROP CONSTRAINT IF EXISTS fk_panico_usuario")
    op.execute("ALTER TABLE trip.panico DROP COLUMN IF EXISTS resuelto_en")
    op.execute("ALTER TABLE trip.panico DROP COLUMN IF EXISTS usuario_id")