"""perfil propietario y cuentas de cobro

- Agrega cuit_cuil y condicion_impositiva a auth.perfil_general.
- Crea payment.cuenta_cobro para CBU/CVU (1 a 5 por usuario).

Revision ID: m3_022 
Revises: m3_021
Create Date: 2026-10-14
"""
from alembic import op


revision = 'm3_022'
down_revision = 'm3_021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Columnas nuevas en auth.perfil_general
    op.execute("""
        ALTER TABLE auth.perfil_general
            ADD COLUMN cuit_cuil            VARCHAR(11) NULL,
            ADD COLUMN condicion_impositiva VARCHAR(50) NULL
    """)

    # 2. CHECK de condicion_impositiva
    op.execute("""
        ALTER TABLE auth.perfil_general
            ADD CONSTRAINT ck_perfil_general_condicion_impositiva
            CHECK (
                condicion_impositiva IS NULL
                OR condicion_impositiva IN (
                    'responsable_inscripto',
                    'monotributo',
                    'exento',
                    'consumidor_final',
                    'no_categorizado'
                )
            )
    """)

    # 3. Tabla de cuentas de cobro
    op.execute("""
        CREATE TABLE payment.cuenta_cobro (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES auth.usuario(id) ON DELETE CASCADE,
            tipo VARCHAR(10) NOT NULL,
            numero VARCHAR(22) NOT NULL,
            alias VARCHAR(50) NULL,
            banco VARCHAR(100) NOT NULL,
            titular VARCHAR(200) NULL,
            predeterminada BOOLEAN NOT NULL DEFAULT false,
            activo BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    # 4. CHECK de tipo
    op.execute("""
        ALTER TABLE payment.cuenta_cobro
            ADD CONSTRAINT ck_cuenta_cobro_tipo
            CHECK (tipo IN ('cbu', 'cvu'))
    """)

    # 5. Indices
    op.execute("""
        CREATE INDEX idx_cuenta_cobro_usuario
            ON payment.cuenta_cobro(usuario_id, activo)
    """)

    op.execute("""
        CREATE UNIQUE INDEX uq_cuenta_cobro_predeterminada
            ON payment.cuenta_cobro(usuario_id)
            WHERE predeterminada = true AND activo = true
    """)

    # 6. Trigger updated_at
    op.execute("""
        CREATE TRIGGER trigger_cuenta_cobro_updated_at
            BEFORE UPDATE ON payment.cuenta_cobro
            FOR EACH ROW
            EXECUTE FUNCTION public.actualizar_updated_at()
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS trigger_cuenta_cobro_updated_at
            ON payment.cuenta_cobro
    """)

    op.execute("""
        DROP INDEX IF EXISTS payment.uq_cuenta_cobro_predeterminada
    """)

    op.execute("""
        DROP INDEX IF EXISTS payment.idx_cuenta_cobro_usuario
    """)

    op.execute("""
        DROP TABLE IF EXISTS payment.cuenta_cobro
    """)

    op.execute("""
        ALTER TABLE auth.perfil_general
            DROP CONSTRAINT IF EXISTS ck_perfil_general_condicion_impositiva
    """)

    op.execute("""
        ALTER TABLE auth.perfil_general
            DROP COLUMN IF EXISTS condicion_impositiva,
            DROP COLUMN IF EXISTS cuit_cuil
    """)