"""m3_039_fix: mover override y plan_grupo a fleet

Revision ID: m3_039_fix
Revises: m3_039

Responsabilidad unica: mover las tablas que en m3_039 quedaron en public
a fleet, para consistencia con el resto de las tablas de flota.

Tablas movidas:
- public.mantenimiento_catalogo_override -> fleet.mantenimiento_catalogo_override
- public.mantenimiento_plan_grupo -> fleet.mantenimiento_plan_grupo

NO modifica datos.
NO modifica constraints.
Solo ALTER TABLE ... SET SCHEMA.

Baseline: m3_039 (head).
"""
from alembic import op

revision = 'm3_039_fix'
down_revision = 'm3_039'
branch_labels = None
depends_on = None


def upgrade():
    # Mover mantenimiento_catalogo_override
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_override'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_override'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_override
                SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)

    # Mover mantenimiento_plan_grupo
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_plan_grupo'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_plan_grupo'
            ) THEN
                ALTER TABLE public.mantenimiento_plan_grupo
                SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)


def downgrade():
    # Mover de vuelta a public
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_plan_grupo'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_plan_grupo'
            ) THEN
                ALTER TABLE fleet.mantenimiento_plan_grupo
                SET SCHEMA public;
            END IF;
        END
        $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_override'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_override'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_override
                SET SCHEMA public;
            END IF;
        END
        $$;
    """)