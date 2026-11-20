"""m3_037: columnas base de mantenimiento en tablas existentes

Revision ID: m3_037
Revises: m3_036

Responsabilidad unica: agregar las columnas que el modulo de mantenimiento
necesita en tablas existentes, y backfillear estado_operativo y control_base_id.

NO crea tablas nuevas (eso va en m3_038 y m3_039).
NO toca datos existentes mas alla de los backfills.

Decisiones:
- mantenimiento_vehiculo.control_base_id: NULLABLE (consistente con
  vehiculo.control_base_id, que es nullable). Backfill desde vehiculo.
- vehiculo.estado_operativo: DEFAULT 'sin_verificar' (P13). Los vehiculos
  existentes siguen operando por habilitado_para_operar=true.
- Indices con nombres custom idx_* (consistente con la DB real).

Baseline: m3_036 (head).
"""
from alembic import op

revision = 'm3_037'
down_revision = 'm3_036'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. fleet.vehiculo: estado_operativo + habilitado + verificacion
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.vehiculo
        ADD COLUMN IF NOT EXISTS estado_operativo varchar(20)
            NOT NULL DEFAULT 'sin_verificar';
    """)

    # CHECK de estado_operativo (idempotente via DO block)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_vehiculo_estado_operativo'
                  AND conrelid = 'fleet.vehiculo'::regclass
            ) THEN
                ALTER TABLE fleet.vehiculo
                ADD CONSTRAINT ck_vehiculo_estado_operativo
                CHECK (estado_operativo IN (
                    'sin_verificar',
                    'en_servicio',
                    'servicio_limitado',
                    'fuera_servicio'
                ));
            END IF;
        END
        $$;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehiculo_estado_operativo
        ON fleet.vehiculo (estado_operativo);
    """)

    op.execute("""
        ALTER TABLE fleet.vehiculo
        ADD COLUMN IF NOT EXISTS habilitado_para_operar boolean
            NOT NULL DEFAULT true;
    """)

    op.execute("""
        ALTER TABLE fleet.vehiculo
        ADD COLUMN IF NOT EXISTS verificacion_tecnica_pendiente boolean
            NOT NULL DEFAULT true;
    """)

    # Backfill explicito (redundante por DEFAULT, pero por si hay NULLs)
    op.execute("""
        UPDATE fleet.vehiculo
        SET estado_operativo = 'sin_verificar'
        WHERE estado_operativo IS NULL;
    """)

    # ============================================================
    # 2. fleet.mantenimiento_vehiculo: control_base_id (nullable)
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo
        ADD COLUMN IF NOT EXISTS control_base_id uuid;
    """)

    # FK a tenant.control_base (idempotente via DO block)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'fk_mantenimiento_vehiculo_control_base'
                  AND conrelid = 'fleet.mantenimiento_vehiculo'::regclass
            ) THEN
                ALTER TABLE fleet.mantenimiento_vehiculo
                ADD CONSTRAINT fk_mantenimiento_vehiculo_control_base
                FOREIGN KEY (control_base_id)
                REFERENCES tenant.control_base(id)
                ON DELETE CASCADE;
            END IF;
        END
        $$;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_mantenimiento_vehiculo_control_base
        ON fleet.mantenimiento_vehiculo (control_base_id);
    """)

    # Backfill desde vehiculo.control_base_id
    op.execute("""
        UPDATE fleet.mantenimiento_vehiculo mv
        SET control_base_id = v.control_base_id
        FROM fleet.vehiculo v
        WHERE mv.vehiculo_id = v.id
          AND mv.control_base_id IS NULL;
    """)

    # ============================================================
    # 3. fleet.turno_chofer: km_sospechoso
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD COLUMN IF NOT EXISTS km_sospechoso boolean
            NOT NULL DEFAULT false;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_turno_chofer_km_sospechoso
        ON fleet.turno_chofer (km_sospechoso)
        WHERE km_sospechoso = true;
    """)


def downgrade():
    # ============================================================
    # 3. fleet.turno_chofer: km_sospechoso (inverso)
    # ============================================================
    op.execute("""
        DROP INDEX IF EXISTS fleet.idx_turno_chofer_km_sospechoso;
    """)
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP COLUMN IF EXISTS km_sospechoso;
    """)

    # ============================================================
    # 2. fleet.mantenimiento_vehiculo: control_base_id (inverso)
    # ============================================================
    op.execute("""
        DROP INDEX IF EXISTS fleet.idx_mantenimiento_vehiculo_control_base;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo
        DROP CONSTRAINT IF EXISTS fk_mantenimiento_vehiculo_control_base;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo
        DROP COLUMN IF EXISTS control_base_id;
    """)

    # ============================================================
    # 1. fleet.vehiculo: estado_operativo + habilitado + verificacion (inverso)
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.vehiculo
        DROP COLUMN IF EXISTS verificacion_tecnica_pendiente;
    """)
    op.execute("""
        ALTER TABLE fleet.vehiculo
        DROP COLUMN IF EXISTS habilitado_para_operar;
    """)
    op.execute("""
        DROP INDEX IF EXISTS fleet.idx_vehiculo_estado_operativo;
    """)
    op.execute("""
        ALTER TABLE fleet.vehiculo
        DROP CONSTRAINT IF EXISTS ck_vehiculo_estado_operativo;
    """)
    op.execute("""
        ALTER TABLE fleet.vehiculo
        DROP COLUMN IF EXISTS estado_operativo;
    """)