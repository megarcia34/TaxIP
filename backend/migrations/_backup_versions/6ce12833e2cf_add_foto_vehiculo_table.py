

"""add foto vehiculo table

Revision ID: 6ce12833e2cf
Revises: d1e5496783df
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '6ce12833e2cf'
down_revision = 'd1e5496783df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear tabla foto_vehiculo
    op.create_table(
        'foto_vehiculo',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('public_id', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('orden', sa.Integer(), server_default='0', nullable=True),
        sa.Column('es_principal', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('subida_por', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['fleet.vehiculo.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subida_por'], ['auth.usuario.id'], ondelete='SET NULL'),
        schema='fleet'
    )

    # 2. Crear índices
    op.create_index('idx_foto_vehiculo_vehiculo', 'foto_vehiculo', ['vehiculo_id'], schema='fleet')
    
    # Índice parcial: solo indexa las filas donde es_principal = TRUE
    op.create_index(
        'idx_foto_vehiculo_principal', 
        'foto_vehiculo', 
        ['vehiculo_id', 'es_principal'], 
        schema='fleet',
        postgresql_where=sa.text('es_principal = TRUE')
    )

    # 3. Crear función del trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION fleet.actualizar_foto_principal()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.es_principal = TRUE THEN
                UPDATE fleet.foto_vehiculo 
                SET es_principal = FALSE 
                WHERE vehiculo_id = NEW.vehiculo_id AND id != NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 4. Crear trigger
    op.execute("""
        CREATE TRIGGER trigger_foto_principal
            BEFORE INSERT OR UPDATE ON fleet.foto_vehiculo
            FOR EACH ROW
            EXECUTE FUNCTION fleet.actualizar_foto_principal();
    """)


def downgrade() -> None:
    # 1. Eliminar trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_foto_principal ON fleet.foto_vehiculo")
    
    # 2. Eliminar función del trigger
    op.execute("DROP FUNCTION IF EXISTS fleet.actualizar_foto_principal()")
    
    # 3. Eliminar índices
    op.drop_index('idx_foto_vehiculo_principal', table_name='foto_vehiculo', schema='fleet')
    op.drop_index('idx_foto_vehiculo_vehiculo', table_name='foto_vehiculo', schema='fleet')
    
    # 4. Eliminar tabla
    op.drop_table('foto_vehiculo', schema='fleet')