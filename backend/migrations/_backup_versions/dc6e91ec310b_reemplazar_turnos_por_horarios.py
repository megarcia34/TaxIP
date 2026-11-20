"""reemplazar turno_asignado por horarios flexibles

Revision ID: dc6e91ec310b
Revises: d98875bb2f42
Create Date: 2026-08-17 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dc6e91ec310b'
down_revision: Union[str, None] = 'd98875bb2f42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 0. ELIMINAR CONSTRAINT check_turno (bloquea el drop de columna)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'check_turno'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                DROP CONSTRAINT check_turno;
            END IF;
        END $$;
    """)

    # ============================================================
    # 1. AGREGAR NUEVAS COLUMNAS DE HORARIOS FLEXIBLES
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- contrato_vehiculo
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='hora_inicio') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN hora_inicio TIME;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='hora_fin') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN hora_fin TIME;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='duracion_minima_horas') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN duracion_minima_horas INTEGER DEFAULT 6;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='permite_extension') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN permite_extension BOOLEAN DEFAULT false;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='hora_fin_extension') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN hora_fin_extension TIME;
            END IF;

            -- turno_chofer (snapshots)
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_hora_inicio') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_hora_inicio TIME;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_hora_fin') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_hora_fin TIME;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_duracion_minima_horas') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_duracion_minima_horas INTEGER;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_permite_extension') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_permite_extension BOOLEAN;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_hora_fin_extension') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_hora_fin_extension TIME;
            END IF;
        END $$;
    """)

    # ============================================================
    # 2. MIGRAR DATOS EXISTENTES
    # ============================================================
    op.execute("""
        UPDATE fleet.contrato_vehiculo
        SET 
            hora_inicio = CASE 
                WHEN turno_asignado = 'DIURNO' THEN '06:00:00'::time
                WHEN turno_asignado = 'NOCTURNO' THEN '22:00:00'::time
                WHEN turno_asignado = 'COMPLETO' THEN '00:00:00'::time
                ELSE NULL
            END,
            hora_fin = CASE 
                WHEN turno_asignado = 'DIURNO' THEN '14:00:00'::time
                WHEN turno_asignado = 'NOCTURNO' THEN '06:00:00'::time
                WHEN turno_asignado = 'COMPLETO' THEN '23:59:00'::time
                ELSE NULL
            END,
            duracion_minima_horas = 6,
            permite_extension = false
        WHERE turno_asignado IS NOT NULL
          AND hora_inicio IS NULL
    """)

    # Migrar snapshots en turno_chofer (solo si la columna snapshot_turno_contractual existe)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema='fleet' AND table_name='turno_chofer' 
                       AND column_name='snapshot_turno_contractual') THEN
                UPDATE fleet.turno_chofer
                SET 
                    snapshot_hora_inicio = CASE 
                        WHEN snapshot_turno_contractual = 'DIURNO' THEN '06:00:00'::time
                        WHEN snapshot_turno_contractual = 'NOCTURNO' THEN '22:00:00'::time
                        WHEN snapshot_turno_contractual = 'COMPLETO' THEN '00:00:00'::time
                        ELSE NULL
                    END,
                    snapshot_hora_fin = CASE 
                        WHEN snapshot_turno_contractual = 'DIURNO' THEN '14:00:00'::time
                        WHEN snapshot_turno_contractual = 'NOCTURNO' THEN '06:00:00'::time
                        WHEN snapshot_turno_contractual = 'COMPLETO' THEN '23:59:00'::time
                        ELSE NULL
                    END,
                    snapshot_duracion_minima_horas = 6,
                    snapshot_permite_extension = false
                WHERE snapshot_turno_contractual IS NOT NULL
                  AND snapshot_hora_inicio IS NULL;
            END IF;
        END $$;
    """)

    # ============================================================
    # 3. AGREGAR CONSTRAINTS (CORREGIDOS para turnos nocturnos)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            -- hora_fin puede ser < hora_inicio (turno nocturno cruza medianoche)
            -- Solo validamos que no sean iguales
            IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints 
                           WHERE constraint_name = 'ck_contrato_horario_valido') THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_horario_valido 
                CHECK (hora_fin IS NULL OR hora_inicio IS NULL OR hora_fin <> hora_inicio);
            END IF;

            -- Extension valida
            IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints 
                           WHERE constraint_name = 'ck_contrato_extension_valida') THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_extension_valida 
                CHECK (
                    (permite_extension = false AND hora_fin_extension IS NULL) OR 
                    (permite_extension = true AND hora_fin_extension IS NOT NULL)
                );
            END IF;

            -- Duracion minima >= 1
            IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints 
                           WHERE constraint_name = 'ck_contrato_duracion_minima') THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT ck_contrato_duracion_minima 
                CHECK (duracion_minima_horas IS NULL OR duracion_minima_horas >= 1);
            END IF;
        END $$;
    """)

    # ============================================================
    # 4. ELIMINAR COLUMNAS OBSOLETAS
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                       AND column_name='turno_asignado') THEN
                ALTER TABLE fleet.contrato_vehiculo DROP COLUMN turno_asignado;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_schema='fleet' AND table_name='turno_chofer' 
                       AND column_name='snapshot_turno_contractual') THEN
                ALTER TABLE fleet.turno_chofer DROP COLUMN snapshot_turno_contractual;
            END IF;
        END $$;
    """)

    # ============================================================
    # 5. HACER COLUMNAS NOT NULL
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM fleet.contrato_vehiculo WHERE hora_inicio IS NULL) THEN
                ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN hora_inicio SET NOT NULL;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM fleet.contrato_vehiculo WHERE hora_fin IS NULL) THEN
                ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN hora_fin SET NOT NULL;
            END IF;

            ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN duracion_minima_horas SET DEFAULT 6;
            ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN duracion_minima_horas SET NOT NULL;

            ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN permite_extension SET DEFAULT false;
            ALTER TABLE fleet.contrato_vehiculo ALTER COLUMN permite_extension SET NOT NULL;
        END $$;
    """)

    # ============================================================
    # 6. ÍNDICES
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                           WHERE schemaname='fleet' AND tablename='contrato_vehiculo' 
                           AND indexname='ix_contrato_vehiculo_hora_inicio') THEN
                CREATE INDEX ix_contrato_vehiculo_hora_inicio 
                ON fleet.contrato_vehiculo(hora_inicio);
            END IF;

            IF NOT EXISTS (SELECT 1 FROM pg_indexes 
                           WHERE schemaname='fleet' AND tablename='contrato_vehiculo' 
                           AND indexname='ix_contrato_vehiculo_hora_fin') THEN
                CREATE INDEX ix_contrato_vehiculo_hora_fin 
                ON fleet.contrato_vehiculo(hora_fin);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 1. Eliminar índices
    op.execute("DROP INDEX IF EXISTS fleet.ix_contrato_vehiculo_hora_fin")
    op.execute("DROP INDEX IF EXISTS fleet.ix_contrato_vehiculo_hora_inicio")

    # 2. Eliminar constraints
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_duracion_minima")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_extension_valida")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS ck_contrato_horario_valido")

    # 3. Restaurar turno_asignado
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='contrato_vehiculo' 
                           AND column_name='turno_asignado') THEN
                ALTER TABLE fleet.contrato_vehiculo ADD COLUMN turno_asignado VARCHAR(20);
            END IF;
        END $$;
    """)

    op.execute("""
        UPDATE fleet.contrato_vehiculo
        SET turno_asignado = CASE 
            WHEN hora_inicio = '06:00:00'::time AND hora_fin = '14:00:00'::time THEN 'DIURNO'
            WHEN hora_inicio = '22:00:00'::time AND hora_fin = '06:00:00'::time THEN 'NOCTURNO'
            WHEN hora_inicio = '00:00:00'::time AND hora_fin = '23:59:00'::time THEN 'COMPLETO'
            ELSE NULL
        END
        WHERE hora_inicio IS NOT NULL AND hora_fin IS NOT NULL
    """)

    # Restaurar constraint check_turno
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints 
                           WHERE constraint_name = 'check_turno') THEN
                ALTER TABLE fleet.contrato_vehiculo 
                ADD CONSTRAINT check_turno 
                CHECK (turno_asignado IN ('DIURNO', 'NOCTURNO', 'COMPLETO'));
            END IF;
        END $$;
    """)

    # 4. Restaurar snapshot_turno_contractual
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_schema='fleet' AND table_name='turno_chofer' 
                           AND column_name='snapshot_turno_contractual') THEN
                ALTER TABLE fleet.turno_chofer ADD COLUMN snapshot_turno_contractual VARCHAR(20);
            END IF;
        END $$;
    """)

    op.execute("""
        UPDATE fleet.turno_chofer
        SET snapshot_turno_contractual = CASE 
            WHEN snapshot_hora_inicio = '06:00:00'::time AND snapshot_hora_fin = '14:00:00'::time THEN 'DIURNO'
            WHEN snapshot_hora_inicio = '22:00:00'::time AND snapshot_hora_fin = '06:00:00'::time THEN 'NOCTURNO'
            WHEN snapshot_hora_inicio = '00:00:00'::time AND snapshot_hora_fin = '23:59:00'::time THEN 'COMPLETO'
            ELSE NULL
        END
        WHERE snapshot_hora_inicio IS NOT NULL AND snapshot_hora_fin IS NOT NULL
    """)

    # 5. Eliminar nuevas columnas
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS snapshot_hora_fin_extension")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS snapshot_permite_extension")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS snapshot_duracion_minima_horas")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS snapshot_hora_fin")
    op.execute("ALTER TABLE fleet.turno_chofer DROP COLUMN IF EXISTS snapshot_hora_inicio")

    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS hora_fin_extension")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS permite_extension")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS duracion_minima_horas")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS hora_fin")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP COLUMN IF EXISTS hora_inicio")