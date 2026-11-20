

"""rename referencia externa to external reference

Revision ID: 915d4cfb4388
Revises: 53a477f5d47c
Create Date: 2026-08-11
"""
from alembic import op

revision = '915d4cfb4388'
down_revision = '53a477f5d47c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Renombrar columna referencia_externa a external_reference"""
    op.execute("""
        DO $$
        BEGIN
            -- Verificar que la columna old existe y la new no existe
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'payment' 
                  AND table_name = 'transaccion' 
                  AND column_name = 'referencia_externa'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'payment' 
                  AND table_name = 'transaccion' 
                  AND column_name = 'external_reference'
            ) THEN
                ALTER TABLE payment.transaccion 
                RENAME COLUMN referencia_externa TO external_reference;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revertir el rename"""
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'payment' 
                  AND table_name = 'transaccion' 
                  AND column_name = 'external_reference'
            ) THEN
                ALTER TABLE payment.transaccion 
                RENAME COLUMN external_reference TO referencia_externa;
            END IF;
        END $$;
    """)