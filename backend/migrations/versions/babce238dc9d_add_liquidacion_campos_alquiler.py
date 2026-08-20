

"""add liquidacion campos alquiler (km_excedentes, saldos)

Revision ID: babce238dc9d
Revises: dc6e91ec310b
Create Date: 2026-08-17 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'babce238dc9d'
down_revision: Union[str, None] = 'dc6e91ec310b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. Agregar columnas a fleet.liquidacion (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- km_excedentes
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'liquidacion' 
                  AND column_name = 'km_excedentes'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD COLUMN km_excedentes NUMERIC(12, 2) NOT NULL DEFAULT 0;
            END IF;

            -- cargo_km_excedentes
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'liquidacion' 
                  AND column_name = 'cargo_km_excedentes'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD COLUMN cargo_km_excedentes NUMERIC(12, 2) NOT NULL DEFAULT 0;
            END IF;

            -- saldo_chofer
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'liquidacion' 
                  AND column_name = 'saldo_chofer'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD COLUMN saldo_chofer NUMERIC(12, 2) NOT NULL DEFAULT 0;
            END IF;

            -- saldo_propietario
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'liquidacion' 
                  AND column_name = 'saldo_propietario'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD COLUMN saldo_propietario NUMERIC(12, 2) NOT NULL DEFAULT 0;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS saldo_propietario")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS saldo_chofer")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS cargo_km_excedentes")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS km_excedentes")