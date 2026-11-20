"""m3_019 vocabulario metodo_pago corporativo + CHECK

Revision ID: m3_019
Revises: m3_018
Create Date: 2026-10-12

R18 - Flujo corporativo.

Agrega CHECK a payment.pago_empresa.metodo_pago con el vocabulario
canonico de pagos empresa -> TaxIP:

    efectivo, transferencia, tarjeta_debito, tarjeta_credito,
    deposito, cheque, otros

Antes: el campo era varchar(50) sin restriccion. Se validaba solo en
Python (empresa_dashboard.py:791).

Requiere backup DB previo.
"""
from alembic import op

revision = 'm3_019'
down_revision = 'm3_018'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE payment.pago_empresa
        ADD CONSTRAINT ck_pago_empresa_metodo_pago
        CHECK (metodo_pago IN (
            'efectivo', 'transferencia', 'tarjeta_debito', 'tarjeta_credito',
            'deposito', 'cheque', 'otros'
        ))
    """)


def downgrade():
    op.execute("""
        ALTER TABLE payment.pago_empresa
        DROP CONSTRAINT ck_pago_empresa_metodo_pago
    """)