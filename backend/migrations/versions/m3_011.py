"""GIST sobre columnas Geography de ORM

Revision ID: m3_011
Revises: m3_010
Create Date: 2026-10-06

GeoAlchemy2 auto-genera un Index GIST sobre columnas Geography con
spatial_index=True (default). El ORM los declara implicitamente, pero
la DB no los tiene creados.

Estos 3 indices faltan en DB:
- fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion (sobre ubicacion).
- trip.panico.idx_panico_ubicacion (sobre ubicacion).
- trip.viaje_solicitado.idx_viaje_solicitado_destino (sobre destino).

Nota: trip.viaje_solicitado.origen ya tiene idx_viaje_origen_gist
(GIST manual declarado en el ORM). No se toca.

Impacto: habilita queries espaciales sin full scan. Deuda
orm.geoalchemy2_indices_no_aplicados.

Ver handoff R9->R10 y DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_011'
down_revision = 'm3_010'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chofer_vehiculo_ubicacion
        ON fleet.chofer_vehiculo
        USING gist (ubicacion)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_panico_ubicacion
        ON trip.panico
        USING gist (ubicacion)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_viaje_solicitado_destino
        ON trip.viaje_solicitado
        USING gist (destino)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS fleet.idx_chofer_vehiculo_ubicacion")
    op.execute("DROP INDEX IF EXISTS trip.idx_panico_ubicacion")
    op.execute("DROP INDEX IF EXISTS trip.idx_viaje_solicitado_destino")