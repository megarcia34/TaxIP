"""m3_018 limpiar indices redundantes R16

Revision ID: m3_018
Revises: m3_017
Create Date: 2026-10-11

Ronda 16 - Deuda tecnica de tooling, Bloque B.

Cambios:

1. Elimina el indice ix_viaje_estado de trip.viaje_solicitado. Es
   redundante con idx_viaje_estado (mismo tipo, misma columna).

2. Elimina el indice idx_comercio_codigo_qr de public.comercio. Es
   redundante con comercio_codigo_qr_key (UNIQUE sobre la misma columna,
   generado por unique=True en el ORM).

Nota: los constraints con nombres numericos
(63669_63825_1_not_null, 63669_63825_38_not_null) no existen en la DB
ni en el ORM. Deuda marcada como cerrada (falso positivo).

Requiere backup DB previo (docs/backups/taxip_db_ronda16.dump).

Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_018'
down_revision = 'm3_017'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Eliminar indice redundante en trip.viaje_solicitado
    op.execute("DROP INDEX trip.ix_viaje_estado")

    # 2. Eliminar indice redundante en public.comercio
    op.execute("DROP INDEX public.idx_comercio_codigo_qr")


def downgrade():
    # 1. Restaurar ix_viaje_estado
    op.execute("""
        CREATE INDEX ix_viaje_estado
        ON trip.viaje_solicitado USING btree (estado)
    """)

    # 2. Restaurar idx_comercio_codigo_qr
    op.execute("""
        CREATE INDEX idx_comercio_codigo_qr
        ON public.comercio USING btree (codigo_qr)
    """)