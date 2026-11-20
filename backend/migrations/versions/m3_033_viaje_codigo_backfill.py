"""m3_033: backfill de codigo en viajes existentes

Revision ID: m3_033
Revises: m3_032

Responsabilidad unica: poblar codigo en viajes existentes, cerrar la columna
(NOT NULL + UNIQUE + indice).
"""
from alembic import op

revision = 'm3_033'
down_revision = 'm3_032'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Backfill: numerar por tenant+año, por created_at, id como desempate
    op.execute("""
        WITH numerados AS (
            SELECT
                id,
                control_base_id,
                EXTRACT(YEAR FROM created_at)::int AS anio,
                ROW_NUMBER() OVER (
                    PARTITION BY control_base_id, EXTRACT(YEAR FROM created_at)
                    ORDER BY created_at ASC, id ASC
                ) AS numero
            FROM trip.viaje_solicitado
        )
        UPDATE trip.viaje_solicitado vs
        SET codigo = 'VJ-' || n.anio || '-' || LPAD(n.numero::text, 6, '0')
        FROM numerados n
        WHERE vs.id = n.id
          AND vs.codigo IS NULL;
    """)

    # 2. Inicializar tabla de control con el ultimo numero real
    op.execute("""
        INSERT INTO trip.viaje_correlativo (control_base_id, anio, ultimo_numero)
        SELECT
            control_base_id,
            EXTRACT(YEAR FROM created_at)::int AS anio,
            MAX(CAST(SUBSTRING(codigo FROM '[0-9]+$') AS integer)) AS ultimo
        FROM trip.viaje_solicitado
        WHERE codigo IS NOT NULL
        GROUP BY control_base_id, EXTRACT(YEAR FROM created_at)
        ON CONFLICT (control_base_id, anio)
        DO UPDATE SET ultimo_numero = EXCLUDED.ultimo_numero;
    """)

    # 3. Cerrar la columna
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ALTER COLUMN codigo SET NOT NULL;
    """)

    # 4. Unicidad
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD CONSTRAINT uq_viaje_solicitado_codigo UNIQUE (codigo);
    """)

    # 5. Indice para busquedas por codigo
    op.execute("""
        CREATE INDEX ix_viaje_solicitado_codigo
        ON trip.viaje_solicitado(codigo);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS trip.ix_viaje_solicitado_codigo;")
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        DROP CONSTRAINT IF EXISTS uq_viaje_solicitado_codigo;
    """)
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ALTER COLUMN codigo DROP NOT NULL;
    """)
    op.execute("""
        UPDATE trip.viaje_solicitado SET codigo = NULL WHERE codigo IS NOT NULL;
    """)