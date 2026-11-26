
"""m3_042: crear tabla payment.vinculacion_mp para OAuth de Mercado Pago

Revision ID: m3_042
Revises: m3_041

Responsabilidad unica: crear la tabla payment.vinculacion_mp con sus
restricciones e indices para almacenar la vinculacion OAuth del propietario
con su cuenta de Mercado Pago.

NO modifica datos ni tablas existentes.

Baseline: m3_041 (head).
"""
from alembic import op

revision = "m3_042"
down_revision = "m3_041"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE payment.vinculacion_mp (
            id UUID NOT NULL DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL,
            mp_user_id BIGINT NOT NULL,
            mp_email VARCHAR(200),
            mp_nickname VARCHAR(120),
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            public_key VARCHAR(200),
            token_type VARCHAR(40) NOT NULL DEFAULT 'Bearer',
            expires_in INTEGER,
            expires_at TIMESTAMP WITHOUT TIME ZONE,
            scope TEXT,
            estado VARCHAR(25) NOT NULL DEFAULT 'vinculada',
            ultimo_error TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT pk_vinculacion_mp PRIMARY KEY (id),
            CONSTRAINT fk_vinculacion_mp_usuario_id_usuario
                FOREIGN KEY (usuario_id) REFERENCES auth.usuario (id) ON DELETE CASCADE,
            CONSTRAINT ck_vinculacion_mp_estado_check
                CHECK (estado IN ('vinculada', 'expirada', 'revocada', 'error'))
        );
    """)

    op.execute("""
        CREATE UNIQUE INDEX uq_vinculacion_mp_usuario_id
        ON payment.vinculacion_mp (usuario_id);
    """)

    op.execute("""
        CREATE INDEX ix_payment_vinculacion_mp_mp_user_id
        ON payment.vinculacion_mp (mp_user_id);
    """)

    op.execute("""
        CREATE INDEX ix_payment_vinculacion_mp_estado
        ON payment.vinculacion_mp (estado);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS payment.ix_payment_vinculacion_mp_estado;")
    op.execute("DROP INDEX IF EXISTS payment.ix_payment_vinculacion_mp_mp_user_id;")
    op.execute("DROP INDEX IF EXISTS payment.uq_vinculacion_mp_usuario_id;")
    op.execute("DROP TABLE IF EXISTS payment.vinculacion_mp;")
