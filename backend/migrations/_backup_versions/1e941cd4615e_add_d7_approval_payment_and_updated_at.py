

"""add d7 approval payment and updated at

Revision ID: 1e941cd4615e
Revises: 6553ec8a1785
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '1e941cd4615e'
down_revision = '6553ec8a1785'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # 1. CAMPOS D7 EN fleet.liquidacion
    # ============================================
    
    # Agregar columnas
    op.execute("""
        DO $$
        BEGIN
            -- aprobada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'aprobada_por'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN aprobada_por UUID;
            END IF;
            
            -- aprobada_en
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'aprobada_en'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN aprobada_en TIMESTAMP;
            END IF;
            
            -- rechazada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'rechazada_por'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN rechazada_por UUID;
            END IF;
            
            -- rechazada_en
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'rechazada_en'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN rechazada_en TIMESTAMP;
            END IF;
            
            -- motivo_rechazo
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'motivo_rechazo'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN motivo_rechazo TEXT;
            END IF;
            
            -- pagada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'pagada_por'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN pagada_por UUID;
            END IF;
            
            -- pagada_en
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'pagada_en'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN pagada_en TIMESTAMP;
            END IF;
            
            -- metodo_pago
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'metodo_pago'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN metodo_pago VARCHAR(50);
            END IF;
            
            -- referencia_pago
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion' AND column_name = 'referencia_pago'
            ) THEN
                ALTER TABLE fleet.liquidacion ADD COLUMN referencia_pago VARCHAR(100);
            END IF;
        END $$;
    """)
    
    # Agregar foreign keys (solo si no existen)
    op.execute("""
        DO $$
        BEGIN
            -- FK aprobada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_liquidacion_aprobada_por'
                AND table_schema = 'fleet' AND table_name = 'liquidacion'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD CONSTRAINT fk_liquidacion_aprobada_por 
                FOREIGN KEY (aprobada_por) REFERENCES auth.usuario(id) ON DELETE SET NULL;
            END IF;
            
            -- FK rechazada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_liquidacion_rechazada_por'
                AND table_schema = 'fleet' AND table_name = 'liquidacion'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD CONSTRAINT fk_liquidacion_rechazada_por 
                FOREIGN KEY (rechazada_por) REFERENCES auth.usuario(id) ON DELETE SET NULL;
            END IF;
            
            -- FK pagada_por
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_liquidacion_pagada_por'
                AND table_schema = 'fleet' AND table_name = 'liquidacion'
            ) THEN
                ALTER TABLE fleet.liquidacion 
                ADD CONSTRAINT fk_liquidacion_pagada_por 
                FOREIGN KEY (pagada_por) REFERENCES auth.usuario(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)
    
    # ============================================
    # 2. COLUMNA updated_at EN fleet.contrato_vehiculo
    # ============================================
    
    op.execute("""
        DO $$
        BEGIN
            -- Agregar columna si no existe
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' AND table_name = 'contrato_vehiculo' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN updated_at TIMESTAMP;
            END IF;
            
            -- Actualizar valores existentes con created_at
            UPDATE fleet.contrato_vehiculo 
            SET updated_at = created_at 
            WHERE updated_at IS NULL;
            
            -- Hacer la columna NOT NULL
            ALTER TABLE fleet.contrato_vehiculo 
            ALTER COLUMN updated_at SET NOT NULL;
        END $$;
    """)


def downgrade() -> None:
    # ============================================
    # 1. REVERTIR updated_at EN fleet.contrato_vehiculo
    # ============================================
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS updated_at")
    
    # ============================================
    # 2. REVERTIR CAMPOS D7 EN fleet.liquidacion
    # ============================================
    
    # Eliminar foreign keys
    op.execute("ALTER TABLE fleet.liquidacion DROP CONSTRAINT IF EXISTS fk_liquidacion_pagada_por")
    op.execute("ALTER TABLE fleet.liquidacion DROP CONSTRAINT IF EXISTS fk_liquidacion_rechazada_por")
    op.execute("ALTER TABLE fleet.liquidacion DROP CONSTRAINT IF EXISTS fk_liquidacion_aprobada_por")
    
    # Eliminar columnas
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS referencia_pago")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS metodo_pago")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS pagada_en")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS pagada_por")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS motivo_rechazo")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS rechazada_en")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS rechazada_por")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS aprobada_en")
    op.execute("ALTER TABLE fleet.liquidacion DROP COLUMN IF EXISTS aprobada_por")