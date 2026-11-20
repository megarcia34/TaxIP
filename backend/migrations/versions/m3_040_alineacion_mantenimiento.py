"""m3_040: alineacion de mantenimiento (FK, comments, schemas, backup)

Revision ID: m3_040
Revises: m3_039_fix

Responsabilidad unica: alinear la DB con el ORM en los 6 items que el
diff de R25 identifico como pendientes:

1. Agregar FK fk_turno_chofer_conciliado_por_usuario (R24, faltaba en DB).
2. Agregar COMMENT ON COLUMN en 4 columnas (R24 + R25).
3. Mover 6 tablas de catalogo de public a fleet (consistencia).
4. Eliminar audit._backup_m3_034 (tabla de backup manual ya validada).

NO toca datos.
NO modifica estructura de columnas existentes.
NO toca las tablas de mantenimiento que se mueven (solo schema).

Baseline: m3_039_fix (head).
"""
from alembic import op

revision = 'm3_040'
down_revision = 'm3_039_fix'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. FK fk_turno_chofer_conciliado_por_usuario (R24)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'fk_turno_chofer_conciliado_por_usuario'
                  AND conrelid = 'fleet.turno_chofer'::regclass
            ) THEN
                ALTER TABLE fleet.turno_chofer
                ADD CONSTRAINT fk_turno_chofer_conciliado_por_usuario
                FOREIGN KEY (conciliado_por) REFERENCES auth.usuario(id);
            END IF;
        END
        $$;
    """)

    # ============================================================
    # 2. COMMENT ON COLUMN (4 columnas)
    # ============================================================
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.conciliado_en
        IS 'Fecha y hora en que se cerró la conciliación';
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.conciliado_por
        IS 'Usuario que concilió el turno (propietario o sistema)';
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.tipo_conciliacion
        IS 'Tipo de conciliación aplicada al cerrar el turno (AUTOMATICA, MANUAL, etc.)';
    """)
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.codigo
        IS 'Codigo persistente del viaje (formato VJ-YYYY-NNNNNN)';
    """)

    # ============================================================
    # 3. Mover 6 tablas de catalogo de public a fleet
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_sistema'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_sistema'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_sistema SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_subsistema'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_subsistema'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_subsistema SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_componente'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_componente'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_componente SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_control'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_control'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_control SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_componente_compatibilidad'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_catalogo_componente_compatibilidad'
            ) THEN
                ALTER TABLE public.mantenimiento_catalogo_componente_compatibilidad SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_checklist_inspeccion'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_checklist_inspeccion'
            ) THEN
                ALTER TABLE public.mantenimiento_checklist_inspeccion SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)

    # ============================================================
    # 4. Eliminar audit._backup_m3_034
    # ============================================================
    op.execute("""
        DROP TABLE IF EXISTS audit._backup_m3_034;
    """)


def downgrade():
    # 4. Recrear audit._backup_m3_034 (no se puede, era backup)
    # Se documenta como no-op.
    op.execute("""
        -- No-op: audit._backup_m3_034 era una tabla de backup manual.
        -- Si se necesita, restaurar desde el dump correspondiente.
    """)

    # 3. Mover tablas de fleet a public
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet'
                  AND tablename = 'mantenimiento_checklist_inspeccion'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_checklist_inspeccion'
            ) THEN
                ALTER TABLE fleet.mantenimiento_checklist_inspeccion SET SCHEMA public;
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
                  AND tablename = 'mantenimiento_catalogo_componente_compatibilidad'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_componente_compatibilidad'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_componente_compatibilidad SET SCHEMA public;
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
                  AND tablename = 'mantenimiento_catalogo_control'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_control'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_control SET SCHEMA public;
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
                  AND tablename = 'mantenimiento_catalogo_componente'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_componente'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_componente SET SCHEMA public;
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
                  AND tablename = 'mantenimiento_catalogo_subsistema'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_subsistema'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_subsistema SET SCHEMA public;
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
                  AND tablename = 'mantenimiento_catalogo_sistema'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = 'mantenimiento_catalogo_sistema'
            ) THEN
                ALTER TABLE fleet.mantenimiento_catalogo_sistema SET SCHEMA public;
            END IF;
        END
        $$;
    """)

    # 2. Quitar comments (opcional; el down los revierte)
    op.execute("COMMENT ON COLUMN trip.viaje_solicitado.codigo IS NULL;")
    op.execute("COMMENT ON COLUMN fleet.turno_chofer.tipo_conciliacion IS NULL;")
    op.execute("COMMENT ON COLUMN fleet.turno_chofer.conciliado_por IS NULL;")
    op.execute("COMMENT ON COLUMN fleet.turno_chofer.conciliado_en IS NULL;")

    # 1. Quitar FK
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP CONSTRAINT IF EXISTS fk_turno_chofer_conciliado_por_usuario;
    """)