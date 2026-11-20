"""Agregar codigo postal a ciudades y ciudad a tenants

Revision ID: c6bc69974304
Revises: 20260721_191150_initial
Create Date: 2026-07-23 17:06:00

"""

revision = 'c6bc69974304'
down_revision = '20260721_191150_initial'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Agregar codigo_postal a geo.ciudad, ciudad_id y direccion a tenant.control_base.
    Los campos de suspension ya existen en tenant.control_base (creados en migracion inicial)."""
    
    # 1. Agregar campo codigo_postal a geo.ciudad
    op.add_column(
        'ciudad',
        sa.Column('codigo_postal', sa.VARCHAR(20), nullable=True),
        schema='geo'
    )
    
    # 2. Crear indice para busquedas rapidas por codigo postal
    op.create_index(
        'idx_ciudad_codigo_postal',
        'ciudad',
        ['codigo_postal'],
        unique=False,
        schema='geo'
    )
    
    # 3. Agregar campo ciudad_id a tenant.control_base
    op.add_column(
        'control_base',
        sa.Column('ciudad_id', sa.UUID(), nullable=True),
        schema='tenant'
    )
    op.create_foreign_key(
        'fk_control_base_ciudad',
        'control_base',
        'ciudad',
        ['ciudad_id'],
        ['id'],
        source_schema='tenant',
        referent_schema='geo'
    )
    
    # 4. Crear indice para busquedas rapidas por ciudad
    op.create_index(
        'idx_control_base_ciudad',
        'control_base',
        ['ciudad_id'],
        unique=False,
        schema='tenant'
    )
    
    # 5. Agregar campo direccion a tenant.control_base
    op.add_column(
        'control_base',
        sa.Column('direccion', sa.VARCHAR(255), nullable=True),
        schema='tenant'
    )
    
    # 6. Sincronizar tenants existentes con ciudades
    op.execute("""
        DO $$
        DECLARE
            tenant_record RECORD;
            ciudad_id_found UUID;
        BEGIN
            FOR tenant_record IN 
                SELECT id, nombre 
                FROM tenant.control_base 
                WHERE ciudad_id IS NULL 
            LOOP
                SELECT id INTO ciudad_id_found 
                FROM geo.ciudad 
                WHERE nombre ILIKE tenant_record.nombre 
                LIMIT 1;
                
                IF ciudad_id_found IS NOT NULL THEN
                    UPDATE tenant.control_base 
                    SET ciudad_id = ciudad_id_found 
                    WHERE id = tenant_record.id;
                END IF;
            END LOOP;
        END $$;
    """)


def downgrade() -> None:
    """Revertir los cambios en orden inverso."""
    
    # Eliminar direccion
    op.drop_column('control_base', 'direccion', schema='tenant')
    
    # Eliminar FK e indice de ciudad
    op.drop_constraint(
        'fk_control_base_ciudad',
        'control_base',
        type_='foreignkey',
        schema='tenant'
    )
    op.drop_index('idx_control_base_ciudad', table_name='control_base', schema='tenant')
    op.drop_column('control_base', 'ciudad_id', schema='tenant')
    
    # Eliminar indice y columna de codigo postal
    op.drop_index('idx_ciudad_codigo_postal', table_name='ciudad', schema='geo')
    op.drop_column('ciudad', 'codigo_postal', schema='geo')