"""m3_016 limpiar catalogo metodo_pago + UNIQUE + CHECK

Revision ID: m3_016
Revises: m3_015
Create Date: 2026-10-11

Ronda 15 - Deuda tecnica funcional.

Limpia el catalogo payment.metodo_pago:

- Elimina 8 filas sobrantes (duplicados literales, sinonimos, valores
  que pertenecen a otros dominios o a etapas futuras).
- Conserva 4 filas del vocabulario canonico Momento 1:
  efectivo, tarjeta_debito, qr, transferencia.
- Agrega UNIQUE sobre nombre (uq_metodo_pago_nombre).
- Agrega CHECK con el vocabulario canonico (ck_metodo_pago_nombre).
- Actualiza comment de la tabla.

Contexto de negocio (R15):
- Momento 1 (hoy): viajes comunes pagan con efectivo/tarjeta_debito/qr/transferencia.
- Momento 2 (futuro): viajes corporativos con cuenta corriente (vocabulario propio).
- Momento 3 (futuro): billetera TaxIP con saldo (se agregara 'billetera' al CHECK).

Verificacion pre-migracion: 0 transacciones referencian el catalogo.

Requiere backup DB previo (docs/backups/taxip_db_ronda15.dump).

Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_016'
down_revision = 'm3_015'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Eliminar 8 filas sobrantes por UUID (no por nombre: hay duplicados)
    op.execute("""
        DELETE FROM payment.metodo_pago
        WHERE id IN (
            'fe092c54-41a9-4146-b0cc-3f5877a246ac',
            '485fde34-f8b0-4129-a9bf-cb05484fa1a7',
            '07ea1d08-a363-420f-81da-20b36c077223',
            '44b8881e-dc1a-4131-8de6-a0b2a4930b88',
            'e089ac07-7413-4c15-9eff-28d12e2fb2bd',
            'd4e6243c-2220-4f47-b2f7-68c3b9d191bc',
            '3d0ed074-ebd4-425f-8e47-4874db5b4d1d',
            '73c5600b-b276-44ec-92b7-91dd422839e3'
        )
    """)

    # 2. UNIQUE sobre nombre
    op.execute("""
        ALTER TABLE payment.metodo_pago
        ADD CONSTRAINT uq_metodo_pago_nombre UNIQUE (nombre)
    """)

    # 3. CHECK con vocabulario canonico Momento 1
    op.execute("""
        ALTER TABLE payment.metodo_pago
        ADD CONSTRAINT ck_metodo_pago_nombre
        CHECK (nombre IN ('efectivo', 'tarjeta_debito', 'qr', 'transferencia'))
    """)

    # 4. Comment de tabla
    op.execute("""
        COMMENT ON TABLE payment.metodo_pago IS
        'Catalogo de metodos de pago para viajes comunes (Momento 1). '
        'Valores canonicos: efectivo, tarjeta_debito, qr, transferencia.'
    """)


def downgrade():
    # 1. Restaurar comment previo (vacio)
    op.execute("COMMENT ON TABLE payment.metodo_pago IS NULL")

    # 2. Eliminar CHECK
    op.execute("""
        ALTER TABLE payment.metodo_pago
        DROP CONSTRAINT ck_metodo_pago_nombre
    """)

    # 3. Eliminar UNIQUE
    op.execute("""
        ALTER TABLE payment.metodo_pago
        DROP CONSTRAINT uq_metodo_pago_nombre
    """)

    # 4. Re-insertar filas con UUIDs originales
    op.execute("""
        INSERT INTO payment.metodo_pago (id, nombre) VALUES
            ('fe092c54-41a9-4146-b0cc-3f5877a246ac', 'efectivo'),
            ('485fde34-f8b0-4129-a9bf-cb05484fa1a7', 'tarjeta_credito'),
            ('07ea1d08-a363-420f-81da-20b36c077223', 'billetera'),
            ('44b8881e-dc1a-4131-8de6-a0b2a4930b88', 'wallet'),
            ('e089ac07-7413-4c15-9eff-28d12e2fb2bd', 'credito'),
            ('d4e6243c-2220-4f47-b2f7-68c3b9d191bc', 'debito'),
            ('3d0ed074-ebd4-425f-8e47-4874db5b4d1d', 'mercadopago'),
            ('73c5600b-b276-44ec-92b7-91dd422839e3', 'mercadopago')
    """)
