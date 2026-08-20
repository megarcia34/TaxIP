

"""add dia_inicio_semana and state constraints for ALQUILER contracts

Revision ID: 182d55b83b69
Revises: 296ea35348e7
Create Date: 2026-08-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '182d55b83b69'
down_revision: Union[str, None] = '296ea35348e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. Agregar columna dia_inicio_semana (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'fleet' 
                  AND table_name = 'contrato_vehiculo' 
                  AND column_name = 'dia_inicio_semana'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD COLUMN dia_inicio_semana VARCHAR(20);
            END IF;
        END $$;
    """)

    # ============================================================
    # 2. Check constraint para dia_inicio_semana (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'ck_contrato_dia_inicio_semana'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_dia_inicio_semana 
                CHECK (dia_inicio_semana IN ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo') OR dia_inicio_semana IS NULL);
            END IF;
        END $$;
    """)

    # ============================================================
    # 3. Normalizar datos existentes antes de crear constraints
    # ============================================================
    op.execute("""
        -- Normalizar estado_contrato: valores inválidos -> 'PENDIENTE_CONFIGURACION'
        UPDATE fleet.contrato_vehiculo 
        SET estado_contrato = 'PENDIENTE_CONFIGURACION'
        WHERE estado_contrato NOT IN ('PENDIENTE_CONFIGURACION', 'PROGRAMADO', 'ACTIVO', 'FINALIZADO')
           OR estado_contrato IS NULL;
        
        -- Sincronizar activo con estado_contrato
        UPDATE fleet.contrato_vehiculo 
        SET activo = (estado_contrato = 'ACTIVO')
        WHERE (estado_contrato = 'ACTIVO' AND activo = false)
           OR (estado_contrato <> 'ACTIVO' AND activo = true);
    """)

    # ============================================================
    # 4. Actualizar constraint de estado_contrato (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- Eliminar constraint existente si existe
            IF EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'ck_contrato_estado'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                DROP CONSTRAINT ck_contrato_estado;
            END IF;
            
            -- Crear nuevo constraint
            ALTER TABLE fleet.contrato_vehiculo 
            ADD CONSTRAINT ck_contrato_estado 
            CHECK (estado_contrato IN ('PENDIENTE_CONFIGURACION', 'PROGRAMADO', 'ACTIVO', 'FINALIZADO'));
        END $$;
    """)

    # ============================================================
    # 5. Constraint de consistencia activo <-> estado_contrato (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'ck_contrato_activo_estado'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_activo_estado 
                CHECK (
                    (estado_contrato = 'ACTIVO' AND activo = true) 
                    OR (estado_contrato IN ('PENDIENTE_CONFIGURACION', 'PROGRAMADO', 'FINALIZADO') AND activo = false)
                );
            END IF;
        END $$;
    """)

    # ============================================================
    # 6. Índice para estado_contrato (IDEMPOTENTE)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE schemaname = 'fleet' 
                  AND tablename = 'contrato_vehiculo' 
                  AND indexname = 'ix_contrato_vehiculo_estado_contrato'
            ) THEN
                CREATE INDEX ix_contrato_vehiculo_estado_contrato 
                ON fleet.contrato_vehiculo(estado_contrato);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # ============================================================
    # 1. Eliminar índice
    # ============================================================
    op.execute("DROP INDEX IF EXISTS fleet.ix_contrato_vehiculo_estado_contrato")

    # ============================================================
    # 2. Eliminar constraints
    # ============================================================
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_activo_estado")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_estado")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_dia_inicio_semana")

    # ============================================================
    # 3. Eliminar columna
    # ============================================================
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS dia_inicio_semana")