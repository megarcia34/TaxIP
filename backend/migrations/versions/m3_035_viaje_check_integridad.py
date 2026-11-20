"""m3_035: CHECK constraints de integridad en viaje_solicitado

Revision ID: m3_035
Revises: m3_034

Responsabilidad unica: impedir que los datos sucios vuelvan a existir.
Requiere m3_033 (codigo NOT NULL) y m3_034 (precio limpio).
"""
from alembic import op

revision = 'm3_035'
down_revision = 'm3_034'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD CONSTRAINT ck_viaje_solicitado_cancelado_sin_precio
        CHECK (estado <> 'cancelado' OR precio_final IS NULL OR precio_final = 0);
    """)

    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD CONSTRAINT ck_viaje_solicitado_finalizado_con_precio
        CHECK (estado <> 'finalizado' OR precio_final IS NOT NULL);
    """)

    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD CONSTRAINT ck_viaje_solicitado_codigo_formato
        CHECK (codigo ~ '^VJ-[0-9]{4}-[0-9]{6}$');
    """)


def downgrade():
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        DROP CONSTRAINT IF EXISTS ck_viaje_solicitado_codigo_formato;
    """)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        DROP CONSTRAINT IF EXISTS ck_viaje_solicitado_finalizado_con_precio;
    """)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        DROP CONSTRAINT IF EXISTS ck_viaje_solicitado_cancelado_sin_precio;
    """)