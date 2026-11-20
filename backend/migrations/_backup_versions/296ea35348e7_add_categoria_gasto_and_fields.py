
"""add categoria_gasto and fields to gasto_vehiculo and gasto_turno

Revision ID: 296ea35348e7
Revises: 1e941cd4615e
Create Date: 2026-08-14 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '296ea35348e7'  # Reemplázalo con el ID que genere alembic
down_revision: Union[str, None] = '1e941cd4615e'  # Reemplázalo
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. Crear tabla categoria_gasto (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                       WHERE table_schema = 'fleet' AND table_name = 'categoria_gasto') THEN
            CREATE TABLE fleet.categoria_gasto (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                control_base_id UUID NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                descripcion TEXT,
                subcategorias JSONB NOT NULL DEFAULT '[]'::jsonb,
                aplica_a JSONB NOT NULL DEFAULT '[]'::jsonb,
                tratamiento_economico VARCHAR(20) NOT NULL DEFAULT 'configurable',
                activo BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        END IF;
    END $$;
    """)

    # ============================================================
    # 2. FK a control_base (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                       WHERE constraint_schema = 'fleet' 
                       AND constraint_name = 'fk_categoria_gasto_control_base') THEN
            ALTER TABLE fleet.categoria_gasto 
            ADD CONSTRAINT fk_categoria_gasto_control_base 
            FOREIGN KEY (control_base_id) 
            REFERENCES tenant.control_base(id) 
            ON DELETE CASCADE;
        END IF;
    END $$;
    """)

    # ============================================================
    # 3. Unique constraint (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                       WHERE constraint_schema = 'fleet' 
                       AND constraint_name = 'uq_categoria_gasto_tenant_nombre') THEN
            ALTER TABLE fleet.categoria_gasto 
            ADD CONSTRAINT uq_categoria_gasto_tenant_nombre 
            UNIQUE (control_base_id, nombre);
        END IF;
    END $$;
    """)

    # ============================================================
    # 4. Index (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                       WHERE schemaname = 'fleet' 
                       AND indexname = 'ix_categoria_gasto_control_base_id') THEN
            CREATE INDEX ix_categoria_gasto_control_base_id 
            ON fleet.categoria_gasto (control_base_id);
        END IF;
    END $$;
    """)

    # ============================================================
    # 5. Agregar columnas a fleet.gasto_vehiculo (IDEMPOTENTE)
    # ============================================================
    # 5a. categoria_id
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_vehiculo' 
                       AND column_name = 'categoria_id') THEN
            ALTER TABLE fleet.gasto_vehiculo 
            ADD COLUMN categoria_id UUID;
        END IF;
    END $$;
    """)

    # 5b. subcategoria
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_vehiculo' 
                       AND column_name = 'subcategoria') THEN
            ALTER TABLE fleet.gasto_vehiculo 
            ADD COLUMN subcategoria VARCHAR(50);
        END IF;
    END $$;
    """)

    # 5c. km_registro (NUEVO, unificado)
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_vehiculo' 
                       AND column_name = 'km_registro') THEN
            ALTER TABLE fleet.gasto_vehiculo 
            ADD COLUMN km_registro NUMERIC(10,2);
        END IF;
    END $$;
    """)

    # ============================================================
    # 6. Migrar datos de kilometraje -> km_registro (si existe)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'fleet' 
                   AND table_name = 'gasto_vehiculo' 
                   AND column_name = 'kilometraje') THEN
            UPDATE fleet.gasto_vehiculo 
            SET km_registro = kilometraje::NUMERIC(10,2) 
            WHERE kilometraje IS NOT NULL AND km_registro IS NULL;
        END IF;
    END $$;
    """)

    # ============================================================
    # 7. Eliminar columna kilometraje (si existe)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'fleet' 
                   AND table_name = 'gasto_vehiculo' 
                   AND column_name = 'kilometraje') THEN
            ALTER TABLE fleet.gasto_vehiculo 
            DROP COLUMN kilometraje;
        END IF;
    END $$;
    """)

    # ============================================================
    # 8. FK para gasto_vehiculo -> categoria_gasto (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                       WHERE constraint_schema = 'fleet' 
                       AND constraint_name = 'fk_gasto_vehiculo_categoria') THEN
            ALTER TABLE fleet.gasto_vehiculo 
            ADD CONSTRAINT fk_gasto_vehiculo_categoria 
            FOREIGN KEY (categoria_id) 
            REFERENCES fleet.categoria_gasto(id) 
            ON DELETE SET NULL;
        END IF;
    END $$;
    """)

    # ============================================================
    # 9. Index para gasto_vehiculo (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                       WHERE schemaname = 'fleet' 
                       AND indexname = 'ix_gasto_vehiculo_categoria_id') THEN
            CREATE INDEX ix_gasto_vehiculo_categoria_id 
            ON fleet.gasto_vehiculo (categoria_id);
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                       WHERE schemaname = 'fleet' 
                       AND indexname = 'ix_gasto_vehiculo_km_registro') THEN
            CREATE INDEX ix_gasto_vehiculo_km_registro 
            ON fleet.gasto_vehiculo (km_registro);
        END IF;
    END $$;
    """)

    # ============================================================
    # 10. Agregar columnas a fleet.gasto_turno (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_turno' 
                       AND column_name = 'categoria_id') THEN
            ALTER TABLE fleet.gasto_turno 
            ADD COLUMN categoria_id UUID;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_turno' 
                       AND column_name = 'subcategoria') THEN
            ALTER TABLE fleet.gasto_turno 
            ADD COLUMN subcategoria VARCHAR(50);
        END IF;
    END $$;
    """)

    # ============================================================
    # 11. FK para gasto_turno -> categoria_gasto (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                       WHERE constraint_schema = 'fleet' 
                       AND constraint_name = 'fk_gasto_turno_categoria') THEN
            ALTER TABLE fleet.gasto_turno 
            ADD CONSTRAINT fk_gasto_turno_categoria 
            FOREIGN KEY (categoria_id) 
            REFERENCES fleet.categoria_gasto(id) 
            ON DELETE SET NULL;
        END IF;
    END $$;
    """)

    # ============================================================
    # 12. Index para gasto_turno (IDEMPOTENTE)
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                       WHERE schemaname = 'fleet' 
                       AND indexname = 'ix_gasto_turno_categoria_id') THEN
            CREATE INDEX ix_gasto_turno_categoria_id 
            ON fleet.gasto_turno (categoria_id);
        END IF;
    END $$;
    """)


def downgrade() -> None:
    # ============================================================
    # 1. Eliminar índices
    # ============================================================
    op.execute("DROP INDEX IF EXISTS fleet.ix_gasto_turno_categoria_id;")
    op.execute("DROP INDEX IF EXISTS fleet.ix_gasto_vehiculo_km_registro;")
    op.execute("DROP INDEX IF EXISTS fleet.ix_gasto_vehiculo_categoria_id;")
    op.execute("DROP INDEX IF EXISTS fleet.ix_categoria_gasto_control_base_id;")

    # ============================================================
    # 2. Eliminar FKs
    # ============================================================
    op.execute("ALTER TABLE fleet.gasto_turno DROP CONSTRAINT IF EXISTS fk_gasto_turno_categoria;")
    op.execute("ALTER TABLE fleet.gasto_vehiculo DROP CONSTRAINT IF EXISTS fk_gasto_vehiculo_categoria;")
    op.execute("ALTER TABLE fleet.categoria_gasto DROP CONSTRAINT IF EXISTS fk_categoria_gasto_control_base;")
    op.execute("ALTER TABLE fleet.categoria_gasto DROP CONSTRAINT IF EXISTS uq_categoria_gasto_tenant_nombre;")

    # ============================================================
    # 3. Eliminar columnas de gasto_turno
    # ============================================================
    op.execute("ALTER TABLE fleet.gasto_turno DROP COLUMN IF EXISTS subcategoria;")
    op.execute("ALTER TABLE fleet.gasto_turno DROP COLUMN IF EXISTS categoria_id;")

    # ============================================================
    # 4. Restaurar kilometraje en gasto_vehiculo
    # ============================================================
    op.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema = 'fleet' 
                       AND table_name = 'gasto_vehiculo' 
                       AND column_name = 'kilometraje') THEN
            ALTER TABLE fleet.gasto_vehiculo ADD COLUMN kilometraje INTEGER;
            UPDATE fleet.gasto_vehiculo SET kilometraje = km_registro::INTEGER WHERE km_registro IS NOT NULL;
        END IF;
    END $$;
    """)

    # ============================================================
    # 5. Eliminar columnas de gasto_vehiculo
    # ============================================================
    op.execute("ALTER TABLE fleet.gasto_vehiculo DROP COLUMN IF EXISTS km_registro;")
    op.execute("ALTER TABLE fleet.gasto_vehiculo DROP COLUMN IF EXISTS subcategoria;")
    op.execute("ALTER TABLE fleet.gasto_vehiculo DROP COLUMN IF EXISTS categoria_id;")

    # ============================================================
    # 6. Eliminar tabla categoria_gasto
    # ============================================================
    op.execute("DROP TABLE IF EXISTS fleet.categoria_gasto;")