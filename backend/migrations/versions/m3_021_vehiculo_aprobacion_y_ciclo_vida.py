"""vehiculo: aprobacion y ciclo de vida

Agrega campos de aprobacion, documentacion y ciclo de vida a fleet.vehiculo.
Agrega parametros de configuracion al tenant.

Revision ID: m3_021
Revises: m3_020
Create Date: 2026-10-13

Reglas del proyecto:
- No usar autogenerate.
- Toda operacion con op.execute (SQL raw).
- ASCII puro en comentarios y docstrings.
- UTF-8 sin BOM.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'm3_021'
down_revision = 'm3_020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Agrega columnas de aprobacion y ciclo de vida a fleet.vehiculo.
    Agrega parametros de configuracion al tenant.
    """

    # 1. Columnas nuevas en fleet.vehiculo
    op.execute("""
        ALTER TABLE fleet.vehiculo
            ADD COLUMN estado_aprobacion        VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            ADD COLUMN documentacion_completa   BOOLEAN     NOT NULL DEFAULT false,
            ADD COLUMN fecha_vencimiento_taxi   DATE        NULL,
            ADD COLUMN override_antiguedad      BOOLEAN     NOT NULL DEFAULT false,
            ADD COLUMN en_revision_desde        TIMESTAMP   NULL,
            ADD COLUMN en_revision_expira_en    TIMESTAMP   NULL,
            ADD COLUMN aprobado_por             UUID        NULL,
            ADD COLUMN aprobado_en              TIMESTAMP   NULL,
            ADD COLUMN rechazado_por            UUID        NULL,
            ADD COLUMN rechazado_en             TIMESTAMP   NULL,
            ADD COLUMN motivo_rechazo           TEXT        NULL
    """)

    # 2. CHECK de estado_aprobacion
    op.execute("""
        ALTER TABLE fleet.vehiculo
            ADD CONSTRAINT ck_vehiculo_estado_aprobacion
            CHECK (estado_aprobacion IN (
                'pendiente', 'en_revision', 'aprobado', 'rechazado'
            ))
    """)

    # 3. FKs de auditoria
    op.execute("""
        ALTER TABLE fleet.vehiculo
            ADD CONSTRAINT fk_vehiculo_aprobado_por
                FOREIGN KEY (aprobado_por) REFERENCES auth.usuario(id),
            ADD CONSTRAINT fk_vehiculo_rechazado_por
                FOREIGN KEY (rechazado_por) REFERENCES auth.usuario(id)
    """)

    # 4. Parametros de configuracion del tenant
    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
            ADD COLUMN antiguedad_maxima_taxi_anios INTEGER NOT NULL DEFAULT 10,
            ADD COLUMN dias_revision_documentos      INTEGER NOT NULL DEFAULT 7
    """)

    # 5. CHECKs de configuracion
    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
            ADD CONSTRAINT ck_configuracion_tenant_antiguedad_maxima
                CHECK (antiguedad_maxima_taxi_anios > 0),
            ADD CONSTRAINT ck_configuracion_tenant_dias_revision
                CHECK (dias_revision_documentos > 0)
    """)

    # 6. Poblar fecha_vencimiento_taxi para vehiculos existentes
    #    Se usa anio del modelo si existe, si no el anio de created_at.
    #    Se asume antiguedad maxima default = 10 anios.
    op.execute("""
        UPDATE fleet.vehiculo v
        SET fecha_vencimiento_taxi = make_date(
            COALESCE(v.anio, EXTRACT(YEAR FROM v.created_at)::int) + 10,
            12, 31
        )
        WHERE v.fecha_vencimiento_taxi IS NULL
    """)


def downgrade() -> None:
    """
    Revierte los cambios de la migracion m3_021.
    """

    # 1. Revertir parametros del tenant
    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
            DROP CONSTRAINT IF EXISTS ck_configuracion_tenant_dias_revision,
            DROP CONSTRAINT IF EXISTS ck_configuracion_tenant_antiguedad_maxima
    """)

    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
            DROP COLUMN IF EXISTS dias_revision_documentos,
            DROP COLUMN IF EXISTS antiguedad_maxima_taxi_anios
    """)

    # 2. Revertir columnas de fleet.vehiculo
    op.execute("""
        ALTER TABLE fleet.vehiculo
            DROP CONSTRAINT IF EXISTS fk_vehiculo_rechazado_por,
            DROP CONSTRAINT IF EXISTS fk_vehiculo_aprobado_por,
            DROP CONSTRAINT IF EXISTS ck_vehiculo_estado_aprobacion
    """)

    op.execute("""
        ALTER TABLE fleet.vehiculo
            DROP COLUMN IF EXISTS motivo_rechazo,
            DROP COLUMN IF EXISTS rechazado_en,
            DROP COLUMN IF EXISTS rechazado_por,
            DROP COLUMN IF EXISTS aprobado_en,
            DROP COLUMN IF EXISTS aprobado_por,
            DROP COLUMN IF EXISTS en_revision_expira_en,
            DROP COLUMN IF EXISTS en_revision_desde,
            DROP COLUMN IF EXISTS override_antiguedad,
            DROP COLUMN IF EXISTS fecha_vencimiento_taxi,
            DROP COLUMN IF EXISTS documentacion_completa,
            DROP COLUMN IF EXISTS estado_aprobacion
    """)