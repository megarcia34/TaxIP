
"""add compensacion_km to contrato_vehiculo

Revision ID: <9cde8795c601>
Revises: babce238dc9d
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = '9cde8795c601'
down_revision = 'babce238dc9d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. Agregar columna compensacion_km (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'contrato_vehiculo' 
                  AND column_name = 'compensacion_km'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD COLUMN compensacion_km VARCHAR(20) NOT NULL DEFAULT 'DIARIA';
            END IF;
        END $$;
    """)

    # ============================================================
    # 2. Check constraint (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'ck_contrato_compensacion_km'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_compensacion_km 
                CHECK (compensacion_km IN ('DIARIA', 'ACUMULADA', 'COMPENSADA'));
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_compensacion_km")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS compensacion_km")