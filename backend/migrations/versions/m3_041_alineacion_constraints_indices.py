"""m3_041: alineacion de constraints e indices de mantenimiento

Revision ID: m3_041
Revises: m3_040

Responsabilidad unica: alinear la DB con el ORM en los 26 items que el
diff de R25 identifico como pendientes:

1. Renombrar 8 CHECKs a la convention de SQLAlchemy (ck_<tabla>_<nombre>).
2. Crear 9 indices que el ORM declara pero la DB no tiene.
3. Alinear el comment de trip.viaje_solicitado.codigo.

NO modifica datos.
NO modifica estructura de tablas.
NO toca las tablas de mantenimiento legacy.

Baseline: m3_040 (head).
"""
from alembic import op

revision = 'm3_041'
down_revision = 'm3_040'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. Renombrar 8 CHECKs a convention SQLAlchemy
    # ============================================================
    # mantenimiento_catalogo_control
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_control
        RENAME CONSTRAINT mantenimiento_catalogo_control_tipo_check
        TO ck_mantenimiento_catalogo_control_tipo;
    """)

    # mantenimiento_catalogo_override
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_override
        RENAME CONSTRAINT mantenimiento_catalogo_override_accion_check
        TO ck_mantenimiento_catalogo_override_accion;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_override
        RENAME CONSTRAINT mantenimiento_catalogo_override_entidad_tipo_check
        TO ck_mantenimiento_catalogo_override_entidad_tipo;
    """)

    # mantenimiento_checklist_inspeccion
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT mantenimiento_checklist_inspeccion_tipo_inspeccion_check
        TO ck_mantenimiento_checklist_inspeccion_tipo_inspeccion;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT mantenimiento_checklist_inspeccion_tipo_respuesta_check
        TO ck_mantenimiento_checklist_inspeccion_tipo_respuesta;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT mantenimiento_checklist_inspeccion_severidad_default_check
        TO ck_mantenimiento_checklist_inspeccion_severidad_default;
    """)

    # mantenimiento_vehiculo_config
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo_config
        RENAME CONSTRAINT mantenimiento_vehiculo_config_motorizacion_check
        TO ck_mantenimiento_vehiculo_config_motorizacion;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo_config
        RENAME CONSTRAINT mantenimiento_vehiculo_config_transmision_check
        TO ck_mantenimiento_vehiculo_config_transmision;
    """)

    # ============================================================
    # 2. Crear 9 indices que el ORM declara pero la DB no tiene
    # ============================================================
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_sistema_orden
        ON fleet.mantenimiento_catalogo_sistema (orden);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_subsistema_sistema
        ON fleet.mantenimiento_catalogo_subsistema (sistema_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_componente_subsistema
        ON fleet.mantenimiento_catalogo_componente (subsistema_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_catalogo_control_componente
        ON fleet.mantenimiento_catalogo_control (componente_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_compatibilidad_componente
        ON fleet.mantenimiento_catalogo_componente_compatibilidad (componente_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_checklist_inspeccion_orden
        ON fleet.mantenimiento_checklist_inspeccion (orden);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_encargado_control_base
        ON fleet.encargado (control_base_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_encargado_propietario
        ON fleet.encargado (propietario_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehiculo_config_control_base
        ON fleet.mantenimiento_vehiculo_config (control_base_id);
    """)

    # ============================================================
    # 3. Alinear el comment de trip.viaje_solicitado.codigo
    # ============================================================
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.codigo
        IS 'Codigo persistente del viaje (VJ-YYYY-NNNNNN). Inmutable. Generado por trip.generar_codigo_viaje.';
    """)


def downgrade():
    # 3. Revertir comment
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.codigo
        IS 'Codigo persistente del viaje (formato VJ-YYYY-NNNNNN)';
    """)

    # 2. Eliminar 9 indices
    op.execute("DROP INDEX IF EXISTS fleet.idx_vehiculo_config_control_base;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_encargado_propietario;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_encargado_control_base;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_checklist_inspeccion_orden;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_compatibilidad_componente;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_catalogo_control_componente;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_catalogo_componente_subsistema;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_catalogo_subsistema_sistema;")
    op.execute("DROP INDEX IF EXISTS fleet.idx_catalogo_sistema_orden;")

    # 1. Renombrar 8 CHECKs de vuelta
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo_config
        RENAME CONSTRAINT ck_mantenimiento_vehiculo_config_transmision
        TO mantenimiento_vehiculo_config_transmision_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_vehiculo_config
        RENAME CONSTRAINT ck_mantenimiento_vehiculo_config_motorizacion
        TO mantenimiento_vehiculo_config_motorizacion_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT ck_mantenimiento_checklist_inspeccion_severidad_default
        TO mantenimiento_checklist_inspeccion_severidad_default_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT ck_mantenimiento_checklist_inspeccion_tipo_respuesta
        TO mantenimiento_checklist_inspeccion_tipo_respuesta_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_checklist_inspeccion
        RENAME CONSTRAINT ck_mantenimiento_checklist_inspeccion_tipo_inspeccion
        TO mantenimiento_checklist_inspeccion_tipo_inspeccion_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_override
        RENAME CONSTRAINT ck_mantenimiento_catalogo_override_entidad_tipo
        TO mantenimiento_catalogo_override_entidad_tipo_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_override
        RENAME CONSTRAINT ck_mantenimiento_catalogo_override_accion
        TO mantenimiento_catalogo_override_accion_check;
    """)
    op.execute("""
        ALTER TABLE fleet.mantenimiento_catalogo_control
        RENAME CONSTRAINT ck_mantenimiento_catalogo_control_tipo
        TO mantenimiento_catalogo_control_tipo_check;
    """)