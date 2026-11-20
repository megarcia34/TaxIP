"""m3_039: override de catalogo + grupos de plan + correcciones de km

Revision ID: m3_039
Revises: m3_038

Responsabilidad unica:
1. Crear mantenimiento_catalogo_override (override del catalogo global por tenant).
2. Crear mantenimiento_plan_grupo (grupos de vehiculos por compatibilidad).
3. Crear fleet.kilometraje_correccion (correcciones manuales de km).
4. Mover public.mantenimiento_vehiculo_config a fleet.mantenimiento_vehiculo_config.

NO crea planes (eso va en R26 con m3_040+).
NO crea OT ni intervenciones (eso va en R28).
NO toca datos existentes.

Decisiones:
- mantenimiento_catalogo_override: por tenant, permite agregar/ocultar/renombrar
  entidades del catalogo global sin duplicar el catalogo.
- mantenimiento_plan_grupo: criterios JSONB (marca, modelo, año, motorizacion).
  Se expande a filas en mantenimiento_plan_vehiculo (que se crea en R26).
- fleet.kilometraje_correccion: trazabilidad de correcciones manuales de km.
  El turno original se marca km_sospechoso=true (columna que ya existe desde m3_037).

Baseline: m3_038 (head).
"""
from alembic import op

revision = 'm3_039'
down_revision = 'm3_038'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. Mover mantenimiento_vehiculo_config de public a fleet
    # ============================================================
    # Verificar que existe en public y no en fleet (idempotente).
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public' AND tablename = 'mantenimiento_vehiculo_config'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet' AND tablename = 'mantenimiento_vehiculo_config'
            ) THEN
                ALTER TABLE public.mantenimiento_vehiculo_config
                SET SCHEMA fleet;
            END IF;
        END
        $$;
    """)

    # ============================================================
    # 2. mantenimiento_catalogo_override
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_override (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            entidad_tipo varchar(20) NOT NULL
                CHECK (entidad_tipo IN ('sistema', 'subsistema', 'componente', 'control')),
            entidad_id uuid NOT NULL,
            accion varchar(20) NOT NULL
                CHECK (accion IN ('agregar', 'ocultar', 'renombrar')),
            payload jsonb,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now(),
            UNIQUE (control_base_id, entidad_tipo, entidad_id, accion)
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_override_control_base
        ON mantenimiento_catalogo_override (control_base_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_override_entidad
        ON mantenimiento_catalogo_override (entidad_tipo, entidad_id);
    """)

    # ============================================================
    # 3. mantenimiento_plan_grupo
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_plan_grupo (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            propietario_id uuid NOT NULL
                REFERENCES auth.usuario(id) ON DELETE CASCADE,
            nombre varchar(150) NOT NULL,
            descripcion text,
            criterios jsonb NOT NULL DEFAULT '{}'::jsonb,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now(),
            UNIQUE (control_base_id, propietario_id, nombre)
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_grupo_control_base
        ON mantenimiento_plan_grupo (control_base_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_grupo_propietario
        ON mantenimiento_plan_grupo (propietario_id);
    """)

    # ============================================================
    # 4. fleet.kilometraje_correccion
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.kilometraje_correccion (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            vehiculo_id uuid NOT NULL
                REFERENCES fleet.vehiculo(id) ON DELETE CASCADE,
            turno_id uuid
                REFERENCES fleet.turno_chofer(id) ON DELETE SET NULL,
            km_anterior numeric(12,2) NOT NULL,
            km_nuevo numeric(12,2) NOT NULL,
            motivo text NOT NULL,
            autor_id uuid NOT NULL
                REFERENCES auth.usuario(id) ON DELETE CASCADE,
            created_at timestamp NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_kilometraje_correccion_vehiculo
        ON fleet.kilometraje_correccion (vehiculo_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_kilometraje_correccion_control_base
        ON fleet.kilometraje_correccion (control_base_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_kilometraje_correccion_fecha
        ON fleet.kilometraje_correccion (created_at);
    """)


def downgrade():
    # 4. fleet.kilometraje_correccion
    op.execute("DROP TABLE IF EXISTS fleet.kilometraje_correccion;")

    # 3. mantenimiento_plan_grupo
    op.execute("DROP TABLE IF EXISTS mantenimiento_plan_grupo;")

    # 2. mantenimiento_catalogo_override
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_override;")

    # 1. Mover mantenimiento_vehiculo_config de fleet a public
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'fleet' AND tablename = 'mantenimiento_vehiculo_config'
            ) AND NOT EXISTS (
                SELECT 1 FROM pg_tables
                WHERE schemaname = 'public' AND tablename = 'mantenimiento_vehiculo_config'
            ) THEN
                ALTER TABLE fleet.mantenimiento_vehiculo_config
                SET SCHEMA public;
            END IF;
        END
        $$;
    """)