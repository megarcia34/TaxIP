"""codigo_metadatos

Revision ID: b25539ad0e3e
Revises: 514f60fb4bab
Create Date: 2026-09-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b25539ad0e3e'
down_revision = '514f60fb4bab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crear tabla auth.codigo_metadatos para almacenar metadatos
    de los codigos de verificacion de tipo INICIO_TURNO.
    """

    # ============================================================
    # 1. CREAR TABLA: auth.codigo_metadatos
    # ============================================================
    op.create_table(
        'codigo_metadatos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('codigo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contrato_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('propietario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['codigo_id'], ['auth.codigo_verificacion.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contrato_id'], ['fleet.contrato_vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['propietario_id'], ['auth.usuario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )

    # ============================================================
    # 2. CREAR INDICES PARA auth.codigo_metadatos
    # ============================================================
    op.create_index('idx_codigo_metadatos_codigo_id', 'codigo_metadatos', ['codigo_id'], schema='auth')
    op.create_index('idx_codigo_metadatos_contrato_id', 'codigo_metadatos', ['contrato_id'], schema='auth')
    op.create_index('idx_codigo_metadatos_vehiculo_id', 'codigo_metadatos', ['vehiculo_id'], schema='auth')
    op.create_index('idx_codigo_metadatos_propietario_id', 'codigo_metadatos', ['propietario_id'], schema='auth')

    # ============================================================
    # 3. MODIFICAR: auth.codigo_verificacion - Agregar valores CHECK para tipo
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.check_constraints cc
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.constraint_name = 'chk_codigo_verificacion_tipo'
                  AND tc.table_schema = 'auth'
                  AND tc.table_name = 'codigo_verificacion'
            ) THEN
                ALTER TABLE auth.codigo_verificacion DROP CONSTRAINT chk_codigo_verificacion_tipo;
            END IF;
        END $$;
    """)

    op.execute("""
        ALTER TABLE auth.codigo_verificacion
        ADD CONSTRAINT chk_codigo_verificacion_tipo
        CHECK (tipo IN ('REGISTRO_CHOFER', 'INICIO_TURNO', 'RECUPERACION_PASSWORD'))
    """)

    # ============================================================
    # 4. MODIFICAR: auth.codigo_verificacion - Agregar columna metadata (JSONB opcional)
    # ============================================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'auth'
                  AND table_name = 'codigo_verificacion'
                  AND column_name = 'metadata'
            ) THEN
                ALTER TABLE auth.codigo_verificacion
                ADD COLUMN metadata JSONB DEFAULT NULL;
            END IF;
        END $$;
    """)

    # ============================================================
    # 5. CREAR INDICE PARA busqueda de codigos por tipo y usado
    # ============================================================
    op.create_index('idx_codigo_verificacion_tipo_usado', 'codigo_verificacion', ['tipo', 'usado'], schema='auth')
    op.create_index('idx_codigo_verificacion_codigo_tipo_usado', 'codigo_verificacion', ['codigo', 'tipo', 'usado'], schema='auth')


def downgrade() -> None:
    """Revertir los cambios"""

    # 5. Eliminar indices
    op.drop_index('idx_codigo_verificacion_codigo_tipo_usado', table_name='codigo_verificacion', schema='auth')
    op.drop_index('idx_codigo_verificacion_tipo_usado', table_name='codigo_verificacion', schema='auth')

    # 4. Eliminar columna metadata
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'auth'
                  AND table_name = 'codigo_verificacion'
                  AND column_name = 'metadata'
            ) THEN
                ALTER TABLE auth.codigo_verificacion DROP COLUMN metadata;
            END IF;
        END $$;
    """)

    # 3. Eliminar constraint (no existia originalmente, no recrear)
    op.execute("""
        ALTER TABLE auth.codigo_verificacion DROP CONSTRAINT IF EXISTS chk_codigo_verificacion_tipo;
    """)

    # 2. Eliminar indices de codigo_metadatos
    op.drop_index('idx_codigo_metadatos_propietario_id', table_name='codigo_metadatos', schema='auth')
    op.drop_index('idx_codigo_metadatos_vehiculo_id', table_name='codigo_metadatos', schema='auth')
    op.drop_index('idx_codigo_metadatos_contrato_id', table_name='codigo_metadatos', schema='auth')
    op.drop_index('idx_codigo_metadatos_codigo_id', table_name='codigo_metadatos', schema='auth')

    # 1. Eliminar tabla
    op.drop_table('codigo_metadatos', schema='auth')