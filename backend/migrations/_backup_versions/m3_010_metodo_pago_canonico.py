"""metodo_pago canonico en trip.viaje_solicitado

Revision ID: m3_010
Revises: m3_009
Create Date: 2026-09-30

Normaliza trip.viaje_solicitado.metodo_pago a los 4 valores canonicos
del negocio (efectivo, tarjeta_debito, qr, transferencia) y agrega
CHECK constraint.

Deuda B7. Ver bitacora M3.
"""
from alembic import op

revision = 'm3_010'
down_revision = 'm3_009'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Normalizar datos simulados (30 NULL + 6 billetera = 36 filas).
    #    Distribucion: 15 efectivo, 9 tarjeta_debito, 8 qr, 4 transferencia.
    op.execute("""
        WITH objetivo AS (
            SELECT id,
                   ROW_NUMBER() OVER (ORDER BY random()) AS rn
            FROM trip.viaje_solicitado
            WHERE metodo_pago IS NULL OR metodo_pago = 'billetera'
        )
        UPDATE trip.viaje_solicitado v
        SET metodo_pago = CASE
            WHEN o.rn <= 15 THEN 'efectivo'
            WHEN o.rn <= 24 THEN 'tarjeta_debito'
            WHEN o.rn <= 32 THEN 'qr'
            ELSE 'transferencia'
        END
        FROM objetivo o
        WHERE v.id = o.id
    """)

    # 2. CHECK constraint. NULL permitido para viajes sin info de pago.
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        ADD CONSTRAINT ck_viaje_solicitado_metodo_pago
        CHECK (
            metodo_pago IS NULL
            OR metodo_pago IN ('efectivo', 'tarjeta_debito', 'qr', 'transferencia')
        )
    """)

    # 3. Comment de columna. Fuente de verdad para futuros devs.
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.metodo_pago IS
        'Medio de pago del pasajero. Valores canonicos: efectivo, tarjeta_debito, qr, transferencia. NULL permitido para viajes sin info. Billetera se agregara cuando se implemente la wallet TaxIP. Deuda B7.'
    """)


def downgrade():
    op.execute("""
        ALTER TABLE trip.viaje_solicitado
        DROP CONSTRAINT IF EXISTS ck_viaje_solicitado_metodo_pago
    """)
    # NOTA: no se revierten los datos normalizados. Los NULL y 'billetera'
    # originales eran datos simulados, no hay valor real que recuperar.