"""m3_032: estructura para codigo persistente de viaje

Revision ID: m3_032
Revises: 611cd889a1b8

Responsabilidad unica: agregar soporte de codigo persistente.
NO toca datos existentes (el backfill va en m3_033).

Baseline del VPS: 611cd889a1b8 (migracion base real produccion).
"""
from alembic import op

revision = 'm3_032'
down_revision = '611cd889a1b8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tabla de control de correlativos por tenant+año
    op.execute("""
        CREATE TABLE trip.viaje_correlativo (
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id),
            anio integer NOT NULL,
            ultimo_numero integer NOT NULL DEFAULT 0,
            CONSTRAINT pk_viaje_correlativo
                PRIMARY KEY (control_base_id, anio)
        );
    """)

    # 2. Columna codigo (nullable por ahora; NOT NULL va en m3_033 tras backfill)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD COLUMN codigo varchar(20);
    """)

    # 3. Funcion atomica de generacion
    op.execute("""
        CREATE OR REPLACE FUNCTION trip.generar_codigo_viaje(
            p_control_base_id uuid,
            p_fecha timestamptz
        ) RETURNS varchar AS $$
        DECLARE
            v_anio integer := EXTRACT(YEAR FROM p_fecha)::int;
            v_numero integer;
        BEGIN
            INSERT INTO trip.viaje_correlativo (control_base_id, anio, ultimo_numero)
            VALUES (p_control_base_id, v_anio, 1)
            ON CONFLICT (control_base_id, anio)
            DO UPDATE SET ultimo_numero = trip.viaje_correlativo.ultimo_numero + 1
            RETURNING ultimo_numero INTO v_numero;

            RETURN 'VJ-' || v_anio || '-' || LPAD(v_numero::text, 6, '0');
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade():
    op.execute("DROP FUNCTION IF EXISTS trip.generar_codigo_viaje(uuid, timestamptz);")
    op.execute("ALTER TABLE trip.viaje_solicitado DROP COLUMN IF EXISTS codigo;")
    op.execute("DROP TABLE IF EXISTS trip.viaje_correlativo;")