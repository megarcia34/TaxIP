"""m3_043: planes de mantenimiento + vencimientos

Revision ID: m3_043
Revises: m3_042

Responsabilidad unica: crear las 4 tablas del modulo de planes.

Convencion de naming:
- CHECKs con name="ck_<tabla>_<nombre>" (explicito, no convention).
- UNIQUEs con name="uq_<tabla>_<columnas>" (explicito, no convention).
- Indices con name="idx_<tabla>_<columna>" (custom).
- FKs con la convention de SQLAlchemy.

Baseline: m3_041 (head).
"""
from alembic import op

revision = 'm3_043'
down_revision = 'm3_042'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. mantenimiento_plan
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.mantenimiento_plan (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            propietario_id uuid NOT NULL
                REFERENCES auth.usuario(id) ON DELETE CASCADE,
            nombre varchar(150) NOT NULL,
            tipo varchar(20) NOT NULL,
            descripcion text,
            umbrales_override jsonb,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now(),
            CONSTRAINT uq_mantenimiento_plan_tenant_propietario_nombre
                UNIQUE (control_base_id, propietario_id, nombre),
            CONSTRAINT ck_mantenimiento_plan_tipo
                CHECK (tipo IN ('preventivo', 'correctivo', 'predictivo'))
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_control_base
        ON fleet.mantenimiento_plan (control_base_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_propietario
        ON fleet.mantenimiento_plan (propietario_id);
    """)

    # ============================================================
    # 2. mantenimiento_plan_item
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.mantenimiento_plan_item (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            plan_id uuid NOT NULL
                REFERENCES fleet.mantenimiento_plan(id) ON DELETE CASCADE,
            componente_id uuid NOT NULL
                REFERENCES fleet.mantenimiento_catalogo_componente(id) ON DELETE CASCADE,
            control_id uuid
                REFERENCES fleet.mantenimiento_catalogo_control(id) ON DELETE SET NULL,
            intervalo_km int,
            intervalo_dias int,
            intervalo_meses int,
            prioridad varchar(20),
            criticidad varchar(20),
            obligatorio boolean NOT NULL DEFAULT true,
            instrucciones text,
            umbrales_override jsonb,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now(),
            CONSTRAINT ck_mantenimiento_plan_item_prioridad
                CHECK (prioridad IN ('alta', 'media', 'baja')),
            CONSTRAINT ck_mantenimiento_plan_item_criticidad
                CHECK (criticidad IN ('critica', 'importante', 'normal'))
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_item_plan
        ON fleet.mantenimiento_plan_item (plan_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_item_componente
        ON fleet.mantenimiento_plan_item (componente_id);
    """)

    # ============================================================
    # 3. mantenimiento_plan_vehiculo
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.mantenimiento_plan_vehiculo (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            plan_id uuid NOT NULL
                REFERENCES fleet.mantenimiento_plan(id) ON DELETE CASCADE,
            vehiculo_id uuid NOT NULL
                REFERENCES fleet.vehiculo(id) ON DELETE CASCADE,
            compatibilidad_override boolean NOT NULL DEFAULT false,
            compatibilidad_override_motivo text,
            compatibilidad_override_autor_id uuid
                REFERENCES auth.usuario(id) ON DELETE SET NULL,
            compatibilidad_override_en timestamp,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            CONSTRAINT uq_mantenimiento_plan_vehiculo_tenant_plan_vehiculo
                UNIQUE (control_base_id, plan_id, vehiculo_id)
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_vehiculo_plan
        ON fleet.mantenimiento_plan_vehiculo (plan_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_plan_vehiculo_vehiculo
        ON fleet.mantenimiento_plan_vehiculo (vehiculo_id);
    """)

    # ============================================================
    # 4. mantenimiento_vencimiento
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.mantenimiento_vencimiento (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            vehiculo_id uuid NOT NULL
                REFERENCES fleet.vehiculo(id) ON DELETE CASCADE,
            plan_item_id uuid NOT NULL
                REFERENCES fleet.mantenimiento_plan_item(id) ON DELETE CASCADE,
            km_actual numeric(12,2),
            km_proximo numeric(12,2),
            fecha_proximo date,
            estado varchar(20) NOT NULL,
            vigente boolean NOT NULL DEFAULT true,
            calculado_en timestamp NOT NULL DEFAULT now(),
            CONSTRAINT uq_mantenimiento_vencimiento_tenant_vehiculo_plan_item
                UNIQUE (control_base_id, vehiculo_id, plan_item_id),
            CONSTRAINT ck_mantenimiento_vencimiento_estado
                CHECK (estado IN ('normal', 'proximo', 'critico', 'vencido'))
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vencimiento_vehiculo
        ON fleet.mantenimiento_vencimiento (vehiculo_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vencimiento_estado
        ON fleet.mantenimiento_vencimiento (estado);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vencimiento_plan_item
        ON fleet.mantenimiento_vencimiento (plan_item_id);
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_vencimiento;")
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_plan_vehiculo;")
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_plan_item;")
    op.execute("DROP TABLE IF EXISTS fleet.mantenimiento_plan;")